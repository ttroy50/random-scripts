#!/usr/bin/env python
# Create a launcher  that can be used to 
# launch an gnome-terminal window that will ssh to a remote
# server.
# Terminals will be in their own window class and not grouped in the launcher
#
# TODO update to python3
#
# Tested on Ubuntu 14.04 
#
# Uses a custom wrapper script around the real gnome-terminal based on the one from Ubuntu 14.04
# The script gnome-terminal-custom should be in your path

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
    # The command
    'gt-command': "gnome-terminal-custom",

    'appDir': homedir + "/.local/share/applications/",
    
    # Prefix to use for the launcher 
    'sshPrefix': 'ssh-',

    # Optional way to specify icons, menu location and any extra xterm requirements
    'work': {
        'icon':'utilities-terminal',
        'extra':'',
        'menu':'remote-servers'
    },
    'cust': {
        'icon':'utilities-terminal',
        'extra':'--profile Customer',
        'menu':'customer-servers'
    },
    'home': {
        'icon':'utilities-terminal',
        'extra':'',
        'menu':'home-servers'
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

def createDesktopFile(command="", server=None, itype='work'):
    """ Create a .desktop file to launch xterm with SSH
    """
    icon = Config[itype]['icon']
    extra = Config[itype]['extra']
    menu = Config[itype]['menu']

    name="%s%s"%(Config['sshPrefix'], server)
    if command is not None:
        comment="Connect to %s (%s)"%(server, command)
        exe="{cmd} {extra} --disable-factory --app-id com.sshmenu.{server} -e \"ssh {command}\"".format(cmd=Config['gt-command'],extra=extra, server=server, command=command)
    else:
        comment="Connect to %s"%(server)
        exe="{cmd} {extra} --disable-factory --app-id com.sshmenu.{server} -e \"ssh {server}\"".format(cmd=Config['gt-command'],extra=extra, server=server)

    deskfile="""[Desktop Entry]
Name={name}
Comment={comment}
Exec={exe}
Icon={icon}
Type=Application
Categories={menu};System;TerminalEmulator;
StartupNotify=true
X-GNOME-SingleWindow=false
OnlyShowIn=GNOME;Unity;
Actions=New
X-Ubuntu-Gettext-Domain=gnome-terminal
StartupWMClass={server}
""".format(name=name, comment=comment,exe=exe,icon=icon,menu=menu,server=server)

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

def main(argv):
    print __name__
    try:
        description = """
Add an ssh link to a desktop file to appear in dash
"""
        # TODO update to ArgParse
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
