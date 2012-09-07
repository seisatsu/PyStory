######################################
## PyStory Storyboard Manager       ##
## pystory.py                       ##
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

##############################
# Main Program and Interface #
##############################

import os, sys, signal
import config, commands, database, menu, storyfile

VERSION = "PyStory v0.0.2-alpha"

### Internal Variables ###

## Interface Context ##
# Holds the user's current "location" in the interface.
# [HeaderText, MenuType, SceneID]
context = [VERSION, "INIT", None]

## Interface Body ##
# Holds the current body of the interface.
body = ""

## Quit Switch ##
# The program will quit if this becomes false.
running = True

### Command Lists ###

cmdlist_init = ['o', 'q', 'h']
cmdlist_story = ['i', 'l', 'v', 'p', 'r', 'm', 's', 'u', 'c', 'q', 'h']
cmdlist_info = ['n', 'a', 'd', 'no', 'mod', 'b', 's', 'u', 'c', 'q', 'h']
cmdlist_scene = ['n', 't', 'b', 's', 'u', 'c', 'q', 'h']

### Helper Functions ###

# Exit prettily.
def sigint_handler(signum, frame):
	clear()
	sys.exit(0)
signal.signal(signal.SIGINT, sigint_handler)

# Pass off commands.
def command_handler(cmd, cmdlist):
	global body, context
	if cmd[0][:3] in cmdlist and \
	   (cmd[0] == cmd[0][:3] or cmd[0] in commands.fullnames): # Three character command.
		c = commands.commands[cmd[0][:3]](cmd[1:], context)
		cc = cmd[0][:3]
	elif cmd[0][:2] in cmdlist and \
	     (cmd[0] == cmd[0][:2] or cmd[0] in commands.fullnames): # Two character command.
		c = commands.commands[cmd[0][:2]](cmd[1:], context)
		cc = cmd[0][:2]
	elif cmd[0][:1] in cmdlist and \
	     (cmd[0] == cmd[0][:1] or cmd[0] in commands.fullnames): # One character command.
		c = commands.commands[cmd[0][:1]](cmd[1:], context)
		cc = cmd[0][:1]
	elif not len(cmd[0]):
		clear()
		return
	else:
		clear()
		body = "Command unknown or out of context."
		return
	if c: # Process returned control hooks.
		if "body" in c: # Set the interface body text.
			body = c["body"]
		if "context" in c: # Modify context.
			if c["context"][0] == "INFO":
				context[0] = "Story: \"{0}\"".format(
					storyfile.data[-1]["info"]["name"]
				)
			elif c["context"][0] == "SCENE":
				print c["context"][1]
				context[0] = "Scene: \"{0}\"".format(
					storyfile.get_scene_by_id(c["context"][1])[1]
				)
			context[1] = c["context"][0]
			context[2] = c["context"][1]
		elif "back" in c: # Move to STORY menu.
			context[0] = storyfile.data[-1]["info"]["name"]
			context[1] = "STORY"
			context[2] = None
		elif "close" in c: # Close the file.
			close()
		elif "name" in c: # Change the story/scene's name.
			context[0] = c["name"]
		elif "open" in c: # Open a file.
			open_story(c["open"])
		elif "quit" in c: # Quit.
			quit()
		elif "save" in c: # Save the file.
			save()
		elif "undo" in c: # Revert changes.
			undo(c["undo"])
			if context[1] == "STORY":
				context[0] = storyfile.data[-1]["info"]["name"]
			elif context[1] == "INFO":
				context[0] = "Story: \"{0}\"".format(
					storyfile.data[-1]["info"]["name"]
				)
			elif context[1] == "SCENE":
				context[0] = "Scene: \"{0}\"".format(
					storyfile.get_scene_by_id(c["context"][1])[1]
				)
	else:
		body = usage(cc)

# Handle closing the current file.
def close():
	global context
	if not storyfile.current():
		choice = None
		while not choice in ["y", "n", "c"]:
			choice = menu.menu_close()
		if choice == "y":
			database.commit_queue(storyfile.abs_to_sql())
		elif choice == "n":
			pass
		else:
			return False
	database.conn.close()
	context = [VERSION, "INIT", None]
	return True

# Handle opening a file.
def open_story(path):
	global body, context
	if not database.opendb(path):
		body = "Unable to open file."
		return
	ver = database.get("SELECT pystory_ver FROM info")[0][0] # Check version.
	if ver != database.PYSTORY_VER:
		body = "Story file structure version mismatch."
		return 
	storyfile.sql_to_abs()
	context = [storyfile.data[-1]["info"]["name"], "STORY", None]

# Handle quitting.
def quit():
	global running
	if context[1] == "INIT":
		clear()
		running = False
		return
	if close():
		clear()
		running = False

# Handle saving the current file.
def save():
	global body
	if not storyfile.current():
		choice = None
		while not choice in ["y", "n"]:
			choice = menu.menu_save()
		if choice == "y":
			database.commit_queue(storyfile.abs_to_sql())
			body = "Saved."
		elif choice == "n":
			pass
	else:
		body = "Nothing to save."

# Handle reverting changes.
def undo(steps):
	global body
	if len(storyfile.data) == 1:
		body = "Nothing to undo."
		return
	elif steps >= len(storyfile.data):
		body = "More undo steps than revisions."
		return
	choice = None
	while not choice in ["y", "n"]:
		choice = menu.menu_undo(steps)
	if choice == "y":
		storyfile.undo(steps)
		body = "Undid {0} revisions.".format(str(steps))
	elif choice == "n":
		pass

# Clear the console. Should work on Windows NT+ and Unixes.
def clear():
	if config.clear_console:
		if os.name == "nt":
			os.system("cls")
		else:
			os.system("clear")

# Wrap a header and footer around a string.
def wrap(string):
	foot = menu.show_header(context[0])
	print string
	print foot

# Show a usage string.
def usage(cmd):
	return "Usage: "+commands.usage[cmd]

### Mainloop ###

clear()
if len(sys.argv) > 1:
	open_story(sys.argv[1])

while running:
	clear()
	
	if len(body):
		wrap(body)
		body = ""
	else:
		menu.show_header(context[0])

	if context[1] == "INIT": # Initial Menu
		command_handler(menu.menu_initial(), cmdlist_init)
	elif context[1] == "STORY": # Story Menu
		command_handler(menu.menu_story(), cmdlist_story)
	elif context[1] == "INFO": # Info Menu
		command_handler(menu.menu_info(), cmdlist_info)
	elif context[1] == "SCENE": # Scene Menu
		command_handler(menu.menu_scene(), cmdlist_scene)

