#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  ned_arff_generator.py
#
#  Copyright 2013 tadl <tadl@taufderl.de>
#
from collections import OrderedDict
import re
import sys
import pickle

########################################################################
########################################################################
#########################      ENTITY      #############################
########################################################################
########################################################################


class Entity:
  def __init__(self, named_entity, name, pre_words, post_words):
    self.named_entity = named_entity
    self.name = name
    self.pre_words = pre_words
    self.post_words = post_words
    self.arff_line = ['0 '+named_entity]
    #self.arff_line = ['0 \"'+named_entity+'\"']
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

  def __init__(self):
    self.x = 1
    self.features = OrderedDict()
    self.classes = []
    self.entities = []

  def read_entities_from_file(self, filename):
    print('read data from [%s]' % filename)
    self.input_file = filename
    lines = open(filename, 'r').readlines()

    for line in lines:
      data = line.split('\t')
      e = Entity(data[0], data[1], [data[2],data[3]], [data[4],data[5].strip()])
      self.entities.append(e)
      if data[0] not in self.classes:
        self.classes.append(data[0])

    self.classes = sorted(self.classes)

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

    words = set()
    for entity in self.entities:
      word = entity.name
      word = self.replace_crucial_characters(word)
      words.add(word)

    #self.features[FEATURE_NAME] = '{'+','.join(sorted(words))+'}'
    self.features[FEATURE_NAME] = words

  def add_feature_all_letters(self):
    for entity in self.entities:
      for token in entity.name.strip():
        self.features['<LETTER>'+self.replace_crucial_characters(token)] = 'numeric'


  def add_feature_entitiy_suffix(self, length):
    FEATURE_NAME = 'entity_suffix-%i' % length
    FEATURE_TYPE = 'string'

    if FEATURE_NAME in self.features:
      return False

    self.features[FEATURE_NAME] = FEATURE_TYPE

    suffixes = set()
    for entity in self.entities:
      suffix = entity.name[-length:]
      suffix = self.replace_crucial_characters(suffix)
      suffixes.add(suffix)

    # finally add feature
    self.features[FEATURE_NAME] = suffixes


  def add_feature_entitiy_prefix(self, length):
    FEATURE_NAME = 'entity_prefix-%i' %length
    FEATURE_TYPE = 'string'

    if FEATURE_NAME in self.features:
      return False

    self.features[FEATURE_NAME] = FEATURE_TYPE

    prefixes = set()
    for entity in self.entities:
      prefix = entity.name[:length]
      prefix = self.replace_crucial_characters(prefix)
      prefixes.add(prefix)

    # otherwise add feature
    self.features[FEATURE_NAME] = prefixes


  def add_feature_direct_preceding_word(self):
    FEATURE_NAME = 'direct_preceding_word'
    FEATURE_TYPE = 'string'

    if FEATURE_NAME in self.features:
      return False

    self.features[FEATURE_NAME] = FEATURE_TYPE

    words = set()
    for entity in self.entities:
      word = entity.pre_words[-1]
      word = self.replace_crucial_characters(word)
      words.add(word)

    # otherwise add feature
    self.features[FEATURE_NAME] = words


  def add_feature_direct_subsequent_word(self):
    FEATURE_NAME = 'direct_subsequent_word'
    FEATURE_TYPE = 'string'

    if FEATURE_NAME in self.features:
      return False

    self.features[FEATURE_NAME] = FEATURE_TYPE

    words = set()
    for entity in self.entities:
      word = entity.post_words[0]
      word = self.replace_crucial_characters(word)
      words.add(word)

    # otherwise add feature
    self.features[FEATURE_NAME] = words

  def add_feature_length(self):
    FEATURE_NAME = 'word_length'
    FEATURE_TYPE = 'numeric'

    if FEATURE_NAME in self.features:
      return False

    self.features[FEATURE_NAME] = FEATURE_TYPE


  def add_feature_contains_numbers(self):
    FEATURE_NAME = 'contains_numbers'
    FEATURE_TYPE = 'numeric'

    if FEATURE_NAME in self.features:
      return False

    self.features[FEATURE_NAME] = FEATURE_TYPE


  def add_feature_number_of_parts(self):
    FEATURE_NAME = 'number_of_parts'
    FEATURE_TYPE = 'numeric'

    if FEATURE_NAME in self.features:
      return False

    self.features[FEATURE_NAME] = FEATURE_TYPE


  def add_feature_contains_hyphen(self):
    FEATURE_NAME = 'contains_hyphen'
    FEATURE_TYPE = 'numeric'

    if FEATURE_NAME in self.features:
      return False

    self.features[FEATURE_NAME] = FEATURE_TYPE


  def add_feature_contains_apostrophe(self):
    FEATURE_NAME = 'contains_hyphen'
    FEATURE_TYPE = 'numeric'

    if FEATURE_NAME in self.features:
      return False

    self.features[FEATURE_NAME] = FEATURE_TYPE


  def add_feature_number_of_capital_letters(self):
    FEATURE_NAME = 'number_of_capital_letters'
    FEATURE_TYPE = 'numeric'

    if FEATURE_NAME in self.features:
      return False

    self.features[FEATURE_NAME] = FEATURE_TYPE

  def add_feature_highest_number_of_capital_letters_in_a_row(self):
    FEATURE_NAME = 'number_of_capital_letters_in_a_row'
    FEATURE_TYPE = 'numeric'

    if FEATURE_NAME in self.features:
      return False

    self.features[FEATURE_NAME] = FEATURE_TYPE


  def add_feature_contains_dot(self):
    FEATURE_NAME = 'contains_dot'
    FEATURE_TYPE = 'numeric'

    if FEATURE_NAME in self.features:
      return False

    self.features[FEATURE_NAME] = FEATURE_TYPE


  def add_feature_preceding_word_suffix(self, length):
    FEATURE_NAME = 'preceding_word_suffix-%i' % length
    FEATURE_TYPE = 'string'

    if FEATURE_NAME in self.features:
      return False

    self.features[FEATURE_NAME] = FEATURE_TYPE

    suffixes = set()
    for entity in self.entities:
      suffix = entity.pre_words[-1][-length:]
      suffix = self.replace_crucial_characters(suffix)
      suffixes.add(suffix)

    # finally add feature
    self.features[FEATURE_NAME] = suffixes

  def add_feature_number_of_whitespaces(self):
    FEATURE_NAME = 'number_of_whitespaces'
    FEATURE_TYPE = 'numeric'

    if FEATURE_NAME in self.features:
      return False

    self.features[FEATURE_NAME] = FEATURE_TYPE


  def write_feature_file(self, filename = 'features.pickle'):
    print('write features to [%s]'%filename)
    pickle.dump(self.features, open(filename, 'wb'))



