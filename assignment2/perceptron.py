#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  perceptron.py
#
#  Copyright 2013 tadl <tadl@taufderl.de>
#
#  This file contains the implementation of the Perceptron Implementation
#  to distinguish between Tweets in Dutch and other languages
import math
import pickle
import os
import sys
import getopt
import random
import numpy

class DutchTweetPerceptron:

  FOLDER = './model/'
  MODEL_FILE = FOLDER + 'perceptron_model.pk'
  FEATURE_FILE = FOLDER + 'perceptron_features.pk'
  Y = {}
  Y['DUTCH'] = 1
  Y['OTHER'] = -1

  def __init__(self, feature_file = None):
    self.model = None
    if feature_file == None:
      self.features = None
    else:
      open_feature_file(feature_file)
    try:
      os.mkdir(self.FOLDER)
    except:
      pass

  def save_model(self):
    print('save model...')
    pickle.dump(self.model, open(self.MODEL_FILE, 'wb'))

  def load_model(self):
    print('load model...')
    self.model = pickle.load(open(self.MODEL_FILE, 'rb'))

  def save_features(self):
    print('save features...')
    pickle.dump(self.features, open(self.FEATURE_FILE, 'wb'))

  def load_features(self):
    print('load features...')
    self.features = pickle.load(open(self.FEATURE_FILE, 'rb'))

  def open_feature_file(self, feature_file):
    feature_file = open(feature_file)
    features = []
    for line in feature_file.readlines():
      features.append(line.split()[1])
    self.features = features

  def preprocess_test_tweets_from_file(self, test_file):
    tweets = open(test_file).readlines()

    preprocessed_tweets = []

    for tweet in tweets:
      x = []
      for feature in self.features:
        x.append(tweet.count(feature))
      preprocessed_tweets.append({'vector': x,'class': '?'})

    return preprocessed_tweets

  def preprocess_tweets_from_files(self, feature_file, dutch_file, other_file):
    self.open_feature_file(feature_file)
    dutch_tweets = open(dutch_file).readlines()
    other_tweets = open(other_file).readlines()

    return self.preprocess_tweets(dutch_tweets, other_tweets)

  def preprocess_tweets(self, dutch_tweets, other_tweets):
    preprocessed_tweets = []

    for tweet in dutch_tweets:
      x = []
      for feature in self.features:
        x.append(tweet.count(feature))

      preprocessed_tweets.append({'vector': x,'class': 'DUTCH'})

    for tweet in other_tweets:
      x = []
      for feature in self.features:
        x.append(tweet.count(feature))

      preprocessed_tweets.append({'vector': x,'class': 'OTHER'})

    return preprocessed_tweets

  def train(self, tweets, iterations = 1):
    w = [0] * (len(tweets[0]['vector']))
    b = 0

    for i in range(1,iterations+1):
      print('\t\tTraining iteration %i of %i' %(i, iterations))
      random.shuffle(tweets)
      for x in tweets:

        # compute activity
        a = numpy.dot(w, x['vector']) + b
        # determine y
        y = self.Y[x['class']] # y elem {-1,1}

        # if mistake
        if y*a <= 0:
          w = [sum(item) for item in zip(w, [y*x_i for x_i in x['vector']])] # add single entries in vector -> vector addition
          b = b + y # TODO: only when if or always???

    self.model = {'w': w, 'b': b}

  def test_tweet(self, tweet):
    a = numpy.dot(self.model['w'], tweet['vector']) + self.model['b']
    if a > 0:
      return 'DUTCH'
    else:
      return 'OTHER'


  def test(self, tweets):
    result = []
    for tweet in tweets:
      result.append(self.test_tweet(tweet))
    return result

  def run_cross_validation(self, featureset_file, dutch_file, other_file, FOLDS = 10, ITERATIONS = 5):
    print('starting %i fold cross validation' %(FOLDS))
    self.open_feature_file(featureset_file)
    dutch_tweets = open(dutch_file).readlines()
    other_tweets = open(other_file).readlines()

    # determine test set length
    x_dutch = int(len(dutch_tweets)/FOLDS)
    x_other = int(len(other_tweets)/FOLDS)

    accuracies = []

    # for each of the ten training and test sets
    for i in range(FOLDS):
      print('Cross-Validation fold %i/%i'%(i+1, FOLDS))
      # determine test sets
      dutch_test_tweets = dutch_tweets[i*x_dutch:i*x_dutch+x_dutch]
      other_test_tweets = other_tweets[i*x_other:i*x_other+x_other]

      # determine training sets
      dutch_training_tweets = dutch_tweets[:]
      other_training_tweets = other_tweets[:]
      dutch_training_tweets[i*x_dutch:i*x_dutch+x_dutch] = []
      other_training_tweets[i*x_other:i*x_other+x_other] = []

      # preprocess training and test tweets
      print('\tPreprocessing tweets.')
      training_tweets = self.preprocess_tweets(dutch_training_tweets, other_training_tweets)
      test_tweets = self.preprocess_tweets(dutch_test_tweets, other_test_tweets)

      # do training with selected training data
      print('\tTraining %i Tweets' %(len(training_tweets)))
      self.train(training_tweets, ITERATIONS)

      # do testing
      print('\tTesting %i tweets.' %(len(test_tweets)))
      correct = 0

      for tweet in test_tweets:
        result = self.test_tweet(tweet)
        #print('>>%s! (is really %s)' % (result, tweet['class']) )
        if (tweet['class'] == result):
          correct += 1

      print('\t%i of %i = %f'%(correct, len(test_tweets), correct/len(test_tweets)))

      # calculate accuracies
      accuracies.append(correct/len(test_tweets))

    print("Accuracy: %f" % (sum(accuracies)/FOLDS))
  # END DEF run_testset


