# POP from sorted sets



## GitHub Provenance



- Repository: redis/redis

- Issue: #1861

- State: closed

- Labels: none

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/1861



## Problem



It would be nice if one could rpop and lpop from a sorted set.

```
ZADD sorted 5 foo
ZADD sorted 3 bar
ZADD sorted 8 baz
ZLPOP sorted
```

Would return bar, probably also the score or one would split the operations to return either the score or the member.



## Curated Answers



### High Signal Answer 1

blocking pop from sorted set makes it easy to implement priority queues with low latency.

- Author: halaei
- Quality score: 19
- URL: https://github.com/redis/redis/issues/1861#issuecomment-146436935

### High Signal Answer 2

workaround for now:

```
MULTI
ZRANGE sorted 0 0 WITHSCORES
ZREMRANGEBYRANK sorted 0 0
EXEC
```

(`-1, -1` for `zrpop` equivalent)

- Author: badboy
- Quality score: 7
- URL: https://github.com/redis/redis/issues/1861#issuecomment-69466049

### High Signal Answer 3

Probably a zrpop would also make sense, maybe even zblpop and zbrpop, which would allow for example creating a queue of repeatedly run tasks, which are ordered and processed based off timestamps.

- Author: reezer
- Quality score: 4
- URL: https://github.com/redis/redis/issues/1861#issuecomment-69464767
