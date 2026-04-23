# [NEW]Scan for hash fields only



## GitHub Provenance



- Repository: redis/redis

- Issue: #12749

- State: closed

- Labels: none

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/12749



## Problem



**The problem/use-case that the feature addresses**

Is it possible to scan the hash field only, value is not necessary

**Description of the feature**


Maybe `HKSCAN`, scans the hash fields only, not loading the hash value, the value may be large


**Alternatives you've considered**



**Additional information**



## Curated Answers



### High Signal Answer 1

i think adding a `[NOVALUES]` argument to HSCAN makes sense.

- Author: oranagra
- Quality score: 6
- URL: https://github.com/redis/redis/issues/12749#issuecomment-1807036810

### High Signal Answer 2

seems that the existing commands aren't sufficient for your needs, perhaps we can extend `HKEY` command with pattern matching.
like `KEY` command:
```
HKEY key [MATCH pattern]
```

ping @redis/redis-committers, please share your thoughts.

- Author: sundb
- Quality score: 4
- URL: https://github.com/redis/redis/issues/12749#issuecomment-1805376687

### High Signal Answer 3

It's not good to use HKEYS for very large hashes because it's O(N) just like KEYS.

I prefer HKSCAN. Another possibility is HSCAN with a new argument like NOVALUES.

- Author: zuiderkwast
- Quality score: 4
- URL: https://github.com/redis/redis/issues/12749#issuecomment-1805520260
