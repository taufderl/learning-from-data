#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  arff_generator.py
#
#  Copyright 2013 tadl <mailætaufderl.de>
#
#  WEKA Format generator
#
#  TODO: improve CPU load and speed
import collections
import sys
import random
import getopt

def open_features(featureset_file):
  ffile = open(featureset_file)
  features = []
  for line in ffile.readlines():
    features.append(line.split()[1])
  return features

def usage():
  print(' ARFF File Generator v1.0 by Tim auf der Landwehr')
  print()
  print(' Usage: arff_generator.py [--features file1] [--out file2]')
  print('\tLoads features from \'features.txt\' and tweets from \'NL.txt\' and \'OTHER.txt\',')
  print('\t and writes arff output to \'NL_OTHER_features.arff\'')
  print()
  print(' --features file')
  print(' \tLoad features from different file.')
  print(' --out file')
  print(' \tChange name of output file.')
  print(' --dutch file')
  print(' \tLoad dutch tweets from different file.')
  print(' --other file')
  print(' \tLoad other tweets from different file.')

if __name__ == '__main__':
  try:
    opts, args = getopt.gnu_getopt(sys.argv[1:],"ho:v",["help","features=", "out=", "dutch=", "other="])
  except (getopt.GetoptError, NameError) as err:
    usage()
    sys.exit()

  dutch_file = 'NL.txt'
  other_file = 'OTHER.txt'
  features_file = 'features.txt'
  output_filename = 'NL_OTHER_features.arff'

  for o,v in opts:
    if o in ('--features'):
      features_file = v
    if o in ('--out'):
      output_filename = v
    if o in ('--dutch'):
      dutch_file = v
    if o in ('--other'):
      other_file = v

  print('reading dutch tweets from from [%s]' %dutch_file)
  print('reading other tweets from [%s]' %other_file)
  print('reading features from [%s]' %features_file)
  print('writing arff to [%s]' %output_filename)

  try:
    dutch_tweets = open(dutch_file).readlines()
    other_tweets = open(other_file).readlines()
    output_file = open(output_filename, 'w')
  except (FileNotFoundError) as err:
    print('Couldn\'t read from one one of the source files, exiting...')
    sys.exit()

  arff_output = []
  arff_output.append('@relation \'dutch tweet recognition, '+dutch_file+'+'+other_file+'\'')
  arff_output.append('@attribute @@class@@ {NL,OTHER}')

  try:
    features = open_features(features_file)
  except (FileNotFoundError) as err:
    print('Couldn\'t read from the features files, exiting...')
    sys.exit()

  print("writing features...")

  for index in range(len(features)):
    # excape dangerous characters
    if features[index] == '\\':
      line = "@attribute ';backslash;' numeric"
    elif features[index] == '\'':
      line = "@attribute ';quote;' numeric"
    elif features[index] == '\n':
      line = "@attribute ';linebreak;' numeric"
    else:
      line = "@attribute '"+features[index]+"' numeric"

    arff_output.append(line)

  arff_output.append('')
  arff_output.append('@data')
  output_file.write('\n'.join(arff_output))

  arff_output = ['\n']

  print("parsing and writing dutch tweets...")
  for tweet in dutch_tweets:
    feature_counts = collections.OrderedDict()
    for feature in features:
      counts = tweet.count(feature)
      if counts > 0:
        feature_counts[feature] = counts

    line = '{'
    line += ','.join(['%s %s' %(features.index(feature)+1, count) for (feature, count) in feature_counts.items()])
    line += '}'

    #output_file.write(line+'\n')
    arff_output.append(line)

  output_file.write('\n'.join(arff_output))
  arff_output = ['\n']

  print("parsing and writing other tweets...")
  for tweet in other_tweets:
    feature_counts = collections.OrderedDict()
    for feature in features:
      counts = tweet.count(feature)
      if counts > 0:
        feature_counts[feature] = counts

    line = '{0 OTHER,'
    line += ','.join(['%s %s' %(features.index(feature)+1, count) for (feature, count) in feature_counts.items()])
    line += '}'

    #output_file.write(line+'\n')
    arff_output.append(line)

  output_file.write('\n'.join(arff_output))
  print('finished successfully.')


