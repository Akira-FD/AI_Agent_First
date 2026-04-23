# [NEW] Optimize HyperLogLog by SIMD acceleration



## GitHub Provenance



- Repository: redis/redis

- Issue: #13551

- State: closed

- Labels: none

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/13551



## Problem



We found that the dense-encoding part of HyperLogLog can be significantly accelerated by SIMD instructions.

Our benchmark tests the performance of merging 3 dense hll structures.

```
pfcount key1 key2 key3
pfmerge keyall key1 key2 key3
```

The result shows a 12x speedup compared to the scalar version.

```
======================================================================================================
Type             Ops/sec    Avg. Latency     p50 Latency     p99 Latency   p99.9 Latency       KB/sec 
------------------------------------------------------------------------------------------------------
PFCOUNT-scalar    5280.76        37.93893        34.81500        69.63100        73.72700       283.63
PFCOUNT-avx2     69802.99         2.85844         2.75100         5.53500         6.97500      3749.18
------------------------------------------------------------------------------------------------------
PFMERGE-scalar    9445.56        21.17554        20.09500        38.91100        41.21500       590.35
PFMERGE-avx2    120642.02         1.65367         1.59100         3.21500         5.11900      7540.13
------------------------------------------------------------------------------------------------------

CPU:    13th Gen Intel® Core™ i9-13900H × 20
Memory: 32.0 GiB
OS:     Ubuntu 22.04.5 LTS
```

+ Fork: https://github.com/Nugine/redis/tree/hll-simd
+ Experiment repo: https://github.com/Nugine/redis-hyperloglog
+ Benchmark: https://github.com/Nugine/redis-hyperloglog/blob/main/scripts/memtier.sh

I'm not sure whether this change is acceptable to maintainers. I will create a PR if it is ok.



## Curated Answers



### High Signal Answer 1

@Nugine nice!! i saw the changed you made in https://github.com/Nugine/redis/commit/92dc40caba4e04840918804ebc1768cc0e4833f8.
seems good to me, although I'm not familiar with SIMD, thanks.

- Author: sundb
- Quality score: 4
- URL: https://github.com/redis/redis/issues/13551#issuecomment-2357360445
