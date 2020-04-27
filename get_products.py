#!/usr/bin/env python
# coding: utf-8

from classes.EtsyApi import EtsyApi
from commons import *
import os
import time

TABLE_NAME = 'products'
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


def insert_products(shop_id, results):
    for r in results:
        data_tuple = (shop_id, get_date_time_now(), r['listing_id'], r['last_modified_tsz'],
                      r['price'], r['currency_code'], r['views'], r['num_favorers'])
        query = f"""INSERT INTO {TABLE_NAME} (shop_id, check_date, product_id, 
                    last_modified_tsz, price, currency_code, views, num_favorers) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)"""
        cursor.execute(query, data_tuple)


g_sheet_status = []
failures = 0

# Connect to the database
connection = sqlite3.connect(DATABASE)
cursor = connection.cursor()

try:
    # Get shops to update
    control_data = sheet.get_all_records()
    if CONFIG_STATUS == 'test':  # limit the number while testing
        control_data = control_data[:TEST_NUMBER_TO_CHECK]

    etsy = EtsyApi(API_KEY_VERSION)

    for index, c in enumerate(control_data):

        page = 1
        count_page = 0
        code = 0
        shop = c['shop_name']
        print(shop)

        while page:

            time.sleep(SLEEP_TIME)
            print('Page : ' + str(page))

            try:
                data = etsy.get_shop_listings(shop, page=page)
                code = etsy.get_request_code()

            except Exception as ex:
                time.sleep(300)  # Wait 5 minutes
                data = etsy.get_shop_listings(shop, page=page)
                code = etsy.get_request_code()

            if code == 200:
                count_page += 1
                if len(data['results']) == 0:
                    count_page = 'no products'
                    print('No products')
                    page = False
                else:
                    insert_products(shop, data['results'])
                page = data['pagination']['next_page']
            else:
                page = False
                failures += 1

        try:
            sheet.update_cell(index + 2, 7, get_date_time_now())
            sheet.update_cell(index + 2, 8, code)
            sheet.update_cell(index + 2, 9, count_page)
        except Exception as ex:
            print("Failed to update Google sheet", ex)

    connection.commit()
    send_success_message(TABLE_NAME, G_SHEET_LINK, failures)

except sqlite3.Error as error:
    print("Failed to insert data into sqlite table", error)
    send_failed_message(TABLE_NAME, G_SHEET_LINK)

finally:
    cursor.close()
    connection.close()
    print("The SQLite connection is closed")