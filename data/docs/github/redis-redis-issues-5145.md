# Make INFO faster again!11one



## GitHub Provenance



- Repository: redis/redis

- Issue: #5145

- State: closed

- Labels: none

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/5145



## Problem



As noted in #4727 at this point INFO risks to be monkey asses slow once there are too many clients. We need to better profile INFO, because it is a very abused command, called in all the contexts, repeatedly called by Redis Sentinel as well... Once identified all the slow spots, there is to find solutions, because sometimes those slow-to-compute information are also very useful for debugging. This issue is a note for me to do some design + implementation work to mitigate this problem before the release of Redis 5, and to get feedbacks about this problem.



## Curated Answers



### High Signal Answer 1

as far as i can tell all of the concerns here are already handled by f69876280c630d49574fa094808d3a4791c5039b.
i'm closing it, let me know if you think otherwise.

- Author: oranagra
- Quality score: 4
- URL: https://github.com/redis/redis/issues/5145#issuecomment-675444625
