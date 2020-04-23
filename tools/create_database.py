#!/usr/bin/env python
# coding: utf-8

import sqlite3

conn = sqlite3.connect('etsy.db')
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
except:
  print('DatFailed to create users base !')
  
try:
  c.execute('''CREATE TABLE `shops` (
    `id` integer PRIMARY KEY,
    `shop_id` text '',
    `check_date` timestamp,
    `is_vacation` integer,
    `last_updated_tsz` integer,
    `listing_active_count` integer,
    `policy_updated_tsz` integer,
    `num_favorers` integer
  )''')
  print('Table shops products !')
except:
  print('DatFailed to create shops base !')

try:
  c.execute('''CREATE TABLE `products` (
    `id` integer PRIMARY KEY,
    `check_date` timestamp,
    `product_id` integer,
    `last_modified_tsz` integer,
    `price` real,
    `views` integer,
    `num_favorers` integer
  )''')
  print('Table users products !')
except:
  print('DatFailed to create products base !')

c.close()
conn.close()



