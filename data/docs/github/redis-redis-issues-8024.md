# [BUG] TimeoutStartSec and TimeoutStopSec values are valid, but redis still warns



## GitHub Provenance



- Repository: redis/redis

- Issue: #8024

- State: closed

- Labels: none

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/8024



## Problem



**OS**: CentOS 8.2
**Redis**: v6.0.9
Redis is installed via remi repo.

This is my service file for systemd:

```bash
[root@test ~]# cat /etc/systemd/system/redis-server.service
[Unit]
Description=Advanced key-value store
Wants=network-online.target
After=network-online.target
Documentation=http://redis.io/documentation, man:redis-server(1)

[Service]
Type=notify
ExecStart=/usr/bin/redis-server /etc/redis.conf --supervised systemd --daemonize no
ExecStop=/bin/kill -s TERM $MAINPID
PIDFile=/run/redis/redis-server.pid
Restart=always
User=redis
Group=redis
RuntimeDirectory=redis
RuntimeDirectoryMode=2755
TimeoutStopSec=infinity
TimeoutStartSec=infinity
UMask=0077
PrivateTmp=yes
NoNewPrivileges=yes
LimitNOFILE=65535
PrivateDevices=yes
ProtectHome=yes
ReadOnlyDirectories=/
WorkingDirectory=/var/lib/redis
ReadWriteDirectories=-/var/lib/redis
ReadWriteDirectories=-/var/log/redis
ReadWriteDirectories=-/var/run/redis

NoNewPrivileges=true
CapabilityBoundingSet=CAP_SETGID CAP_SETUID CAP_SYS_RESOURCE
MemoryDenyWriteExecute=true
ProtectKernelModules=true
ProtectKernelTunables=true
ProtectControlGroups=true
RestrictRealtime=true
RestrictNamespaces=true
RestrictAddressFamilies=AF_INET AF_INET6 AF_UNIX

ProtectSystem=true
ReadWriteDirectories=-/etc/redis

[Install]
WantedBy=multi-user.target
Alias=redis.service
```

Redis starts fine and accepts connections. However, the logs describe, what looks to me, a heavy warning:

```bash
5425:C 05 Nov 2020 20:17:29.707 # WARNING supervised by systemd - you MUST set appropriate values for TimeoutStartSec and TimeoutStopSec in your service unit.
5425:C 05 Nov 2020 20:17:29.707 # oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
5425:C 05 Nov 2020 20:17:29.707 # Redis version=6.0.9, bits=64, commit=00000000, modified=0, pid=5425, just started
5425:C 05 Nov 2020 20:17:29.707 # Configuration loaded
5425:M 05 Nov 2020 20:17:29.708 * Running mode=standalone, port=6379.
5425:M 05 Nov 2020 20:17:29.708 # Server initialized
5425:M 05 Nov 2020 20:17:29.708 * Loading RDB produced by version 6.0.9
5425:M 05 Nov 2020 20:17:29.708 * RDB age 9 seconds
5425:M 05 Nov 2020 20:17:29.708 * RDB memory usage when created 0.32 Mb
5425:M 05 Nov 2020 20:17:29.708 * DB loaded from disk: 0.000 seconds
5425:M 05 Nov 2020 20:17:29.708 * Ready to accept connections
```

Between 'systemctl daemon-reload' and restarting the redis server, I've tried changing the values of TimeoutStopSec and TimeoutStartSec to either 0, 0s, 1, 1s, 90, 90s and I've removed both keys to see whether Redis stopped complaining about the issue, but it doesn't. I've also fiddled around with other values to see whether it would made a change, but it doesn't...

I assume this is a bug, since I've tried various settings and copied the settings [as per the documentation](https://github.com/redis/redis/blob/8e937ce4cc1462d996bae6a45e8c0a66f71e7ee6/utils/systemd-redis_server.service).

For convience, here is my /etc/redis.conf

```bash
pidfile /var/run/redis/redis.pid
port 6379
bind 127.0.0.1
timeout 300
loglevel notice
logfile /var/log/redis/redis-server.log
databases 16
save 900 1
save 300 10
save 60 10000
rdbcompression yes
dbfilename dump.rdb
dir /var/lib/redis
maxclients 128
tcp-backlog 511
appendonly no
appendfsync everysec
no-appendfsync-on-rewrite no
```



## Curated Answers



### High Signal Answer 1

This still occur in redis v6.0.16. 
Thumbs up if you come from search engine and frustating about this

- Author: erikdemarco
- Quality score: 28
- URL: https://github.com/redis/redis/issues/8024#issuecomment-1609214506

### High Signal Answer 2

@yossigo Well, this is absurd right, as a user seeing this message from Redis (which is at version 6!).

I mean, look at this:
**WARNING supervised by systemd - you MUST set appropriate values for TimeoutStartSec and TimeoutStopSec in your service unit.**

I assume either the text has to be changed, the warning has to be removed, or the redis has to check for the correct values and report on that. 

The warning clearly states "you MUST", which leads me to believe my configuration is faulty and Redis will perform poorly.

- Author: csuka
- Quality score: 5
- URL: https://github.com/redis/redis/issues/8024#issuecomment-722654159
