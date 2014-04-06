#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  dutch_language_recognizer.py
#  Copyright 2013 tadl <tadl@taufderl.de>
#
#  This program uses the Naive Bayes algorithm to learn to
#  distinguish between Tweets in Dutch and in other languages.
#
#  This version is based on words.
#
#
import math
import pickle
import os
import sys
import getopt

# Define folder and filenames for trained data
FOLDER = './data/'
TRAINED_DATA_FILE_DUTCH = FOLDER + 'trained_data_dutch_v2.pk'
TRAINED_DATA_FILE_OTHER = FOLDER + 'trained_data_other_v2.pk'
TRAINED_DATA_FILE_PROPERTIES = FOLDER + 'trained_data_properties_v2.pk'

class DutchLanguageRecognizer:

  # init
  def __init__(self):
    try:
      os.mkdir(FOLDER)
    except:
      pass

  # Trains on the given data in lists and stores everything into
  # the files
  def train(self, dutch_tweets, other_tweets):
    properties = {}

    # count tweets
    properties['N_dutch'] = len(dutch_tweets)
    properties['N_other'] = len(other_tweets)
    properties['N'] = properties['N_dutch'] + properties['N_other']

    # calculate prior values
    properties['DUTCH_PRIOR'] = properties['N_dutch']/properties['N']
    properties['OTHER_PRIOR'] = properties['N_other']/properties['N']

    # extract vocabulary size
    V = set()
    for line in dutch_tweets+other_tweets:
      for word in line.split():
        V.add(word)
    vocabulary = len(V)

    # count tokens in dutch tweets
    words = {}
    total_words = 0
    for line in dutch_tweets:
      for word in line.split():
        total_words += 1
        if word in words:
          words[word] += 1
        else:
          words[word] = 2 # initially added one to set one if 0 occurencys

    # calculate probability for each token
    dutch_data = {}
    for word in words:
      dutch_data[word] = (words[word]/(total_words+vocabulary))

    # calculate probability for unknown tokens
    dutch_data['UNKNOWN_TOKEN'] = 1/(total_words+vocabulary)

    # count tokens in other tweets
    words = {}
    total_words = 0
    for line in other_tweets:
      for word in line.split():
        total_words += 1
        if word in words:
          words[word] += 1
        else:
          words[word] = 2 # initially added one to set one if 0 occurencys

    # calculate probability for each token
    other_data = {}
    for word in words:
      other_data[word] = (words[word]/(total_words+vocabulary))

    # calculate probability for unknown tokens
    other_data['UNKNOWN_TOKEN'] = 1/(total_words+vocabulary)

    pickle.dump(properties, open(TRAINED_DATA_FILE_PROPERTIES, 'wb'))
    pickle.dump(dutch_data, open(TRAINED_DATA_FILE_DUTCH, 'wb'))
    pickle.dump(other_data, open(TRAINED_DATA_FILE_OTHER, 'wb'))

    print("N: "+str(properties['N']))
    print("N_dutch: "+str(properties['N_dutch'])+" | prior_dutch: "+str(properties['DUTCH_PRIOR']))
    print("N_other: "+str(properties['N_other'])+" | prior_other: "+str(properties['OTHER_PRIOR']))
    print('saved training data to files:')
    print('>>'+TRAINED_DATA_FILE_PROPERTIES)
    print('>>'+TRAINED_DATA_FILE_DUTCH)
    print('>>'+TRAINED_DATA_FILE_OTHER)
  # END_DEF train


  # train on data from files
  def train_from_files(self, dutch_file, other_file):
    print('training... dutch: <'+dutch_file+'> other: <'+other_file+'>')

    # load all tweets
    dutch_tweets = open(dutch_file, 'r').readlines()
    other_tweets = open(other_file, 'r').readlines()

    self.train(dutch_tweets, other_tweets)
  # END_DEF train_from_files


  # test given tweets on the saved data
  def test(self, tweets):

    # open trained data
    properties = pickle.load(open(TRAINED_DATA_FILE_PROPERTIES, 'rb'))
    dutch_prob = pickle.load(open(TRAINED_DATA_FILE_DUTCH, 'rb'))
    other_prob = pickle.load(open(TRAINED_DATA_FILE_OTHER, 'rb'))

    results = []

    # test file input
    for tweet in tweets:
      score = {}
      score['DUTCH'] = -math.log(properties['DUTCH_PRIOR'])
      score['OTHER'] = -math.log(properties['OTHER_PRIOR'])
      for word in tweet.split():
        if word in dutch_prob:
          score['DUTCH'] += -math.log(dutch_prob[word])
        else:
          score['DUTCH'] += -math.log(dutch_prob['UNKNOWN_TOKEN'])
        if word in other_prob:
          score['OTHER'] += -math.log(other_prob[word])
        else:
          score['OTHER'] += -math.log(other_prob['UNKNOWN_TOKEN'])
      if score['DUTCH'] < score['OTHER']:
        results.append('DUTCH: '+tweet)
      else:
        results.append('OTHER: '+tweet)

    return results
  # END DEF test


  # test given data, requires training before
  def test_file(self, filename, output_file = False):
    print('testing <'+filename+'>')

    # open input file
    tweets = open(filename, 'r').readlines()

    results = self.test(tweets)

    # if write to file set
    if output_file:
      out_file = open(output_file, 'w')
      for line in results:
        out_file.write(line)
      out_file.close()
      print('written results to '+ output_file)

    return results
  # END DEF test_file

  #
  def run_test_and_verify(self):
    print('run testset...')
    # test dutch testset
    results = self.test('TEST_DUTCH.txt')

    n = len(results)
    dutch = 0

    for line in results:
      if line.startswith('DUTCH'):
        dutch += 1

    print('Result for DUTCH:')
    print('>>: '+str(dutch/n))

    # test other testset
    results = self.test('TEST_OTHER.txt')

    n = len(results)
    other = 0

    for line in results:
      if line.startswith('OTHER'):
        other += 1

    print('Result for OTHER:')
    print('>>: '+str(other/n))


  # train on all 1/10 of Data and test on other 9/10
  # calculates accuracy of algorithm
  def run_cross_validation(self):
    print('test each 10th of the data after trained on the other 9/10...')
    dutch_tweets = open('NL.txt').readlines()
    other_tweets = open('OTHER.txt').readlines()

    # determine test set length
    x_dutch = int(len(dutch_tweets)/10)
    x_other = int(len(other_tweets)/10)

    dutch_accuracy = []
    other_accuracy = []

    # for each of the ten training and test sets
    for i in range(10):
      # determine test sets
      dutch_test_tweets = dutch_tweets[i*x_dutch:i*x_dutch+x_dutch]
      other_test_tweets = other_tweets[i*x_other:i*x_other+x_other]

      # determine training sets
      dutch_training_tweets = dutch_tweets[:]
      other_training_tweets = other_tweets[:]
      dutch_training_tweets[i*x_dutch:i*x_dutch+x_dutch] = []
      other_training_tweets[i*x_other:i*x_other+x_other] = []

      print("DUTCH: Test "+str(len(dutch_test_tweets))+" against "+str(len(dutch_training_tweets)))
      print("OTHER: Test "+str(len(other_test_tweets))+" against "+str(len(other_training_tweets)))

      # do training with selected training data
      self.train(dutch_training_tweets, other_training_tweets)

      # test the other 1/10 of Dutch tweets
      dutch_result = self.test(dutch_test_tweets)
      # test the other 1/10 of Other tweets
      other_result = self.test(other_test_tweets)

      # count how many are Dutch
      dutch = 0
      for line in dutch_result:
        if line.startswith('DUTCH'):
          dutch += 1

      # count how many are Other
      other = 0
      for line in other_result:
        if line.startswith('OTHER'):
          other += 1

      # calculate accuracies
      dutch_accuracy.append(dutch/x_dutch)
      other_accuracy.append(other/x_other)

      out_file = open('v2_dutch_result_'+str(i)+"|"+str(dutch)+"<"+str(x_dutch)+".txt", 'w')
      for line in dutch_result:
        out_file.write(line)
      out_file.close()
      out_file = open('v2_other_result_'+str(i)+"|"+str(other)+"<"+str(x_other)+".txt", 'w')
      for line in other_result:
        out_file.write(line)
      out_file.close()

    print("Accuracies:")
    print("Dutch "+str(sum(dutch_accuracy)/10))
    print(dutch_accuracy)
    print("Other "+str(sum(other_accuracy)/10))
    print(other_accuracy)
  # END DEF run_testset

