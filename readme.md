# osx-reverse-tunnel

When you only need a reverse tunnel to an OSX machine. Based on [this blog post](http://blog.kylemanna.com/osx/2013/06/20/ssh-reverse-tunnel-on-mac-os-x/).

There is a bug right now where it seems to set up everything correctly, but then the last step `sudo launchctl load` cannot execute the `ssh` command. You can `launchctl load` without sudo just fine, and you can run the command manually as `sudo`, but `launchd` returns error 255.