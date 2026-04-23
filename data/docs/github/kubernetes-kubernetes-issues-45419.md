# Node flapping between Ready/NotReady with PLEG issues



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #45419

- State: closed

- Labels: kind/bug, area/reliability, sig/node

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/45419



## Problem



<!-- Thanks for filing an issue! Before hitting the button, please answer these questions.-->

**Is this a request for help?** No


**What keywords did you search in Kubernetes issues before filing this one?** (If you have found any duplicates, you should instead reply there.): PLEG NotReady kubelet

---

**Is this a BUG REPORT or FEATURE REQUEST?** Bug

<!--
If this is a BUG REPORT, please:
  - Fill in as much of the template below as you can.  If you leave out
    information, we can't help you as well.

If this is a FEATURE REQUEST, please:
  - Describe *in detail* the feature/behavior/change you'd like to see.

In both cases, be ready for followup questions, and please respond in a timely
manner.  If we can't reproduce a bug or think a feature already exists, we
might close your issue.  If we're wrong, PLEASE feel free to reopen it and
explain why.
-->

**Kubernetes version** (use `kubectl version`): 1.6.2


**Environment**:
- **Cloud provider or hardware configuration**: CoreOS on AWS
- **OS** (e.g. from /etc/os-release):CoreOS 1353.7.0
- **Kernel** (e.g. `uname -a`): 4.9.24-coreos
- **Install tools**:
- **Others**:


**What happened**:

I have a 3-worker cluster. Two and sometimes all three nodes keep dropping into `NotReady`with the following messages in `journalctl -u kubelet`:

```
May 05 13:59:56 ip-10-50-20-208.ec2.internal kubelet[2858]: I0505 13:59:56.872880    2858 kubelet_node_status.go:379] Recording NodeNotReady event message for node ip-10-50-20-208.ec2.internal
May 05 13:59:56 ip-10-50-20-208.ec2.internal kubelet[2858]: I0505 13:59:56.872908    2858 kubelet_node_status.go:682] Node became not ready: {Type:Ready Status:False LastHeartbeatTime:2017-05-05 13:59:56.872865742 +0000 UTC LastTransitionTime:2017-05-05 13:59:56.872865742 +0000 UTC Reason:KubeletNotReady Message:PLEG is not healthy: pleg was last seen active 3m7.629592089s ago; threshold is 3m0s}
May 05 14:07:57 ip-10-50-20-208.ec2.internal kubelet[2858]: I0505 14:07:57.598132    2858 kubelet_node_status.go:379] Recording NodeNotReady event message for node ip-10-50-20-208.ec2.internal
May 05 14:07:57 ip-10-50-20-208.ec2.internal kubelet[2858]: I0505 14:07:57.598162    2858 kubelet_node_status.go:682] Node became not ready: {Type:Ready Status:False LastHeartbeatTime:2017-05-05 14:07:57.598117026 +0000 UTC LastTransitionTime:2017-05-05 14:07:57.598117026 +0000 UTC Reason:KubeletNotReady Message:PLEG is not healthy: pleg was last seen active 3m7.346983738s ago; threshold is 3m0s}
May 05 14:17:58 ip-10-50-20-208.ec2.internal kubelet[2858]: I0505 14:17:58.536101    2858 kubelet_node_status.go:379] Recording NodeNotReady event message for node ip-10-50-20-208.ec2.internal
May 05 14:17:58 ip-10-50-20-208.ec2.internal kubelet[2858]: I0505 14:17:58.536134    2858 kubelet_node_status.go:682] Node became not ready: {Type:Ready Status:False LastHeartbeatTime:2017-05-05 14:17:58.536086605 +0000 UTC LastTransitionTime:2017-05-05 14:17:58.536086605 +0000 UTC Reason:KubeletNotReady Message:PLEG is not healthy: pleg was last seen active 3m7.275467289s ago; threshold is 3m0s}
May 05 14:29:59 ip-10-50-20-208.ec2.internal kubelet[2858]: I0505 14:29:59.648922    2858 kubelet_node_status.go:379] Recording NodeNotReady event message for node ip-10-50-20-208.ec2.internal
May 05 14:29:59 ip-10-50-20-208.ec2.internal kubelet[2858]: I0505 14:29:59.648952    2858 kubelet_node_status.go:682] Node became not ready: {Type:Ready Status:False LastHeartbeatTime:2017-05-05 14:29:59.648910669 +0000 UTC LastTransitionTime:2017-05-05 14:29:59.648910669 +0000 UTC Reason:KubeletNotReady Message:PLEG is not healthy: pleg was last seen active 3m7.377520804s ago; threshold is 3m0s}
May 05 14:44:00 ip-10-50-20-208.ec2.internal kubelet[2858]: I0505 14:44:00.938266    2858 kubelet_node_status.go:379] Recording NodeNotReady event message for node ip-10-50-20-208.ec2.internal
May 05 14:44:00 ip-10-50-20-208.ec2.internal kubelet[2858]: I0505 14:44:00.938297    2858 kubelet_node_status.go:682] Node became not ready: {Type:Ready Status:False LastHeartbeatTime:2017-05-05 14:44:00.938251338 +0000 UTC LastTransitionTime:2017-05-05 14:44:00.938251338 +0000 UTC Reason:KubeletNotReady Message:PLEG is not healthy: pleg was last seen active 3m7.654775919s ago; threshold is 3m0s}
```

docker daemon is fine (local `docker ps`, `docker images`, etc. all work and respond immediately). 

using weave networking installed via `kubectl apply -f https://git.io/weave-kube-1.6`

**What you expected to happen**:

Nodes to be ready.


**How to reproduce it** (as minimally and precisely as possible):

Wish I knew how!


**Anything else we need to know**:

All of the nodes (workers and masters) on same private subnet with NAT gateway to Internet. Workers in security group that allows unlimited access (all ports) from masters security group; masters allow all ports from same subnet. proxy is running on workers; apiserver, controller-manager, scheduler on masters. 

`kubectl logs` and `kubectl exec` always hang, even when run from the master itself (or from outside).



## Curated Answers



### High Signal Answer 1

The PLEG health check does very little. In every iteration, it calls `docker ps` to detect container states changes, and call `docker ps` and `inspect` to get the details of those containers. 
After finishing each iteration, it updates a timestamp. If the timestamp hasn't been updated for a while (i.e., 3 minutes), the health check fails.

Unless your node is loaded with huge number of pods that PLEG can't finish doing all these in 3 minutes (which should not happen), the most probable cause would be that docker is slow. You may not observe that in your occasional `docker ps` check, but that doesn't mean it's not there. 

If we don't expose the "unhealthy" status, it'd hide many problems from the users and potentially cause more issue. For example, kubelet'd silently not reacting to changes in a timely manner and cause even more confusion. 

Suggestions on how to make this more debuggable are welcome...

- Author: yujuhong
- Quality score: 73
- URL: https://github.com/kubernetes/kubernetes/issues/45419#issuecomment-304413713

### High Signal Answer 2

@deitch pleg is for kubelet to periodically list pods in the node to check healthy and update cache. If you see pleg timeout log, it may not be related to dns, but because kubelet's call to docker is timeout.

- Author: qiujian16
- Quality score: 30
- URL: https://github.com/kubernetes/kubernetes/issues/45419#issuecomment-300713759

### High Signal Answer 3

@deitch most likely docker was not as responsive at times, causing PLEG to miss its threshold.

- Author: yujuhong
- Quality score: 11
- URL: https://github.com/kubernetes/kubernetes/issues/45419#issuecomment-300872123
