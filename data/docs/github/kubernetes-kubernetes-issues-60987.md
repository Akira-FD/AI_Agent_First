# Orphaned pod found - but volume paths are still present on disk



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #60987

- State: closed

- Labels: sig/storage, sig/node, needs-triage

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/60987



## Problem



<!-- This form is for bug reports and feature requests ONLY! 

If you're looking for help check [Stack Overflow](https://stackoverflow.com/questions/tagged/kubernetes) and the [troubleshooting guide](https://kubernetes.io/docs/tasks/debug-application-cluster/troubleshooting/).
-->

**Is this a BUG REPORT or FEATURE REQUEST?**:
BUG

**What happened**:
Kubelet is periodically going into an error state and causing errors with our storage layer (ceph, shared filesystem). Upon cleaning out the orphaned pod directory things eventually right themselves.
* Workaround: `rmdir /var/lib/kubelet/pods/*/volumes/*rook/*`

**What you expected to happen**:
Kubelet should intelligently deal with orphaned pods. Cleaning a stale directory manually should not be required.

**How to reproduce it (as minimally and precisely as possible)**:
Using rook-0.7.0 (this isn't a rook problem as far as I can tell but this is how we're reproducing):
kubectl create -f rook-operator.yaml
kubectl create -f rook-cluster.yaml
kubectl create -f rook-filesystem.yaml

Mount/write to the shared filesystem and monitor /var/log/messages for the following:
`
kubelet: E0309 16:46:30.429770    3112 kubelet_volumes.go:128] Orphaned pod "2815f27a-219b-11e8-8a2a-ec0d9a3a445a" found, but volume paths are still present on disk : There were a total of 1 errors similar to this. Turn up verbosity to see them.
`

**Anything else we need to know?**:
This looks identical to the following: https://github.com/kubernetes/kubernetes/issues/45464 but for a different plugin.

**Environment**:
- Kubernetes version (use `kubectl version`):
`
Client Version: version.Info{Major:"1", Minor:"9", GitVersion:"v1.9.3", GitCommit:"d2835416544f298c919e2ead3be3d0864b52323b", GitTreeState:"clean", BuildDate:"2018-02-07T12:22:21Z", GoVersion:"go1.9.2", Compiler:"gc", Platform:"linux/amd64"}
Server Version: version.Info{Major:"1", Minor:"9", GitVersion:"v1.9.3", GitCommit:"d2835416544f298c919e2ead3be3d0864b52323b", GitTreeState:"clean", BuildDate:"2018-02-07T11:55:20Z", GoVersion:"go1.9.2", Compiler:"gc", Platform:"linux/amd64"}
`

- Cloud provider or hardware configuration:
Bare-metal private cloud
- OS (e.g. from /etc/os-release):
Red Hat Enterprise Linux Server release 7.4 (Maipo)
- Kernel (e.g. `uname -a`):
Linux 4.4.115-1.el7.elrepo.x86_64 #1 SMP Sat Feb 3 20:11:41 EST 2018 x86_64 x86_64 x86_64 GNU/Linux
- Install tools:
kubeadm



## Curated Answers



### High Signal Answer 1

I observe lot of those errors logged by kubelet in my clusters , this bugs seems to be releated to pods that were using a custom bash-flexvolume plugin ( which mount cifs volumes ), anyway this is very annoing I about 90% of the kubelet logs are those

```console
E0823 10:31:01.847946    1303 kubelet_volumes.go:140] Orphaned pod "19a4e3e6-a562-11e8-9a25-309c23027882" found, but volume paths are still present on disk : There were a total of 2 errors similar to this. Turn up verbosity to see them.
E0823 10:31:03.840552    1303 kubelet_volumes.go:140] Orphaned pod "19a4e3e6-a562-11e8-9a25-309c23027882" found, but volume paths are still present on disk : There were a total of 2 errors similar to this. Turn up verbosity to see them.
````
printed every two seconds.. fixing require a manual operation ( or automate a risky rm -Rf operation based on a log line parser )  but this is a poor-man workaround.. while kubelet  could/should/must! handle that problem itself
I see discussion around this bug since more than one year.. it's possible that no one consider this to be fixed? 
if no one want to fix it I suggest to decrease the error-level ( outputting "ERROR" in 90% of my logs lines   when you don't consider this as a serious bug is wrong )

- Author: fvigotti
- Quality score: 18
- URL: https://github.com/kubernetes/kubernetes/issues/60987#issuecomment-415370444

### High Signal Answer 2

@fredkan running the script on the host, watch orphaned pod and remove them in runtime.

where is the script?

- Author: qinzhao168
- Quality score: 14
- URL: https://github.com/kubernetes/kubernetes/issues/60987#issuecomment-429203142

### High Signal Answer 3

Having the same issue with Kubernetes 1.11, Docker 18.06.0-ce and ceph 13.2.1

- Author: owend
- Quality score: 9
- URL: https://github.com/kubernetes/kubernetes/issues/60987#issuecomment-410093014
