#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  reuters_cluster_arff_gen.py
#
#  Copyright 2013 tadl <tadl@taufderl.de>
#
#  Task:
#  Preparing the arff file. In this assignment, you will be working on
#  text categorization using Reuters texts classified in 6 categories.
#  The file is available as /net/shared/simsuster/reuters-allcats.csv
#  (comma-separated, class label then a list of words).
#  Convert the csv file to arff.
#  Please document all processing steps that you take.
#  Report the number of documents in each class.
#
#
#
#
#
from collections import OrderedDict
import json
import re
import sys
import getopt

########################################################################
########################################################################
#########################      ENTITY      #############################
########################################################################
########################################################################
class Entity:

  def __init__(self, class_name, content):
    self.class_name = class_name
    self.content = content
    self.arff_line = ['0 '+class_name]
    self.features = OrderedDict()

  def add_feature(self, feature_no, value):
    if not feature_no in self.features:
      self.features[feature_no] = value
    else:
      if value == 1:
        self.features[feature_no] += 1

  def get_arff_line(self):
    for feature_no, value in self.features.items():
      self.arff_line.append('%i \'%s\'' %(feature_no, value))
    return '{'+', '.join(self.arff_line)+ '}\n'

  def __repr__(self):
    return '[%s] %s <<%s>> %s' % (self.named_entity, ' '.join(self.pre_words), self.name, ' '.join(self.post_words))

########################################################################
########################################################################
#######################  FEATURE GENERATOR  ############################
########################################################################
########################################################################
class FeatureGenerator:

  def __init__(self, entity_filename):
    self.entities = []
    self.classes = OrderedDict()
    self.features = OrderedDict()
    self.read_entities_from_file(entity_filename)

  def read_entities_from_file(self, filename):
    lines = open(filename, 'r').readlines()[1:]
    for i, line in enumerate(lines):
      no = len(self.entities)
      cla,con = line.split(',')
      self.entities.append(Entity(cla, con))
      if cla not in self.classes:
        self.classes[cla] = 1
      else:
        self.classes[cla] += 1

      #if len(self.entities) == no:
      #  print(line,'>>>>',i)

  def print_data(self):
    print('FeatureGenerator says:')
    print('%i entities'%len(self.entities))
    for cla,n in self.classes.items():
      print('\t[%s]   #%i'%(cla,n))

  # Add all features
  def add_features(self):


    self.add_feature_all_letters()
    #self.add_feature_all_words()
    self.add_feature_city()
    self.add_feature_date()
    self.add_feature_words_in_title()


  # ALL LETTERS
  def add_feature_all_letters(self):
    words = []
    for entity in self.entities:
      for token in entity.content.strip():
        self.features['<LETTER>'+token] = 'numeric'

  # ALL WORDS
  def add_feature_all_words(self):
    words = []
    for entity in self.entities:
      for token in entity.content.split():
        self.features['<WORD>'+token] = 'numeric'

  # CITY after 5 whitespaces '     '
  def add_feature_city(self):
    cities = []
    for entity in self.entities:
      city = re.search('    ([A-Z,\s]+)  ',entity.content)
      if not city == None:
        city = city.group(1).strip()
        #print('>'+city+'<')
        if not city in cities:
          cities.append(city)

    cities = sorted(cities)
    self.features['<CITY>'] = cities


  # DATE
  def add_feature_date(self):
    dates = []
    for entity in self.entities:
      date = re.search('     (.+)  ([A-z,\s]+[0-9]{2}) - ',entity.content)
      if (not date == None) and (len(date.group(2)) < 15):
        date = date.group(2).strip()
        #print('>'+date+'<')
        if not date in dates:
          dates.append(date)

    dates = sorted(dates)
    self.features['<DATE>'] = dates


  # WORDS IN TITLE
  def add_feature_words_in_title(self):
    words = []
    for entity in self.entities:
      title = re.search('2 ([A-Z,\s]+)     ',entity.content)
      if not title == None:
        title = title.group(1)
        #print(title, title.split())
        for token in title.split():
          self.features['<WORD_IN_TITLE>'+token] = 'numeric'

  def write_features_to_file(self, filename = 'reuters.features.json'):
    outfile = open(filename, 'w')
    json.dump(self.features,outfile)


