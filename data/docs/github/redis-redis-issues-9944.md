# Module API for providing command infromation



## GitHub Provenance



- Repository: redis/redis

- Issue: #9944

- State: closed

- Labels: none

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/9944



## Problem



Once https://github.com/redis/redis/pull/9656 is merged we need to come up with a module API to allow
module to provide extra information about their commands

Ideally we would like it to be as declarative as possible, rather than calling a dedicated API for every
tiny bit of information



## Curated Answers



### High Signal Answer 1

we discussed this in the core-team meeting, and concluded we wanna proceed with the declarative approach.
@zuiderkwast i know @guybe7 is busy, maybe you can take this forward?

- Author: oranagra
- Quality score: 4
- URL: https://github.com/redis/redis/issues/9944#issuecomment-1004710396
