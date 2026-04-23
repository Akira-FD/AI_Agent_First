# Eviction does not occur during lua scripts



## GitHub Provenance



- Repository: redis/redis

- Issue: #6565

- State: closed

- Labels: none

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/6565



## Problem



There appears to no eviction happening during evalsha (as well as eval) commands even with allkeys-lru set. This is causing OOM errors while running scripts.

### Repo:
Redis server was set with:
```
maxmemory 10000000
maxmemory-policy allkeys-lru
```

We will use a simple script to insert data:
``` lua
local function commit()
        local key = ARGV[1]
        local value = ARGV[2]
        redis.call('HSET', key, 'value', value)
end

return commit()
```

Insert the script:
`echo -E "script load \"local function commit()\n local key = ARGV[1]\n local value = ARGV[2]\n redis.call('HSET', key, 'value', value)\nend\n\nreturn commit()\"" | redis-cli --pipe`

Than populate the db:
`for i in {1..100}; do; redis-cli evalsha ac5b6905f1d2186b86ee8868aaacb38eda65596e 0 "$i" "$(head -c 100000000 /dev/urandom | tr -dc A-Za-z0-9 | head -c 100000 ; echo '')"; done`

You should see a few keys being added, followed by the max memory being hit:
`(error) ERR Error running script (call to f_ac5b6905f1d2186b86ee8868aaacb38eda65596e): @user_script:4: @user_script: 4: -OOM command not allowed when used memory > 'maxmemory'.`

### Expected:
The expected result is the same as other hset calls, to evict keys based on the eviction policy. The issue appears to be in scripting.c throwing the exception instead of attempting to evict keys using `freeMemoryIfNeededAndSafe()`

I attempted to add that call to line 527 before pushing the error and it appears to fix the issue, however I worry that it may not exist because of some conflict with replication.



## Curated Answers



### High Signal Answer 1

Hello @asgeirrr, I backported the fix to 5.0 (already in the branch), and will push a new release ASAP.

- Author: antirez
- Quality score: 5
- URL: https://github.com/redis/redis/issues/6565#issuecomment-618414682

### High Signal Answer 2

@schmidp IIUC the fix is in 5.0.10

- Author: guybe7
- Quality score: 4
- URL: https://github.com/redis/redis/issues/6565#issuecomment-718063623
