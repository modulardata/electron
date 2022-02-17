#!/usr/bin/env python

from __future__ import print_function
import os
import sys
import re


SOURCE_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
DOCS_DIR = os.path.join(SOURCE_ROOT, 'docs')


def main():
  os.chdir(SOURCE_ROOT)

  filepaths = []
  totalDirs = 0
  try:
    for root, dirs, files in os.walk(DOCS_DIR):
      totalDirs += len(dirs)
      filepaths.extend(os.path.join(root, f) for f in files if f.endswith('.md'))
  except KeyboardInterrupt:
    print('Keyboard interruption. Please try again.')
    return

  totalBrokenLinks = sum(getBrokenLinks(path) for path in filepaths)
  print(((f'Parsed through {len(filepaths)}' +
          ' files within docs directory and its ') + str(totalDirs) +
         ' subdirectories.'))
  print(f'Found {str(totalBrokenLinks)} broken relative links.')
  return totalBrokenLinks


def getBrokenLinks(filepath):
  currentDir = os.path.dirname(filepath)
  brokenLinks = []

  try:
    f = open(filepath, 'r')
    lines = f.readlines()
  except KeyboardInterrupt:
    print('Keyboard interruption whle parsing. Please try again.')
  finally:
    f.close()

  regexLink = re.compile('\[(.*?)\]\((?P<links>(.*?))\)')
  links = []
  for line in lines:
    if matchLinks := regexLink.search(line):
      relativeLink = matchLinks.group('links')
      if not str(relativeLink).startswith('http'):
        links.append(relativeLink)

  for link in links:
    sections = link.split('#')
    if len(sections) < 2:
      if not os.path.isfile(os.path.join(currentDir, link)):
        brokenLinks.append(link)
    elif str(link).startswith('#'):
      if not checkSections(sections, lines):
        brokenLinks.append(link)
    else:
      tempFile = os.path.join(currentDir, sections[0])
      if os.path.isfile(tempFile):
        try:
          newFile = open(tempFile, 'r')
          newLines = newFile.readlines()
        except KeyboardInterrupt:
          print('Keyboard interruption whle parsing. Please try again.')
        finally:
          newFile.close()

        if not checkSections(sections, newLines):
          brokenLinks.append(link)
      else:
        brokenLinks.append(link)


  print_errors(filepath, brokenLinks)
  return len(brokenLinks)


def checkSections(sections, lines):
  sectionHeader = sections[1].replace('-', '')
  regexSectionTitle = re.compile('# (?P<header>.*)')
  for line in lines:
    if matchHeader := regexSectionTitle.search(line):
      matchHeader = filter(str.isalnum, str(matchHeader.group('header')))
      if matchHeader.lower() == sectionHeader:
       return True
  return False


def print_errors(filepath, brokenLink):
  if brokenLink:
    print(f'File Location: {filepath}')
    for link in brokenLink:
      print("\tBroken links: " + link)


if __name__ == '__main__':
  sys.exit(main())
