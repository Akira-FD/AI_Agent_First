# Kube-apiserver high memory usage on pending pods storm



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #98423

- State: closed

- Labels: kind/bug, sig/scalability, sig/scheduling, sig/api-machinery, triage/accepted

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/98423



## Problem



**What happened**:
The kube-apiserver consumed memory spiked to ~90G the moment we upscaled the cluster with +400 nodes while having thousands of pending pods.
![image](https://user-images.githubusercontent.com/2542264/105851679-1722a880-5fec-11eb-9517-081e77c029a2.png)
This resulted in OOM kill of the kube-apiserver pods causing outage. Example:
![image](https://user-images.githubusercontent.com/2542264/105851827-43d6c000-5fec-11eb-8d36-3ec6b92c8365.png)

**What you expected to happen**:
The kube-apiserver should not consume that much memory resulting in OOM. I understand that under the presented conditions there could be performance penalties on kube-apiserver or kube-scheduler delaying the pods' startup, but it should not lead to OOM kill.

**How to reproduce it (as minimally and precisely as possible)**:
1. Have a deployment with pods requesting for 4CPU and 4G MEM
2. Scale the deployment to a huge number of replicas: 2000
3. Prevent the CA to autoscale the cluster (i.e. uninstall the cluster-autoscaler/scale it to 0 replicas)
4. Wait for ~30min-1h (there is no pattern here, it could happen even faster)
5. Manually scale the cluster out to 400 nodes
6. Monitor the kube-apiserver MEM usage

**Anything else we need to know?**:
This in conjunction with cilium and contour+envoy could lead to ingress failures.

**Environment**:
- Kubernetes version (use `kubectl version`):
```
$ kubectl version
Client Version: version.Info{Major:"1", Minor:"16", GitVersion:"v1.16.2", GitCommit:"c97fe5036ef3df2967d086711e6c0c405941e14b", GitTreeState:"clean", BuildDate:"2019-10-15T23:41:55Z", GoVersion:"go1.12.10", Compiler:"gc", Platform:"darwin/amd64"}
Server Version: version.Info{Major:"1", Minor:"18", GitVersion:"v1.18.14", GitCommit:"89182bdd065fbcaffefec691908a739d161efc03", GitTreeState:"clean", BuildDate:"2020-12-18T12:02:35Z", GoVersion:"go1.13.15", Compiler:"gc", Platform:"linux/amd64"}
```
- Cloud provider or hardware configuration:
`AWS`
- OS (e.g: `cat /etc/os-release`):
```
# cat /etc/os-release
NAME="Flatcar Container Linux by Kinvolk"
ID=flatcar
ID_LIKE=coreos
VERSION=2605.10.0
VERSION_ID=2605.10.0
BUILD_ID=2020-12-15-1904
PRETTY_NAME="Flatcar Container Linux by Kinvolk 2605.10.0 (Oklo)"
ANSI_COLOR="38;5;75"
HOME_URL="https://flatcar-linux.org/"
BUG_REPORT_URL="https://issues.flatcar-linux.org"
FLATCAR_BOARD="amd64-usr"
```
- Kernel (e.g. `uname -a`):
```
# uname -a
Linux ip-10-79-147-99 5.4.83-flatcar #1 SMP Tue Dec 15 18:31:34 -00 2020 x86_64 Intel(R) Xeon(R) Platinum 8275CL CPU @ 3.00GHz GenuineIntel GNU/Linux
```
- Install tools:
- Network plugin and version (if this is a network-related bug):
- Others:



## Curated Answers



### High Signal Answer 1

This is unfortunatly one of the known problems when you have a large number of objects in your cluster and will be addresses in teh following kep

https://github.com/kubernetes/enhancements/tree/master/keps/sig-api-machinery/3157-watch-list#motivation

/close

- Author: aojea
- Quality score: 5
- URL: https://github.com/kubernetes/kubernetes/issues/98423#issuecomment-1680377898
