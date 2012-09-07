######################################
## PyStory Storyboard Manager       ##
## storyfile.py                     ##
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

########################
# SQL Data Abstraction #
########################

import copy, os, subprocess, time
import config
from database import PYSTORY_VER, get
from database import escape as E

### Internal Variables ###

## Initial Data ##
# This is the initial value for the data storage structure.
init_data = {
	"info": {
		#"name": "",
		#"author": "",
		#"description": "",
		#"notes": ""
	},
	"scenes": [
		#{
			#"order_id": 0,
			#"name": "",
			#"contents": ""
		#}
	]
}

## Data Storage##
# This stores an abstraction of the story data as a list of revisions. At save
# time, the last revision is converted into an SQL statement and committed.
data = []

## Last Save ##
# This is a copy of the last saved revision of the data for comparison.
last_save = {}

### Helper Functions ###

def new_revision():
	global data
	data.append(copy.deepcopy(data[-1]))

def record_save():
	global last_save
	last_save = copy.deepcopy(data[-1])

def current():
	if data:
		return data[-1] == last_save
	return True

def undo(steps):
	global data
	i = 0
	while i < steps:
		data.pop()
		i += 1

def add_scene(order_id, name):
	global data
	for n, scene in enumerate(data[-1]["scenes"]): # Push other scenes out of the way.
		if scene["order_id"] >= order_id:
			data[-1]["scenes"][n]["order_id"] += 1
	data[-1]["scenes"].append({ # Insert the new scene.
		"order_id": order_id,
		"name": name,
		"contents": ""
	})

def remove_scene(order_id):
	global data
	found = False
	for n, scene in enumerate(data[-1]["scenes"]): # Find and delete the scene.
		if scene["order_id"] == order_id:
			data[-1]["scenes"].pop(n)
			found = True
	for n, scene in enumerate(data[-1]["scenes"]): # Move other scenes to fill the gap.
		if scene["order_id"] > order_id:
			data[-1]["scenes"][n]["order_id"] -= 1
	return found

def move_scene(pos, newpos): # Broken
	"""global data
	found = False
	for n, scene in enumerate(data[-1]["scenes"]): # Find the target to move.
		if scene["order_id"] == pos:
			pos_oid = n
			data[-1]["scenes"][n]["order_id"] = -1 # Move this out of the way.
			found = True
	if not found:
		return False
	for n, scene in enumerate(data[-1]["scenes"]): # Start by filling the gap.
		if pos < newpos:
			if scene["order_id"] > pos:
				data[-1]["scenes"][n]["order_id"] -= 1
		else:
			if scene["order_id"] >= pos:
				data[-1]["scenes"][n]["order_id"] += 1
	for n, scene in enumerate(data[-1]["scenes"]): # Push other scenes out of the way.
			if scene["order_id"] >= newpos:
				data[-1]["scenes"][n]["order_id"] += 1
	data[-1]["scenes"][pos_oid]["order_id"] = newpos # Re-insert."""
	return False#True
	
	
def set_info(key, value):
	global data
	print data
	data[-1]["info"][key] = value

def set_scene(order_id, key, value):
	global data
	for n, scene in enumerate(data[-1]["scenes"]):
		if scene["order_id"] == order_id:
			data[-1]["scenes"][n][key] = value
			return

def get_scene_by_id(order_id):
	for scene in data[-1]["scenes"]:
		if scene["order_id"] == order_id:
			return (scene["order_id"], scene["name"], scene["contents"])
	return ()

def get_scenes_by_pattern(pattern):
	scenes = []
	for scene in data[-1]["scenes"]:
		if pattern in scene["name"]:
			scenes.append((scene["order_id"], scene["name"]))
	return tuple(sorted(scenes))

def get_scenes_by_id_range(begin, end):
	scenes = []
	for scene in data[-1]["scenes"]:
		if scene["order_id"] >= begin and scene["order_id"] <= end:
			scenes.append((scene["order_id"], scene["name"]))
	return tuple(sorted(scenes))

def get_all_scenes_by_id():
	scenes = []
	for scene in data[-1]["scenes"]:
		scenes.append((scene["order_id"], scene["name"]))
	return tuple(sorted(scenes))

def text_edit(curr):
	try:
		f = open("{0}{1}".format( # Make sure the tempfile will exist.
			config.working_dir, config.temp_file
		) , "w")
	except (IOError): # Couldn't open the tempfile.
		return False
	if curr: # Put the current contents into the tempfile.
		f.write(curr)
	f.close()
	subprocess.call("{0} {1}{2}".format( # Open the editor on the tempfile.
		config.editor, config.working_dir, config.temp_file
	), shell=True)
	f = open("{0}{1}".format( # Open the tempfile.
		config.working_dir, config.temp_file
	) , "r")
	contents = f.read() # Read the tempfile contents.
	f.close()
	os.remove("{0}{1}".format( # Delete the tempfile.
		config.working_dir, config.temp_file
	))
	return contents

### Converters ###

# Convert abstract data to SQL.
def abs_to_sql():
	global last_save
	qqueue = []
	
	qqueue.append( # Save the info table.
		"""UPDATE info SET pystory_ver='{0}', name='{1}', author='{2}',
		description='{3}', notes='{4}', last_modified='{5}'""".format(
			PYSTORY_VER,
			E(data[-1]["info"]["name"]), E(data[-1]["info"]["author"]),
			E(data[-1]["info"]["description"]), E(data[-1]["info"]["notes"]),
			str(int(time.time()))
		)
	)
	
	qqueue.append("DELETE FROM scenes") # Clear the scenes table for rewriting.
	
	for scene in data[-1]["scenes"]: # Save scenes.
		qqueue.append(
			"""INSERT INTO scenes (order_id, name, contents, last_modified)
			VALUES ('{0}', '{1}', '{2}', '{3}')""".format(
				str(scene["order_id"]), E(scene["name"]), E(scene["contents"]),
				str(int(time.time()))
			)
		)
	
	last_save = copy.deepcopy(data[-1])
	return qqueue

# Convert SQL to abstract data.
def sql_to_abs():
	global data, last_save
	data = [copy.deepcopy(init_data)] # Make sure data is reset.
	
	info = get("SELECT name,author,description,notes FROM info")[0] # Get info.
	data[0]["info"] = {"name": info[0], "author": info[1], 
	                   "description": info[2], "notes": info[3]}
	
	scenes = get("SELECT order_id,name,contents FROM scenes") # Get scenes.
	for scene in scenes:
		data[0]["scenes"].append({"order_id": scene[0], "name": scene[1], "contents": scene[2]})
	
	last_save = copy.deepcopy(data[-1])

