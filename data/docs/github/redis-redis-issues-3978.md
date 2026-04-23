# rename-command in redis.conf seems to break redis-cli if command starts with a number



## GitHub Provenance



- Repository: redis/redis

- Issue: #3978

- State: closed

- Labels: class:bug

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/3978



## Problem



Version: Redis 4.0-rc3 / Platform: Linux Ubuntu

In redis.conf you add in the line:

`rename-command KEYS 21591e49a59cfd7c`

Then in `redis-cli` issue the command `21591e49a59cfd7c *` the result is
```
(error) ERR unknown command '*'

[... hundreds of lines ...]

(error) ERR unknown command '*'
(error) ERR unknown command '*'
(error) ERR unknown command '*'
(error) ERR unknown command '*'
(1.12s)
```

However, if, in redis.conf you put in the line:

`rename-command KEYS r21591e49a59cfd7c` 
(note the 'r' at the start of the second argument, the only difference)

Restart redis and issue the command `r21591e49a59cfd7c *` in `redis-cli` it works as expected:

```
(empty list or set)
```



## Curated Answers



### High Signal Answer 1

Verified, and there are actually two issues here:

1. Redis allows renaming to anything, whereas the cli treats a number in the first (0) position in the argv array as the repeat modifier. That means that if you rename a command to a number, you won't be able to run it via redis-cli.

2. Some hash functions yieldings  begin with digits, and these may be used to generate "random" command names that you would use as renaming target (perhaps to increase security). Assuming that the above is an example of that, it makes sense IMO to fix the cli's behavior so it will support digit-prefixed commands (arguably, modules may also introduce commands beginning with names beginning with digits, although that may not necessarily be best practice).

There are at least two ways I can think of to fix this, and would appreciate @antirez's guidance to on hax0ring around line 1337:

1. Use something with errno checking
2. Scan argv[0] for isalpha && || isdigit

- Author: itamarhaber
- Quality score: 4
- URL: https://github.com/redis/redis/issues/3978#issuecomment-298996231
