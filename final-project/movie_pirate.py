#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  movie_pirate.py
#
#  Copyright 2014 tadl <tadl@taufderl.de>
#
import sys
import getopt
import xml.etree.ElementTree as ET
from collections import OrderedDict
import string
import os
import json
from math import log
import re
import operator

DEBUG = False

POS_DIR = 'pos/'
PARSED_DIR = 'parsed/'
TEXT_DIR = 'text/'
META_DIR = 'metacritic+starpower+holiday+revenue+screens+reviews/'
WEKA_JAR_PATH = './weka.jar'

STOPWORDS_FILE = 'STOPWORDS'
#STOPWORDS_FILE = 'MOST_FREQUENT_WORDS'

ARFF_PATH = './arff/'
FEATURES_FILE = 'features.json'

def tokenize(string):
  tokens = []
  string = string.replace("--",'')

  chars = "…’‘´–—_#+‚•½$%&¡!?.,\"“”*/\\()[]{}<>=\n:;\xad"

  for char in chars:
    string = string.replace(char, '')

  tokens = string.lower().split()
  return tokens

def replace_crucial_characters(string):
    string = string.replace('\'', ';quote;')
    string = string.replace(',', ';komma;')
    #string = string.replace(' ', ';whitespace;')
    string = string.replace('\"', ';doublequote;')
    if string == '':
      string = ';empty;'
    return string

def read_movies_file(input_file):
  movies = []
  nbc = 0
  with open(input_file, 'r') as movie_file:

    for line in movie_file.readlines():
      title = line[:-5] #remove .xml\n at the end
      movie = Movie(title)

      tree = ET.parse(movie.meta_file)
      root = tree.getroot()

      # weekend_gross = yvalue
      yvalue = root.find('weekend_gross').text
      yvalue = yvalue[1:].replace(',','')
      movie.yvalue = int(yvalue)

      # genres
      genres = root.find('genres').findall('genre')
      movie.genres = [d.text for d in genres if d.text is not None]

      # directors
      directors = root.find('directors').findall('director')
      movie.directors = [d.text for d in directors if d.text is not None]

      # actors
      actors = root.find('actors').findall('actor')
      movie.actors = [a.text for a in actors if a.text is not None]

      # authors
      authors = root.find('authors').findall('author')
      movie.authors = [a.text for a in authors if a.text is not None]

      #screens
      screens = root.find('number_of_screens').text
      movie.screens = screens.replace(',','')

      #production_budget
      node = root.find('production_budget')
      if node == None:
        movie.production_budget = '?'
      else:
        budget = node.text
        budget = budget[1:].replace(',','')
        movie.production_budget = budget

      #num_highest_grossing_actors
      node = root.find('num_highest_grossing_actors')
      if node == None:
        movie.num_highest_grossing_actors = '?'
      else:
        movie.num_highest_grossing_actors = node.text

      # running_time
      rt = root.find('running_time').text
      if rt.isdigit():
        movie.running_time = rt
      else:
        movie.running_time = '?'

      # rating
      movie.rating = root.find('rating').text

      #company
      movie.company = root.find('company').text

      #origin
      origins = root.find('origins').findall('origin')
      movie.origins = [o.text for o in origins]

      #summer realease
      summer_release = root.find('summer_release').text
      if summer_release == 'false':
        movie.summer_release = 0
      elif summer_release == 'true':
        movie.summer_release = 1
      else:
        print('No summer release info for %s'%movie)

      #christmas realease
      christmas_release = root.find('christmas_release').text
      if christmas_release == 'false':
        movie.christmas_release = 0
      elif christmas_release == 'true':
        movie.christmas_release = 1
      else:
        print('No christmas release info for %s'%movie)

      #memorial realease
      memorial_release = root.find('memorial_release').text
      if memorial_release == 'false':
        movie.memorial_release = 0
      elif memorial_release == 'true':
        movie.memorial_release = 1
      else:
        print('No memorial release info for %s'%movie)

      #independence realease
      independence_release = root.find('independence_release').text
      if independence_release == 'false':
        movie.independence_release = 0
      elif independence_release == 'true':
        movie.independence_release = 1
      else:
        print('No independence release info for %s'%movie)

      #labor realease
      labor_release = root.find('labor_release').text
      if labor_release == 'false':
        movie.labor_release = 0
      elif labor_release == 'true':
        movie.labor_release = 1
      else:
        print('No labor release info for %s'%movie)

      # snippets
      nodes = root.find('reviews').findall('review')
      snippets = [node.find('snippet').text for node in nodes]

      movie.snippets = [tokenize(s) for s in snippets if s is not None]

      # snippet writers
      nodes = root.find('reviews').findall('review')
      movie.snippet_writers = [node.find('critic').text for node in nodes]

      # append to return list
      movies.append(movie)

  return movies

