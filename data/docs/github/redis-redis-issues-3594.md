# Redis is trying to write to /var/spool/cron



## GitHub Provenance



- Repository: redis/redis

- Issue: #3594

- State: closed

- Labels: none

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/3594



## Problem



We are experiencing really weired behavior of Redis server, which is randomly appearing (at least it looks like that). When problem happens, Redis is locked, not responding and even won't stop (must be killed with signal 9). This is appearing in logs until server is killed and started again:

20704:M 06 Nov 14:41:17.090 * 10 changes in 300 seconds. Saving...
20704:M 06 Nov 14:41:17.091 * Background saving started by pid 5333
5333:C 06 Nov 14:41:17.091 # Failed opening the RDB file root (in server root dir /var/spool/cron) for saving: Read-only file system
20704:M 06 Nov 14:41:17.191 # Background saving error

Note that error 'Read-only file system' means that systemd is not allowing Redis to write to that directory (it is running in different mount namespace, the filesystem is really mounted in read-write mode).

I was also strace-ing it and Redis is really trying to create temporary files in /var/spool/cron and is ignoring settings in configuration file:
dbfilename dump.rdb
dir /var/lib/redis

System is Debian Jessie, package is from dotdeb.org, 64bit OpenStack VPS.

Any hints?



## Curated Answers



### High Signal Answer 1

Is your Redis server accessible to the public? If so, this could be an
attempted attack.

On Nov 6, 2016 5:11 PM, "azurit" notifications@github.com wrote:

> We are experiencing really weired behavior of Redis server, which is
> randomly appearing (at least it looks like that). When problem happens,
> Redis is locked, not responding and even won't stop (must be killed with
> signal 9). This is appearing in logs until server is killed and started
> again:
> 
> 20704:M 06 Nov 14:41:17.090 \* 10 changes in 300 seconds. Saving...
> 20704:M 06 Nov 14:41:17.091 \* Background saving started by pid 5333
> 5333:C 06 Nov 14:41:17.091 # Failed opening the RDB file root (in server
> root dir /var/spool/cron) for saving: Read-only file system
> 20704:M 06 Nov 14:41:17.191 # Background saving error
> 
> Note that error 'Read-only file system' means that systemd is not allowing
> Redis to write to that directory (it is running in different mount
> namespace, the filesystem is really mounted in read-write mode).
> 
> I was also strace-ing it and Redis is really trying to create temporary
> files in /var/spool/cron and is ignoring settings in configuration file:
> dbfilename dump.rdb
> dir /var/lib/redis
> 
> System is Debian Jessie, package is from dotdeb.org, 64bit OpenStack VPS.
> 
> Any hints?
> 
> —
> You are receiving this because you are subscribed to this thread.
> Reply to this email directly, view it on GitHub
> https://github.com/antirez/redis/issues/3594, or mute the thread
> https://github.com/notifications/unsubscribe-auth/AFx1_KhYzEZupnh0VfATUQqnHbBfH3YEks5q7e4PgaJpZM4KqlBk
> .

- Author: itamarhaber
- Quality score: 11
- URL: https://github.com/redis/redis/issues/3594#issuecomment-258688559

### High Signal Answer 2

@cuongnm265 yes i was able to resolve it, it appeard that some kind of bots were trying to somehow hack the server using Redis by online changing it's configuration (with CONFIG command). I did:
bind 127.0.0.1
protected-mode yes
rename-command CONFIG ""

As Redis doesn't have any priviledge separation, anyone can run command CONFIG and, at least, doing a DoS attack to Redis. So i decided to completely disable CONFIG command, even for local users.

- Author: azurit
- Quality score: 5
- URL: https://github.com/redis/redis/issues/3594#issuecomment-394598143
