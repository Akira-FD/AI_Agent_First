# SCRIPT LIST command desirable



## GitHub Provenance



- Repository: redis/redis

- Issue: #3846

- State: closed

- Labels: none

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/3846



## Problem



@antirez Currently if you know the `SHA1` for a loaded script you can check for its existence with `SCRIPT EXISTS`.  If you don't know the `SHA1` value there is no way to get a list of scripts in the cache.  It would be useful if it were possible to list the `SHA1` values in the cache, and ideally the script associated with the `SHA1`.

The situation is that scripts get updated/versioned and loaded into Redis.  Old ones need to be deleted, but the `SHA1` values are not necessarily recorded.  With a listing function and the ability to see the script that was loaded, old scripts can be manually deleted.

Secondarily, if the data is available, a `SCRIPT GET SHA1` would be useful.



## Curated Answers



### High Signal Answer 1

@allanwax @usernameisnull, redis philosophy is that it intentionally doesn't want to let you get the script code back (i.e. `SCRIPT GET SHA1`), the design is that the scripts are the responsibility of the client application, and are only cached by redis to improve performance.
The application should always fall back to `SCRIPT LOAD` or `EVAL` if `EVALSHA` or `SCRIPT EXIST` fail.

> If you don't know the SHA1 value there is no way to get a list of scripts in the cache

The application must!! know the SHA1 value, and actually have the script code ready to be re-loaded! redis should not be the one that gives you the SHA1 of a script you wish to execute! it's not a coincidence that scripts are not named! doing that would introduce a versioning problem (you'll need to make sure you run the right version of your named script), which is what redis aims to avoid!

You should not attempt or wish to delete old scripts from the cache! so i also don't see any reason for a `SCRIPT LIST` command.

Please describe what's the use case for your request.

- Author: oranagra
- Quality score: 4
- URL: https://github.com/redis/redis/issues/3846#issuecomment-693189533

### High Signal Answer 2

@rocksteady-david and others. would that solve your problems?
we can add
`DEBUG SCRIPT LIST`
`DEBUG SCRIPT <SHA>`
both of which, print their output to the redis log file, and reply `+OK`

- Author: oranagra
- Quality score: 4
- URL: https://github.com/redis/redis/issues/3846#issuecomment-1053379318

### High Signal Answer 3

@mgravell the intention here is NOT to add another command and a capability for client applications, it is actually the opposite.
I don't want this command to be used by anyone, note that it'll be under the DEBUG command, (not the SCRIPT command).
It's not about security, but rather about preventing people from abusing the philosophy about EVAL scripts, which dictates that they are part of the client application (not hosted by Redis).
So such a command is only intended to use for debugging, specifically when one's hosting a 3rd party redis application or a library.

- Author: oranagra
- Quality score: 4
- URL: https://github.com/redis/redis/issues/3846#issuecomment-1053926487
