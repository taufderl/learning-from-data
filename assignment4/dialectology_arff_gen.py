#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  dialectology_arff_gen.py
#
#  Copyright 2013 tadl <tadl@taufderl.de>
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

def escape_character(string):
  string = string.replace('\'', ';quote;')
  string = string.replace(',', ';komma;')
  string = string.replace(' ', ';whitespace;')
  string = string.replace('\"', ';doublequote;')
  string = string.replace('\\', ';backslash;')
  return string


########################################################################
########################################################################
#######################  FEATURE GENERATOR  ############################
########################################################################
########################################################################
class FeatureGenerator:

  def __init__(self, entity_filename = None):
    self.entities = []
    self.classes = OrderedDict()
    self.features = OrderedDict()
    if not entity_filename == None:
      self.read_entities_from_file(entity_filename)

  def read_entities_from_file(self, filename):
    lines = open(filename, 'r').readlines()[1:]
    for i, line in enumerate(lines):
      no = len(self.entities)
      cla,con = line.split(',')
      self.entities.append(Entity(cla.strip(), con.strip()))
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

    #self.add_feature_letters()
    self.add_feature_unicode_letters(list(range(32,1000)))

  #  LETTERS
  def add_feature_letters(self):
    words = []
    for entity in self.entities:
      for token in entity.content.strip():
        self.features['<LETTER>'+token] = 'numeric'

  # UNICODE LETTERS
  def add_feature_unicode_letters(self, unicode_range):
    for code in unicode_range:
      self.features['<LETTER>'+escape_character(chr(code))] = 'numeric'


  def write_features_to_file(self, filename = 'features.json'):
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
      self.entities.append(Entity(cla.strip(), con.strip()))
      if cla not in self.classes:
        self.classes[cla] = 1
      else:
        self.classes[cla] += 1

  def read_features_from_file(self, filename = 'features.json'):
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
      #print('%i/%i: %s'%(feature_no, l, FEATURE_NAME))


      if FEATURE_NAME.startswith('<LETTER>'):
        feature = FEATURE_NAME.split('>')[1]
        sys.stdout.write(feature)
        sys.stdout.flush()
        for entity in self.entities:
          for token in entity.content:
              if escape_character(token) == feature:
                entity.add_feature(feature_no, 1)

      else:
        print('NO IMPLEMENTATION FOR FEATURE %s' %FEATURE_NAME)
        sys.exit(1)
    print()

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
  print(' Dialectology-ARFF-Generator v1.0 by Tim auf der Landwehr')
  print()
  print(' Usage: dialectology_arff_gen.py')
  print('\tLoads features from \'features.json\' and dialectology from \'035_annotated.txt\'')
  print('\t and writes arff output to \'035.arff\'')
  print()
  print(' --features')
  print(' \tGenerates features file [features.json].')
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
  input_filename = '035_annotated.txt'
  output_filename = '035.arff'

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
    print('Generating features file...[features.json]')
    fg = FeatureGenerator()
    fg.add_features()
    fg.write_features_to_file()


  arff = ARFFGenerator(input_filename)
  arff.print_data()
  print('Counting features in %s' %input_filename)
  arff.apply_all_features_to_entities()
  arff.write_arff_file(output_filename)




