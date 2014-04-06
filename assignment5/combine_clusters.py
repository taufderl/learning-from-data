#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  combine_clusters.py
#
#  Copyright 2013 tadl <tadl@tadl-vaio-fedora>
#
#
#
import getopt
import sys

def usage():
  print(' CombineClusters v1.0 by Tim auf der Landwehr')
  print()
  print(' Usage: combine_clusters.py')
  print('\tCombines the labels and the annotated classes')
  print('\tand prints them sorted by class')
  print()
  print(' --l file')
  print('\tFile that contains labels, default: [name_vectors.mat.rlabel]')
  print(' --c file')
  print('\tFile that contains classes, default: [name_vectors.mat.clustering.10]')
  print(' --out file')
  print(' \tWrite woutput to file, default: STDOUT.')


if __name__ == '__main__':
  try:
    opts, args = getopt.gnu_getopt(sys.argv[1:],"ho:v",["help", "l=", "c=", "out="])
  except (getopt.GetoptError, NameError) as err:
    usage()
    sys.exit()

  # defaults
  label_file = 'name_vectors.mat.rlabel'
  classes_file = 'name_vectors.mat.clustering.10'
  write_file = False


  for o,v in opts:
    if o in ('--l'):
      label_file = v
    elif o in ('--c'):
      classes_file = v
    elif o in ('--out'):
      write_file = True
      outfile = v
    elif o in ('-h','--help'):
      usage()
      sys.exit(1)
    else:
      print('unknown parameter %s'%o)
      sys.exit(1)

  classes = {}

  with open(label_file, 'r') as labels, open(classes_file, 'r') as classes_file:
    row_labels = labels.readlines()
    row_classes = classes_file.readlines()

    if not len(row_labels) == len(row_classes):
      print('Files do not have the same length: %i != %i'%(len(row_labels), len(row_classes)))
      sys.exit(3)

    for i in range(len(row_labels)):
      clas = int(row_classes[i].strip())
      ner = str(row_labels[i].strip())

      if not clas in classes:
        classes[clas] = [ner]
      else:
        classes[clas].append(ner)

  if write_file:
    with open(outfile, 'w') as outfile:
      for i in classes.keys():
        outfile.write('Class %i:\n'%i)
        for ner in classes[i]:
          outfile.write('\t%s\n'%ner)
  else:
    for i in classes.keys():
      print('Class %i:'%i)
      for ner in classes[i]:
          print('\t%s'%ner)


