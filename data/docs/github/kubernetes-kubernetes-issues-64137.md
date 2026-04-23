# Kubelet CPU/Memory Usage linearly increases using CronJob



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #64137

- State: closed

- Labels: kind/bug, sig/node, area/teardown, area/workload-api/cronjob, lifecycle/rotten

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/64137



## Problem



<!-- This form is for bug reports and feature requests ONLY!

If you're looking for help check [Stack Overflow](https://stackoverflow.com/questions/tagged/kubernetes) and the [troubleshooting guide](https://kubernetes.io/docs/tasks/debug-application-cluster/troubleshooting/).

If this may be security issue, please disclose it privately via https://kubernetes.io/security/.
-->

**Is this a BUG REPORT or FEATURE REQUEST?**:
/kind bug

**What happened**:
For the past couple of months, we have been experiencing issues with kubelet on different nodes starts using more and more CPU and Memory. This happens somewhat randomly, but we think we have tracked it down to an issue with CronJob. This didn't happen before we started using CronJob in the beginning of the year. For the past two days, we had three separate occurrences of this issue.

**_Incident 1:_**
![screen shot 2018-05-22 at 09 40 17](https://user-images.githubusercontent.com/4429108/40348538-42e440de-5da4-11e8-884b-304ae6a7a049.png)
As seen in the graph above, the mode=system usage increases fairly linear over a period of 16-17 hours. When ssh'ing into the node and running top, it's apparent that the kubelet is using a lot of resources.

We try to dig deeper, by going through the kubelet logs at the time when the increase seems to begin (15:34), we find the following:
```
2018-05-20 15:34:08.000 | I0520 13:34:08.144400 21616 kubelet_pods.go:1080] Killing unwanted pod "bec-monitoring-1526823240-kvccs" |  
-- | -- | --
2018-05-20 15:34:08.000 | W0520 13:34:08.149174 21616 cni.go:265] CNI failed to retrieve network namespace path: Cannot find network namespace for the terminated container "edd71e53c8d95571cc8ff38cc852852a776739555ccf294d5b003015b326cb07" |  
2018-05-20 15:34:08.000 | weave-cni: unable to release IP address: 400 Bad Request: Delete: no addresses for edd71e53c8d95571cc8ff38cc852852a776739555ccf294d5b003015b326cb07 |  
2018-05-20 15:34:08.000 | I0520 13:34:08.188712 21616 qos_container_manager_linux.go:320] [ContainerManager]: Updated QoS cgroup configuration |  
2018-05-20 15:34:06.000 | I0520 13:34:06.176080 21616 kubelet_pods.go:1080] Killing unwanted pod "bec-monitoring-1526823240-kvccs" |  
2018-05-20 15:34:06.000 | E0520 13:34:06.234083 21616 cni.go:301] Error adding network: error setting up interface addresses: nsenter: cannot open /proc/20332/ns/net: No such file or directory |  
2018-05-20 15:34:06.000 | : exit status 1 |  
2018-05-20 15:34:06.000 | E0520 13:34:06.234106 21616 cni.go:250] Error while adding to cni network: error setting up interface addresses: nsenter: cannot open /proc/20332/ns/net: No such file or directory |  
2018-05-20 15:34:06.000 | : exit status 1 |  
2018-05-20 15:34:06.000 | weave-cni: error removing interface "eth0": nsenter: cannot open /proc/20332/ns/net: No such file or directory |  
2018-05-20 15:34:06.000 | : exit status 1 |  
2018-05-20 15:34:06.000 | E0520 13:34:06.332674 21616 remote_runtime.go:92] RunPodSandbox from runtime service failed: rpc error: code = Unknown desc = NetworkPlugin cni failed to set up pod "bec-monitoring-1526823240-kvccs_prod" network: error setting up interface addresses: nsenter: cannot open /proc/20332/ns/net: No such file or directory |  
2018-05-20 15:34:06.000 | : exit status 1 |  
2018-05-20 15:34:06.000 | E0520 13:34:06.332787 21616 kuberuntime_sandbox.go:54] CreatePodSandbox for pod "bec-monitoring-1526823240-kvccs_prod(75c1598e-5c32-11e8-9dae-0642ea7387e6)" failed: rpc error: code = Unknown desc = NetworkPlugin cni failed to set up pod "bec-monitoring-1526823240-kvccs_prod" network: error setting up interface addresses: nsenter: cannot open /proc/20332/ns/net: No such file or directory |  
2018-05-20 15:34:06.000 | : exit status 1 |  
2018-05-20 15:34:06.000 | E0520 13:34:06.332819 21616 kuberuntime_manager.go:636] createPodSandbox for pod "bec-monitoring-1526823240-kvccs_prod(75c1598e-5c32-11e8-9dae-0642ea7387e6)" failed: rpc error: code = Unknown desc = NetworkPlugin cni failed to set up pod "bec-monitoring-1526823240-kvccs_prod" network: error setting up interface addresses: nsenter: cannot open /proc/20332/ns/net: No such file or directory |  
2018-05-20 15:34:06.000 | : exit status 1 |  
2018-05-20 15:34:06.000 | E0520 13:34:06.332917 21616 pod_workers.go:182] Error syncing pod 75c1598e-5c32-11e8-9dae-0642ea7387e6 ("bec-monitoring-1526823240-kvccs_prod(75c1598e-5c32-11e8-9dae-0642ea7387e6)"), skipping: failed to "CreatePodSandbox" for "bec-monitoring-1526823240-kvccs_prod(75c1598e-5c32-11e8-9dae-0642ea7387e6)" with CreatePodSandboxError: "CreatePodSandbox for pod \"bec-monitoring-1526823240-kvccs_prod(75c1598e-5c32-11e8-9dae-0642ea7387e6)\" failed: rpc error: code = Unknown desc = NetworkPlugin cni failed to set up pod \"bec-monitoring-1526823240-kvccs_prod\" network: error setting up interface addresses: nsenter: cannot open /proc/20332/ns/net: No such file or directory\n: exit status 1" |  
2018-05-20 15:34:06.000 | I0520 13:34:06.335458 21616 qos_container_manager_linux.go:320] [ContainerManager]: Updated QoS cgroup configuration |  
2018-05-20 15:34:06.000 | I0520 13:34:06.871789 21616 kubelet.go:1871] SyncLoop (PLEG): "bec-monitoring-1526823240-kvccs_prod(75c1598e-5c32-11e8-9dae-0642ea7387e6)", event: &pleg.PodLifecycleEvent{ID:"75c1598e-5c32-11e8-9dae-0642ea7387e6", Type:"ContainerDied", Data:"edd71e53c8d95571cc8ff38cc852852a776739555ccf294d5b003015b326cb07"} |  
2018-05-20 15:34:06.000 | W0520 13:34:06.871899 21616 pod_container_deletor.go:77] Container "edd71e53c8d95571cc8ff38cc852852a776739555ccf294d5b003015b326cb07" not found in pod's containers |  
2018-05-20 15:34:05.000 | W0520 13:34:05.008121 21616 prober.go:98] No ref for container "docker://98727dbc83cae5409b67c4c2c1c5494c7e4a2eb9bb413045e6e2c33cc445dc32" (default-http-backend-cbjnl_networking(3eb636ca-4935-11e8-9dae-0642ea7387e6):default-http-backend) |  
2018-05-20 15:34:05.000 | I0520 13:34:05.008194 21616 prober.go:101] Liveness probe for "default-http-backend-cbjnl_networking(3eb636ca-4935-11e8-9dae-0642ea7387e6):default-http-backend" errored: net/http: request canceled (Client.Timeout exceeded while reading body) |  
2018-05-20 15:34:05.000 | I0520 13:34:05.023101 21616 operation_generator.go:545] UnmountVolume.TearDown succeeded for volume "kubernetes.io/secret/#########" (OuterVolumeSpecName: "######") pod "75c1598e-5c32-11e8-9dae-0642ea7387e6" (UID: "75c1598e-5c32-11e8-9dae-0642ea7387e6"). InnerVolumeSpecName "#####". PluginName "kubernetes.io/secret", VolumeGidValue "" |  
2018-05-20 15:34:05.000 | I0520 13:34:05.097481 21616 reconciler.go:290] Volume detached for volume "######" (UniqueName: "kubernetes.io/secret/########") on node "ip-10-3-39-100.eu-west-1.compute.internal" DevicePath "" |  
2018-05-20 15:34:05.000 | I0520 13:34:05.850001 21616 kubelet.go:1871] SyncLoop (PLEG): "bec-monitoring-1526823240-kvccs_prod(75c1598e-5c32-11e8-9dae-0642ea7387e6)", event: &pleg.PodLifecycleEvent{ID:"75c1598e-5c32-11e8-9dae-0642ea7387e6", Type:"ContainerDied", Data:"308625733a3b7c04115317413eb5ea7947e0a8082c3c014cf7751fc03c241267"} |  
2018-05-20 15:34:05.000 | W0520 13:34:05.850083 21616 pod_container_deletor.go:77] Container "308625733a3b7c04115317413eb5ea7947e0a8082c3c014cf7751fc03c241267" not found in pod's containers |  
2018-05-20 15:34:05.000 | I0520 13:34:05.853298 21616 kuberuntime_manager.go:392] No ready sandbox for pod "bec-monitoring-1526823240-kvccs_prod(75c1598e-5c32-11e8-9dae-0642ea7387e6)" can be found. Need to start a new one |  
2018-05-20 15:34:05.000 | W0520 13:34:05.855801 21616 cni.go:265] CNI failed to retrieve network namespace path: Cannot find network namespace for the terminated container "308625733a3b7c04115317413eb5ea7947e0a8082c3c014cf7751fc03c241267" |  
2018-05-20 15:34:05.000 | weave-cni: unable to release IP address: 400 Bad Request: Delete: no addresses for 308625733a3b7c04115317413eb5ea7947e0a8082c3c014cf7751fc03c241267

```

**_Incident 2_**
![screen shot 2018-05-22 at 09 52 35](https://user-images.githubusercontent.com/4429108/40349125-e3625964-5da5-11e8-97e6-e86a113288a4.png)
Same pattern as Incident 1. Linear increse in CPU and decrease in memory. 

Digging in to the logs at the starting point again: (multiple of the following lines) 
```

2018-05-20 13:47:12.000 | I0520 11:47:12.142453 21616 kubelet_pods.go:1080] Killing unwanted pod "bec-monitoring-1526816820-cftnn" |  
-- | -- | --
2018-05-20 13:47:12.000 | W0520 11:47:12.146932 21616 cni.go:265] CNI failed to retrieve network namespace path: Cannot find network namespace for the terminated container "28c448f8b5fffb62168c4bab2a779c200715874723a7c61fe2ffcf3c0cc78129" |  
2018-05-20 13:47:12.000 | weave-cni: unable to release IP address: 400 Bad Request: Delete: no addresses for 28c448f8b5fffb62168c4bab2a779c200715874723a7c61fe2ffcf3c0cc78129 |  
2018-05-20 13:47:12.000 | I0520 11:47:12.170373 21616 qos_container_manager_linux.go:320] [ContainerManager]: Updated QoS cgroup configuration |  
2018-05-20 13:47:10.000 | I0520 11:47:10.155868 21616 kubelet_pods.go:1080] Killing unwanted pod "bec-monitoring-1526816820-cftnn" |  
2018-05-20 13:47:10.000 | weave-cni: error removing interface "eth0": nsenter: cannot open /proc/7186/ns/net: No such file or directory |  
2018-05-20 13:47:10.000 | : exit status 1 |  
2018-05-20 13:47:10.000 | I0520 11:47:10.305582 21616 qos_container_manager_linux.go:320] [ContainerManager]: Updated QoS cgroup configuration |  
2018-05-20 13:47:10.000 | I0520 11:47:10.555789 21616 kubelet.go:1871] SyncLoop (PLEG): "bec-monitoring-1526816820-cftnn_prod(84d6a4fc-5c23-11e8-9dae-0642ea7387e6)", event: &pleg.PodLifecycleEvent{ID:"84d6a4fc-5c23-11e8-9dae-0642ea7387e6", Type:"ContainerDied", Data:"28c448f8b5fffb62168c4bab2a779c200715874723a7c61fe2ffcf3c0cc78129"} |  
2018-05-20 13:47:10.000 | W0520 11:47:10.555946 21616 pod_container_deletor.go:77] Container "28c448f8b5fffb62168c4bab2a779c200715874723a7c61fe2ffcf3c0cc78129" not found in pod's containers |  
2018-05-20 13:47:09.000 | I0520 11:47:09.535015 21616 kubelet.go:1871] SyncLoop (PLEG): "bec-monitoring-1526816820-cftnn_prod(84d6a4fc-5c23-11e8-9dae-0642ea7387e6)", event: &pleg.PodLifecycleEvent{ID:"84d6a4fc-5c23-11e8-9dae-0642ea7387e6", Type:"ContainerStarted", Data:"28c448f8b5fffb62168c4bab2a779c200715874723a7c61fe2ffcf3c0cc78129"} |  
2018-05-20 13:47:08.000 | I0520 11:47:08.143561 21616 kubelet_pods.go:1080] Killing unwanted pod "bec-monitoring-1526816820-cftnn" |  
2018-05-20 13:47:08.000 | W0520 11:47:08.148106 21616 cni.go:265] CNI failed to retrieve network namespace path: Cannot find network namespace for the terminated container "9e4eb4c2933fc27d59b63a5a9c23e273d7ba974a8cca516f1a4b12d0233dc54d" |  
2018-05-20 13:47:08.000 | weave-cni: unable to release IP address: 400 Bad Request: Delete: no addresses for 9e4eb4c2933fc27d59b63a5a9c23e273d7ba974a8cca516f1a4b12d0233dc54d
```

**_Incident 3_**
![screen shot 2018-05-22 at 09 58 14](https://user-images.githubusercontent.com/4429108/40349351-ac718708-5da6-11e8-9dca-ac9a2d8b7267.png)
Again the same pattern.

And the logs around that time is the same as before:
```
@timestamp | log |  
-- | -- | --
2018-05-21 14:08:06.000 | W0521 12:08:06.252658 3821 pod_container_deletor.go:77] Container "b775f90ece2d8674b6e033edd606fb119e66d55f8353f56c84d1badbb4e5812f" not found in pod's containers |  
2018-05-21 14:08:05.000 | I0521 12:08:05.134309 3821 kubelet_pods.go:1080] Killing unwanted pod "bec-monitoring-1526904480-cfchl" |  
2018-05-21 14:08:05.000 | weave-cni: error removing interface "eth0": nsenter: cannot open /proc/7009/ns/net: No such file or directory |  
2018-05-21 14:08:05.000 | : exit status 1 |  
2018-05-21 14:08:05.000 | I0521 12:08:05.212048 3821 kubelet.go:1871] SyncLoop (PLEG): "bec-monitoring-1526904480-cfchl_prod(9b836cca-5cef-11e8-9dae-0642ea7387e6)", event: &pleg.PodLifecycleEvent{ID:"9b836cca-5cef-11e8-9dae-0642ea7387e6", Type:"ContainerStarted", Data:"b775f90ece2d8674b6e033edd606fb119e66d55f8353f56c84d1badbb4e5812f"} |  
2018-05-21 14:08:05.000 | I0521 12:08:05.286498 3821 qos_container_manager_linux.go:320] [ContainerManager]: Updated QoS cgroup configuration |  
2018-05-21 14:08:04.000 | I0521 12:08:04.177863 3821 kubelet.go:1871] SyncLoop (PLEG): "bec-monitoring-1526904480-cfchl_prod(9b836cca-5cef-11e8-9dae-0642ea7387e6)", event: &pleg.PodLifecycleEvent{ID:"9b836cca-5cef-11e8-9dae-0642ea7387e6", Type:"ContainerDied", Data:"def4398c4393075f4fb36fcc4d55ae6bc9ca9439c7b0175d28facbf146a6ba61"} |  
2018-05-21 14:08:04.000 | W0521 12:08:04.177970 3821 pod_container_deletor.go:77] Container "def4398c4393075f4fb36fcc4d55ae6bc9ca9439c7b0175d28facbf146a6ba61" not found in pod's containers |  
2018-05-21 14:08:04.000 | I0521 12:08:04.181260 3821 kuberuntime_manager.go:392] No ready sandbox for pod "bec-monitoring-1526904480-cfchl_prod(9b836cca-5cef-11e8-9dae-0642ea7387e6)" can be found. Need to start a new one |  
2018-05-21 14:08:04.000 | W0521 12:08:04.183702 3821 cni.go:265] CNI failed to retrieve network namespace path: Cannot find network namespace for the terminated container "def4398c4393075f4fb36fcc4d55ae6bc9ca9439c7b0175d28facbf146a6ba61" |  
2018-05-21 14:08:04.000 | weave-cni: unable to release IP address: 400 Bad Request: Delete: no addresses for def4398c4393075f4fb36fcc4d55ae6bc9ca9439c7b0175d28facbf146a6ba61
```

We have a 3 cronjobs running at regurlar intervals, one of them is the mentioned container in the logs: bec-monitoring. We suspect that cronjobs may be the reason to this problem. 
`restartPolicy: Never` is set in all cronjobs.

The most aggressive cronjob is running every minute with the following configuration: (some details removed)
```
apiVersion: batch/v1beta1
kind: CronJob
metadata:
  name: bec-monitoring
spec:
  schedule: '*/1 * * * *'
  jobTemplate:
    spec:
      template:
        metadata:
          name: bec-monitoring
          labels:
            app: bec-monitoring
        spec:
          containers:
          - name: bec-monitoring
            image: <IMAGE>
            args:
            - ./bec
            - --identifiers
            - 12345678
          restartPolicy: Never
```

We have been looking into similar issues related to docker shim: https://github.com/kubernetes/kubernetes/issues/55620
https://github.com/kubernetes/kubernetes/pull/55641

But we don't see any id's in the docker shim folder, which is not referencing a currently running container. Except in one of the case where a cronjob container was exited  18 minutes prior - and therefore not relating to the beginning of the linear increase many hours before.

The solution to the increase, is to restart the kubelet, and everything seems to return to normal.


**What you expected to happen**:
The Kubelet not to use all of the resources. 

**How to reproduce it (as minimally and precisely as possible)**:
Unfortunately I haven't found a way to reproduce. 

**Anything else we need to know?**:
Running weavenet as CNI, with the following image: `weaveworks/weave-kube:2.2.0`

**Environment**:
- Kubernetes version (use `kubectl version`):
```
$ kubectl version
Client Version: version.Info{Major:"1", Minor:"10", GitVersion:"v1.10.0", GitCommit:"fc32d2f3698e36b93322a3465f63a14e9f0eaead", GitTreeState:"clean", BuildDate:"2018-03-26T16:55:54Z", GoVersion:"go1.9.3", Compiler:"gc", Platform:"darwin/amd64"}
Server Version: version.Info{Major:"1", Minor:"8", GitVersion:"v1.8.10", GitCommit:"044cd262c40234014f01b40ed7b9d09adbafe9b1", GitTreeState:"clean", BuildDate:"2018-03-19T17:44:09Z", GoVersion:"go1.8.3", Compiler:"gc", Platform:"linux/amd64"}
```
- Cloud provider or hardware configuration:
```
AWS
```
- OS (e.g. from /etc/os-release):
```
admin@ip-10-3-39-100:~$ cat /etc/os-release
PRETTY_NAME="Debian GNU/Linux 8 (jessie)"
NAME="Debian GNU/Linux"
VERSION_ID="8"
VERSION="8 (jessie)"
ID=debian
HOME_URL="http://www.debian.org/"
SUPPORT_URL="http://www.debian.org/support"
BUG_REPORT_URL="https://bugs.debian.org/"
```
- Kernel (e.g. `uname -a`):
```
admin@ip-10-3-39-100:~$ uname -a
Linux ip-10-3-39-100 4.4.111-k8s #1 SMP Sun Jan 14 19:32:08 UTC 2018 x86_64 GNU/Linux
```
- Install tools:
```
kops
```



## Curated Answers



### High Signal Answer 1

Hi everyone,

We believe we're having the same issue. We were able to identify that every run of a cronjob with a mounted secret causes the OS to leak one more cgroup, as evidenced by `systemd-cgls -a | egrep "run-.*scope"`

This in turn causes huge CPU and memory load for kubelet, at least in part because we scrape the cAdvisor statistics, which include cpu and memory usage for every cgroup present on the system. 

I was able to reproduce this issue with a simple CronJob with nodeSelector set for a specific node:
```
apiVersion: batch/v1beta1
kind: CronJob
metadata:
  name: test-cgroups-bug
  namespace: tt2-stable
spec:
  schedule: "*/1 * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          nodeSelector:
            kubernetes.io/hostname: tt-k8s1-w69.ko.seznam.cz
          containers:
          - name: hello
            image: debian:stretch
            args:
            - /bin/sh
            - -c
            - date
            volumeMounts:
            - mountPath: /secret
              name: test-secret
          restartPolicy: OnFailure
          volumes:
          - name: test-secret
            secret:
              defaultMode: 420
              secretName: test-cgroup-secret
```

When I delete the secret from CronJob spec, the cgroup count stays the same.

We're using k8s 1.10.2, docker 17.3.1 and 17.3.2, we're running on our own infrastructure on Ubuntu 16.04, kernel 4.14. We use calico as our network plugin. 

Is there anything that we can do to help you debug the issue? This issue is extremely problematic for us because we need to drain and reboot nodes in order to fix the issue.

- Author: zloo
- Quality score: 4
- URL: https://github.com/kubernetes/kubernetes/issues/64137#issuecomment-394342449

### High Signal Answer 2

FWIW, below:

`find /sys/fs/cgroup/ -name run-*.scope -type d -exec rmdir {} \; `

is an hack that works

- Author: bjhaid
- Quality score: 4
- URL: https://github.com/kubernetes/kubernetes/issues/64137#issuecomment-410860823