########################################################################
########################################################################
#########################  ARFF GENERATOR  #############################
########################################################################
########################################################################
class ARFFGenerator:

  def __init__(self, entity_filename):
    self.entities = []
    self.classes = OrderedDict()
    self.features = OrderedDict()
    self.read_entities_from_file(entity_filename)
    self.read_features_from_file()

  def read_entities_from_file(self, filename):
    self.input_file = filename
    lines = open(filename, 'r').readlines()[1:]
    for i, line in enumerate(lines):
      no = len(self.entities)
      cla,con = line.split(',')
      self.entities.append(Entity(cla, con))
      if cla not in self.classes:
        self.classes[cla] = 1
      else:
        self.classes[cla] += 1

  def read_features_from_file(self, filename = 'reuters.features.json'):
    infile = open(filename, 'r')
    self.features = OrderedDict(json.load(infile,object_pairs_hook=OrderedDict))

  def print_data(self):
    print('ARFFGenerator says:')
    print('%i entities'%len(self.entities))
    for cla,n in self.classes.items():
      print('\t[%s]   #%i'%(cla,n))
    print('Features: %i'%len(self.features))
    #for feature in self.features:
    #  print('\t%s'%(feature))


  def apply_all_features_to_entities(self):

    for FEATURE_NAME, FEATURE_VALUES in self.features.items():
      feature_no = list(self.features).index(FEATURE_NAME)+1
      l = len(self.features)
      print('%i/%i: %s'%(feature_no, l, FEATURE_NAME))

      if FEATURE_NAME == '<CITY>':
        for entity in self.entities:
          city = re.search('    ([A-Z,\s]+)  ',entity.content)
          if not city == None:
            city = city.group(1).strip()
            if city in FEATURE_VALUES:
              entity.add_feature(feature_no, city)


      elif FEATURE_NAME == '<DATE>':
        for entity in self.entities:
          date = re.search('     (.+)  ([A-z,\s]+[0-9]{2}) - ',entity.content)
          if (not date == None) and (len(date.group(2)) < 15):
            date = date.group(2).strip()
            if date in FEATURE_VALUES:
              entity.add_feature(feature_no, date)

      elif FEATURE_NAME.startswith('<WORD_IN_TITLE>'):
        feature = FEATURE_NAME.split('>')[1]
        for entity in self.entities:
          title = re.search('2 ([A-Z,\s]+)     ',entity.content)
          if not title == None:
            title = title.group(1)
            #print(title, title.split())
            for token in title.split():
              if token == feature:
                entity.add_feature(feature_no, 1)

      elif FEATURE_NAME.startswith('<LETTER>'):
        feature = FEATURE_NAME.split('>')[1]
        for entity in self.entities:
          for token in entity.content.strip():
            if token == feature:
              entity.add_feature(feature_no, 1)


      elif FEATURE_NAME.startswith('<WORD>'):
        feature = FEATURE_NAME.split('>')[1]
        for entity in self.entities:
          for token in entity.content.split():
            if token == feature:
              entity.add_feature(feature_no, 1)

      else:
        print('NO IMPLEMENTATION FOR FEATURE %s' %FEATURE_NAME)
        sys.exit(1)

  def write_arff_file(self, output_file = 'ned.arff'):
    print('writing arff to %s' %output_file)
    outfile = open(output_file, 'w')

    # write realtion line
    outfile.write('@relation \'arff created from <%s> using ned_arff_generator.py\'\n' % (self.input_file))

    # write classes line
    outfile.write('@attribute @@class@@ {%s}\n' % (','.join(sorted(self.classes))))

    # write attributes
    for feature in self.features:
      if self.features[feature] == 'numeric':
        outfile.write('@attribute \'%s\' numeric\n' %feature)
      else:
        outfile.write('@attribute \'%s\' {\'%s\'}\n' %(feature, '\',\''.join(sorted(self.features[feature]))))

    # write entity lines
    outfile.write('\n@data\n')
    for entity in self.entities:
      outfile.write(entity.get_arff_line())

########################################################################
########################################################################
###############################  MAIN  #################################
########################################################################
########################################################################

def usage():
  print(' Reuters-ARFF-Generator v1.0 by Tim auf der Landwehr')
  print()
  print(' Usage: reuters_cluster_arff_gen.py')
  print('\tLoads features from [reuters.features.json] and dialectology from [reuters-allcats.csv]')
  print('\t and writes arff output to [reuters-allcats.arff]')
  print()
  print(' --features')
  print(' \tGenerates features to [reuters.features.json].')
  print(' --in file')
  print(' \tChange name of the annotated input file.')
  print(' --out file')
  print(' \tChange name of the arff output file.')

if __name__ == '__main__':
  try:
    opts, args = getopt.gnu_getopt(sys.argv[1:],"ho:v",["help","features", "in=", "out="])
  except (getopt.GetoptError, NameError) as err:
    usage()
    sys.exit()

  # defaults
  features = False
  input_filename = 'reuters-allcats.csv'
  output_filename = 'reuters-allcats.arff'


  for o,v in opts:
    if o == '--features':
      features = True
    elif o in ('--in'):
      input_filename = v
    elif o in ('--out'):
      output_filename = v
    elif o in ('-h','--help'):
      usage()
      sys.exit(1)
    else:
      print('unknown parameter %s'%o)
      sys.exit(1)


  if (features):
    fg = FeatureGenerator(input_filename)
    fg.print_data()
    fg.add_features()
    fg.write_features_to_file()

  arff = ARFFGenerator(input_filename)
  arff.print_data()
  arff.apply_all_features_to_entities()
  arff.write_arff_file(output_filename)


