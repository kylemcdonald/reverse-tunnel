# reverse-tunnel

Make an ssh reverse tunnel from a Mac or Linux client to a Linux server.

Based on [this blog post](http://blog.kylemanna.com/osx/2013/06/20/ssh-reverse-tunnel-on-mac-os-x/) for Mac support and [this post](https://blog.kylemanna.com/linux/ssh-reverse-tunnel-on-linux-with-systemd/) for systemd/Linux support.

```
> python make-reverse-tunnel.py --help
usage: make-reverse-tunnel.py [-h]
  --serverusername SERVERUSERNAME
  --serveraddress SERVERADDRESS
  --serverhostname SERVERHOSTNAME
  [--serverport SERVERPORT]
  [--clientusername CLIENTUSERNAME]
  [--allowcommands]
  [--dryrun]
  [--delete]

Make ssh reverse tunnel from a Mac or Linux client to a Linux server.

optional arguments:
  -h, --help            show this help message and exit
  --serverusername SERVERUSERNAME
                        root, or username on server (default: None)
  --serveraddress SERVERADDRESS
                        mywebsitename.com, or an IP address (default: None)
  --serverhostname SERVERHOSTNAME
                        mywebsitename (default: None)
  --serverport SERVERPORT
                        Unique port on server assigned to this client.
                        (default: 12345)
  --allowcommands       Allow client to ssh into server using this identity.
                        (default: False)
  --clientusername CLIENTUSERNAME
                        Username on this client/local machine. (default: `whoami`)
  --dryrun              Just show commands, don't execute them. (default:
                        False)
  --delete              Remove a reverse tunnel. (default: False)
```