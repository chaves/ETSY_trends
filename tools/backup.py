#!/usr/bin/env python
# coding: utf-8

import shutil
import os
from os import path
import datetime

DATABASE_NAME = 'etsy.db'
DATABASE_FOLDER = os.path.join(os.path.dirname(__file__), '../outputs/')
BACKUP_FOLDER = DATABASE_FOLDER + 'backup/'
DATABASE_PATH = DATABASE_FOLDER + DATABASE_NAME

TODAY = datetime.datetime.now().strftime('%Y-%m-%d')

def main():
  try:
    shutil.copy(DATABASE_PATH, BACKUP_FOLDER + f'{TODAY}_etsy.db')
    print('Database copied !')
  except:
    print('Database copy failled !')

main()