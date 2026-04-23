# Redis 5.0.5: WARNING: The TCP backlog setting of 511 cannot be enforced because /proc/sys/net/core/somaxconn is set to the lower value of 128



## GitHub Provenance



- Repository: redis/redis

- Issue: #6123

- State: closed

- Labels: none

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/6123



## Problem



I have `windows 10 home`, where is installed `Ubuntu`

    lsb_release -a
    No LSB modules are available.
    Distributor ID: Ubuntu
    Description:    Ubuntu 18.04.2 LTS
    Release:        18.04
    Codename:       bionic

I have installed `Redis 5.0.5` (it mostly with `make` and `make install`)

When I startup the server with `redis-server` it shows some warnings.

I have removed one about `overcommit_memory`

But about:

    WARNING: The TCP backlog setting of 511 cannot be enforced because /proc/sys/net/core/somaxconn is set to the lower value of 128.

I have read these two links:

* [WARNING: /proc/sys/net/core/somaxconn is set to the lower value of 128. #35][1]
* [Performance tips for Redis Cache Server][2]

Thus both indicate do the following: 

* Go to the `/etc` directory 
* Create the `rc.local` file, `sudo vim rc.local` 
* Add the `sysctl -w net.core.somaxconn=65535` content and save

I can confirm through

    cat rc.local
    sysctl -w net.core.somaxconn=65535

Well in a _secondary_ terminal I execute `redis-cli shutdown` and in the _primary_ terminal execute again `redis-server`

**Problem** the same warning appears, What is missing?

**Note** I have the same situation even after to execute `sudo chmod +x rc.local` 

  [1]: https://github.com/docker-library/redis/issues/35
  [2]: https://www.techandme.se/performance-tips-for-redis-cache-server/



## Curated Answers



### High Signal Answer 1

Hi,

have you try to `echo 1024 > /proc/sys/net/core/somaxconn` with `root` user and restart Redis ?

If works, you can add `net.core.somaxconn=65535` in the `/etc/sysctl.conf` file and restart ?

Regards,

- Author: emeric-martineau
- Quality score: 37
- URL: https://github.com/redis/redis/issues/6123#issuecomment-512808174

### High Signal Answer 2

I only can do edit somaxconn value with this command:
`sysctl -w net.core.somaxconn=512`

- Author: rafaeldev
- Quality score: 19
- URL: https://github.com/redis/redis/issues/6123#issuecomment-547449221

### High Signal Answer 3

@manueljordan Please note that WSL 2.0 is actually a VM (like VirtualBox) and may solve these issues as well.

- Author: yossigo
- Quality score: 4
- URL: https://github.com/redis/redis/issues/6123#issuecomment-779310210
