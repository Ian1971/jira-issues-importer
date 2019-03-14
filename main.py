#!/usr/bin/env python

import getpass
from collections import namedtuple
from lxml import objectify
from project import Project
from importer import Importer
import asyncio

def read_xml_sourcefile(file_name):
  all_text = open(file_name).read()
  return objectify.fromstring(all_text)


file_name = input('Path to JIRA XML query file: ')
jiraProj = input('JIRA project name to use: ')
us = input('GitHub account name: ')
repo = input('GitHub project name: ')
user = input('GitHub username: ')
pw = getpass.getpass('GitHub access token: ')
mode = input('operation mode. blank=default, skip_milestones, skip_labels')

async def main():
    
  #skip.txt is a list of jira id's to skip
  f = open('skip.txt', 'r')
  skip = f.read().splitlines()
  f.close()

  all_xml = read_xml_sourcefile(file_name)
  Options = namedtuple("Options", "user passwd account repo skip batch_size")
  opts = Options(user=user, passwd=pw, account=us, repo=repo, skip=skip, batch_size=50)

  project = Project(jiraProj)

  for item in all_xml.channel.item:
    project.add_item(item)

  project.merge_labels_and_components()
  project.prettify()

  '''
  Steps:
    1. Create any milestones
    2. Create any labels
    3. Create each issue with comments, linking them to milestones and labels
    4: Post-process all comments to replace issue id placeholders with the real ones
  '''

  importer = Importer(opts, project)

  if "skip_milestones" not in mode:
    importer.import_milestones()

  if "skip_labels" not in mode:
    importer.import_labels()
  await importer.import_issues()
  importer.post_process_comments()

  

asyncio.run(main())
