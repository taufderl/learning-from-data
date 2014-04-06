#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  ned_arff_generator.py
#
#  Copyright 2013 tadl <tadl@taufderl.de>
#
from collections import OrderedDict
import re

class Entity:
  def __init__(self, named_entity, name, pre_words, post_words):
    self.named_entity = named_entity
    self.name = name
    self.pre_words = pre_words
    self.post_words = post_words
    self.arff_line = ['0 '+named_entity]
    #self.arff_line = ['0 \"'+named_entity+'\"']

  def add_feature(self, feature_no, value):
    self.arff_line.append('%i %s' %(feature_no, value))

  def get_arff_line(self):
    return '{'+', '.join(self.arff_line)+ '}\n'

  def __repr__(self):
    return '[%s] %s <<%s>> %s' % (self.named_entity, ' '.join(self.pre_words), self.name, ' '.join(self.post_words))

class ARFFGenerator:

  def __init__(self):
    self.x = 1
    self.features = OrderedDict()
    self.classes = []
    self.entities = []

  def read_entities_from_file(self, filename):
    self.input_file = filename
    lines = open(filename, 'r').readlines()

    for line in lines:
      data = line.split('\t')
      e = Entity(data[0], data[1], [data[2],data[3]], [data[4],data[5].strip()])
      self.entities.append(e)
      if data[0] not in self.classes:
        self.classes.append(data[0])

  def print_data(self):
    print('Classes: [%s]' %(', '.join(self.classes)))
    print('Entities: #%i' %(len(self.entities)))

  def replace_crucial_characters(self, string):
    string = string.replace('\'', ';quote;')
    string = string.replace(',', ';komma;')
    string = string.replace(' ', ';whitespace;')
    string = string.replace('\"', ';doublequote;')
    if string == '':
      string = ';empty;'
    return string

  def add_feature_entity_name(self):
    FEATURE_NAME = 'entity_name'
    FEATURE_TYPE = 'string'

    if FEATURE_NAME in self.features:
      return False

    self.features[FEATURE_NAME] = FEATURE_TYPE
    feature_no = list(self.features).index(FEATURE_NAME)+1

    words = set()
    for entity in self.entities:
      word = entity.name
      word = self.replace_crucial_characters(word)
      entity.add_feature(feature_no, word)
      words.add(word)

    # otherwise add feature
    self.features[FEATURE_NAME] = '{'+','.join(sorted(words))+'}'

  def add_feature_entitiy_suffix(self, length):
    FEATURE_NAME = 'entity_suffix-%i' % length
    FEATURE_TYPE = 'string'

    if FEATURE_NAME in self.features:
      return False

    self.features[FEATURE_NAME] = FEATURE_TYPE
    feature_no = list(self.features).index(FEATURE_NAME)+1

    suffixes = set()
    for entity in self.entities:
      suffix = entity.name[-length:]
      suffix = self.replace_crucial_characters(suffix)
      entity.add_feature(feature_no, suffix)
      suffixes.add(suffix)

    # finally add feature
    self.features[FEATURE_NAME] = '{'+','.join(sorted(suffixes))+'}'


  def add_feature_entitiy_prefix(self, length):
    FEATURE_NAME = 'entity_prefix-%i' %length
    FEATURE_TYPE = 'string'

    if FEATURE_NAME in self.features:
      return False

    self.features[FEATURE_NAME] = FEATURE_TYPE
    feature_no = list(self.features).index(FEATURE_NAME)+1

    prefixes = set()
    for entity in self.entities:
      prefix = entity.name[:length]
      prefix = self.replace_crucial_characters(prefix)
      entity.add_feature(feature_no, prefix)
      prefixes.add(prefix)

    # otherwise add feature
    self.features[FEATURE_NAME] = '{'+','.join(sorted(prefixes))+'}'


  def add_feature_direct_preceding_word(self):
    FEATURE_NAME = 'direct_preceding_word'
    FEATURE_TYPE = 'string'

    if FEATURE_NAME in self.features:
      return False

    self.features[FEATURE_NAME] = FEATURE_TYPE
    feature_no = list(self.features).index(FEATURE_NAME)+1

    words = set()
    for entity in self.entities:
      word = entity.pre_words[-1]
      word = self.replace_crucial_characters(word)
      entity.add_feature(feature_no, word)
      words.add(word)

    # otherwise add feature
    self.features[FEATURE_NAME] = '{'+','.join(sorted(words))+'}'


  def add_feature_direct_subsequent_word(self):
    FEATURE_NAME = 'direct_subsequent_word'
    FEATURE_TYPE = 'string'

    if FEATURE_NAME in self.features:
      return False

    self.features[FEATURE_NAME] = FEATURE_TYPE
    feature_no = list(self.features).index(FEATURE_NAME)+1

    words = set()
    for entity in self.entities:
      word = entity.post_words[0]
      word = self.replace_crucial_characters(word)
      entity.add_feature(feature_no, word)
      words.add(word)

    # otherwise add feature
    self.features[FEATURE_NAME] = '{'+','.join(sorted(words))+'}'

  def add_feature_length(self):
    FEATURE_NAME = 'word_length'
    FEATURE_TYPE = 'numeric'

    if FEATURE_NAME in self.features:
      return False

    self.features[FEATURE_NAME] = FEATURE_TYPE
    feature_no = list(self.features).index(FEATURE_NAME)+1

    for entity in self.entities:
      word_length = len(entity.name)
      entity.add_feature(feature_no, word_length)

  def add_feature_contains_numbers(self):
    FEATURE_NAME = 'contains_numbers'
    FEATURE_TYPE = 'numeric'

    if FEATURE_NAME in self.features:
      return False

    self.features[FEATURE_NAME] = FEATURE_TYPE
    feature_no = list(self.features).index(FEATURE_NAME)+1

    _digits = re.compile('\d')

    for entity in self.entities:
      if bool(_digits.search(entity.name)):
        b = 1
      else:
        b = 0
      entity.add_feature(feature_no, b)

  def add_feature_number_of_parts(self):
    FEATURE_NAME = 'number_of_parts'
    FEATURE_TYPE = 'numeric'

    if FEATURE_NAME in self.features:
      return False

    self.features[FEATURE_NAME] = FEATURE_TYPE
    feature_no = list(self.features).index(FEATURE_NAME)+1

    for entity in self.entities:
      n = len(entity.name.split())
      entity.add_feature(feature_no, n)

  def add_feature_contains_hyphen(self):
    FEATURE_NAME = 'contains_hyphen'
    FEATURE_TYPE = 'numeric'

    if FEATURE_NAME in self.features:
      return False

    self.features[FEATURE_NAME] = FEATURE_TYPE
    feature_no = list(self.features).index(FEATURE_NAME)+1

    for entity in self.entities:
      if '-' in entity.name:
        b = 1
      else:
        b = 0
      entity.add_feature(feature_no, b)

  def add_feature_contains_apostrophe(self):
    FEATURE_NAME = 'contains_hyphen'
    FEATURE_TYPE = 'numeric'

    if FEATURE_NAME in self.features:
      return False

    self.features[FEATURE_NAME] = FEATURE_TYPE
    feature_no = list(self.features).index(FEATURE_NAME)+1

    for entity in self.entities:
      if '\'' in entity.name:
        b = 1
      else:
        b = 0
      entity.add_feature(feature_no, b)


  def add_feature_number_of_capital_letters(self):
    FEATURE_NAME = 'number_of_capital_letters'
    FEATURE_TYPE = 'numeric'

    if FEATURE_NAME in self.features:
      return False

    self.features[FEATURE_NAME] = FEATURE_TYPE
    feature_no = list(self.features).index(FEATURE_NAME)+1

    for entity in self.entities:
      c = sum(x.isupper() for x in entity.name)
      entity.add_feature(feature_no, c)

  def add_feature_contains_dot(self):
    FEATURE_NAME = 'contains_dot'
    FEATURE_TYPE = 'numeric'

    if FEATURE_NAME in self.features:
      return False

    self.features[FEATURE_NAME] = FEATURE_TYPE
    feature_no = list(self.features).index(FEATURE_NAME)+1

    for entity in self.entities:

      if '.' in entity.name:
        b = 1
      else:
        b = 0
      entity.add_feature(feature_no, b)

  def add_feature_preceding_word_suffix(self, length):
    FEATURE_NAME = 'preceding_word_suffix-%i' % length
    FEATURE_TYPE = 'string'

    if FEATURE_NAME in self.features:
      return False

    self.features[FEATURE_NAME] = FEATURE_TYPE
    feature_no = list(self.features).index(FEATURE_NAME)+1

    suffixes = set()
    for entity in self.entities:
      suffix = entity.pre_words[-1][-length:]
      suffix = self.replace_crucial_characters(suffix)
      entity.add_feature(feature_no, suffix)
      suffixes.add(suffix)

    # finally add feature
    self.features[FEATURE_NAME] = '{'+','.join(sorted(suffixes))+'}'

  def add_feature_number_of_whitespaces(self):
    FEATURE_NAME = 'number_of_whitespaces'
    FEATURE_TYPE = 'numeric'

    if FEATURE_NAME in self.features:
      return False

    self.features[FEATURE_NAME] = FEATURE_TYPE
    feature_no = list(self.features).index(FEATURE_NAME)+1

    for entity in self.entities:
      n = sum(x == ' ' for x in entity.name)
      entity.add_feature(feature_no, n)

  def write_arff_file(self, output_file):
    outfile = open(output_file, 'w')

    # write realtion line
    outfile.write('@relation \'arff created from <%s> using ned_arff_generator.py\'\n' % (self.input_file))

    # write classes line
    outfile.write('@attribute @@class@@ {%s}\n' % (','.join(self.classes)))

    # write attributes
    for feature in self.features:
      outfile.write('@attribute \'%s\' %s\n' %(feature, self.features[feature]))

    # write entity lines
    outfile.write('\n@data\n')
    for entity in self.entities:
      outfile.write(entity.get_arff_line())


if __name__ == '__main__':
  g = ARFFGenerator()
  g.read_entities_from_file('ned.train')
  g.print_data()

  g.add_feature_entity_name()

  g.add_feature_entitiy_prefix(2)
  g.add_feature_entitiy_prefix(3)
  g.add_feature_entitiy_prefix(4)
  g.add_feature_entitiy_suffix(2)
  g.add_feature_entitiy_suffix(3)
  g.add_feature_entitiy_suffix(4)

  g.add_feature_direct_preceding_word()      # good ?
  g.add_feature_direct_subsequent_word()     # good ?
  #g.add_feature_length()                     # NOT good (?)

  g.add_feature_contains_numbers()           # good ?
  g.add_feature_number_of_parts()            # good ?
  g.add_feature_number_of_capital_letters()  # good ?
  #capital letters in a row!!
  g.add_feature_number_of_whitespaces()

  g.add_feature_contains_hyphen()
  g.add_feature_contains_apostrophe()
  g.add_feature_contains_dot()

  #g.add_feature_preceding_word_suffix(2)
  #g.add_feature_preceding_word_suffix(3)
  g.add_feature_preceding_word_suffix(4)

  g.write_arff_file('ned.train.arff')
