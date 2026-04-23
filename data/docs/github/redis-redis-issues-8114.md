# [BUG]Job for redis-server.service failed because the control process exited with error code.



## GitHub Provenance



- Repository: redis/redis

- Issue: #8114

- State: closed

- Labels: none

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/8114



## Problem



**Describe the bug**
Server Startup for redis is failing because of an unidentified bug. 
A short description of the bug.
Exit Error Code  
See "systemctl status redis-server.service" and "journalctl -xe" for details.

**To reproduce**
Install Ubuntu 18.04 OS.
sudo apt update
Sudo apt get redis-server.
sudo systemctl restart redis.service

Steps to reproduce the behavior and/or a minimal code sample.

**Expected behavior**
Redis Server is (re)started
A description of what you expected to happen.
I expect to have seen the redis server to start.
**Additional information**

Any additional information that is relevant to the problem.
No redis logs avalable.



## Curated Answers



### High Signal Answer 1

I am having the same issue.
I installed it by following this article by - [Digitalocean article](https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-redis-on-ubuntu-20-04)

I am receiving the same error. 
```bash
Job for redis-server.service failed because the control process exited with error code.
See "systemctl status redis-server.service" and "journalctl -xe" for details.
```
When I edited the conf for the first time and restarted it ran fine. 
But when turned my laptop again the next day, it is not starting. 
I tried using this command to start it - `sudo service redis-server start` also - `sudo service redis-server start`

On running `sudo service redis-server status` I get -
```bash
● redis-server.service - Advanced key-value store
     Loaded: loaded (/lib/systemd/system/redis-server.service; enabled; vendor preset: enabled)
     Active: failed (Result: exit-code) since Sat 2021-10-30 18:18:51 IST; 4min 24s ago
       Docs: http://redis.io/documentation,
             man:redis-server(1)
    Process: 19855 ExecStart=/usr/bin/redis-server /etc/redis/redis.conf --supervised systemd --daem>
   Main PID: 19855 (code=exited, status=1/FAILURE)

Oct 30 18:18:51 dell-pop-os systemd[1]: redis-server.service: Scheduled restart job, restart counter>
Oct 30 18:18:51 dell-pop-os systemd[1]: Stopped Advanced key-value store.
Oct 30 18:18:51 dell-pop-os systemd[1]: redis-server.service: Start request repeated too quickly.
Oct 30 18:18:51 dell-pop-os systemd[1]: redis-server.service: Failed with result 'exit-code'.
Oct 30 18:18:51 dell-pop-os systemd[1]: Failed to start Advanced key-value store.
```
Version of redis - `Redis server v=6.0.11 sha=00000000:0 malloc=jemalloc-5.2.1 bits=64 build=83fe9b039c768864`

My system information -
```bash
OS: Pop!_OS 21.04 x86_64 
Host: Vostro 3584 
Kernel: 5.13.0-7614-generic 
Uptime: 4 hours, 52 mins 
Packages: 1908 (dpkg), 8 (snap) 
Shell: zsh 5.8 
esolution: 1366x768, 2560x1440 
DE: Unity 
WM: Mutter 
WM Theme: Adwaita 
Theme: Numix [GTK2/3] 
Icons: Numix-Square-Light [GTK2/3] 
Terminal: vscode 
CPU: Intel i3-7020U (4) @ 2.300GHz 
GPU: Intel Device 5921 
Memory: 4537MiB / 7852MiB 
```

It also happens on my other Laptop with the same config but Pop!_os - 20.04

For anyone experiencing this error-
Set supervised as no in the config file
```config
supervised no
```
Then start redis like this -
```bash
sudo redis-server /etc/redis/redis.conf
```
Edit the path to conf as required.

- Author: therohitdas
- Quality score: 7
- URL: https://github.com/redis/redis/issues/8114#issuecomment-955206864

### High Signal Answer 2

@yossigo I found the error, it was -
```bash
Nov 18 18:29:44 dell-pop-os redis-server[187213]: *** FATAL CONFIG FILE ERROR (Redis 6.0.11) ***
Nov 18 18:29:44 dell-pop-os redis-server[187213]: Reading the configuration file, at line 260
Nov 18 18:29:44 dell-pop-os redis-server[187213]: >>> 'logfile /var/log/redis/redis-server.log'
Nov 18 18:29:44 dell-pop-os redis-server[187213]: Can't open the log file: Permission denied
Nov 18 18:29:44 dell-pop-os systemd[1]: redis-server.service: Main process exited, code=exited, status=1/FAILURE
```
Also, I removed the dump and tried starting the Redis again.

I did not know that you can scroll up after opening `journalctl -xe`.
Redis used to fail once because of the permission issue and then try to restart, this lead to another issue - `redis-server.service: Start request repeated too quickly` 
And it was at the end of the journal. So, I was focusing on it!

Solved the permission issue using - [Redis startup error: Can't open the log file: Permission denied](https://www.fatalerrors.org/a/can-t-open-the-log-file-permission-denied.html)

Now everything works fine. 

![Thank you](https://media.giphy.com/media/3o6Zt6KHxJTbXCnSvu/giphy.gif)
Thank you @yossigo

- Author: therohitdas
- Quality score: 4
- URL: https://github.com/redis/redis/issues/8114#issuecomment-972854759
