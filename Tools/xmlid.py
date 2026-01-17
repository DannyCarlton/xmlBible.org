#!/usr/bin/env python3

'''Assigns element ID to xmlBible.org Interlinear XML.

The assignment is done as follows:

  * book id is kept as-is.
  * chapter id is 'c{chapter.num}'
  * verse id is 'v{verse.num}'
  * word id is 'v{verse.num}-w{word.num}'

Where '{tag.num}' is the 'num' attribute of the element of 'tag'.

URL fragment is used to select a particular element in the document:
https://developer.mozilla.org/en-US/docs/Web/URI/Reference/Fragment

The fragment selection also works for XML ID:
https://www.w3.org/DesignIssues/Fragment.html

XML ID is formally defined as the 'xml:id' attribute of any element:
https://www.w3.org/TR/xml-id/

It can also informally be the 'id' attribute of any element:
https://www.w3.org/html/wg/wiki/IdAndTypeID
'''

import argparse
import glob
import io
import logging
import os
import re
import sys

from typing import Dict, List, Optional, Set, Tuple


def Parser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument(
      '--interlinear-xml-dir', metavar='DIR', default='../Interlinear',
      help='The directory containing xmlBible.org Interlinear XML files.')
  parser.add_argument(
      '--output-dir', metavar='DIR', required=True,
      help='The output directory of the processed XML files.  '
      'Existing files are skipped.  Files getting fatal errors are '
      'renamed with an .error suffix.  Running again will resume after the '
      'last successful file.')
  return parser


PARSER = Parser()


def Main():
  args = PARSER.parse_args()

  xmls = glob.glob(os.path.join(args.interlinear_xml_dir, '*/*.xml'))
  if len(xmls) != 1189:
    logging.error(
        'The --interlinear_xml_dir does not have the expected number of files: '
        'got %d, want %d: %s',
        len(xmls), 1189, args.output)
    return 1

  xmls.sort()

  for in_xml in xmls:
    stem = os.path.relpath(in_xml, args.interlinear_xml_dir)
    out_xml = os.path.join(args.output_dir, stem)
    if os.path.exists(out_xml):
      logging.warning('Skipping already exists: %s', out_xml)
      continue

    logging.info('Processing: %s', stem)
    dirname = os.path.dirname(out_xml)
    if not os.path.isdir(dirname):
      os.makedirs(dirname)

    try:
      out_file = open(out_xml, 'x')
    except FileExistsError:
      logging.warning('Skipping already created: %s', out_xml)
      continue

    with open(in_xml) as in_file, out_file:
      try:
        Process(out_file, in_file)
      except:
        os.rename(out_xml, out_xml + '.error')
        raise


RE_BOOK = re.compile(r'<book name="(.*?)" id="(.*?)"(.*?)>')
RE_CHAPTER = re.compile(r'<chapter num="(.*?)"(.*?)>')
RE_VERSE = re.compile(r'<verse num="(.*?)"(.*?)>')
RE_WORD = re.compile(r'<word num="(.*?)"(.*?)>')


def Process(out_file: io.TextIOBase, in_file: io.TextIOBase):
  """Assigns XML element IDs line by line.

  Args:
    out_file: The output file object.
    in_file: The input file object.
  """
  book_id = 0
  chapter_num = 0
  verse_num = 0
  word_num = 0

  for line in in_file:
    if line.startswith('<?xml'):
      out_file.write(line)
      continue

    m = RE_BOOK.search(line)
    if m:
      book_id = int(m.group(2))
      book_testament = m.group(3)
      out_file.write(line)
      continue

    m = RE_CHAPTER.search(line)
    if m:
      chapter_num = int(m.group(1))
      if 'id="' not in line:
        line = line.replace('>', f' id="c{chapter_num}">')
      out_file.write(line)
      continue

    m = RE_VERSE.search(line)
    if m:
      verse_num = int(m.group(1))
      if 'id="' not in line:
        line = line.replace('>', f' id="v{verse_num}">')
      out_file.write(line)
      continue

    m = RE_WORD.search(line)
    if m:
      word_num = int(m.group(1))
      if 'id="' not in line:
        line = line.replace('>', f' id="v{verse_num}-w{word_num}">')
      out_file.write(line)
      continue

    # Passthrough any other lines not recognized.
    out_file.write(line)


if __name__ == '__main__':
  sys.exit(Main())
