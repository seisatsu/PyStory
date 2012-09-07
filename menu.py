######################################
## PyStory Storyboard Manager       ##
## menu.py                          ##
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

###########################
# Interface Menu Sections #
###########################

### Helper Functions ###

# Format and print a menu header. Return an appropriate footer.
def show_header(text):
	print text
	print "="*len(text)
	return "-"*len(text)

### Menu Sections ###

# Initial menu shown when no story is loaded.
def menu_initial():
	print "(o)pen, (q)uit, (h)elp"
	return raw_input("> ").split(" ")

# Menu shown when a story has been loaded.
def menu_story():
	print "[(v)iew], (n)ame, (a)uthor, (d)escription, (no)tes, (l)ist, (p)ut, (r)emove, (m)ove, (mod)ified, (s)ave, (u)ndo, (c)lose, (q)uit, (h)elp"
	return raw_input("> ").split(" ")

# Menu shown for scene info.
def menu_scene():
	print "[(b)ack], (n)ame, (t)ext, (s)ave, (u)ndo, (c)lose, (q)uit, (h)elp"
	return raw_input("> ").split(" ")

# Menu shown when saving.
def menu_save():
	print "Really Save?"
	print "------------"
	print "(y)es, (n)o"
	test = raw_input("> ").lower()
	if test in ["y", "yes"]:
		return "y"
	elif test in ["n", "no"]:
		return "n"
	else:
		return False

# Menu shown when closing before saving.
def menu_close():
	print "Save Before Closing?"
	print "--------------------"
	print "(y)es, (n)o, (c)ancel"
	test = raw_input("> ").lower()
	if test in ["y", "yes"]:
		return "y"
	elif test in ["n", "no"]:
		return "n"
	elif test in ["c", "cancel"]:
		return "c"
	else:
		return False

# Menu shown when undoing.
def menu_undo(steps):
	print "Really Undo {0} Revisions?".format(str(steps))
	print "-----------------------"+'-'*len(str(steps))
	print "(y)es, (n)o"
	test = raw_input("> ").lower()
	if test in ["y", "yes"]:
		return "y"
	elif test in ["n", "no"]:
		return "n"
	else:
		return False

