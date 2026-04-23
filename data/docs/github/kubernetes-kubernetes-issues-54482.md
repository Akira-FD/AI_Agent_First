# --hostname-override ignored when --cloud-provider is specified



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #54482

- State: closed

- Labels: kind/bug, priority/backlog, area/cloudprovider, sig/node, kind/feature, lifecycle/frozen, area/provider/aws, sig/cloud-provider, needs-triage

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/54482



## Problem



**Is this a BUG REPORT or FEATURE REQUEST?**:

/kind bug
/sig aws


**What happened**:
Trying to start kubelet with --hostname-override=ip-172-28-68-60 but still see in the logs:
```
Attempting to register node ip-172-28-68-60.eu-west-1.compute.internal
Unable to register node "ip-172-28-68-60.eu-west-1.compute.internal" with API server: nodes "ip-172-28-68-60.eu-west-1.compute.internal" is forbidden: node "ip-172-28-68-60" cannot modify node "ip-172-28-68-60.eu-west-1.compute.internal"
```
ps aux:
root      4610  3.3  7.7 404596 78320 ?        Ssl  12:58   0:00 /usr/bin/kubelet ...... --hostname-override=ip-172-28-68-60

**What you expected to happen**:
Hostname should be ip-172-28-68-60 instead of ip-172-28-68-60.eu-west-1.compute.internal

**How to reproduce it (as minimally and precisely as possible)**:
set
--cloud-provider=aws --hostname-override=ip-172-28-68-60
for kubelet

**Anything else we need to know?**:

**Environment**:
- Kubernetes version (use `kubectl version`):
Client Version: version.Info{Major:"1", Minor:"8", GitVersion:"v1.8.1", GitCommit:"f38e43b221d08850172a9a4ea785a86a3ffa3b3a", GitTreeState:"clean", BuildDate:"2017-10-11T23:27:35Z", GoVersion:"go1.8.3", Compiler:"gc", Platform:"linux/amd64"}
Server Version: version.Info{Major:"1", Minor:"8", GitVersion:"v1.8.1", GitCommit:"f38e43b221d08850172a9a4ea785a86a3ffa3b3a", GitTreeState:"clean", BuildDate:"2017-10-11T23:16:41Z", GoVersion:"go1.8.3", Compiler:"gc", Platform:"linux/amd64"}

- Cloud provider or hardware configuration**: aws

- OS (e.g. from /etc/os-release):
NAME="Ubuntu"
VERSION="16.04.2 LTS (Xenial Xerus)"
ID=ubuntu
ID_LIKE=debian
PRETTY_NAME="Ubuntu 16.04.2 LTS"
VERSION_ID="16.04"
HOME_URL="http://www.ubuntu.com/"
SUPPORT_URL="http://help.ubuntu.com/"
BUG_REPORT_URL="http://bugs.launchpad.net/ubuntu/"
VERSION_CODENAME=xenial
UBUNTU_CODENAME=xenial

- Kernel (e.g. `uname -a`): Linux ip-172-28-68-60 4.4.0-1038-aws #47-Ubuntu SMP Thu Sep 28 20:05:35 UTC 2017 x86_64 x86_64 x86_64 GNU/Linux

- Install tools:
- Others:



## Curated Answers



### High Signal Answer 1

We have this issue also. Our DEV Kubernetes live at baremetal env where kubelet `--hostname-override` option works fine and hence we are able to set node names to:
```
node01-dev.<project_name>.com
node02-dev.<project_name>.com
node03-dev.<project_name>.com
...
```

But our staging and PROD envs are on AWS where we use `--provider aws`. In this case kubelet does not allow us to set node names according to our naming convention. In AWS we have the self-descriptive DNS names like `node02-staging.<project_name>.com` but cannot make node names to be equal to these DNS names because kubelet overrides it with ugly AWS `ip-xx-yy-zz.us-west-1.compute.internal`.

Imagine that you have a team of engineers and they receive an alert 'staging Kubernetes node 5 - disk full'. What would you like them to see when they run `kubectl get nodes` - `node05.staging - NotReady` or `ip-124-12-34.13.us-west-1.compute.internal - NotReady`? ;) Especially taking into account that `node05.staging` is a resolvable DNS name convenient for the team to use and that 'staging' word is in the node name so it is less possible for the engineer to accidentally go to a wrong env..

What I want to say is that in AWS having a human-frindly CNAME record for each node and node name equal to this DNS record allows to make `kubectl get node` and `kubectl describe node` commands to give a more human-friendly representation of the cluster and reduce the human error factor.

- Author: daniilyar
- Quality score: 20
- URL: https://github.com/kubernetes/kubernetes/issues/54482#issuecomment-375070306

### High Signal Answer 2

This is causing so much trouble for us. We have a naming scheme which quickly allows us to see zone/environment for a node, but the "hardcoded" node naming in Kubernetes hinders all of this. Logfiles/metrics are super-hard to work with, as I have to cross-check the "auto-name" against our inventory list all the time. This is a real problem, and it really needs to be solved.

- Author: trondhindenes
- Quality score: 15
- URL: https://github.com/kubernetes/kubernetes/issues/54482#issuecomment-409468930

### High Signal Answer 3

This is affecting me too! I believe it is using the EC2 instance's private hostname and ignoring `--hostname-override`. We are not using `kubeadm` so we haven't found a workaround.

- Author: 2rs2ts
- Quality score: 11
- URL: https://github.com/kubernetes/kubernetes/issues/54482#issuecomment-356683050