########################################################################
########################################################################
#########################      Movie       #############################
########################################################################
########################################################################
class Movie:
  def __init__(self, filename, yvalue = 0):
    self.meta_file = ''.join([META_DIR,filename,'.xml'])
    self.pos_file = POS_DIR + filename
    self.parsed_file = PARSED_DIR + filename
    self.text_file = TEXT_DIR + filename
    self.title = replace_crucial_characters(filename)

    self.genres = []
    self.directors = []
    self.actors = []
    self.authors = []
    self.screens = None
    self.company = None
    self.origins = []
    self.production_budget = None
    self.num_highest_grossing_actors = None
    self.running_time = None
    self.rating = None

    self.summer_release = None
    self.christmas_release = None
    self.memorial_release = None
    self.independence_release = None
    self.labor_release = None

    self.snippets = []
    self.snippet_writers = []

    self.yvalue = yvalue
    self.arff_line = []
    self.features = OrderedDict()

  def add_feature(self, feature_no, value):
    if not feature_no in self.features:
      self.features[feature_no] = value
    else:
      if value == 1:
        self.features[feature_no] += 1

  def get_arff_line(self, yindex):
    for feature_no, value in self.features.items():
      self.arff_line.append('%i %s' %(feature_no, value))
    return '{'+', '.join(self.arff_line)+', '+str(yindex)+' '+str(self.yvalue)+'}\n'

  def __repr__(self):
    return 'Movie [%s]: <<%s>>' % (self.title, self.yvalue)


########################################################################
########################################################################
####################     FEATURE GENERATOR      ########################
########################################################################
########################################################################
class FeatureGenerator:

  def __init__(self, input_file):
    print("\n*************** FeatureGenerator ***************")
    self.input_file = input_file
    print('  > read movies from [%s]'%input_file)
    self.movies = read_movies_file(input_file)
    print('  > found %i movies'%len(self.movies))

    self.features = OrderedDict()

    self.STOPWORDS = []
    with open(STOPWORDS_FILE, 'r') as fwf:
      for line in fwf.readlines():
        self.STOPWORDS.append(line[:-1])

    #print(self.STOPWORDS)
    #print(len(self.STOPWORDS))

    if (DEBUG):
      for i,m in enumerate(self.movies):
        print('%i\t%s'%(i+1,m.title))


