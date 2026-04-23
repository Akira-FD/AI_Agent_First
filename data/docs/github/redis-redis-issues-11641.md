# [BUG] Sentinels can't decide on a master and are stuck in loop



## GitHub Provenance



- Repository: redis/redis

- Issue: #11641

- State: closed

- Labels: none

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/11641



## Problem



**Describe the bug**

When a master get's deleted sentinels should choose a new one ,but in my situation they get stuck in a loop unable to choose a new master.
it's a rare occurance that can  happen after deleting the master a lot of times 
even after 1h no master was selected
**To reproduce**

have a configuration of :
1 redis-master
2 redis-slave
3 sentinel containers runing on each of the pods
I am using helmchart version 5.0.7 by bitnami 
redis image: bitnami/redis:5.0.7-debian-10-r32
sentinel image: bitnami/redis-sentinel:5.0.7-debian-10-r27

changes to values.yaml :
` cluster:
    enabled: true
    slaveCount: 2
  sentinel:
    enabled: true
    downAfterMilliseconds: 4000
    failoverTimeout: 3000`
    
  
delete master untill an infinete loop apears to be happening between the sentinels

during testing I run  script that deleted the new master every couple of minutes 
This behavior doesn't always happen 
**Expected behavior**

For a new master to be selected in a short period of time 

**Additional information**
last log lines from sentinel container
from redis-master-0 pod

1:X 18 Dec 2022 14:49:06.203 # 025a2750a85d0b9e7275c2ffbcfb4c1586be86ff voted for b836e7b84512125456d22fdd66462121203258b9 223
1:X 18 Dec 2022 14:49:09.353 # -failover-abort-not-elected master mymaster 10.40.171.228 6379
1:X 18 Dec 2022 14:49:09.416 # Next failover delay: I will not start a failover before Sun Dec 18 14:49:12 2022
1:X 18 Dec 2022 14:49:10.686 # +new-epoch 224
1:X 18 Dec 2022 14:49:12.356 # +new-epoch 225
1:X 18 Dec 2022 14:49:12.356 # +try-failover master mymaster 10.40.171.228 6379
1:X 18 Dec 2022 14:49:12.360 # +vote-for-leader b836e7b84512125456d22fdd66462121203258b9 225
1:X 18 Dec 2022 14:49:12.368 # 025a2750a85d0b9e7275c2ffbcfb4c1586be86ff voted for b836e7b84512125456d22fdd66462121203258b9 225
1:X 18 Dec 2022 14:49:15.727 # -failover-abort-not-elected master mymaster 10.40.171.228 6379
1:X 18 Dec 2022 14:49:15.779 # Next failover delay: I will not start a failover before Sun Dec 18 14:49:18 2022
1:X 18 Dec 2022 14:49:16.802 # +new-epoch 226
1:X 18 Dec 2022 14:49:18.694 # +new-epoch 227
1:X 18 Dec 2022 14:49:18.694 # +try-failover master mymaster 10.40.171.228 6379
1:X 18 Dec 2022 14:49:18.696 # +vote-for-leader b836e7b84512125456d22fdd66462121203258b9 227
1:X 18 Dec 2022 14:49:18.702 # 025a2750a85d0b9e7275c2ffbcfb4c1586be86ff voted for b836e7b84512125456d22fdd66462121203258b9 227

last log lines from sentinel container
from redis-slave-0 pod

