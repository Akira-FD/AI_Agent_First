# "Test HINCRBYFLOAT for correct float representation" failing on non x86 architectures



## GitHub Provenance



- Repository: redis/redis

- Issue: #3768

- State: closed

- Labels: state:to-be-closed

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/3768



## Problem



Hi,

[This is redis 4.0-rc2]

The "Test HINCRBYFLOAT for correct float representation" appears to be failing on non x86 architectures. See, for example:

 * https://buildd.debian.org/status/fetch.php?pkg=redis&arch=armel&ver=4%3A4.0-rc2-2&stamp=1483816143&raw=0
 * https://buildd.debian.org/status/fetch.php?pkg=redis&arch=armhf&ver=4%3A4.0-rc2-2&stamp=1483816489&raw=0
 * https://buildd.debian.org/status/fetch.php?pkg=redis&arch=mips&ver=4%3A4.0-rc2-2&stamp=1483817927&raw=0
 * https://buildd.debian.org/status/fetch.php?pkg=redis&arch=mipsel&ver=4%3A4.0-rc2-2&stamp=1483817273&raw=0

See also https://github.com/antirez/redis/issues/2846



## Curated Answers



### High Signal Answer 1

Same issue when testing on the Bash available as a Linux Subsystem under Windows 10 x64.

Version: 4.0.1 stable
The two tests that fail are:

*** [err]: Test HINCRBYFLOAT for correct float representation (issue #2846) in tests/unit/type/hash.tcl
Expected condition '[r hincrbyfloat myhash float 1.23] eq {1.23}' to be true ([r hincrbyfloat myhash float 1.23] eq {1.23})
*** [err]: PUBLISH/PSUBSCRIBE after PUNSUBSCRIBE without arguments in tests/unit/pubsub.tcl

- Author: dandrei
- Quality score: 6
- URL: https://github.com/redis/redis/issues/3768#issuecomment-326393986
