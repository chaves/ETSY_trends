#!/usr/bin/env python
# coding: utf-8

from classes.EtsyApi import EtsyApi
import pandas as pd
import configparser
import time
import gspread
import datetime
from oauth2client.service_account import ServiceAccountCredentials
import smtplib, ssl
import sqlite3

TODAY = datetime.datetime.now().strftime('%Y-%m-%d')
PRIVATE_FOLDER = './private/'

config_parser = configparser.ConfigParser()
config_parser.read(PRIVATE_FOLDER + 'etsy.conf')

G_SHEET_CREDENTIALS_FILE = PRIVATE_FOLDER + config_parser.get('G_SHEET', 'credentials_file')
G_SHEET_NAME = config_parser.get('G_SHEET', 'sheet_name')
G_SHEET_LINK = config_parser.get('G_SHEET', 'sheet_link')

OUTPUTS_FOLDER = './outputs/'
SQLITE_DATABASE = OUTPUTS_FOLDER + 'etsy.db'

SMTP_SERVER = config_parser.get('EMAIL', 'smtp_server')
SENDER_EMAIL = config_parser.get('EMAIL', 'sender_email')
RECEIVER_EMAIL = config_parser.get('EMAIL', 'receiver_email')
PASSWORD = config_parser.get('EMAIL', 'password')

# Get Google sheet object
def get_sheet_object():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(G_SHEET_CREDENTIALS_FILE, scope)
    gspread_client = gspread.authorize(credentials)
    return gspread_client.open(G_SHEET_NAME).sheet1


sheet = get_sheet_object()

def send_message(subject, text):
    PORT = 587  # For starttls
    message = 'Subject: {}\n\n{}'.format(subject, text)
    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_SERVER, PORT) as server:
        server.starttls(context=context)
        server.login(SENDER_EMAIL, PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, message)


# ### Specific for products

def make_insert_product_query(data_tuple, cursor):
    query = """INSERT INTO products (check_date, product_id, last_modified_tsz, price, views, num_favorers) 
    VALUES (?, ?, ?, ?, ?, ?)"""
    cursor.execute(query, data_tuple)
    return cursor.rowcount

g_sheet_status = []
failures = 0

try:
    # Get shops to update
    control_data = sheet.get_all_records()
    control_data = control_data[:3]
    
    # Connect to the database
    connection = sqlite3.connect(SQLITE_DATABASE)
    cursor = connection.cursor()
    
    etsy = EtsyApi()
    
    for index, c in enumerate(control_data):

        page = 1
        count_page = 0
        no_products = False
        print(c['shop_name'])
        
        while page:

            time.sleep(1)
            print('Page : ' + str(page))

            data = etsy.get_shop_listings(c['shop_name'], page=page)
            code = etsy.get_request_code()

            if code == 200:
                count_page += 1
                if len(data['results']) == 0:
                    no_products = True
                    print('No products')
                    page = False
                else:
                    for result in data['results']:
                        date_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') 
                        data_tuple = (date_now, result['listing_id'], result['last_modified_tsz'], 
                        result['price'], result['views'], result['num_favorers'])
                        make_insert_product_query(data_tuple, cursor)
                page = data['pagination']['next_page']
            
        try:
            if (no_products):
                count_page = 'no products'
            sheet.update_cell(index + 2, 7, date_now)
            sheet.update_cell(index + 2, 8, count_page)
        except:
            print("Failled to update Google sheet")

    connection.commit()
    cursor.close()
    
except sqlite3.Error as error:
    print("Failed to insert data into sqlite table", error)
        
    subject = "Failled to update the products database."
    text = f"Failled to update the products database.\n{G_SHEET_LINK}"
    send_message(subject, text)

finally:
    if (connection):    
        connection.close()
        print("The SQLite connection is closed")
        
        subject = "Products database updated."
        text = f"Products database updated with {failures} failures.\n{G_SHEET_LINK}"
        send_message(subject, text)
