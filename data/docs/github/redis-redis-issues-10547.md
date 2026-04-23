# [CRASH] Redis sentinel enters tilt mode and dies after a time



## GitHub Provenance



- Repository: redis/redis

- Issue: #10547

- State: closed

- Labels: state:to-be-closed

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/10547



## Problem



**Crash report**

```
...
Mon, Apr 4 2022 9:35:15 pm | 1:X 05 Apr 2022 03:35:15.396 # -sdown sentinel 33f1828dea40e299b1c83d4824a2c329cc4e3ac7 redis1-node-1.redis1 30018 @ mymaster redis1-node-1.redis1 30019
Mon, Apr 4 2022 9:37:22 pm | 1:X 05 Apr 2022 03:37:22.709 # +tilt #tilt mode entered
Mon, Apr 4 2022 9:37:52 pm | 1:X 05 Apr 2022 03:37:52.796 # -tilt #tilt mode exited
Mon, Apr 4 2022 9:39:49 pm | 1:X 05 Apr 2022 03:39:49.641 # +tilt #tilt mode entered
Mon, Apr 4 2022 9:40:19 pm | 1:X 05 Apr 2022 03:40:19.698 # -tilt #tilt mode exited
Mon, Apr 4 2022 9:47:31 pm | 1:X 05 Apr 2022 03:47:31.739 # +tilt #tilt mode entered
Mon, Apr 4 2022 9:48:01 pm | 1:X 05 Apr 2022 03:48:01.793 # -tilt #tilt mode exited
Mon, Apr 4 2022 9:48:18 pm | 1:X 05 Apr 2022 03:48:18.242 # +sdown sentinel 034a2c242957d1854224b48c3583b3fb18173e51 redis1-node-2.redis1 30020 @ mymaster redis1-node-1.redis1 30019
Mon, Apr 4 2022 9:48:21 pm | 1:X 05 Apr 2022 03:48:21.916 # -sdown sentinel 034a2c242957d1854224b48c3583b3fb18173e51 redis1-node-2.redis1 30020 @ mymaster redis1-node-1.redis1 30019
Mon, Apr 4 2022 9:49:21 pm | 1:X 05 Apr 2022 03:49:21.832 # +sdown sentinel 33f1828dea40e299b1c83d4824a2c329cc4e3ac7 redis1-node-1.redis1 30018 @ mymaster redis1-node-1.redis1 30019
Mon, Apr 4 2022 9:49:35 pm | 1:X 05 Apr 2022 03:49:35.659 # -sdown sentinel 33f1828dea40e299b1c83d4824a2c329cc4e3ac7 redis1-node-1.redis1 30018 @ mymaster redis1-node-1.redis1 30019
Mon, Apr 4 2022 9:49:47 pm | 1:X 05 Apr 2022 03:49:47.207 # +tilt #tilt mode entered
Mon, Apr 4 2022 9:50:03 pm | 1:X 05 Apr 2022 03:50:03.126 # +tilt #tilt mode entered
Mon, Apr 4 2022 9:50:14 pm | 1:X 05 Apr 2022 03:50:14.364 # +tilt #tilt mode entered
Mon, Apr 4 2022 9:50:26 pm | 1:X 05 Apr 2022 03:50:26.260 # +tilt #tilt mode entered
Mon, Apr 4 2022 9:50:36 pm | 1:X 05 Apr 2022 03:50:36.989 # +tilt #tilt mode entered
Mon, Apr 4 2022 9:50:37 pm | 1:signal-handler (1649130637) Received SIGTERM scheduling shutdown...
Mon, Apr 4 2022 9:50:38 pm | 1:X 05 Apr 2022 03:50:38.052 # User requested shutdown...
Mon, Apr 4 2022 9:50:38 pm | 1:X 05 Apr 2022 03:50:38.052 # Sentinel is now ready to exit, bye bye..
```

**Additional information**

1. OS distribution and version
Deployed onto k8s, issue appears on multiple k8s versions and OS's

2. Steps to reproduce (if any)
Deploy bitnami helm chart, with simple values.
Wait about an hour for sentinel to crash.

I first opened the issue on bitnami chart, https://github.com/bitnami/charts/issues/9689
For full information you can go to that issue and see additional info.
However it should not be a chart issue, but an infra issue.

I am posting here hoping that someone has seen something like this before. Any help would be greatly appreciated.



## Curated Answers



### High Signal Answer 1

@jonathon2nd,  please keep us update with any new findings. Thanks.

- Author: moticless
- Quality score: 5
- URL: https://github.com/redis/redis/issues/10547#issuecomment-1100693018
