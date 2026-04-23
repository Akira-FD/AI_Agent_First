# etcdserver: read-only range request took too long with etcd 3.2.24



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #70082

- State: closed

- Labels: kind/bug, area/etcd, sig/api-machinery, lifecycle/rotten

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/70082



## Problem



**Is this a BUG REPORT or FEATURE REQUEST?**:

> Uncomment only one, leave it on its own line:
>
/kind bug
> /kind feature


**What happened**:

When deploying a brand new cluster with either t2.medium (with 4Go RAM) instances or even t3.large (with 8Go RAM) I get errors in ETCD logs :

```
2018-10-22 11:22:14.706081 W | etcdserver: read-only range request "key:\"foo\" " with result "range_response_count:0 size:5" took too long (1.310910984s) to execute
2018-10-22 11:22:16.247803 W | etcdserver: read-only range request "key:\"/registry/persistentvolumeclaims/\" range_end:\"/registry/persistentvolumeclaims0\" " with
result "range_response_count:0 size:5" took too long (128.414553ms) to execute                                                                                       
2018-10-22 11:22:16.361601 W | etcdserver: read-only range request "key:\"/registry/persistentvolumeclaims\" range_end:\"/registry/persistentvolumeclaimt\" count_onl
y:true " with result "range_response_count:0 size:5" took too long (242.137365ms) to execute                                                                         
2018-10-22 11:22:16.363943 W | etcdserver: read-only range request "key:\"/registry/configmaps\" range_end:\"/registry/configmapt\" count_only:true " with result "ra
nge_response_count:0 size:7" took too long (115.223655ms) to execute                                                                                                 
2018-10-22 11:22:16.364641 W | etcdserver: read-only range request "key:\"/registry/configmaps/\" range_end:\"/registry/configmaps0\" " with result "range_response_c
ount:1 size:2564" took too long (117.026891ms) to execute                                                                                                            
2018-10-22 11:22:18.298297 W | wal: sync duration of 1.84846442s, expected less than 1s                                                                             
2018-10-22 11:22:20.375327 W | wal: sync duration of 2.067539108s, expected less than 1s                                                                             
proto: no coders for int                                                      
proto: no encoder for ValueSize int [GetProperties]                                                                                                                  
2018-10-22 11:22:20.892736 W | etcdserver: request "header:<ID:16312995093338348449 username:\"kube-apiserver-etcd-client\" auth_revision:1 > txn:<compare:<target:MO
D key:\"/registry/serviceaccounts/kube-system/node-controller\" mod_revision:283 > success:<request_put:<key:\"/registry/serviceaccounts/kube-system/node-controller\
" value_size:166 >> failure:<>>" with result "size:16" took too long (516.492646ms) to execute    
```

**What you expected to happen**:

I expect the logs to be exempt of errors.

**How to reproduce it (as minimally and precisely as possible)**:

Launch a kubeadm cluster with Kubernetes version v1.12.1

**Anything else we need to know?**:

When downgrading to Kubernetes v1.11.3 there are no error anymore, also, staying in v1.12.1 and manually downgrading etcd to version v3.2.18 (which is ship with kubernetes v1.11.3) workaround the issue.

**Environment**:
- Kubernetes version (use `kubectl version`): v.1.12.1
- Cloud provider or hardware configuration: aws
- OS (e.g. from /etc/os-release): Coreos 1855.4.0
- Kernel (e.g. `uname -a`): `Linux ip-10-0-3-11.eu-west-1.compute.internal 4.14.67-coreos #1 SMP Mon Sep 10 23:14:26 UTC 2018 x86_64 Intel(R) Xeon(R) Platinum 8175M CPU @ 2.50GHz GenuineIntel GNU/Linux`
- Install tools: kubeadm
- Others: etcd version 3.2.24 as per kubernetes 1.12.1



## Curated Answers



### High Signal Answer 1

@ArchiFleKs It says of 354842 total operations, 228127 took less than or equal to .002 seconds, 348658 took less than or equal to .004 seconds,where the 348658 number includes those that took less than .002 seconds as well. There are a very small portion (85 to be exact) of disk backend commits taking over 128ms. I'm not well enough calibrated to say for sure if those number are out of healthy range or not, but they don't look particularly alarming.   The `wal: sync duration of 2.067539108s, expected less than 1s` line from the original report does, however, look quite alarming and suggests high disk IO latency. How about your `etcd_disk_wal_fsync_duration_seconds_bucket` metric, @ArchiFleKs? Does that show anything?

- Author: jpbetz
- Quality score: 4
- URL: https://github.com/kubernetes/kubernetes/issues/70082#issuecomment-434791965
