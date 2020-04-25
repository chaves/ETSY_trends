#!/usr/bin/env python
# coding: utf-8

import os
import glob
import shutil
import datetime

databases = glob.glob('../outputs/*.sqlite')

for database in databases:

    DATABASE_NAME = database.split('/')[-1]
    DATABASE_FOLDER = os.path.join(os.path.dirname(__file__), '../outputs/')
    BACKUP_FOLDER = DATABASE_FOLDER + 'backup/'
    DATABASE_PATH = DATABASE_FOLDER + DATABASE_NAME
    TODAY = datetime.datetime.now().strftime('%Y-%m-%d')

    try:
        shutil.copy(DATABASE_PATH, BACKUP_FOLDER + f'{TODAY}_{DATABASE_NAME}')
        print(f'Database {DATABASE_NAME} copied !')
    except Exception as ex:
        print(f'Database {DATABASE_NAME} copy failed !', ex)