# osx-reverse-tunnel

When you only need a reverse tunnel to an OSX machine. Based on [this blog post](http://blog.kylemanna.com/osx/2013/06/20/ssh-reverse-tunnel-on-mac-os-x/).

```
usage: make-reverse-tunnel.py [-h] --serverusername SERVERUSERNAME
                              --serveraddress SERVERADDRESS --serverhostname
                              SERVERHOSTNAME [--serverport SERVERPORT]
                              [--allowcommands]
                              [--clientusername CLIENTUSERNAME] [--dryrun]
                              [--delete]

Make ssh reverse tunnel from OSX to a Linux machine.

optional arguments:
  -h, --help            show this help message and exit
  --serverusername SERVERUSERNAME
                        root, or username on server
  --serveraddress SERVERADDRESS
                        mywebsitename.com, or an IP address
  --serverhostname SERVERHOSTNAME
                        mywebsitename
  --serverport SERVERPORT
                        Unique port on server assigned to this client.
  --allowcommands       Allow client to ssh into server using this identity.
  --clientusername CLIENTUSERNAME
  --dryrun              Just show commands, don't execute them.
  --delete              Remove a reverse tunnel.
```