#!/usr/bin/env python
# coding: utf-8

from classes.EtsyApi import EtsyApi
from commons import *
import os
import time

TABLE_NAME = 'shops'
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


def make_insert_shop_query(d):
    data_tuple = (d['shop_name'], d['user_id'], get_date_time_now(), d['is_vacation'], d['last_updated_tsz'],
                  d['listing_active_count'], d['policy_updated_tsz'], d['num_favorers'])
    query = f"""INSERT INTO {TABLE_NAME} (shop_id, user_id, check_date, is_vacation, last_updated_tsz, 
        listing_active_count, policy_updated_tsz, num_favorers) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
    cursor.execute(query, data_tuple)
    return cursor.rowcount


g_sheet_status = []
failures = 0

try:
    # Get shops to update
    control_data = sheet.get_all_records()
    if CONFIG_STATUS == 'test':  # limit the number while testing
        control_data = control_data[:TEST_NUMBER_TO_CHECK]
    
    # Connect to the database
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    
    etsy = EtsyApi(API_KEY_VERSION)
    
    for index, c in enumerate(control_data):
        
        time.sleep(SLEEP_TIME)
        
        data = etsy.get_shop(c['shop_name'])
        code = etsy.get_request_code()
        
        if code == 200:
            make_insert_shop_query(data)
        else:
            failures += 1
            
        try:
            sheet.update_cell(index + 2, 5, get_date_time_now())
            sheet.update_cell(index + 2, 6, code)
        except:
            print("Failed to update Google sheet")

    connection.commit()
    cursor.close()
    
except sqlite3.Error as error:
    print("Failed to insert data into sqlite table", error)
    send_failed_message(TABLE_NAME, G_SHEET_LINK)

finally:
    if (connection):    
        connection.close()
        print("The SQLite connection is closed")
        send_success_message(TABLE_NAME, G_SHEET_LINK, failures)
