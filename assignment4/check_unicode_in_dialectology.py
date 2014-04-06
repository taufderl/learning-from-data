#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  check_unicode_in_dialectology.py
#
#  Copyright 2013 tadl <tadl@tadl-vaio-fedora>
#
#
import unicodedata

def check_for_unicodes_in_file(filename, unicode_range):
  chars = []
  for code in unicode_range:
    chars.append(chr(code))

  lines = open(filename, 'r').readlines()

  for line in lines:
    for token in line.strip():
      if token in chars:
        #print('found %s in chars at %i'%(token, chars.index(token)))
        # DO NOTHING
        x = 1
      else:
        print('DID NOT FIND %s'%token)

if __name__ == '__main__':
  check_for_unicodes_in_file('007.txt', list(range(32,1000)))

