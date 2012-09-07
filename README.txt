PyStory Storyboard Manager
Copyright (c) 2012 Michael D. Reiley <mreiley@omegasdg.com>

Released under the MIT/Expat License.

This is an experimental command line menu driven program for managing and 
editing a textual storyboard.

Usage: ./pystory.py [file]

File List:
* pystory.py : Main Program and Interface
* config.py : User Configuration
* database.py : SQLite Database Handling
* storyfile.py : SQL Data Abstraction
* menu.py : Interface Menu Sections
* commands.py : Interface Command Handling

Storyboard Structure:
* Story:
** Name
** Author
** Description
** Notes
** Scenes:
*** Position
*** Name
*** Contents