####################   FEATURE SET DEFINITIONS   #######################

  def add_featuresets(self, SETS):
    add = {  1 : self.add_featureset_1,
             2 : self.add_featureset_2,
             3 : self.add_featureset_3,
             4 : self.add_featureset_4,
             5 : self.add_featureset_5,
             6 : self.add_featureset_6,
             7 : self.add_featureset_7,
             8 : self.add_featureset_8,
             9 : self.add_featureset_9,
             10 : self.add_featureset_10,
             11 : self.add_featureset_11
          }
    for number in SETS:
      add[number]()

  def add_features(self, FEATURE_NAMES):
    add = {  'TEST'   : self.add_featureset_test,
             'TITLE'  : self.add_feature_title,
             'ALL'    : self.add_featureset_all,
             'BEST'    : self.add_featureset_11
          }
    for name in FEATURE_NAMES:
      add[name]()


  def add_featureset_all(self):
    # METADATA FEATURES
    self.add_feature_origin_USA()                     # P 1
  # self.add_feature_origin(5)                        #   1b (worse)
    self.add_feature_runnning_time()                  # P 2
  # self.add_feature_log_production_budget()          # P 3
    self.add_feature_production_budget()              #   3 better!
    self.add_feature_number_of_screens()              # P 4
    self.add_feature_genres(1)                        # P 5
    self.add_feature_rating()                         # P 6
    self.add_feature_summer_release()                 # P 7
    self.add_feature_christmas_release()              # P 7
    self.add_feature_memorial_release()               # P 7
    self.add_feature_independence_release()           # P 7
    self.add_feature_labor_release()                  # P 7
  # self.add_feature_oscar_actors()                   # P 8 ->CHEATING!
  # self.add_feature_oscar_directors()                # P 8 ->CHEATING!
    self.add_feature_num_highest_grossing_actors()    # P 9

    self.add_feature_x_most_frequent_snippet_writers(20)

    # note very sucessful
  # self.add_feature_directors(3)                     #
  # self.add_feature_actors(7)                        #
  # self.add_feature_authors(4)                       #
  # self.add_feature_company(5)                       #

    # REVIEW FEATURES
    #self.add_feature_word_unigrams(90)
    #self.add_feature_word_bigrams(60)
    #self.add_feature_word_trigrams(30)
    # not yet implemented
    #self.add_feature_pos_unigrams()
    #self.add_feature_pos_bigrams()
    #self.add_feature_pos_trigrams()
    #self.add_feature_dependency_triples()


  def add_featureset_test(self):
    print('  > Using featureset 11 [test]')
    #self.add_feature_word_bigrams(45)
    self.add_feature_x_most_frequent_word_unigrams(50)
    self.add_feature_x_most_frequent_word_bigrams(50)
    self.add_feature_x_most_frequent_word_trigrams(50)



  def add_featureset_1(self):
    print('  > Using featureset 1 [original metadata only]')
    self.add_feature_origin_USA()                     # P 1
    self.add_feature_runnning_time()                  # P 2
    self.add_feature_log_production_budget()          # P 3
    self.add_feature_number_of_screens()              # P 4
    self.add_feature_genres(1)                        # P 5
    self.add_feature_rating()                         # P 6
    self.add_feature_summer_release()                 # P 7
    self.add_feature_christmas_release()              # P 7
    self.add_feature_memorial_release()               # P 7
    self.add_feature_independence_release()           # P 7
    self.add_feature_labor_release()                  # P 7
    self.add_feature_num_highest_grossing_actors()    # P 9

  def add_featureset_2(self):
    print('  > Using featureset 2 [original metadata + all origins]')
    self.add_feature_origin(5)                        #   1b (worse)
    self.add_feature_runnning_time()                  # P 2
    self.add_feature_log_production_budget()          # P 3
    self.add_feature_number_of_screens()              # P 4
    self.add_feature_genres(1)                        # P 5
    self.add_feature_rating()                         # P 6
    self.add_feature_summer_release()                 # P 7
    self.add_feature_christmas_release()              # P 7
    self.add_feature_memorial_release()               # P 7
    self.add_feature_independence_release()           # P 7
    self.add_feature_labor_release()                  # P 7
    self.add_feature_num_highest_grossing_actors()    # P 9

  def add_featureset_3(self):
    print('  > Using featureset 3 [original metadata using plain budget]')
    self.add_feature_origin_USA()                     # P 1
    self.add_feature_runnning_time()                  # P 2
    self.add_feature_production_budget()              #   3 better!
    self.add_feature_number_of_screens()              # P 4
    self.add_feature_genres(1)                        # P 5
    self.add_feature_rating()                         # P 6
    self.add_feature_summer_release()                 # P 7
    self.add_feature_christmas_release()              # P 7
    self.add_feature_memorial_release()               # P 7
    self.add_feature_independence_release()           # P 7
    self.add_feature_labor_release()                  # P 7
    self.add_feature_num_highest_grossing_actors()    # P 9

  def add_featureset_4(self):
    print('  > Using featureset 4 [original metadata using plain budget + authors - genres]')
    self.add_feature_origin_USA()                     # P 1
    self.add_feature_runnning_time()                  # P 2
    self.add_feature_production_budget()              #   3 better!
    self.add_feature_number_of_screens()              # P 4

    self.add_feature_rating()                         # P 6
    self.add_feature_summer_release()                 # P 7
    self.add_feature_christmas_release()              # P 7
    self.add_feature_memorial_release()               # P 7
    self.add_feature_independence_release()           # P 7
    self.add_feature_labor_release()                  # P 7
    self.add_feature_num_highest_grossing_actors()    # P 9
    self.add_feature_authors(4)                       #

  def add_featureset_11(self):
    print('  > Using featureset 4 [original metadata using plain budget + authors - genres]')
    self.add_feature_origin_USA()                     # P 1
    self.add_feature_runnning_time()                  # P 2
    self.add_feature_production_budget()              #   3 better!
    self.add_feature_number_of_screens()              # P 4

    self.add_feature_rating()                         # P 6
    self.add_feature_summer_release()                 # P 7
    self.add_feature_christmas_release()              # P 7
    self.add_feature_memorial_release()               # P 7
    self.add_feature_independence_release()           # P 7
    self.add_feature_labor_release()                  # P 7
    self.add_feature_num_highest_grossing_actors()    # P 9
    self.add_feature_authors(4)                       #
    self.add_feature_x_most_frequent_snippet_writers(20)

  def add_featureset_5(self):
    print('  > Using featureset 5 [word uni-/bi-/tri-grams]')
    self.add_feature_word_unigrams(100)
    self.add_feature_word_bigrams(60)
    self.add_feature_word_trigrams(40)

  def add_featureset_6(self):
    print('  > Using featureset 6 [word uni-/bi-/tri-grams]')
    self.add_feature_word_unigrams(200)
    self.add_feature_word_bigrams(100)
    self.add_feature_word_trigrams(50)

  def add_featureset_7(self):
    print('  > Using featureset 7 [word uni-/bi-/tri-grams]')
    self.add_feature_word_unigrams(250)
    self.add_feature_word_bigrams(120)
    self.add_feature_word_trigrams(40)

  def add_featureset_8(self):
    print('  > Using featureset 8 [word uni-/bi-/tri-grams]')
    self.add_feature_x_most_frequent_word_unigrams(100)
    self.add_feature_x_most_frequent_word_bigrams(100)
    self.add_feature_x_most_frequent_word_trigrams(100)

  def add_featureset_9(self):
    print('  > Using featureset 9 [word uni-/bi-/tri-grams]')
    self.add_feature_x_most_frequent_word_unigrams(150)
    self.add_feature_x_most_frequent_word_bigrams(150)

  def add_featureset_10(self):
    print('  > Using featureset 10 [word uni-/bi-/tri-grams]')
    self.add_feature_x_most_frequent_word_unigrams(150)
    self.add_feature_x_most_frequent_word_bigrams(150)
    self.add_feature_x_most_frequent_word_trigrams(50)

