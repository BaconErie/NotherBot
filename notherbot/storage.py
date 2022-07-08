# Database Wrapper
# Turns Python functions into SQL

import sqlite3
from json import loads, dumps

####################
# GLOBAL USER DATA #
####################

def get_global_user_data(user_id, key):
    connection = sqlite3.connect('bot-data.db')
    cursor = connection.cursor()

    cursor.execute('SELECT value, type FROM global_user_data WHERE user_id=? AND key=?', (user_id, key))

    output = cursor.fetchone()

    if output == None or len(output) == 0:
        # No data exists
        connection.close()
        return None

    value = output[0]
    value_type = output[1]

    if value_type == 'int':
        value = int(value)
    elif value_type == 'bool':
        value = bool(value)
    elif value_type == 'str':
        value = str(value)
    elif value_type == 'dict' or value_type == 'list':
        value = loads(value)

    connection.commit()
    connection.close()

    return value

def set_global_user_data(user_id, key, value):
    connection = sqlite3.connect('bot-data.db')
    cursor = connection.cursor()

    value_type = type(value).__name__

    # If the value is a dictionary or list, turn it into a string
    if value_type == 'dict' or value_type == 'list':
        value = dumps(value)
    
    value = str(value)

    # Delete previous entry
    cursor.execute('DELETE FROM global_user_data WHERE user_id=? AND key=?', (user_id, key))

    # Add new entry
    cursor.execute('INSERT INTO global_user_data (user_id, key, value, type) VALUES (?,?,?,?)', (user_id, key, value, value_type))

    connection.commit()
    connection.close()

###################
# GUILD USER DATA #
###################

def get_guild_user_data(guild_id, user_id, key):
    connection = sqlite3.connect('bot-data.db')
    cursor = connection.cursor()

    cursor.execute('SELECT value, type FROM guild_user_data WHERE guild_id=? AND user_id=? AND key=?', (guild_id, user_id, key))

    output = cursor.fetchone()

    if output == None or len(output) == 0:
        # No data exists
        connection.close()
        return None

    value = output[0]
    value_type = output[1]

    if value_type == 'int':
        value = int(value)
    elif value_type == 'bool':
        value = bool(value)
    elif value_type == 'str':
        value = str(value)
    elif value_type == 'dict' or value_type == 'list':
        value = loads(value)

    connection.commit()
    connection.close()

    return value

def set_guild_user_data(guild_id, user_id, key, value):
    connection = sqlite3.connect('bot-data.db')
    cursor = connection.cursor()

    value_type = type(value).__name__

    # If the value is a dictionary or list, turn it into a string
    if value_type == 'dict' or value_type == 'list':
        value = dumps(value)    

    value = str(value)

    # Delete previous entry
    cursor.execute('DELETE FROM guild_user_data WHERE guild_id=? AND user_id=? AND key=?', (guild_id, user_id, key))

    # Add new entry
    cursor.execute('INSERT INTO guild_user_data (guild_id, user_id, key, value, type) VALUES (?,?,?,?,?)', (guild_id, user_id, key, value, value_type))

    connection.commit()
    connection.close()

##############
# GUILD DATA #
##############

def get_guild_data(guild_id, key):
    connection = sqlite3.connect('bot-data.db')
    cursor = connection.cursor()

    cursor.execute('SELECT value, type FROM guild_data WHERE guild_id=? AND key=?', (guild_id, key))

    output = cursor.fetchone()

    if output == None or len(output) == 0:
        # No data exists
        connection.close()
        return None

    value = output[0]
    value_type = output[1]

    if value_type == 'int':
        value = int(value)
    elif value_type == 'bool':
        value = bool(value)
    elif value_type == 'str':
        value = str(value)
    elif value_type == 'dict' or value_type == 'list':
        value = loads(value)

    connection.commit()
    connection.close()

    return value

def set_guild_data(guild_id, key, value):
    connection = sqlite3.connect('bot-data.db')
    cursor = connection.cursor()

    value_type = type(value).__name__

    # If the value is a dictionary or list, turn it into a string
    if value_type == 'dict' or value_type == 'list':
        value = dumps(value)

    value = str(value)

    # Delete previous entry
    cursor.execute('DELETE FROM guild_data WHERE guild_id=? AND key=?', (guild_id, key))

    # Add new entry
    cursor.execute('INSERT INTO guild_data (guild_id, key, value, type) VALUES (?,?,?,?)', (guild_id, key, value, value_type))

    connection.commit()

    connection.close()