########################################################################
########################################################################
#########################  ARFF GENERATOR  #############################
########################################################################
########################################################################

class ARFFGenerator:

  def __init__(self):
    self.x = 1
    self.features = pickle.load(open('features.pickle', 'rb'))
    self.classes = []
    self.entities = []

  def read_entities_from_file(self, filename):
    print('read from %s' % filename)
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

  def apply_all_features_to_entities(self):

    for FEATURE_NAME, FEATURE_VALUES in self.features.items():
      print(FEATURE_NAME)
      if FEATURE_NAME == 'entity_name':
        feature_no = list(self.features).index(FEATURE_NAME)+1

        for entity in self.entities:
          word = entity.name
          word = self.replace_crucial_characters(word)
          if word in FEATURE_VALUES:
            entity.add_feature(feature_no, word)


      elif FEATURE_NAME.startswith('entity_suffix-'):
        length = int(FEATURE_NAME[-1:])
        feature_no = list(self.features).index(FEATURE_NAME)+1

        for entity in self.entities:
          suffix = entity.name[-length:]
          suffix = self.replace_crucial_characters(suffix)
          if suffix in FEATURE_VALUES:
            entity.add_feature(feature_no, suffix)


      elif FEATURE_NAME.startswith('entity_prefix-'):
        length = int(FEATURE_NAME[-1:])
        feature_no = list(self.features).index(FEATURE_NAME)+1

        for entity in self.entities:
          prefix = entity.name[:length]
          prefix = self.replace_crucial_characters(prefix)
          if prefix in FEATURE_VALUES:
            entity.add_feature(feature_no, prefix)


      elif FEATURE_NAME == 'direct_preceding_word':
        feature_no = list(self.features).index(FEATURE_NAME)+1

        for entity in self.entities:
          word = entity.pre_words[-1]
          word = self.replace_crucial_characters(word)
          if word in FEATURE_VALUES:
            entity.add_feature(feature_no, word)

      elif FEATURE_NAME == 'direct_subsequent_word':
        feature_no = list(self.features).index(FEATURE_NAME)+1

        for entity in self.entities:
          word = entity.post_words[0]
          word = self.replace_crucial_characters(word)
          if word in FEATURE_VALUES:
            entity.add_feature(feature_no, word)


      elif FEATURE_NAME == 'word_length':
        feature_no = list(self.features).index(FEATURE_NAME)+1

        for entity in self.entities:
          word_length = len(entity.name)
          entity.add_feature(feature_no, word_length)

      elif FEATURE_NAME == 'contains_numbers':
        feature_no = list(self.features).index(FEATURE_NAME)+1

        _digits = re.compile('\d')

        for entity in self.entities:
          if bool(_digits.search(entity.name)):
            b = 1
          else:
            b = 0
          entity.add_feature(feature_no, b)

      elif FEATURE_NAME == 'number_of_parts':
        feature_no = list(self.features).index(FEATURE_NAME)+1

        for entity in self.entities:
          n = len(entity.name.split())
          entity.add_feature(feature_no, n)

      elif FEATURE_NAME == 'contains_hyphen':
        feature_no = list(self.features).index(FEATURE_NAME)+1

        for entity in self.entities:
          if '-' in entity.name:
            b = 1
          else:
            b = 0
          entity.add_feature(feature_no, b)

      elif FEATURE_NAME == 'contains_hyphen':
        feature_no = list(self.features).index(FEATURE_NAME)+1

        for entity in self.entities:
          if '\'' in entity.name:
            b = 1
          else:
            b = 0
          entity.add_feature(feature_no, b)

      elif FEATURE_NAME == 'number_of_capital_letters':
        feature_no = list(self.features).index(FEATURE_NAME)+1

        for entity in self.entities:
          c = sum(x.isupper() for x in entity.name)
          entity.add_feature(feature_no, c)


      elif FEATURE_NAME == 'number_of_capital_letters_in_a_row':
        feature_no = list(self.features).index(FEATURE_NAME)+1

        for entity in self.entities:
          c = re.findall("([A-Z]+)",entity.name)
          if len(c) == 0:
            entity.add_feature(feature_no, 0)
          else:
            n = max(map(len,c))
            entity.add_feature(feature_no, n)


      elif FEATURE_NAME == 'contains_dot':
        feature_no = list(self.features).index(FEATURE_NAME)+1

        for entity in self.entities:

          if '.' in entity.name:
            b = 1
          else:
            b = 0
          entity.add_feature(feature_no, b)

      elif FEATURE_NAME.startswith('preceding_word_suffix-'):
        length = int(FEATURE_NAME[-1:])
        feature_no = list(self.features).index(FEATURE_NAME)+1

        for entity in self.entities:
          suffix = entity.pre_words[-1][-length:]
          suffix = self.replace_crucial_characters(suffix)
          if suffix in FEATURE_VALUES:
            entity.add_feature(feature_no, suffix)

      elif FEATURE_NAME == 'number_of_whitespaces':
        feature_no = list(self.features).index(FEATURE_NAME)+1

        for entity in self.entities:
          n = sum(x == ' ' for x in entity.name)
          entity.add_feature(feature_no, n)

      elif FEATURE_NAME.startswith('<LETTER>'):
        feature_no = list(self.features).index(FEATURE_NAME)+1

        feature = FEATURE_NAME.split('>')[1]
        for entity in self.entities:
          for token in entity.name.strip():
            if self.replace_crucial_characters(token) == feature:
              entity.add_feature(feature_no, 1)

      else:
        print('NO IMPLEMENTATION FOR FEATURE %s' %FEATURE_NAME)

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


