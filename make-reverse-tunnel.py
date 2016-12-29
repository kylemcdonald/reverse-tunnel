#!/usr/bin/env python

import argparse
import platform, glob, re, shutil, fileinput, os, sys

parser = argparse.ArgumentParser(
	description='Make ssh reverse tunnel from a Mac or Linux client to a Linux server.',
	formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--serverusername', required=True, help='root, or username on server')
parser.add_argument('--serveraddress', required=True, help='mywebsitename.com, or an IP address')
parser.add_argument('--serverhostname', required=True, help='mywebsitename')
parser.add_argument('--serverport', default=12345, help='Unique port on server assigned to this client.')
parser.add_argument('--allowcommands', action='store_true', help='Allow client to ssh into server using this identity.')
parser.add_argument('--clientusername', default=os.getenv('USER'), help='Username on this client/local machine.')
parser.add_argument('--dryrun', action='store_true', help='Just show commands, don\'t execute them.')
parser.add_argument('--delete', action='store_true', help='Remove a reverse tunnel.') # todo
args = parser.parse_args()

def sh(cmd):
	print(cmd)
	if not args.dryrun:
		os.system(cmd)

def replaceInFile(filename, pattern, replacement):
	for line in fileinput.FileInput(filename, inplace=1):
		print re.sub(pattern, replacement, line),

systemName = platform.system()
ubuntu = False
if systemName == 'Linux':
	print 'Using systemd on Linux'
	ubuntu = True
elif systemName == 'Darwin':
	print 'Using launchd on Mac'
else:
	print 'Platform {} not supported, exiting.'.format(systemName)
	sys.exit()

if not args.delete and ubuntu:
	sh('sudo apt-get install openssh-server')
	sh('eval "$(ssh-agent)"')

# prepare name of keepalive script
if ubuntu:
	sourceScript = 'reverse.clientusername.serverhostname.service'
	dupScript = sourceScript
	dupScript = re.sub('serverhostname', args.serverhostname, dupScript)
	dupScript = re.sub('clientusername', args.clientusername, dupScript)
	targetScript = os.path.join('/etc/systemd/system', dupScript)
else:
	sourceScript = 'reverse.clientusername.serverhostname.plist' 
	dupScript = sourceScript
	dupScript = re.sub('serverhostname', args.serverhostname, dupScript)
	dupScript = re.sub('clientusername', args.clientusername, dupScript)
	targetScript = os.path.join('/Library/LaunchDaemons', dupScript)

# prepare name of identity file
homePrefix = '/home' if ubuntu else '/Users'
serviceName = 'reverse.{}.{}'.format(args.clientusername, args.serverhostname)
identityFile = '{}/{}/.ssh/{}'.format(homePrefix, args.clientusername, serviceName)

if args.delete:
	if ubuntu:
		sh('sudo systemctl stop {}'.format(serviceName))
		sh('sudo systemctl disable {}'.format(serviceName))
	else:
		sh('sudo stop {}'.format(serviceName))
	sh('sudo rm {}'.format(targetScript))
	sh('ssh-add -d {}'.format(identityFile))
	sh('rm {}*'.format(identityFile))
	# sh('sudo systemsetup -setremotelogin off') # this will disable other tunnels
	# also: Remove the client's public key from the server's authorized_keys
	# also: Remove the server's public key from the client's known_hosts
	print('- ' * 40)
	print('Done!')
	sys.exit(0)

if not ubuntu:
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
keySshCommand = '{0} | ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no {1}@{2} "umask 077; (test -d .ssh || (mkdir .ssh ; ssh-keygen -f .ssh/id_rsa -P \\"\\")) ; cat >> .ssh/authorized_keys; cat .ssh/*.pub" >> ~/.ssh/authorized_keys'.format(keyEchoCommand, args.serverusername, args.serveraddress)
sh(keySshCommand) # this will ask for server password unless already configured for ssh

# copy and create systemd service / launchd plist
print('Preparing {}'.format(dupScript))
shutil.copy(sourceScript, dupScript)
replaceInFile(dupScript, 'serverhostname', args.serverhostname)
replaceInFile(dupScript, 'serveraddress', args.serveraddress)
replaceInFile(dupScript, 'serverusername', args.serverusername)
replaceInFile(dupScript, 'serverport', str(args.serverport))
replaceInFile(dupScript, 'clientusername', args.clientusername)

# move to /etc/systemd/system or /Library/LaunchDaemons
sh('sudo mv {0} {1}'.format(dupScript, targetScript))

# make sure script has the right permissions and launch daemon on client
if ubuntu:
	sh('sudo chown root:root {}'.format(targetScript))
	sh('sudo chmod 644 {}'.format(targetScript))
	sh('sudo systemctl restart {}'.format(serviceName))
	# sh('sudo systemctl status -l {}'.format(serviceName))
	sh('sudo systemctl enable {}'.format(serviceName))
else:
	sh('sudo chown root:wheel {}'.format(targetScript))
	sh('sudo launchctl load {}'.format(targetScript))

print('- ' * 40)
print('Done! If you ssh into the server, now you can reverse tunnel to this client:')
print('\tssh {0}@{1}'.format(args.serverusername, args.serveraddress))
print('\tssh {0}@localhost -p {1}'.format(args.clientusername, args.serverport))
if not args.allowcommands:
	print('If you want to ssh into the server from the client, you will need to type:')
	print('\tssh -o PubKeyAuthentication=no {0}@{1}'.format(args.serverusername, args.serveraddress))
print('To make the server reconnect faster, ssh into the server and run:')
print('\techo "ClientAliveInterval 60" | sudo tee -a /etc/ssh/sshd_config ; sudo restart ssh')
