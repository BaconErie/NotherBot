# Code to run the first time you start up the bot
# This will setup the database in the notherbot folder

import sqlite3

connection = sqlite3.connect('notherbot/bot-data.db')
cursor = connection.cursor()

cursor.execute('CREATE TABLE global_user_data (user_id int, key text, value text, type text)')
cursor.execute('CREATE TABLE guild_user_data (guild_id int, user_id int, key text, value text, type text)')
cursor.execute('CREATE TABLE guild_data (guild_id int, key text, value text, type text)')

connection.commit()

connection.close()

print('Completed startup stuff. You can now run main.py in the "notherbot" folder.')