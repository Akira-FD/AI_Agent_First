# Performance degrade 7.0.3 vs 6.2.7



## GitHub Provenance



- Repository: redis/redis

- Issue: #10981

- State: closed

- Labels: state:needs-investigation

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/10981



## Problem



Hi,
I tested on different systems, but every time the results are the same, 7.x works worse than 6.x.
(config attached)

```
redis-benchmark -q -n 1000000 --threads 64
```
<img width="456" alt="image" src="https://user-images.githubusercontent.com/95714796/179132949-33f35b0f-c881-4015-81d5-3978f41ec136.png">


[redis_conf.txt](https://github.com/redis/redis/files/9117133/redis_conf.txt)



## Curated Answers



### High Signal Answer 1

~#8015 results in 15% performance degration.~
~Since `server.repl_backlog` will be created even if there is no slave, all commands propagate will be wasted.~
~ping @soloestoy~
Already fixed in #9166

- Author: sundb
- Quality score: 4
- URL: https://github.com/redis/redis/issues/10981#issuecomment-1319783746
