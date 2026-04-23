# Potential container runtime state mess-up cause Pod stuck in "Terminating" state



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #75065

- State: closed

- Labels: kind/bug, area/kubelet, sig/node, lifecycle/rotten

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/75065



## Problem



<!-- Please use this template while reporting a bug and provide as much info as possible. Not doing so may result in your bug not being addressed in a timely manner. Thanks!

If the matter is security related, please disclose it privately via https://kubernetes.io/security/
-->


**What happened**:
When we issue `kubectl delete pod xxx`, pod stuck in "Terminating" state. PLEG is unable to update pod cache (unable to retrieve container status) and therefore stopped sending event about the pod to kubelet, causing this pod not get processed at all.

See [https://github.com/kubernetes/kubernetes/blob/release-1.12/pkg/kubelet/pleg/generic.go#L246](url)

The following kubectl snippets showed that there are 2 pods stuck (there were more but I cleaned them up), after investigation, its with same reason
```bash

$ kubectl get pods -o wide
--
NAME                      READY   STATUS        RESTARTS   AGE     IP              NODE                            NOMINATED NODE
prod-648bc5b867-jqvsh     2/2     Running       0          2d20h   10.12.105.255   ip-10-12-100-232.ec2.internal   <none>
webapp-54d7665b67-gs6qd   1/2     Terminating   0          3d      10.12.119.193   ip-10-12-113-150.ec2.internal   <none>
webapp-5974b77df4-57758   2/2     Running       190        2d21h   10.12.2.53      ip-10-12-13-140.ec2.internal    <none>
webapp-858597759d-mkwfv   1/2     Terminating   12         3d18h   10.12.78.5      ip-10-12-64-69.ec2.internal     <none>
```


**What you expected to happen**:
Pod gets deleted gracefully by kubelet. In such case, if there is really some state mess up, either in kubelet or in containerd, kubelet should handle it more gracefully, i.e. PLEG should not skip the pod but still send event to kubelet, and if it needs to be teared down, ignore the container that does not exist

**How to reproduce it (as minimally and precisely as possible)**:
Happens intermittently in production, frequency is high enough to warn people about k8s stability, not able to reproduce manually

**Anything else we need to know?**:
More details about my debugging

1. kubelet log showed that it started to get container status with container id (container is created already), but container run time reported "No such container"
2. container started and terminated (failed, not k8s / docker related)
3. kubelet kept on getting "No such container" for all subsequent changes

```bash
Mar  1 18:41:24 node-k8s-use1-prod-shared-001-kubecluster-3-0a0c7196 kubelet[6746]: E0301 18:41:24.389774    6746 remote_runtime.go:282] ContainerStatus "bbb334ceee527fa8dba09922038cab7107b85b3bf87000dda812f4edc20f65d0" from runtime service failed: rpc error: code = Unknown desc = Error: No such container: bbb334ceee527fa8dba09922038cab7107b85b3bf87000dda812f4edc20f65d0
--
Mar  1 18:41:24 node-k8s-use1-prod-shared-001-kubecluster-3-0a0c7196 kubelet[6746]: E0301 18:41:24.389800    6746 kuberuntime_container.go:393] ContainerStatus for bbb334ceee527fa8dba09922038cab7107b85b3bf87000dda812f4edc20f65d0 error: rpc error: code = Unknown desc = Error: No such container: bbb334ceee527fa8dba09922038cab7107b85b3bf87000dda812f4edc20f65d0
Mar  1 18:41:24 node-k8s-use1-prod-shared-001-kubecluster-3-0a0c7196 kubelet[6746]: E0301 18:41:24.389809    6746 kuberuntime_manager.go:866] getPodContainerStatuses for pod "webapp-54d7665b67-gs6qd_webapp(6edfc89a-3c51-11e9-b48f-025c9b2a13c0)" failed: rpc error: code = Unknown desc = Error: No such container: bbb334ceee527fa8dba09922038cab7107b85b3bf87000dda812f4edc20f65d0
Mar  1 18:41:24 node-k8s-use1-prod-shared-001-kubecluster-3-0a0c7196 kubelet[6746]: E0301 18:41:24.389821    6746 generic.go:241] PLEG: Ignoring events for pod webapp-54d7665b67-gs6qd/webapp: rpc error: code = Unknown desc = Error: No such container: bbb334ceee527fa8dba09922038cab7107b85b3bf87000dda812f4edc20f65d0
Mar  1 18:41:24 node-k8s-use1-prod-shared-001-kubecluster-3-0a0c7196 dockerd[7294]: time="2019-03-01T18:41:24Z" level=info msg="shim docker-containerd-shim started" address="/containerd-shim/moby/bbb334ceee527fa8dba09922038cab7107b85b3bf87000dda812f4edc20f65d0/shim.sock" debug=false pid=25663
Mar  1 18:41:24 node-k8s-use1-prod-shared-001-kubecluster-3-0a0c7196 dockerd[7294]: time="2019-03-01T18:41:24Z" level=info msg="shim reaped" id=bbb334ceee527fa8dba09922038cab7107b85b3bf87000dda812f4edc20f65d0
Mar  1 19:00:48 node-k8s-use1-prod-shared-001-kubecluster-3-0a0c7196 kubelet[6746]: E0301 19:00:48.664741    6746 remote_runtime.go:282] ContainerStatus "bbb334ceee527fa8dba09922038cab7107b85b3bf87000dda812f4edc20f65d0" from runtime service failed: rpc error: code = Unknown desc = Error: No such container: bbb334ceee527fa8dba09922038cab7107b85b3bf87000dda812f4edc20f65d0
Mar  1 19:00:59 node-k8s-use1-prod-shared-001-kubecluster-3-0a0c7196 kubelet[6746]: E0301 19:00:59.208832    6746 remote_runtime.go:282] ContainerStatus "bbb334ceee527fa8dba09922038cab7107b85b3bf87000dda812f4edc20f65d0" from runtime service failed: rpc error: code = Unknown desc = Error: No such container: bbb334ceee527fa8dba09922038cab7107b85b3bf87000dda812f4edc20f65d0
Mar  1 19:08:55 node-k8s-use1-prod-shared-001-kubecluster-3-0a0c7196 kubelet[6746]: E0301 19:08:55.529721    6746 remote_runtime.go:282] ContainerStatus "bbb334ceee527fa8dba09922038cab7107b85b3bf87000dda812f4edc20f65d0" from runtime service failed: rpc error: code = Unknown desc = Error: No such container: bbb334ceee527fa8dba09922038cab7107b85b3bf87000dda812f4edc20f65d0

```

kubelet is actually able to collect the containers return status (from `kubectl describe pod`):
```bash

Name:                      webapp-54d7665b67-gs6qd
--
Namespace:                 webapp
Priority:                  0
PriorityClassName:         <none>
Node:                      ip-10-12-113-150.ec2.internal/10.12.113.150
Start Time:                Fri, 01 Mar 2019 18:40:06 +0000
Labels:                    app=webapp
Annotations:
Status:                    Terminating (lasts <invalid>)
Termination Grace Period:  30s
IP:                        10.12.119.193
Controlled By:             ReplicaSet/webapp-54d7665b67

Init Containers:
xxxxxxxxxxx

Containers:
webapp:
Container ID:  docker://bbb334ceee527fa8dba09922038cab7107b85b3bf87000dda812f4edc20f65d0
Image:         xxxxx
Image ID:      docker-pullable://xxxxxx
Port:          <none>
Host Port:     <none>
Command:xxx
State:          Terminated
Reason:       Error
Exit Code:    127
Started:      Fri, 01 Mar 2019 18:41:24 +0000
Finished:     Fri, 01 Mar 2019 18:41:24 +0000
Ready:          False
Restart Count:  0

......

QoS Class:       Burstable
Node-Selectors:  freeeni=true
Tolerations:     node.kubernetes.io/not-ready:NoExecute for 300s
node.kubernetes.io/unreachable:NoExecute for 300s
Events:          <none>

```

Finally, force kill pod is able to remove the pod

**Environment**:
- Kubernetes version (use `kubectl version`): 1.12
- Cloud provider or hardware configuration: aws ec2
- OS (e.g: `cat /etc/os-release`): 
```bash
cat /etc/os-release
NAME="Ubuntu"
VERSION="16.04.5 LTS (Xenial Xerus)"
ID=ubuntu
ID_LIKE=debian
PRETTY_NAME="Ubuntu 16.04.5 LTS"
VERSION_ID="16.04"
HOME_URL="http://www.ubuntu.com/"
SUPPORT_URL="http://help.ubuntu.com/"
BUG_REPORT_URL="http://bugs.launchpad.net/ubuntu/"
VERSION_CODENAME=xenial
UBUNTU_CODENAME=xenial
```
- Kernel (e.g. `uname -a`): `Linux node-k8s-use1-prod-shared-001-kubecluster-3-0a0c7196 4.15.0-15-generic #16~16.04.1-Ubuntu SMP Thu Apr 5 12:19:23 UTC 2018 x86_64 x86_64 x86_64 GNU/Linux`
- Install tools: kops
- Others: 
```bash
$ docker info
Server Version: 18.06.2-ce
Storage Driver: overlay2
 Backing Filesystem: extfs
 Supports d_type: true
 Native Overlay Diff: true
Logging Driver: json-file
Cgroup Driver: cgroupfs
Plugins:
 Volume: efs local
 Network: bridge host macvlan null overlay
 Log: awslogs fluentd gcplogs gelf journald json-file logentries splunk syslog
Swarm: inactive
Runtimes: nvidia runc
Default Runtime: nvidia
Init Binary: docker-init
containerd version: 468a545b9edcd5932818eb9de8e72413e616e86e
runc version: 6635b4f0c6af3810594d2770f662f34ddc15b40d-dirty (expected: 69663f0bd4b60df09991c08812a60108003fa340)
init version: fec3683
Security Options:
 apparmor
 seccomp
  Profile: default
Kernel Version: 4.15.0-15-generic
Operating System: Ubuntu 16.04.5 LTS
OSType: linux
Architecture: x86_64
CPUs: 36
Total Memory: 68.69GiB
Name: node-k8s-use1-prod-shared-001-kubecluster-3-0a0c7196
ID: WJOR:OJJU:WMOR:L2SG:OS42:YRGB:SNAO:UAKZ:FM22:MBQC:JQKL:D5JR
Docker Root Dir: /mnt/docker
Debug Mode (client): false
Debug Mode (server): false
Registry: https://index.docker.io/v1/
Labels:
Experimental: false
Insecure Registries:
 127.0.0.0/8
Live Restore Enabled: true

WARNING: No swap limit support
```



## Curated Answers



### High Signal Answer 1

+1 noticed this bug before

- Author: WanLinghao
- Quality score: 9
- URL: https://github.com/kubernetes/kubernetes/issues/75065#issuecomment-470370667

### High Signal Answer 2

also getting this in AWS EKS. I think the Docker machine is totally swamped and unable to manage all the pods correctly, and then this happens.

- Author: kevitan
- Quality score: 4
- URL: https://github.com/kubernetes/kubernetes/issues/75065#issuecomment-729219235