######################   FEATURE DEFINITIONS   #########################

  def add_feature_title(self):
    self.features['title'] = 'string'
    titles = []
    for movie in self.movies:
      titles.append(movie.title)

    self.features['title'] = titles

  def add_feature_title_length(self):
    self.features['title_length'] = 'numeric'

  def add_feature_genres(self, MIN_NUMBER):
    genres = OrderedDict()
    for movie in self.movies:
      for genre in movie.genres:
        if genre == None:
          print('%s <- %s'%(genre,movie))
        if genre in genres:
          genres[genre] += 1
        else:
          genres[genre] = 1

    for d,n in genres.items():
      if n>=MIN_NUMBER:
        self.features['<GENRE>'+replace_crucial_characters(d)] = 'numeric'

  def add_feature_directors(self, MIN_NUMBER):
    directors = OrderedDict()
    for movie in self.movies:
      for director in movie.directors:
        if director in directors:
          directors[director] += 1
        else:
          directors[director] = 1

    for d,n in directors.items():
      if n>=MIN_NUMBER:
        self.features['<DIRECTOR>'+replace_crucial_characters(d)] = 'numeric'

  def add_feature_actors(self,MIN_NUMBER):
    actors = OrderedDict()
    for movie in self.movies:
      for actor in movie.actors:
        if actor in actors:
          actors[actor] += 1
        else:
          actors[actor] = 1
    for d,n in actors.items():
      if n>=MIN_NUMBER:
        self.features['<ACTOR>'+replace_crucial_characters(d)] = 'numeric'

  def add_feature_authors(self,MIN_NUMBER):
    authors = OrderedDict()
    for movie in self.movies:
      for author in movie.authors:
        if author in authors:
          authors[author] += 1
        else:
          authors[author] = 1

    for d,n in authors.items():
      if n>=MIN_NUMBER:
        self.features['<AUTHOR>'+replace_crucial_characters(d)] = 'numeric'

  def add_feature_company(self,MIN_NUMBER):
    companies = OrderedDict()
    for movie in self.movies:
      company = movie.company
      if company in companies:
        companies[company] += 1
      else:
        companies[company] = 1

    for d,n in companies.items():
      if n>=MIN_NUMBER:
        self.features['<COMPANY>'+replace_crucial_characters(d)] = 'numeric'

  def add_feature_origin(self, MIN_NUMBER):
    origins = OrderedDict()
    for movie in self.movies:
      for origin in movie.origins:
        if origin in origins:
          origins[origin] += 1
        else:
          origins[origin] = 1

    for d,n in origins.items():
      if n>=MIN_NUMBER:
        self.features['<ORIGIN>'+replace_crucial_characters(d)] = 'numeric'

  def add_feature_origin_USA(self):
    self.features['<ORIGIN_USA>'] = 'numeric'

  def add_feature_runnning_time(self):
    self.features['<RUNNING_TIME>'] = 'numeric'

  def add_feature_rating(self):
    ratings = ['G','PG','PG-13','R','NC-17']
    for rating in ratings:
      self.features['<RATING>'+rating] = 'numeric'

  def add_feature_production_budget(self):
    self.features['<PRODUCTION_BUDGET>'] = 'numeric'

  def add_feature_log_production_budget(self):
    self.features['<LOG_PRODUCTION_BUDGET>'] = 'numeric'

  def add_feature_num_highest_grossing_actors(self):
    self.features['<NUM_GROSSING_ACTORS>'] = 'numeric'

  def add_feature_summer_release(self):
    self.features['<RELEASE>summer_release'] = 'numeric'

  def add_feature_christmas_release(self):
    self.features['<RELEASE>christmas_release'] = 'numeric'

  def add_feature_memorial_release(self):
    self.features['<RELEASE>memorial_release'] = 'numeric'

  def add_feature_independence_release(self):
    self.features['<RELEASE>independence_release'] = 'numeric'

  def add_feature_labor_release(self):
    self.features['<RELEASE>labor_release'] = 'numeric'

  def add_feature_number_of_screens(self):
    self.features['<NUMBER_OF_SCREENS>'] = 'numeric'

  def add_feature_oscar_actors(self):
    self.features['<OSCAR_ACTORS>'] = 'numeric'

  def add_feature_oscar_directors(self):
    self.features['<OSCAR_DIRECTORS>'] = 'numeric'

  def add_feature_x_most_frequent_snippet_writers(self,NUMBER):
    snippet_writers = OrderedDict()
    for movie in self.movies:
      for snippet_writer in movie.snippet_writers:
        if snippet_writer in snippet_writers:
          snippet_writers[snippet_writer] += 1
        else:
          snippet_writers[snippet_writer] = 1

    for d,n in sorted(snippet_writers.items(), key=operator.itemgetter(1))[-NUMBER:]:
      #print('%s %i'%(d,n))
      self.features['<SNIPPET_WRITER>'+replace_crucial_characters(d)] = 'numeric'

  ## REVIEW TEXT FEATURES

  def add_feature_word_unigrams(self, MIN_NUMBER):
    unigrams = OrderedDict()
    for movie in self.movies:
      for snippet in movie.snippets:
        for word in snippet:
          if word in unigrams:
            unigrams[word] += 1
          elif word not in self.STOPWORDS:
            unigrams[word] = 1
          #else:
            #print('skip %s because is in STOPWORD'%word)
    for word,n in unigrams.items():
      if n>=MIN_NUMBER:
        self.features['<WORD_UNIGRAM>'+replace_crucial_characters(word)] = 'numeric'


  def add_feature_word_bigrams(self, MIN_NUMBER):
    bigrams = OrderedDict()
    for movie in self.movies:
      for snippet in movie.snippets:
        for w1, w2 in zip(snippet[:-1], snippet[1:]):
          if (w1,w2) in bigrams:
            bigrams[(w1,w2)] += 1
          elif (w1 not in self.STOPWORDS and
                w2 not in self.STOPWORDS):
            bigrams[(w1,w2)] = 1
          #else:
            #if w1 in self.STOPWORDS: x = True
            #if w2 in self.STOPWORDS: y = True
            #print('skip %s=%i,%s=%i because is in STOPWORDS'%(w1,x,w2,y))
    for bigram,n in bigrams.items():
      if n>=MIN_NUMBER:
        #print('%s        -> %i'%(bigram, n))
        self.features['<WORD_BIGRAM>'+replace_crucial_characters(' '.join(bigram))] = 'numeric'

  def add_feature_word_trigrams(self, MIN_NUMBER):
    trigrams = OrderedDict()

    for movie in self.movies:
      for snippet in movie.snippets:
        for w1, w2, w3 in [snippet[i:i+3] for i in range(len(snippet) - 2)]:
          if (w1,w2,w3) in trigrams:
            trigrams[(w1,w2,w3)] += 1
          elif (w1 not in self.STOPWORDS or
                w2 not in self.STOPWORDS or
                w3 not in self.STOPWORDS):
            trigrams[(w1,w2,w3)] = 1
          #else:
            #if w1 in self.STOPWORDS: x = True
            #if w2 in self.STOPWORDS: y = True
            #if w3 in self.STOPWORDS: z = True
            #print('skip %s=%i,%s=%i,%s=%i because is in STOPWORDS'%(w1,x,w2,y,w3,z))
    for trigram,n in trigrams.items():
      if n>=MIN_NUMBER:
        self.features['<WORD_TRIGRAM>'+replace_crucial_characters(' '.join(trigram))] = 'numeric'


  # ADD EXACTLY X MOST FREQUENT FEATURES

  def add_feature_x_most_frequent_word_unigrams(self, NUMBER):
    unigrams = {}

    for movie in self.movies:
      for snippet in movie.snippets:
        for word in snippet:
          if word in unigrams:
            unigrams[word] += 1
          elif word not in self.STOPWORDS:
            unigrams[word] = 1
    for word,n in sorted(unigrams.items(), key=operator.itemgetter(1))[-NUMBER:]:
      self.features['<WORD_UNIGRAM>'+replace_crucial_characters(word)] = 'numeric'


  def add_feature_x_most_frequent_word_bigrams(self, NUMBER):
    bigrams = {}
    for movie in self.movies:
      for snippet in movie.snippets:
        for w1, w2 in zip(snippet[:-1], snippet[1:]):
          if (w1,w2) in bigrams:
            bigrams[(w1,w2)] += 1
          elif (w1 not in self.STOPWORDS and
                w2 not in self.STOPWORDS):
            bigrams[(w1,w2)] = 1
    for bigram,n in sorted(bigrams.items(), key=operator.itemgetter(1))[-NUMBER:]:
      self.features['<WORD_BIGRAM>'+replace_crucial_characters(' '.join(bigram))] = 'numeric'

  def add_feature_x_most_frequent_word_trigrams(self, NUMBER):
    trigrams = {}
    for movie in self.movies:
      for snippet in movie.snippets:
        for w1, w2, w3 in [snippet[i:i+3] for i in range(len(snippet) - 2)]:
          if (w1,w2,w3) in trigrams:
            trigrams[(w1,w2,w3)] += 1
          elif (w1 not in self.STOPWORDS or
                w2 not in self.STOPWORDS or
                w3 not in self.STOPWORDS):
            trigrams[(w1,w2,w3)] = 1
    for trigram,n in sorted(trigrams.items(), key=operator.itemgetter(1))[-NUMBER:]:
      self.features['<WORD_TRIGRAM>'+replace_crucial_characters(' '.join(trigram))] = 'numeric'


  def add_feature_pos_unigrams(self, MIN_NUMBER):
    x = 1 #TODO

  def add_feature_pos_bigrams(self, MIN_NUMBER):
    x = 1 #TODO

  def add_feature_pos_trigrams(self, MIN_NUMBER):
    x = 1 #TODO

  def add_feature_dependency_triples(self, MIN_NUMBER):
    x = 1 #TODO

  def write_feature_file(self):
    print('  > extracted %i features'%(len(self.features)))
    print('  > write features to [%s]'%(FEATURES_FILE))
    outfile = open(FEATURES_FILE, 'w')
    json.dump(self.features,outfile)


