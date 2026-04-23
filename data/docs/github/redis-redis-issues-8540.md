# [BUG]Sentinel  stuck with +sdown upon replica pod restart  



## GitHub Provenance



- Repository: redis/redis

- Issue: #8540

- State: closed

- Labels: none

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/8540



## Problem



Hellow Team,  @yossigo , thanks for releasing the 6.2.0 with sentinel host name support and fixing all the related issues.

https://github.com/redis/redis/issues/8507
https://github.com/redis/redis/pull/8517
https://github.com/redis/redis/pull/8481
https://github.com/redis/redis/issues/8300 

We are evaluating to run sentinel based redis cluster on kubernetes, so  went ahead and verified [6.2.0](https://hub.docker.com/_/redis/) from Docker Hub , but surprisingly find out that, upon replica pod restart, `sentinel replicas mymaster` stuck with `    9) "flags"
   10) "s_down,slave"` state and never recovered.

```
127.0.0.1:26379> sentinel replicas mymaster
1)  1) "name"
    2) "redis-1.redis.FQDN"
    3) "ip"
    4) "redis-1.redis.FQDN"
    5) "port"
    6) "6379"
    7) "runid"
    8) "7b69bdd9dec849aa17bd9912b7e994cb6095b524"
    9) "flags"
   10) "s_down,slave"
   11) "link-pending-commands"
   12) "39"
   13) "link-refcount"
   14) "1"
   15) "last-ping-sent"
   16) "704052"
   17) "last-ok-ping-reply"
   18) "704597"
   19) "last-ping-reply"
   20) "704597"
   21) "s-down-time"
   22) "699026"
   23) "down-after-milliseconds"
   24) "5000"
   25) "info-refresh"
   26) "706516"
   27) "role-reported"
   28) "slave"
   29) "role-reported-time"
   30) "887409"
   31) "master-link-down-time"
   32) "0"
   33) "master-link-status"
   34) "ok"
   35) "master-host"
   36) "redis-0.redis.FQDN"
   37) "master-port"
   38) "6379"
   39) "slave-priority"
   40) "100"
   41) "slave-repl-offset"
   42) "66025"
```

last log on sentinel 

```
1:X 23 Feb 2021 21:21:47.545 # +sdown slave redis-1.redis.FQDN:6379 redis-1.redis.FQDN 6379 @ mymaster redis-0.redis.FQDN 6379
```


happy to provide more details if required, thanks!



## Curated Answers



### High Signal Answer 1

Hope this [PR](https://github.com/redis/redis/pull/10146) will fix it. 
Thanks

- Author: moticless
- Quality score: 4
- URL: https://github.com/redis/redis/issues/8540#issuecomment-1016542180