1:X 18 Dec 2022 14:49:06.200 # +new-epoch 223
1:X 18 Dec 2022 14:49:06.203 # +vote-for-leader b836e7b84512125456d22fdd66462121203258b9 223
1:X 18 Dec 2022 14:49:06.222 # Next failover delay: I will not start a failover before Sun Dec 18 14:49:12 2022
1:X 18 Dec 2022 14:49:09.658 # +new-epoch 224
1:X 18 Dec 2022 14:49:09.662 # +vote-for-leader 4d9fa1c092ff634f0678188b14e3b5b5629b9d2c 224
1:X 18 Dec 2022 14:49:09.714 # Next failover delay: I will not start a failover before Sun Dec 18 14:49:15 2022
1:X 18 Dec 2022 14:49:12.365 # +new-epoch 225
1:X 18 Dec 2022 14:49:12.367 # +vote-for-leader b836e7b84512125456d22fdd66462121203258b9 225
1:X 18 Dec 2022 14:49:12.392 # Next failover delay: I will not start a failover before Sun Dec 18 14:49:18 2022
1:X 18 Dec 2022 14:49:16.442 # +new-epoch 226
1:X 18 Dec 2022 14:49:16.445 # +vote-for-leader 4d9fa1c092ff634f0678188b14e3b5b5629b9d2c 226
1:X 18 Dec 2022 14:49:16.496 # Next failover delay: I will not start a failover before Sun Dec 18 14:49:22 2022
1:X 18 Dec 2022 14:49:18.700 # +new-epoch 227
1:X 18 Dec 2022 14:49:18.702 # +vote-for-leader b836e7b84512125456d22fdd66462121203258b9 227
1:X 18 Dec 2022 14:49:18.733 # Next failover delay: I will not start a failover before Sun Dec 18 14:49:25 2022

last log lines from sentinel container
from redis-slave-1 pod

1:X 18 Dec 2022 14:49:12.796 # 025a2750a85d0b9e7275c2ffbcfb4c1586be86ff voted for b836e7b84512125456d22fdd66462121203258b9 225
1:X 18 Dec 2022 14:49:13.419 # -failover-abort-not-elected master mymaster 10.40.171.228 6379
1:X 18 Dec 2022 14:49:13.490 # Next failover delay: I will not start a failover before Sun Dec 18 14:49:16 2022
1:X 18 Dec 2022 14:49:16.433 # +new-epoch 226
1:X 18 Dec 2022 14:49:16.433 # +try-failover master mymaster 10.40.171.228 6379
1:X 18 Dec 2022 14:49:16.435 # +vote-for-leader 4d9fa1c092ff634f0678188b14e3b5b5629b9d2c 226
1:X 18 Dec 2022 14:49:16.444 # 025a2750a85d0b9e7275c2ffbcfb4c1586be86ff voted for 4d9fa1c092ff634f0678188b14e3b5b5629b9d2c 226
1:X 18 Dec 2022 14:49:19.041 # +new-epoch 227
1:X 18 Dec 2022 14:49:19.533 # 025a2750a85d0b9e7275c2ffbcfb4c1586be86ff voted for b836e7b84512125456d22fdd66462121203258b9 227
1:X 18 Dec 2022 14:49:20.391 # -failover-abort-not-elected master mymaster 10.40.171.228 6379
1:X 18 Dec 2022 14:49:20.481 # Next failover delay: I will not start a failover before Sun Dec 18 14:49:23 2022
1:X 18 Dec 2022 14:49:23.385 # +new-epoch 228
1:X 18 Dec 2022 14:49:23.385 # +try-failover master mymaster 10.40.171.228 6379
1:X 18 Dec 2022 14:49:23.388 # +vote-for-leader 4d9fa1c092ff634f0678188b14e3b5b5629b9d2c 228
1:X 18 Dec 2022 14:49:23.394 # 025a2750a85d0b9e7275c2ffbcfb4c1586be86ff voted for 4d9fa1c092ff634f0678188b14e3b5b5629b9d2c 228

ips of running pods :

`
redis-master-0           10.40.161.215   

redis-slave-0             10.40.32.52    

redis-slave-1             10.40.77.32 

`
from the logs the ip 10.40.171.228 seems to be one of the previuosly deleted redis masters



## Curated Answers



### High Signal Answer 1

You can try [latest release 7.0.7](https://github.com/redis/redis/releases). Thanks.

- Author: moticless
- Quality score: 4
- URL: https://github.com/redis/redis/issues/11641#issuecomment-1372229681
