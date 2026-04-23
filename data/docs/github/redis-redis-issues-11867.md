# [QUESTION]Redis allkeys-lfu eviction policy. What happens if multiple keys have least frequency?



## GitHub Provenance



- Repository: redis/redis

- Issue: #11867

- State: closed

- Labels: none

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/11867



## Problem



Im new to Redis, i'm trying to set eviction policy 
In Redis we can specify eviction policy in the conf file in case the cache size crosses ```maxmemory``` specified

```conf
maxmemory-policy allkeys-lfu
```

What will happen if multiple keys have same least frequency . Will it delete all the keys or just enough to free up memory? If it deletes all keys what is the best way I can ensure that does'nt happen?

I configured my conf like this

```
maxmemory 230m
maxmemory-policy allkeys-lfu
```

I tried manually and it seems to clear up all the keys with the same frequency. (Not sure if misconfigured something). If this is the expected behaviour please explain why?



## Curated Answers



### High Signal Answer 1

Hello @josephjacobmorris 

Redis eviction kicks in when there's memory pressure. The server will spend some of its cycles trying to evict data according to the selected eviction policy. The server uses random sampling of the keyspace as a compromise to find suitable eviction candidates. This continues until the pressure is relieved.

What you're describing - all keys being evicted - differs from what I'd expect during regular operation (i.e., excluding edge cases and synthetic examples).

See also: [Key Eviction: How the eviction process works](https://redis.io/docs/reference/eviction/#how-the-eviction-process-works)

- Author: itamarhaber
- Quality score: 4
- URL: https://github.com/redis/redis/issues/11867#issuecomment-1450276434
