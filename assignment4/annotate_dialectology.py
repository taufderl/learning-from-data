#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  annotate_dialectology.py
#
#  Copyright 2013 tadl <tadl@tadl-vaio-fedora>
#
#

def annotate_035txt():
  lines = open('035.txt', 'r').readlines()
  outfile = open('035_annotated.txt', 'w')

  for line in lines:
    if line.startswith('d'):
      outfile.write('devil,'+line)
    elif line.startswith('l'):
      outfile.write('lucifer,'+line)
    else:
      outfile.write('no_class,'+line)

if __name__ == '__main__':
  annotate_035txt()

