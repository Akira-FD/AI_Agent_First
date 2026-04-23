# peak memory > max memory?



## GitHub Provenance



- Repository: redis/redis

- Issue: #6646

- State: closed

- Labels: none

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/6646



## Problem



How is it possible when I set `maxmemory 64mb` in `redis.conf` that the peak memory usage is almost twice its size -> `used_memory_peak_human:106.23M`?

I've seen this on 5.0.7 and git master.

```
$ redis-cli -s /tmp/redis.sock info memory
# Memory
used_memory:3194560
used_memory_human:3.05M
used_memory_rss:135745536
used_memory_rss_human:129.46M
used_memory_peak:111389024
used_memory_peak_human:106.23M
used_memory_peak_perc:2.87%
used_memory_overhead:2198952
used_memory_startup:1016656
used_memory_dataset:995608
used_memory_dataset_perc:45.71%
allocator_allocated:3110992
allocator_active:135707648
allocator_resident:135707648
total_system_memory:34359738368
total_system_memory_human:32.00G
used_memory_lua:37888
used_memory_lua_human:37.00K
used_memory_scripts:0
used_memory_scripts_human:0B
number_of_cached_scripts:0
maxmemory:67108864
maxmemory_human:64.00M
maxmemory_policy:noeviction
allocator_frag_ratio:43.62
allocator_frag_bytes:132596656
allocator_rss_ratio:1.00
allocator_rss_bytes:0
rss_overhead_ratio:1.00
rss_overhead_bytes:37888
mem_fragmentation_ratio:43.63
mem_fragmentation_bytes:132634544
mem_not_counted_for_evict:0
mem_replication_backlog:0
mem_clients_slaves:0
mem_clients_normal:66664
mem_aof_buffer:0
mem_allocator:libc
active_defrag_running:0
lazyfree_pending_objects:0
```



## Curated Answers



### High Signal Answer 1

If `maxmemory` is not related to RSS, how are you supposed to know which value to set it? Should your database be 50% of the available memory? 30%? There is no math you can do to reliably say how much memory redis will actually need while running, and since the whole point (in my case using it as cache) is to be fast, falling back to swap is not an option, I have to keep all my database in memory.

- Author: rafaelsierra
- Quality score: 8
- URL: https://github.com/redis/redis/issues/6646#issuecomment-765335122

### High Signal Answer 2

> If those tests are failing for you then that’s a whole different problem! I’ll assume they’re passing?

They pass. But that's not the point. I rather meant that maybe the test itself is broken.

> The use case you appear to be asking for is a hard RSS limit, which isn’t currently implemented

I think you still didn't get my point. Of course I'm asking for a limit on the max memory the app is using. That's what max memory means. At least in every other app in the world.
I seriously don't care about the internals. If I set maxmemory, I want that the app doesn't use more memory than that. Otherwise this parameter is useless!!!

**Why would anyone set this, if noone knows how much memory will actually be used?** As I said I have seen 3 times the value of max memory used in peak memory.

- Author: tessus
- Quality score: 7
- URL: https://github.com/redis/redis/issues/6646#issuecomment-573274796

### High Signal Answer 3

This seems odd though.

In that case I don't need a `maxmemory` parameter, if it's not honored. Either there's a limit for how much memory can be used by Redis, or there isn't. There's no inbetween. It's a mutually exclusive premise.

The following example is extreme, but possible: Swap is turned off. Machine has 8 GB RAM. maxmemory is set to 7GB. -> crash - because Redis ignores the maxmemory limit.

I set it to 64MB, but the peak was about twice that. So it's not exceeding it. It's ignoring it. Exceeding would probably be like 5% over, but not 100% over. 

In either case, I seriously do not understand how this is possible. If there's a re-alloc happening or a malloc which would exceed maxmem, don't allocate. So apparently this check is not working or ignored, or not present.

- Author: tessus
- Quality score: 6
- URL: https://github.com/redis/redis/issues/6646#issuecomment-562810175
