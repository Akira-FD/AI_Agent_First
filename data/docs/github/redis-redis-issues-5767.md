# [ZREVRANGEBYSCORE] When the offset is too large, the query is very slow.



## GitHub Provenance



- Repository: redis/redis

- Issue: #5767

- State: closed

- Labels: none

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/5767



## Problem



ZREVRANGEBYSCORE key max min [WITHSCORES] [LIMIT offset count]
When the offset is too large, the query is very slow.  Especially when the offset is greater than the length of zset. For this invalid query, I think it should determine whether the offset is greater than the length of zset at first, and If it exceed the length of zset, then return directly.



## Curated Answers



### High Signal Answer 1

Hello @fuxiaotong 

This is the expected behavior, see the docs for [`ZRANGEBYSCORE`](https://redis.io/commands/ZRANGEBYSCORE):

> Keep in mind that if offset is large, the sorted set needs to be traversed for offset elements before getting to the elements to return, which can add up to O(N) time complexity.

The edge case, where the offset exceeds the length of the zset, could perhaps be optimized to break early, although it will have little impact overall.

- Author: itamarhaber
- Quality score: 4
- URL: https://github.com/redis/redis/issues/5767#issuecomment-453505803
