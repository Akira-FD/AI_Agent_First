# redis-server with ubuntu server 20.04



## GitHub Provenance



- Repository: redis/redis

- Issue: #7361

- State: closed

- Labels: state:to-be-closed

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/7361



## Problem



Hey, tryng to use redis-server with new ubuntu server 20.04, but i get always same error:
redis-server.service: Can't open PID file /run/redis/redis-server.pid (yet?) after start: Operation not permitted

Any ideas ?
Thnaks.



## Curated Answers



### High Signal Answer 1

```
nano /etc/systemd/system/redis.service

[Service]
ExecStop=/bin/kill -s TERM $MAINPID
ExecStartPost=/bin/sh -c "echo $MAINPID > /var/run/redis/redis.pid"  

sudo systemctl daemon-reload
sudo systemctl enable redis-server
sudo systemctl restart redis.service
```

- Author: Sulshag
- Quality score: 82
- URL: https://github.com/redis/redis/issues/7361#issuecomment-917631161

### High Signal Answer 2

I suggest to check for the real reason in `/var/log/redis/redis-server.log`. 
For example, I was getting the same error as reported above but the real reason was that I had disabled IPv6 and hence had to remove `::1` from `bind 127.0.0.1 ::1` in `/etc/redis/redis.conf`. Simply removing this, fixed it all.

- Author: intelliant01
- Quality score: 10
- URL: https://github.com/redis/redis/issues/7361#issuecomment-1080399300

### High Signal Answer 3

So,

For me the only working solution was commenting out this line of the `/etc/systemd/system/redis.service` file:

`PIDFile=/run/redis/redis-server.pid`

So now it goes:

```
[Service]
Type=forking
ExecStart=/usr/bin/redis-server /etc/redis/redis.conf
#PIDFile=/run/redis/redis-server.pid
TimeoutStopSec=0
Restart=always
User=redis
Group=redis
RuntimeDirectory=redis
RuntimeDirectoryMode=2755
```

Since then the issue is gone for good.
Ubuntu 20.04 LTS on WSL2.

- Author: Ziggizag
- Quality score: 10
- URL: https://github.com/redis/redis/issues/7361#issuecomment-1136528254