def usage():
  print('Usage:')
  print('First run:')
  print('\t--gen-feature-file entity_file \t\t>This will generate the feature file')
  print('Second run:')
  print('\t--gen-arff entity_file arff_out_file \t\t>This will generate the arff file')
  sys.exit(1)


if __name__ == '__main__':
  if len(sys.argv) < 3:
    usage()
  if sys.argv[1] == '--gen-feature-file':
    fg = FeatureGenerator()
    fg.read_entities_from_file(sys.argv[2])
    fg.print_data()

    fg.add_feature_entity_name()

    fg.add_feature_all_letters()

    fg.add_feature_entitiy_prefix(2)
    fg.add_feature_entitiy_prefix(3)
    fg.add_feature_entitiy_prefix(4)
    fg.add_feature_entitiy_prefix(5)
    fg.add_feature_entitiy_prefix(6)
    fg.add_feature_entitiy_suffix(2)
    fg.add_feature_entitiy_suffix(3)
    fg.add_feature_entitiy_suffix(4)
    fg.add_feature_entitiy_suffix(5)
    fg.add_feature_entitiy_suffix(6)

    fg.add_feature_direct_preceding_word()      # good ?
    fg.add_feature_direct_subsequent_word()     # good ?
    fg.add_feature_length()                     # NOT good (?)

    fg.add_feature_contains_numbers()           # good ?
    fg.add_feature_number_of_parts()            # good ?
    fg.add_feature_number_of_capital_letters()  # good ?
    fg.add_feature_highest_number_of_capital_letters_in_a_row()
    #capital letters in a row!!
    fg.add_feature_number_of_whitespaces()

    fg.add_feature_contains_hyphen()
    fg.add_feature_contains_apostrophe()
    fg.add_feature_contains_dot()

    fg.add_feature_preceding_word_suffix(2)
    fg.add_feature_preceding_word_suffix(3)
    fg.add_feature_preceding_word_suffix(4)

    fg.write_feature_file()

  elif sys.argv[1] == '--gen-arff':

    arff = ARFFGenerator()
    arff.read_entities_from_file(sys.argv[2])
    arff.apply_all_features_to_entities()
    arff.write_arff_file(sys.argv[3])

  elif sys.argv[1] == '--debug':
    arff = ARFFGenerator()
    arff.read_entities_from_file('ned.train_10')
    #arff.apply_all_features_to_entities()
    arff.write_arff_file('DEBUG_ned.train_10')

    arff2 = ARFFGenerator()
    arff2.read_entities_from_file('ned.train_90')
    arff2.write_arff_file('DEBUG_ned.train_90')

  else:
    usage()
