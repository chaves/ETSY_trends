import configparser
import datetime
import smtplib
import ssl
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import sqlite3

SLEEP_TIME = 3

TODAY = datetime.datetime.now().strftime('%Y-%m-%d')
PRIVATE_FOLDER = './private/'
OUTPUTS_FOLDER = './outputs/'

config_parser = configparser.ConfigParser()
config_parser.read(PRIVATE_FOLDER + 'etsy.conf')

CONFIG_STATUS = config_parser.get('CONFIG', 'status')
TEST_NUMBER_TO_CHECK = int(config_parser.get('CONFIG', 'test_number_to_check'))  # config_parser returns a string

G_SHEET_CREDENTIALS_FILE = PRIVATE_FOLDER + config_parser.get('GOOGLE', 'credentials_file')

SMTP_SERVER = config_parser.get('EMAIL', 'smtp_server')
SENDER_EMAIL = config_parser.get('EMAIL', 'sender_email')
RECEIVER_EMAIL = config_parser.get('EMAIL', 'receiver_email')
PASSWORD = config_parser.get('EMAIL', 'password')


# Send status email
def send_message(subject, text):
    message = 'Subject: {}\n\n{}'.format(subject, text)
    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_SERVER, 587) as server:
        server.starttls(context=context)
        server.login(SENDER_EMAIL, PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, message)


# Get Google sheet object
def get_sheet_object(g_sheet_name):

    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(G_SHEET_CREDENTIALS_FILE, scope)
    gspread_client = gspread.authorize(credentials)
    return gspread_client.open(g_sheet_name).sheet1


def send_failed_message(table_name, g_sheet_link):
    subject = f"Failed to update the {table_name} database."
    text = f"Failed to update the {table_name} database.\n{g_sheet_link}"
    send_message(subject, text)


def send_success_message(table_name, g_sheet_link, failures):
    subject = f"{table_name.title()} database updated."
    text = f"{table_name.title()} database updated with {failures} failures.\n{g_sheet_link}"
    send_message(subject, text)


def get_date_time_now():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def create_database(database):

    conn = sqlite3.connect(database)
    c = conn.cursor()

    try:
        c.execute('''CREATE TABLE `users` (
        `id` integer PRIMARY KEY,
        `user_id` integer,
        `check_date` timestamp,
        `transaction_buy_count` integer,
        `transaction_sold_count` integer
      )''')
        print('Table users created !')
    except sqlite3.Error as error:
        print('Failed to create users table !', error)

    try:
        c.execute('''CREATE TABLE `shops` (
        `id` integer PRIMARY KEY,
        `shop_id` text '',
        `user_id` integer,
        `check_date` timestamp,
        `is_vacation` integer,
        `last_updated_tsz` integer,
        `listing_active_count` integer,
        `policy_updated_tsz` integer,
        `num_favorers` integer
      )''')
        print('Table shops created !')
    except sqlite3.Error as error:
        print('Failed to create shops table !', error)

    try:
        c.execute('''CREATE TABLE `products` (
        `id` integer PRIMARY KEY,
        `shop_id` text '',
        `check_date` timestamp,
        `product_id` integer,
        `last_modified_tsz` integer,
        `price` real,
        `views` integer,
        `num_favorers` integer
      )''')
        print('Table products created!')
    except sqlite3.Error as error:
        print('Failed to create products table !', error)

    c.close()
    conn.close()