########################################################################
########################################################################
#########################  ARFF GENERATOR  #############################
########################################################################
########################################################################

class ARFFGenerator:

  def __init__(self, input_file):
    print("\n*************** ARFFGenerator    ***************")
    self.input_file = input_file
    print('  > read movies from [%s]'%input_file)
    self.movies = read_movies_file(input_file)
    print('  > found %i movies'%len(self.movies))

    print('  > read features from [%s]'%FEATURES_FILE)
    features_file = open(FEATURES_FILE, 'r')
    self.features = OrderedDict(json.load(features_file,object_pairs_hook=OrderedDict))
    print('  > found %i features'%len(self.features))



  def apply_all_features(self):
    print('  > apply features to [%s]'%self.input_file)

    feature_length = len(self.features)
    for FEATURE_NUMBER, (FEATURE_NAME, FEATURE_VALUES) in enumerate(self.features.items()):
      #print('  %i/%i: %s'%(FEATURE_NUMBER,feature_length,FEATURE_NAME))
      sys.stdout.write('\r                                                              ')
      sys.stdout.flush
      sys.stdout.write('\r  > %i/%i: %s'%(FEATURE_NUMBER+1,feature_length,FEATURE_NAME))
      sys.stdout.flush

      if FEATURE_NAME == 'title':
        for movie in self.movies:
          word = movie.title
          word = replace_crucial_characters(word)
          movie.add_feature(FEATURE_NUMBER, word)

      elif FEATURE_NAME == 'title_length':
        for movie in self.movies:
          x = len(movie.title)
          movie.add_feature(FEATURE_NUMBER, x)

      elif FEATURE_NAME.startswith('<DIRECTOR>'):
        director = FEATURE_NAME[10:]
        for movie in self.movies:
          if director in movie.directors:
            movie.add_feature(FEATURE_NUMBER, 1)

      elif FEATURE_NAME.startswith('<ACTOR>'):
        actor = FEATURE_NAME[7:]
        for movie in self.movies:
          if actor in movie.actors:
            movie.add_feature(FEATURE_NUMBER, 1)

      elif FEATURE_NAME.startswith('<AUTHOR>'):
        author = FEATURE_NAME[8:]
        for movie in self.movies:
          if author in movie.authors:
            movie.add_feature(FEATURE_NUMBER, 1)

      elif FEATURE_NAME.startswith('<ORIGIN>'):
        origin = FEATURE_NAME[8:]
        for movie in self.movies:
          if origin in movie.origins:
            movie.add_feature(FEATURE_NUMBER, 1)

      elif FEATURE_NAME == '<ORIGIN_USA>':
        for movie in self.movies:
          if 'USA' in ''.join(movie.origins):
            movie.add_feature(FEATURE_NUMBER, 1)

      elif FEATURE_NAME.startswith('<COMPANY>'):
        company = FEATURE_NAME[9:]
        for movie in self.movies:
          if company == movie.company:
            movie.add_feature(FEATURE_NUMBER, 1)

      elif FEATURE_NAME.startswith('<RELEASE>'):
        release = FEATURE_NAME[9:]
        for movie in self.movies:
          if release == 'summer_release':
            movie.add_feature(FEATURE_NUMBER,movie.summer_release)
          elif release == 'christmas_release':
            movie.add_feature(FEATURE_NUMBER,movie.christmas_release)
          elif release == 'memorial_release':
            movie.add_feature(FEATURE_NUMBER,movie.memorial_release)
          elif release == 'independence_release':
            movie.add_feature(FEATURE_NUMBER,movie.independence_release)
          elif release == 'labor_release':
            movie.add_feature(FEATURE_NUMBER,movie.labor_release)
          else:
            print('Unknown release type [%s] for %s'%(release,movie))

      elif FEATURE_NAME.startswith('<RATING>'):
        rating = FEATURE_NAME[8:]
        RATINGS = ['G','PG','PG-13','R','NC-17']
        for movie in self.movies:
          if movie.rating in RATINGS:
            if movie.rating == rating:
              movie.add_feature(FEATURE_NUMBER,1)
          else:
            movie.add_feature(FEATURE_NUMBER,'?')

      elif FEATURE_NAME == '<OSCAR_ACTORS>':
        with open('OSCAR_ACTORS', 'r') as actor_file:
          oscar_actors = [line[:-1] for line in actor_file]
          for movie in self.movies:
            n = 0
            for actor in movie.actors:
              if actor in oscar_actors:
                n += 1
                print('Found %s in %s'%(actor,movie))
            movie.add_feature(FEATURE_NUMBER,n)

      elif FEATURE_NAME == '<OSCAR_DIRECTORS>':
        with open('OSCAR_DIRECTORS', 'r') as director_file:
          oscar_directors = [line[:-1] for line in director_file]
          for movie in self.movies:
            n = 0
            for director in movie.directors:
              if director in oscar_directors:
                n += 1
                print('Found %s in %s'%(director,movie))
            movie.add_feature(FEATURE_NUMBER,n)


      elif FEATURE_NAME == '<NUMBER_OF_SCREENS>':
        for movie in self.movies:
          movie.add_feature(FEATURE_NUMBER, movie.screens)

      elif FEATURE_NAME == '<RUNNING_TIME>':
        for movie in self.movies:
          movie.add_feature(FEATURE_NUMBER, movie.running_time)

      elif FEATURE_NAME == '<PRODUCTION_BUDGET>':
        for movie in self.movies:
          movie.add_feature(FEATURE_NUMBER, movie.production_budget)

      elif FEATURE_NAME == '<LOG_PRODUCTION_BUDGET>':
        for movie in self.movies:
          budget = movie.production_budget
          if not budget == '?':
            budget = log(float(budget))
          movie.add_feature(FEATURE_NUMBER, budget)

      elif FEATURE_NAME == '<NUM_GROSSING_ACTORS>':
        for movie in self.movies:
          movie.add_feature(FEATURE_NUMBER, movie.num_highest_grossing_actors)

      elif FEATURE_NAME.startswith('<GENRE>'):
        genre = FEATURE_NAME[7:]
        for movie in self.movies:
          if genre in movie.genres:
            movie.add_feature(FEATURE_NUMBER,1)

      elif FEATURE_NAME.startswith('<SNIPPET_WRITER>'):
        snippet_writer = FEATURE_NAME[16:]
        for movie in self.movies:
          if snippet_writer in movie.snippet_writers:
            movie.add_feature(FEATURE_NUMBER, 1)

      elif FEATURE_NAME.startswith('<WORD_UNIGRAM>'):
        unigram = FEATURE_NAME[14:]
        for movie in self.movies:
          value = 0
          for snippet in movie.snippets:
            for word in snippet:
              if word == unigram:
                value += 1
          movie.add_feature(FEATURE_NUMBER,value)

      elif FEATURE_NAME.startswith('<WORD_BIGRAM>'):
        bigram = FEATURE_NAME[13:]
        for movie in self.movies:
          value = 0
          for snippet in movie.snippets:
            for words in zip(snippet[:-1], snippet[1:]):
              if ' '.join(words) == bigram:
                value += 1
          movie.add_feature(FEATURE_NUMBER,value)

      elif FEATURE_NAME.startswith('<WORD_TRIGRAM>'):
        trigram = FEATURE_NAME[14:]
        for movie in self.movies:
          value = 0
          for snippet in movie.snippets:
            for words in snippet:
              if ' '.join(words) == trigram:
                value += 1
          movie.add_feature(FEATURE_NUMBER,value)

      elif FEATURE_NAME.startswith('<POS_UNIGRAM>'):
        unigram = FEATURE_NAME[13:]
        for movie in self.movies:
          value = 0
          for snippet in movie.snippets:
            for word in snippet:
              if word == unigram:
                value += 1
          movie.add_feature(FEATURE_NUMBER,value)

      elif FEATURE_NAME.startswith('<POS_BIGRAM>'):
        bigram = FEATURE_NAME[12:]
        for movie in self.movies:
          value = 0
          for snippet in movie.snippets:
            for words in zip(snippet[:-1], snippet[1:]):
              if ' '.join(words) == bigram:
                value += 1
          movie.add_feature(FEATURE_NUMBER,value)

      elif FEATURE_NAME.startswith('<POS_TRIGRAM>'):
        trigram = FEATURE_NAME[13:]
        for movie in self.movies:
          value = 0
          for snippet in movie.snippets:
            for words in snippet:
              if ' '.join(words) == trigram:
                value += 1
          movie.add_feature(FEATURE_NUMBER,value)


      #PLACE FOR MORE FEATURE IMPLEMENTATIONS

      else:
        print('NO IMPLEMENTATION FOR FEATURE %s' %FEATURE_NAME)

    # move to next line
    sys.stdout.write('\r                                              ')
    sys.stdout.flush
    sys.stdout.write('\r  > finished!\n')

  def write_to_arff_file(self, outfile):
    print('  > write arff file to [%s]' %outfile)
    outfile = open(outfile, 'w')

    # write relation line
    outfile.write('@relation \'arff created from <%s> using movie_pirate.py\'\n' % (self.input_file))

    # write attributes
    for feature in self.features:
      if self.features[feature] == 'numeric':
        outfile.write('@attribute \'%s\' numeric\n' %feature)
      else:
        outfile.write('@attribute \'%s\' {%s}\n' %(feature, ','.join(sorted(self.features[feature]))))

    outfile.write('@attribute \'yvalue\' numeric\n')

    # write entity lines
    outfile.write('\n@data\n')
    for movie in self.movies:
      outfile.write(movie.get_arff_line(len(self.features)))