# Usage output for command line
def usage(error_message = False):
  print(' Perceptron for Dutch Language Recognition v1.0 by Tim auf der Landwehr')
  print(' Distinguishes the language of a text between >Dutch and >Other ')
  if error_message:
    print()
    print(' Error: '+error_message)
  print()
  print(' Usage: perceptron.py [options] [file(s)]')
  print()
  print(' Options:')
  print(' -h --help')
  print(' \tShow this usage information')
  print()
  print(' --train feature_file dutch_file other_file')
  print(' \tTrains features on given data, requires all 3 files given')
  print()
  print(' --test test_file [test_file ...]')
  print(' \tTests each line in the input file')
  print(' -v --verbose')
  print(' \tPrint test results on stdout.')
  print(' --write')
  print(' \tWrite results to \'filename.results\'.')
  print()
  print(' --run-cross-validation')
  print(' \tRun 10 fold cross validation and calculate success.')
  print(" \tExpects the files 'features.txt', 'NL.txt' and 'OTHER.txt' to lie in the same directory'")
  sys.exit()
# END usage

# if this is run, start command line script
if __name__ == "__main__":

  try:
    opts, args = getopt.gnu_getopt(sys.argv[1:],"ho:v",["help","train","test", "verbose", "run-cross-validation", "write"])
  except getopt.GetoptError as err:
    usage(str(err))

  if ('--help', '') in opts:
    usage()
  elif ('-h', '') in opts:
    usage()

  # create class instance
  perceptron = DutchTweetPerceptron()

  # If run-testset is set
  if ('--run-cross-validation', '') in opts:
    perceptron.run_cross_validation('features.txt', 'NL.txt', 'OTHER.txt', 10, 1)

  # If train is set
  elif ('--train', '') in opts:
    if len(args) != 3:
      usage("Training requires 3 input files.");
    else:
      # do training
      try:
        tweets = perceptron.preprocess_tweets_from_files(args[0], args[1], args[2])
        perceptron.train(tweets, 1)
        perceptron.save_model()
        perceptron.save_features()
      except FileNotFoundError as err:
        usage(str(err))

  # If test is set
  elif ('--test', '') in opts:
    if len(args) < 1:
      usage("Testing requires at least one input file");
    else:
      perceptron.load_model()
      perceptron.load_features()
      # Do testing
      try:
        for filename in args:
          print('test [%s]...' % filename)
          tweets = perceptron.preprocess_test_tweets_from_file(filename)
          result = perceptron.test(tweets)
          if ('--verbose', '') in opts or ('-v', '') in opts:
            for r in result:
              print(r)
          if ('--write', '') in opts:
            outfile = open(filename+'.results', 'w')
            for r in result:
              outfile.write('%s\n' % r)
            print('written results to [%s]' % str(outfile.name))

      except FileNotFoundError as err:
        usage(str(err))
  # if nothing set, print usage
  else:
    usage()


# END_OF_FILE
