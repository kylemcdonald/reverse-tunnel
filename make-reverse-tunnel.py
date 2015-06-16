#!/bin/python

import argparse
import glob, re, shutil, fileinput, os, sys

parser = argparse.ArgumentParser(
	description='Make ssh reverse tunnel from OSX to a Linux machine.')
parser.add_argument('--serverusername', required=True, help='root, or username on server')
parser.add_argument('--serveraddress', required=True, help='mywebsitename.com, or an IP address')
parser.add_argument('--serverhostname', required=True, help='mywebsitename')
parser.add_argument('--serverport', default=12345, help='Unique port on server assigned to this client.')
parser.add_argument('--allowcommands', action='store_true', help='Allow client to ssh into server using this identity.')
parser.add_argument('--clientusername', default=os.getlogin())
parser.add_argument('--dryrun', action='store_true', help='Just show commands, don\'t execute them.')
parser.add_argument('--delete', action='store_true', help='Remove a reverse tunnel.') # todo
args = parser.parse_args()

def sh(cmd):
	print(cmd)
	if not args.dryrun:
		os.system(cmd)

# prepare name of plist file
sourcePlist = 'reverse.clientusername.serverhostname.plist' 
dupPlist = sourcePlist
dupPlist = re.sub('serverhostname', args.serverhostname, dupPlist)
dupPlist = re.sub('clientusername', args.clientusername, dupPlist)
targetPlist = os.path.join('/Library/LaunchDaemons', dupPlist)

# prepare name of identity file
identityFile = '/Users/{0}/.ssh/reverse-{0}-{1}'.format(args.clientusername, args.serverhostname)

if args.delete:
	sh('sudo launchctl unload {}'.format(targetPlist))
	sh('sudo rm {}'.format(targetPlist))
	sh('ssh-add -d {}'.format(identityFile))
	sh('rm {}*'.format(identityFile))
	# sh('sudo systemsetup -setremotelogin off') # this will disable other tunnels
	# also: Remove the client's public key from the server's authorized_keys
	# also: Remove the server's public key from the client's known_hosts
	sys.exit(0)

# make sure remote login is on (in the sharing settings)
sh('sudo systemsetup -setremotelogin on')

# create identity for the reverse tunnel
sh('ssh-keygen -f {} -P ""'.format(identityFile))

# add the identity on client
sh('ssh-add {}'.format(identityFile))

# add the identity on the server
keyEchoCommand = 'cat {}.pub'.format(identityFile)
if not args.allowcommands:
	keyEchoCommand = 'echo "command=\\"\\",no-pty `{}`"'.format(keyEchoCommand)
keySshCommand = '{0} | ssh {1}@{2} "umask 077; test -d .ssh || mkdir .ssh ; cat >> .ssh/authorized_keys"'.format(keyEchoCommand, args.serverusername, args.serveraddress)
sh(keySshCommand) # this will ask for server password unless already configured for ssh

# copy and create plist
print('Preparing {}'.format(dupPlist))
shutil.copy(sourcePlist, dupPlist)
def replaceInFile(filename, pattern, replacement):
	for line in fileinput.FileInput(filename, inplace=1):
		print re.sub(pattern, replacement, line),
replaceInFile(dupPlist, 'serverhostname', args.serverhostname)
replaceInFile(dupPlist, 'serveraddress', args.serveraddress)
replaceInFile(dupPlist, 'serverusername', args.serverusername)
replaceInFile(dupPlist, 'serverport', str(args.serverport))
replaceInFile(dupPlist, 'clientusername', args.clientusername)

# move plist to /Library/LaunchDaemons
sh('sudo mv {0} {1}'.format(dupPlist, targetPlist))

# make sure plist has the right permissions
sh('sudo chown root:wheel {}'.format(targetPlist))

# launch daemon on client
sh('sudo launchctl load {}'.format(targetPlist))

print('To make the server reconnect faster, ssh into the server and run:')
print('\techo "ClientAliveInterval 60" | sudo tee -a /etc/ssh/sshd_config ; sudo restart ssh')
print('Done! You can now reverse ssh here from the server:')
print('\tssh {0}@localhost -p {1}'.format(args.clientusername, args.serverport))