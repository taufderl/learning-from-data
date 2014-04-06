#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  mutual_information_letters.py
#
#  Copyright 2013 tadl <tadl@taufderl.de>
#
#
#
import math
from collections import OrderedDict
from operator import itemgetter

class MutualInformation:

  def __init__(self, dutch_file, other_file):
    self.features = set()

    self.dutch_tweets = open(dutch_file, 'r').readlines()
    self.other_tweets = open(other_file, 'r').readlines()

  def count_letters(self):
    dutch_frequencies = {}
    dutch_letters = 0

    for tweet in self.dutch_tweets:
      for letter in tweet:
        self.features.add(letter)
        dutch_letters += 1
        if letter in dutch_frequencies.keys():
          dutch_frequencies[letter] += 1
        else:
          dutch_frequencies[letter] = 1

    print('Dutch letters: %i' % dutch_letters)

    other_frequencies = {}
    other_letters = 0

    for tweet in self.other_tweets:
      for letter in tweet:
        self.features.add(letter)
        other_letters += 1
        if letter in other_frequencies.keys():
          other_frequencies[letter] += 1
        else:
          other_frequencies[letter] = 1

    print('Other letters: %i' % other_letters)

    # dutch prior FOR LETTERS!!!
    total_tweets = float(len(self.dutch_tweets)+len(self.other_tweets))

    self.dutch_prior = len(self.dutch_tweets)/total_tweets
    self.other_prior = len(self.other_tweets)/total_tweets

    self.dutch_letters = dutch_letters
    self.other_letters = other_letters
    self.dutch_frequencies = dutch_frequencies
    self.other_frequencies = other_frequencies
    self.total_letters = dutch_letters+other_letters

  def P(self, letter):
    if letter in self.dutch_frequencies.keys():
      dutch_freq = self.dutch_frequencies[letter]
    else:
      dutch_freq = 0
    if letter in self.other_frequencies.keys():
      other_freq = self.other_frequencies[letter]
    else:
      other_freq = 0

    return (float(dutch_freq+other_freq)/self.total_letters)

  def P_dutch(self, letter):
    if letter in self.dutch_frequencies.keys():
      return (float(self.dutch_frequencies[letter])/self.total_letters)
    else:
      return 0

  def P_other(self, letter):
    if letter in self.other_frequencies.keys():
      return (float(self.other_frequencies[letter])/self.total_letters)
    else:
      return 0

  def total_frequency_of(self, feature):
    s1 = s2 = 0
    if feature in self.dutch_frequencies.keys():
      s1 = self.dutch_frequencies[feature]
    if feature in self.other_frequencies.keys():
      s2 = self.other_frequencies[feature]
    return s1+s2

  def mutual_information(self, f):
    if self.P_dutch(f) == 0:
      p1 = 0
    else:
      p1 = self.P_dutch(f)*math.log(self.P_dutch(f)/(self.dutch_prior*self.P(f)))
    if self.P_other(f) == 0:
      p2 = 0
    else:
      p2 = self.P_other(f)*math.log(self.P_other(f)/(self.other_prior*self.P(f)))
    return p1+p2

  def calc_mutual_information_for_letters(self):
    mi = {}
    for feature in self.features:
      if (self.total_frequency_of(feature) >= 50):
        mi[feature] = self.mutual_information(feature)

    ordered_mi = OrderedDict(reversed(sorted(mi.items(), key=itemgetter(1))))

    self.results = list(ordered_mi.items())[:25]

    #for f, v in mi.items():
    #  print('%s: %f' %(f, v))

  def print_results(self):
    for k, v in self.results:
      print('%s: %f' %(k, v))

if __name__ == '__main__':
  mi = MutualInformation('NL.txt', 'OTHER.txt')
  mi.count_letters()
  mi.calc_mutual_information_for_letters()
  mi.print_results()
