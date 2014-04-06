#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  feature_generator.py
#
#  Copyright 2013 tadl <mail@taufderl.de>
#
#  feauture generator
#
import sys
import getopt

def extended_alphabet():
  return ['!','"','#','\'','(',')','+',',','-','.','/','0','1','2','3','4','5','6','7','8','9',':',';','<','?','@','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','R','S','T','U','V','W','Z','_','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

def basic_alphabet():
  return ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','R','S','T','U','V','W','Z','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

def words_from_files(file1, file2):
  tweets1 = read_tweets_from_file(file1)
  tweets2 = read_tweets_from_file(file2)
  return extract_words(tweets1+tweets2)

def read_tweets_from_file(filename):
  tweetfile = open(filename, 'r')
  return tweetfile.readlines()

def extract_words(tweets):
  features = set()
  for tweet in tweets:
    words = tweet.split()
    for word in words:
      valid_word = True
      for letter in word:
        if letter not in basic_alphabet():
          valid_word = False
      if valid_word:
        features.add(word)
  return list(features)

def write_features(outfile, features):
  out = open(outfile, 'w')
  for i, feature in enumerate(features):
    out.write(str(i+1)+' '+feature+'\n')
  out.close()

def open_features(featureset_file):
  ffile = open(featureset_file)
  features = []
  for line in ffile.readlines():
    features.append(line.split()[1])
  return features

def usage():
  print(' Feature File Generator v1.0 by Tim auf der Landwehr')
  print()
  print(' Usage: feature_generator.py [--out file]')
  print('\tWrite features to \'features.txt\'.')
  print()
  print(' --out file')
  print(' \tWrite features to the specified file.')

if __name__ == '__main__':
  try:
    opts, args = getopt.gnu_getopt(sys.argv[1:],"ho:v",["help","out="])
  except (getopt.GetoptError, NameError) as err:
    usage()
    sys.exit()

  features_file = 'features.txt'

  for o, name in opts:
    if o in ('--out'):
      features_file = name

  #features = basic_alphabet()
  #features = words_from_files('NL.txt', 'OTHER.txt')
  features = extended_alphabet()
  #features = ['ik', 'Ik']

  write_features(features_file, features)
  print('written %i features to [%s]' % (len(features),features_file))



