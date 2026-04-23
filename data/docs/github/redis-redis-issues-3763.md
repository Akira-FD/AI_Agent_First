# Does redis-cli require a time-out option?



## GitHub Provenance



- Repository: redis/redis

- Issue: #3763

- State: closed

- Labels: none

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/3763



## Problem



When using redis-cli to connect to the remote redis server, redis-cli will have to wait more than 1 minutes to return an error if the network fails.
When redis-cli is used in the script, the above problem can cause the script to execute slowly.
So is it possible to add a timeout option to redis-cli to solve the problem?



## Curated Answers



### High Signal Answer 1

Sounds like a good feature have that shouldn't be too hard to add.

- Author: itamarhaber
- Quality score: 4
- URL: https://github.com/redis/redis/issues/3763#issuecomment-274080078
