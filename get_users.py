#!/usr/bin/env python
# coding: utf-8

from classes.EtsyApi import EtsyApi
from commons import *
import os
import time

TABLE_NAME = 'users'
# So the script can run un several servers
SERVER = 'SERVER_KIM'
G_SHEET_NAME = config_parser.get(SERVER, 'sheet_name')
G_SHEET_LINK = config_parser.get(SERVER, 'sheet_link')
DATABASE_NAME = config_parser.get(SERVER, 'database_name')
# With several API keys
API_KEY_VERSION = 'api_key_google_mail'

DATABASE = OUTPUTS_FOLDER + DATABASE_NAME

# Get the Google Sheet control object
sheet = get_sheet_object(G_SHEET_NAME)

if not os.path.isfile(DATABASE):
    create_database(DATABASE)

# ### Specific for users

def make_insert_user_query(d):
    data_tuple = (d['user_id'], get_date_time_now(), d['transaction_buy_count'], d['transaction_sold_count'])
    query = f"""INSERT INTO {TABLE_NAME} (user_id, check_date, transaction_buy_count, transaction_sold_count) 
    VALUES (?, ?, ?, ?)"""
    cursor.execute(query, data_tuple)
    return cursor.rowcount

g_sheet_status = []
failures = 0

# Connect to the database
connection = sqlite3.connect(DATABASE)
cursor = connection.cursor()

try:
    # Get users to update
    control_data = sheet.get_all_records()
    if CONFIG_STATUS == 'test':  # limit the number while testing
        control_data = control_data[:TEST_NUMBER_TO_CHECK]
    
    etsy = EtsyApi(API_KEY_VERSION)
    
    for index, c in enumerate(control_data):
        
        time.sleep(SLEEP_TIME)

        try:
            data = etsy.user_profile(c['user_id'])
            code = etsy.get_request_code()

        except Exception as ex:
            time.sleep(300)  # Wait 5 minutes
            data = etsy.user_profile(c['user_id'])
            code = etsy.get_request_code()
        
        if code == 200:
            make_insert_user_query(data)
        else:
            failures += 1
            
        try:
            sheet.update_cell(index + 2, 2, get_date_time_now())
            sheet.update_cell(index + 2, 3, code)
        except Exception as ex:
            print("Failed to update Google sheet", ex)

    connection.commit()

    send_success_message(TABLE_NAME, G_SHEET_LINK, failures)
    
except sqlite3.Error as error:
    print("Failed to insert data into sqlite table", error)
    send_failed_message(TABLE_NAME, G_SHEET_LINK)

finally:
    if (connection):
        cursor.close()
        connection.close()
        print("The SQLite connection is closed")