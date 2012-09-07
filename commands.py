######################################
## PyStory Storyboard Manager       ##
## commands.py                      ##
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
# Interface Command Handling #
##############################

import time
import config, menu
from database import get
import storyfile as sf

### Commands ###

def cmd_author(args, context):
	if len(args) == 0: # Show story author.
		body = "Author: "+sf.data[-1]["info"]["author"]
	else: # Change story author.
		sf.new_revision()
		sf.set_info("author", ' '.join(args))
		body = "Author updated."
	return {"body": body}

def cmd_back(args, context):
	if len(args) != 0:
		return False
	return {"back": True}

def cmd_close(args, context):
	if len(args) != 0:
		return False
	return {"close": True}

def cmd_description(args, context):
	if len(args) == 0: # Show story description.
		body = "Description: "+sf.data[-1]["info"]["description"]
	else: # Change story description.
		sf.new_revision()
		sf.set_info("description", ' '.join(args))
		body = "Description updated."
	return {"body": body}

def cmd_help(args, context):
	if len(args) > 1:
		return False
	if len(args) == 0:
		body = ""
		for cmd in sorted(list(usage)):
			if body:
				body += "\n"
			body += usage[cmd]
	elif args[0][:3] in usage and \
	   (args[0] == args[0][:3] or args[0] in fullnames): # Three letter command.
		body = "Usage: "+usage[args[0][:3]]
		body += "\n"+help[args[0][:3]]
	elif args[0][:2] in usage and \
	   (args[0] == args[0][:2] or args[0] in fullnames): # Two letter command.
		body = "Usage: "+usage[args[0][:2]]
		body += "\n"+help[args[0][:2]]
	elif args[0][:1] in usage and \
	   (args[0] == args[0][:1] or args[0] in fullnames): # One letter command.
		body = "Usage: "+usage[args[0][:1]]
		body += "\n"+help[args[0][:1]]
	else:
		return False
	return {"body": body}

def cmd_info(args, context):
	if len(args) != 0:
		return False
	return {"context": ("INFO", None)}

def cmd_list(args, context):
	if len(args) > 1:
		return False
	if len(args) == 0: # List all scenes.
		scenes = sf.get_all_scenes_by_id()
	elif len(args) == 1: # Range is supplied.
		scene_range = args[0].split('-')
		if not len(scene_range) in [1, 2] : # Range must be one or two numbers.
			return False
		try: # Convert range to integers, check for non-integers.
			scene_range[0] = int(scene_range[0])
			if len(scene_range) == 2:
				scene_range[1] = int(scene_range[1])
		except (ValueError):
			return False
		if len(scene_range) == 1: # Get single scene.
			scenes = (sf.get_scene_by_id(scene_range[0]),)
			print scenes
		elif len(scene_range) == 2: # Get range of scenes.
			if scene_range[0] > scene_range[1]: # Check for backwards range.
				return False
			scenes = sf.get_scenes_by_id_range(scene_range[0], scene_range[1])
	body = "Scene listing:"
	for scene in scenes:
		body += "\n"
		body += "({0}) {1}".format(str(scene[0]), scene[1])
	return {"body": body}

def cmd_move(args, context):
	if len(args) != 2:
		return False
	try:
		pos = int(args[0])
		amount = int(args[1])
	except (ValueError):
		return False
	if pos < 1 or pos > len(sf.data[-1]["scenes"]):
		return False
	if pos + amount < 1 or pos + amount > len(sf.data[-1]["scenes"]):
		return False
	sf.new_revision()
	if not sf.move_scene(pos, amount):
		return False
	body = "Scene moved."
	return {"body": body}

def cmd_name(args, context):
	if context[1] == "INFO":
		if len(args) == 0: # Show story name.
			body = "Story Name: "+sf.data[-1]["info"]["name"]
		else: # Change story name.
			sf.new_revision()
			sf.set_info("name", ' '.join(args))
			body = "Story name updated."
			c = "Story: "
	elif context[1] == "SCENE":
		if len(args) == 0: # Show scene name.
			body = "Scene Name: "+sf.get_scene_by_id(context[2])[1]
		else: # Change scene name.
			sf.new_revision()
			sf.set_scene(context[2], "name", ' '.join(args))
			body = "Scene name updated."
			c = "Scene: "
	if len(args) != 0:
		return {"body": body, "name": "{0}\"{1}\"".format(
			c, ' '.join(args)
		)}
	else:
		return {"body": body}

def cmd_open(args, context):
	if len(args) != 1:
		return False
	return {"open": args[0]}

def cmd_put(args, context):
	if len(args) < 2:
		return False
	try: # Get destination position and fit within bounds.
		pos = int(args[0])
		if pos < 1:
			pos = 1
		elif pos > len(sf.data[-1]["scenes"])+1:
			pos = len(sf.data[-1]["scenes"])+1
	except (ValueError):
		return False
	sf.new_revision()
	sf.add_scene(pos, ' '.join(args[1:]))
	body = "New scene inserted."
	return {"body": body}

def cmd_quit(args, context):
	if len(args) != 0:
		return False
	return {"quit": True}

