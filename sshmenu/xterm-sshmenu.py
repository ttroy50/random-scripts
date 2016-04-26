#!/usr/bin/env python
# Create a launcher and menu item that can be used to 
# launch an xterm window that will ssh to a remote
# server
# Tested with Ubuntu 12.04 but should work with all

import os, sys
import pwd
from optparse import OptionParser
from shutil import copyfile, move, rmtree
import xml.etree.ElementTree as ET
import time
import shutil
from os.path import expanduser

homedir = expanduser("~")

Config = {
	'appDir': homedir + "/.local/share/applications/",
	'menuFile': homedir + "/.config/menus/gnome-applications.menu",
	'backDir': homedir + "/.bk/appMenu/",

	# Gnome menu to use.
	'myMenu': 'remote-servers',
	
	# Prefix to use for the launcher 
	'sshPrefix': 'ssh-',

	# Optional way to specify icons, menu location and any extra xterm requirements
	'work': {
		'icon':'xterm-color',
		'extra':'',
		'dirFile':'remote-servers'
	},
	'cust': {
		'icon':'xterm-color',
		'extra':'-bg grey10',
		'dirFile':'customer-servers'
	},
	'home': {
		'icon':'xterm-color',
		'extra':'',
		'dirFile':'home-servers'
	},
}

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """
    valid = {"yes":True,   "y":True,  "ye":True,
             "no":False,     "n":False}
    if default == None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "\
                             "(or 'y' or 'n').\n")


def addToMenu(fileName='', itype='work'):
	""" Add to the gnome applications menu if it exists
	"""
	try:
		if not os.path.isfile(Config['menuFile']) :
			return

		backFile = str(Config['backDir']) + 'gnome-applications.menu.' + str(int(time.time()))
		shutil.copyfile(Config['menuFile'], backFile)
		tree=ET.parse(Config['menuFile'])
		root = tree.getroot()

		for menu in root.findall('Menu'):
			name = menu.find('Name')
			print name.text
			if name.text == Config['myMenu']:
				print 'found myMenu'
				if name.text == Config[itype]['dirFile']:
					inc = ET.SubElement(menu, 'Include')
					fn = ET.SubElement(inc, 'Filename')
					fn.text = fileName

				for sub in menu.findall('Menu'):
					sname = sub.find('Name')
					print sname.text
					if sname.text == Config[itype]['dirFile']:
						print 'found dirFile in sub'
						inc = ET.SubElement(menu, 'Include')
						fn = ET.SubElement(inc, 'Filename')
						fn.text = fileName

		tree.write(Config['menuFile'])
	except Exception, e:
		print e
		print 'Unable to add to menuFile [%s]'%Config['menuFile']
		sys.exit(1)

def createDesktopFile(command="", server=None, itype='work'):
	""" Create a .desktop file to launch xterm with SSH
	"""
	icon = Config[itype]['icon']
	extra = Config[itype]['extra']

	name="%s%s"%(Config['sshPrefix'], server)
	if command is not None:
		comment="Connect to %s (%s)"%(server, command)
		exe="xterm {extra} -T {server} -name xterm -class {server} -e ssh {command}".format(extra=extra, server=server, command=command)
	else:
		comment="Connect to %s"%(server)
		exe="xterm {extra} -T {server} -name xterm -class {server} -e ssh {server}".format(extra=extra, server=server)

	deskfile="""[Desktop Entry]
Name={name}
Comment={comment}
Exec={exe}
Terminal=false
Type=Application
#Encoding=UTF-8
Icon={icon}
#StartupWMClass=work
""".format(name=name, comment=comment,exe=exe,icon=icon)

	existed = False
	newFile = str(Config['appDir']) + str(Config['sshPrefix']) + str(server) + ".desktop"
	if os.path.isfile(newFile) :
		existed = True
		res = query_yes_no("File [%s%s.desktop] already exists. Overwrite?"%(Config['sshPrefix'], server))
		if res == True:
			print "Will overwrite file"
		else:
			print "Exiting"
			sys.exit(0)

	f = open(newFile, 'w+')
	f.write(deskfile)
	f.close()

	print "File written to [%s]"%newFile
	print ""
	print deskfile

	if existed == False:
		addToMenu(str(Config['sshPrefix']) + str(server) + ".desktop", itype)
	else:
		print 'Not adding to menu file because it already existed'

def main(argv):
    print __name__
    try:
        description = """
Add an ssh link to a desktop file to appear in dash
"""

        parser = OptionParser(description=description, version='%prog v0.1')
        parser.add_option("-c", "--command", dest="command", help="SSH Command (after -e ssh)")
        parser.add_option("-s", "--server", dest="server", help="server name (one word only). Used as command if -c is blank")
        parser.add_option("-t", "--type", dest="type", help="Type of icon")
	(options, args) = parser.parse_args()
    except Exception, e:
        print "caught an exception in options [%s]"%e
        sys.exit(1)

    if options.server is None or options.server == "":
        print "server cannot be empty"
        parser.print_help()
        sys.exit(1)

    if options.type is None or options.type == "":
        options.type = 'work'
    else:
    	try:
    		if Config[options.type] is None:
    			print 'Invalid Type'
    			sys.exit(1)
    	except:
    		print 'Invalid Type'
    		sys.exit(1)

    createDesktopFile(options.command, options.server, options.type)

if __name__ == '__main__':
    main(sys.argv)
