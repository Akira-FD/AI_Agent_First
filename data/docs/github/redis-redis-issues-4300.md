# Support for password rotation (feature request)



## GitHub Provenance



- Repository: redis/redis

- Issue: #4300

- State: closed

- Labels: none

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/4300



## Problem



Today, Redis supports basic authentication with the requirepass configuration and AUTH command. However, some production environments require password rotation at regular intervals (for example, every N months) for compliance and security reasons. Other databases provide the concept of "user accounts" with varying levels of access. This allows password rotation with steps 1) create a new user/password pair in the database 2) reconfigure clients to use the new user/password pair instead of the old one 3) remove the old user/password pair from the database.

Achieving password rotation in Redis does not require user accounts, necessarily. One option: allow a list of accepted passwords, instead of a single password. Steps to rotate a password would be 1) modify redis.conf to add new password to passwords list & perform rolling restart of Redis instances 2) reconfigure clients to use the new password 3) modify redis.conf to remove 
 old password from passwords list & perform rolling restart of Redis instances.

Thoughts, questions and comments welcome.

Thanks,
Ryan



## Curated Answers



### High Signal Answer 1

With the introduction of ACL in v6, each user may have zero, one or more passwords. This seems to resolve this issue so it will be closed - please feel free to reopen or create a new one if needed.

- Author: itamarhaber
- Quality score: 4
- URL: https://github.com/redis/redis/issues/4300#issuecomment-676518335