def cmd_remove(args, context):
	if len(args) == 0:
		return False
	try: # See if the scene specifier is an integer.
		if len(args) == 1:
			pos = int(args[0])
			if pos < 1 or pos > len(sf.data[-1]["scenes"]):
				return False
		else:
			raise ValueError
	except (ValueError): # It wasn't.
		scenes = sf.get_scenes_by_pattern(' '.join(args))
		if not scenes: # No such scene.
			return False
		if len(scenes) > 1: # Multiple matches.
			body = "Ambiguous scene selection."
			return {"body": body}
		pos = scenes[0][0]
	if not sf.remove_scene(pos): # No such scene.
		return False
	body = "Scene deleted."
	return {"body": body}

def cmd_save(args, context):
	if len(args) != 0:
		return False
	return {"save": True}

def cmd_text(args, context):
	if len(args) != 0:
		return False
	contents = sf.text_edit(sf.get_scene_by_id(context[2])[2])
	if not contents:
		body = "Error processing tempfile."
		return {"body": body}
	sf.set_scene(context[2], "contents", contents)
	body = "Scene content updated."
	return {"body": body}

def cmd_undo(args, context):
	if len(args) > 1:
		return False
	if len(args) == 1:
		try:
			steps = int(args[0])
		except (ValueError):
			return False
		if steps < 1:
			return False
	else:
		steps = 1
	return {"undo": steps}

def cmd_view(args, context):
	if len(args) == 0:
		return False
	try: # See if the scene specifier is an integer.
		if len(args) == 1:
			pos = int(args[0])
			if pos < 1:
				return False
			if pos > len(sf.data[-1]["scenes"]):
				return False
		else:
			raise ValueError
	except (ValueError): # It wasn't.
		scenes = sf.get_scenes_by_pattern(' '.join(args))
		if not scenes: # No such scene.
			return False
		if len(scenes) > 1: # Multiple matches.
			body = "Ambiguous scene selection."
			return {"body": body}
		pos = scenes[0][0]
	return {"context": ("SCENE", pos)}

def cmd_notes(args, context):
	if len(args) != 0:
		return False
	contents = sf.text_edit(sf.data[-1]["info"]["notes"])
	if not contents:
		body = "Error processing tempfile."
		return {"body": body}
	sf.set_info("notes", contents)
	body = "Notes updated."
	return {"body": body}

def cmd_modified(args, context):
	if len(args) != 0:
		return False
	lm = get("SELECT last_modified FROM info")
	lm = lm[0][0]
	body = "Last modified: {0}".format(
		time.strftime("%B %d %Y at %I:%M:%S%P %Z", time.localtime(lm))
	)
	return {"body": body}

### Maps ###

## Command Map ##
# Map of command names to command functions.
commands = {
	"a": cmd_author,
	"b": cmd_back,
	"c": cmd_close,
	"d": cmd_description,
	"h": cmd_help,
	"i": cmd_info,
	"l": cmd_list,
	"m": cmd_move,
	"n": cmd_name,
	"o": cmd_open,
	"p": cmd_put,
	"q": cmd_quit,
	"r": cmd_remove,
	"s": cmd_save,
	"t": cmd_text,
	"u": cmd_undo,
	"v": cmd_view,
	"no": cmd_notes,
	"mod": cmd_modified
}

## Fullname Map ##
# Map of long command names.
fullnames = [
	"author",
	"back",
	"close",
	"description",
	"help",
	"info",
	"list",
	"move",
	"name",
	"open",
	"put",
	"quit",
	"remove",
	"save",
	"text",
	"undo",
	"view",
	"notes",
	"modified"
]

## Usage Map ##
# Map of short command usage messages.
usage = {
	"a": "(a)uthor [value]",
	"b": "(b)ack",
	"c": "(c)lose",
	"d": "(d)escription [value]",
	"h": "(h)elp [command]",
	"i": "(i)nfo",
	"l": "(l)ist [range]",
	"m": "(m)ove <number> <+/-amount>",
	"n": "(n)ame [value]",
	"o": "(o)pen <file>",
	"p": "(p)ut <position> <name>",
	"q": "(q)uit",
	"r": "(r)emove <scene>",
	"s": "(s)ave",
	"t": "(t)ext",
	"u": "(u)ndo [steps]",
	"v": "(v)iew <scene>",
	"no": "(no)tes",
	"mod": "(mod)ified"
}

## Help Map ##
# Map of long command help messages.
help = {
	"a": "View or change the author string.",
	"b": "Return to the previous menu.",
	"c": "Close the current story file.",
	"d": "View or change the description string.",
	"h": "View the help for a command, or the list of commands.",
	"i": "Enter the story's info menu.",
	"l": "List the scenes in the story, in order or by range.",
	"m": "Modify the position of the numbered scene by the specified amount.",
	"n": "View or change the name string of the story or scene.",
	"o": "Open a story file.",
	"p": "Insert a new scene of the specified name at the specified position.",
	"q": "Quit PyStory.",
	"r": "Delete the specified scene by name or position.",
	"s": "Save the current story file.",
	"t": "Edit the contents of the scene.",
	"u": "Undo the previous action, or several previous actions.",
	"v": "Enter the specified scene's menu by name or position.",
	"no": "Edit the story notes.",
	"mod": "Show when the story was last saved."
}

