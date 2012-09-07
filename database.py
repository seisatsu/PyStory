######################################
## PyStory Storyboard Manager       ##
## database.py                      ##
## Copyright 2012 Michael D. Reiley ##
######################################

## **********
## Permission is hereby granted, free of charge, to any person obtaining a copy 
## of this software and associated documentation files (the "Software"), to 
## deal in the Software without restriction, including without limitation the 
## rights to use, copy, modify, merge, publish, distribute, sublicense, and/or 
## sell copies of the Software, and to permit persons to whom the Software is 
## furnished to do so, subject to the following conditions:
##
## The above copyright notice and this permission notice shall be included in 
## all copies or substantial portions of the Software.
##
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
## IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
## FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
## AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
## LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
## FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS 
## IN THE SOFTWARE.
## **********

############################
# SQLite Database Handling #
############################

import sqlite3, time

SQLITE3_MAX_INT = 9223372036854775808
PYSTORY_VER = "PYSTORY_002"

### Database Structure ###
"""
info:= pystory_ver, name, author, description, last_modified
	pystory_ver:= PYSTORY_002
	name:= A Disastrous Celebration
	author:= The Mighty Shwan Nolastname
	description:= A party goes terribly wrong.
	last_modified:= 1346807742

scenes:= order_id, name, contents, last_modified
	order_id:= 12
	name:= The Big Party
	contents:= (SCENE SCRIPT)
	last_modified:= 1346807742
"""

### Internal Variables ###

## Info Table ##
# Structure of the info table. Changing this will break the software.
i_table = """CREATE TABLE IF NOT EXISTS info
          (pystory_ver TEXT, name TEXT, author TEXT, description TEXT,
          last_modified INTEGER)"""

## Scenes Table ##
# Structure of the scenes table. Changing this will break the software.
s_table = """CREATE TABLE IF NOT EXISTS scenes
          (order_id INTEGER, name TEXT, contents TEXT, last_modified INTEGER)"""

## Initial Info ##
# This is the initial contents of the info table.
initinfo = """INSERT INTO info (pystory_ver, name, author, description,
           last_modified) VALUES ('{0}', 'Untitled Story', 'Unknown Author',
           'No Description', '{1}')""".format(PYSTORY_VER, str(int(time.time())))

## Database Handle ##
# A connection to the story file database.
conn = sqlite3.Connection

### Database Functions ###

# Open database, and initialize if new.
def opendb(dbname):
	global conn
	try:
		conn = sqlite3.connect(dbname)
	except (sqlite3.OperationalError):
		return False
	C = conn.cursor()
	C.execute(i_table)
	C.execute(s_table)
	conn.commit()
	C.close()
	
	chk = get("SELECT * FROM info") # Check if info table exists.
	if not chk: # Create initial info.
		put(initinfo)
	
	return True

# Get rows from the database.
def get(query):
	C = conn.cursor()
	C.execute(query)
	rows = C.fetchall()
	C.close()
	return rows

# Commit an update to the database.
def put(query):
	C = conn.cursor()
	C.execute(query)
	conn.commit()
	C.close()

# Commit a list of updates.
def commit_queue(queue):
	for query in queue:
		put(query)

# Escape user input.
def escape(userstr):
	return userstr.replace("'", "''")

