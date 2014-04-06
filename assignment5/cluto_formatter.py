#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  cluto_formatter.py
#
#  Copyright 2013 tadl <tadl@taufderl.de>
#
#
#
import getopt
import sys

########################################################################
########################################################################
#####################      ClutoFormatter      #########################
########################################################################
########################################################################
class ClutoFormatter:

  def __init__(self, input_file):
    print('Reading from [%s] ...'%input_file)
    self.input_file = input_file

  def write_to_matrix_file(self, output_file, write_labels = False):
    rlabel_output_file = output_file + '.rlabel'
    clabel_output_file = output_file + '.clabel'

    with open(input_file, 'r') as source:

      dimensions = []
      for word in source.readline().split():
        dimensions.append(word)

      # pop first because it is 'NAME'
      dimensions.pop(0)
      if write_labels:
        # write dimensions
        print('Writing clabels to [%s]...'%(clabel_output_file))
        with open(clabel_output_file, 'w') as clabel_out:
          for d in dimensions:
            clabel_out.write(d+'\n')

      ners = []
      matrix = []
      for line in source.readlines():
        line = line.split()
        ners.append(line[0])
        line.pop(0)
        matrix.append(line)

    if write_labels:
      # Write NER labels
      print('Writing rlabels to [%s]...'%(rlabel_output_file))

      with open(rlabel_output_file, 'w') as rlabel_out:
        for ner in ners:
          rlabel_out.write(ner+'\n')

    # write matrix file
    print('Dimensions: %i'%len(dimensions))
    print('NERS: %i'%len(ners))
    print('Writing dense matrix to [%s]...'%(output_file))
    with open(output_file, 'w') as outfile:
      outfile.write('%s %s\n'%(len(ners),len(dimensions)))
      for line in matrix:
        outfile.write('%s\n'%(' '.join(line)))

########################################################################
########################################################################
##########################      MAIN      ##############################
########################################################################
########################################################################

def usage():
  print(' ClutoFormatter v1.0 by Tim auf der Landwehr')
  print()
  print(' Usage: cluto_formatter.py')
  print('\tLoads annotated ner data from [name_vectors.txt]')
  print('\tand writes dense matrix output to [name_vectors.mat]')
  print()
  print(' --labels')
  print('\t Additionally the files [*.rlabel] and [*.rlabel] are created')
  print(' --in file')
  print(' \tChange name of the input file.')
  print(' --out file')
  print(' \tChange name of the dense matrix output file.')



if __name__ == '__main__':
  try:
    opts, args = getopt.gnu_getopt(sys.argv[1:],"ho:v",["help", "in=", "out=", "labels"])
  except (getopt.GetoptError, NameError) as err:
    usage()
    sys.exit()

  # defaults
  input_file = 'name_vectors.txt'
  output_file = 'name_vectors.mat'
  labels = False

  for o,v in opts:
    if o in ('--in'):
      input_file = v
    elif o in ['--out']:
      output_file = v
    elif o in ('--labels'):
      labels = True
    elif o in ('-h','--help'):
      usage()
      sys.exit(1)
    else:
      print('unknown parameter %s'%o)
      sys.exit(1)


  cf = ClutoFormatter(input_file)
  cf.write_to_matrix_file(output_file, labels)