## END OF CLASS


# Usage output for command line
def usage(error_message = False):
  print(' Dutch Language Recognizer v1.0 by Tim auf der Landwehr')
  print(' Distinguishes the language of a text between >Dutch and >Other ')
  if error_message:
    print()
    print(' Error: '+error_message)
  print()
  print(' Usage: dutch_language_recognizer.py [options] [file(s)]')
  print()
  print(' Options:')
  print(' -h --help')
  print(' \tShow this usage information')
  print(' --train  dutch_file other_file')
  print(' \tTrains on given data, requires both files given')
  print(' --test test_file [test_file ...]')
  print(' \tTests each line in the input file')
  print(' -v --verbose')
  print(' \tPrint test results on stdout.')
  print()
  print(' --run-cross-validation')
  print(' \tRun 10 fold cross validation and calculate success.')
  print(" \tExpects the files 'NL.txt and OTHER.txt to ly in the same directory'")
  sys.exit()
# END usage

# if this is run, start command line script
if __name__ == "__main__":

  try:
    opts, args = getopt.gnu_getopt(sys.argv[1:],"ho:v",["help","train","test", "verbose", "run-cross-validation"])
  except getopt.GetoptError as err:
    usage(str(err))

  if ('--help', '') in opts:
    usage()
  elif ('-h', '') in opts:
    usage()

  # create class instance
  recognizer = DutchLanguageRecognizer()

  # If run-testset is set
  if ('--run-cross-validation', '') in opts:
    recognizer.run_cross_validation()

  # If train is set
  elif ('--train', '') in opts:
    if len(args) != 2:
      usage("Training requires two input files.");
    else:
      # do training
      try:
        recognizer.train_from_files(args[0], args[1])
      except FileNotFoundError as err:
        usage(str(err))

  # If test is set
  elif ('--test', '') in opts:
    if len(args) < 1:
      usage("Testing requires at least one input file");
    else:
      # Do testing
      recognizer = DutchLanguageRecognizer()
      try:
        for file in args:
          results = recognizer.test_file(file, "RESULTS_"+file)
          if ('--verbose', '') in opts or ('-v', '') in opts:
            for line in results:
              print(line, end="")
      except FileNotFoundError as err:
        usage(str(err))
  # if nothing set, print usage
  else:
    usage()

# END_OF_FILE