########################################################################
########################################################################
##########################      MAIN      ##############################
########################################################################
########################################################################

def usage():
  print("\n movie_pirate.py v1.0 by Tim auf der Landwehr")
  print()
  print(' Usage: movie_pirate.py')
  print('   > Add at least a single feature or a feature set')
  print('')
  print(' --fs [1..11]')
  print(' \tAdd a set of features')
  print(' --f [feature]')
  print(' \tAdd a single feature')
  print('')
  print(' --train <file>')
  print(' \tUse <file> as training file, default: <train>')
  print(' --test <file>')
  print(' \tUse <file> as training file, default: <dev>')
  print(' --run-weka')
  print(' \tRun WEKA on the generated output files,')
  print(" \t > requires [weka.jar] in $CLASSPATH or ./weka.jar\n")


if __name__ == '__main__':
  try:
    opts, args = getopt.gnu_getopt(sys.argv[1:],"ho:v",["help", "train=", "test=", "f=", "fs=", "run-weka"])
  except (getopt.GetoptError, NameError) as err:
    usage()
    sys.exit()

  # defaults
  training_file = 'train'
  test_file = 'dev'
  featureset_ids = []
  feature_names = []
  run_weka = False

  for o,v in opts:
    if o in ['--train']:
      training_file = v
    elif o in ['--test']:
      test_file = v
    elif o in ['-h','--help']:
      usage()
      sys.exit(1)
    elif o in ['--f']:
      feature_names.append(v)
    elif o in ['--fs']:
      featureset_ids.append(int(v))
    elif o in ['--run-weka']:
      run_weka = True
    else:
      print('unknown parameter %s'%o)
      sys.exit(1)

  if featureset_ids == [] and feature_names == []:
    usage()
    sys.exit(1)

  feature_string = ('+'.join('fs'+str(id) for id in featureset_ids)
                        + '_'
                        + '+'.join(feature_names))

  outfile_ending = '_'+feature_string+'.arff'

  if not os.path.exists(ARFF_PATH):
    os.makedirs(ARFF_PATH)

  training_output_file = ARFF_PATH + training_file + outfile_ending
  test_output_file = ARFF_PATH + test_file + outfile_ending

  fg = FeatureGenerator(training_file)
  fg.add_featuresets(featureset_ids)
  fg.add_features(feature_names)
  fg.write_feature_file()

  aw = ARFFGenerator(training_file)
  aw.apply_all_features()
  aw.write_to_arff_file(training_output_file)

  aw = ARFFGenerator(test_file)
  aw.apply_all_features()
  aw.write_to_arff_file(test_output_file)

  if run_weka:
    command = "java -cp %s:$CLASSPATH weka.classifiers.functions.LinearRegression -t %s -T %s"%(WEKA_JAR_PATH,training_output_file,test_output_file)
    print("\nRunning weka classifier:\n  > %s"%command)
    x = os.system(command)
    if not x == 0:
      print("Please make sure [weka.jar] is available in this directory or is in the classpath\n")
      sys.exit(x)

  else:
    print("\nTo test the output in WEKA use the following command:")
    print("\n  java [-cp weka.jar] weka.classifiers.functions.LinearRegression -t \033[1m%s\033[0m -T \033[1m%s\033[0m \n\n"%(training_output_file,test_output_file))
