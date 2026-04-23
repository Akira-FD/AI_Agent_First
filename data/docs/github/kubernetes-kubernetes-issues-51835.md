# Pods stuck on terminating



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #51835

- State: closed

- Labels: kind/bug, sig/storage, sig/node

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/51835



## Problem



<!-- This form is for bug reports and feature requests ONLY! 

If you're looking for help check [Stack Overflow](https://stackoverflow.com/questions/tagged/kubernetes) and the [troubleshooting guide](https://kubernetes.io/docs/tasks/debug-application-cluster/troubleshooting/).
-->

**Is this a BUG REPORT or FEATURE REQUEST?**:

/kind bug

**What happened**:
Pods stuck on terminating for a long time

**What you expected to happen**:
Pods get terminated

**How to reproduce it (as minimally and precisely as possible)**:
1. Run a deployment
2. Delete it
3. Pods are still terminating

**Anything else we need to know?**:
Kubernetes pods stuck as `Terminating` for a few hours after getting deleted.

Logs:
kubectl describe pod my-pod-3854038851-r1hc3
```
Name:				my-pod-3854038851-r1hc3
Namespace:			container-4-production
Node:				ip-172-16-30-204.ec2.internal/172.16.30.204
Start Time:			Fri, 01 Sep 2017 11:58:24 -0300
Labels:				pod-template-hash=3854038851
				release=stable
				run=my-pod-3
Annotations:			kubernetes.io/created-by={"kind":"SerializedReference","apiVersion":"v1","reference":{"kind":"ReplicaSet","namespace":"container-4-production","name":"my-pod-3-3854038851","uid":"5816c...
				prometheus.io/scrape=true
Status:				Terminating (expires Fri, 01 Sep 2017 14:17:53 -0300)
Termination Grace Period:	30s
IP:
Created By:			ReplicaSet/my-pod-3-3854038851
Controlled By:			ReplicaSet/my-pod-3-3854038851
Init Containers:
  ensure-network:
    Container ID:	docker://guid-1
    Image:		XXXXX
    Image ID:		docker-pullable://repo/ensure-network@sha256:guid-0
    Port:		<none>
    State:		Terminated
      Exit Code:	0
      Started:		Mon, 01 Jan 0001 00:00:00 +0000
      Finished:		Mon, 01 Jan 0001 00:00:00 +0000
    Ready:		True
    Restart Count:	0
    Environment:	<none>
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from default-token-xxxxx (ro)
Containers:
  container-1:
    Container ID:	docker://container-id-guid-1
    Image:		XXXXX
    Image ID:		docker-pullable://repo/container-1@sha256:guid-2
    Port:		<none>
    State:		Terminated
      Exit Code:	0
      Started:		Mon, 01 Jan 0001 00:00:00 +0000
      Finished:		Mon, 01 Jan 0001 00:00:00 +0000
    Ready:		False
    Restart Count:	0
    Limits:
      cpu:	100m
      memory:	1G
    Requests:
      cpu:	100m
      memory:	1G
    Environment:
      XXXX
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from default-token-xxxxx (ro)
  container-2:
    Container ID:	docker://container-id-guid-2
    Image:		alpine:3.4
    Image ID:		docker-pullable://alpine@sha256:alpine-container-id-1
    Port:		<none>
    Command:
      X
    State:		Terminated
      Exit Code:	0
      Started:		Mon, 01 Jan 0001 00:00:00 +0000
      Finished:		Mon, 01 Jan 0001 00:00:00 +0000
    Ready:		False
    Restart Count:	0
    Limits:
      cpu:	20m
      memory:	40M
    Requests:
      cpu:		10m
      memory:		20M
    Environment:	<none>
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from default-token-xxxxx (ro)
  container-3:
    Container ID:	docker://container-id-guid-3
    Image:		XXXXX
    Image ID:		docker-pullable://repo/container-3@sha256:guid-3
    Port:		<none>
    State:		Terminated
      Exit Code:	0
      Started:		Mon, 01 Jan 0001 00:00:00 +0000
      Finished:		Mon, 01 Jan 0001 00:00:00 +0000
    Ready:		False
    Restart Count:	0
    Limits:
      cpu:	100m
      memory:	200M
    Requests:
      cpu:	100m
      memory:	100M
    Readiness:	exec [nc -zv localhost 80] delay=1s timeout=1s period=5s #success=1 #failure=3
    Environment:
      XXXX
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from default-token-xxxxx (ro)
  container-4:
    Container ID:	docker://container-id-guid-4
    Image:		XXXX
    Image ID:		docker-pullable://repo/container-4@sha256:guid-4
    Port:		9102/TCP
    State:		Terminated
      Exit Code:	0
      Started:		Mon, 01 Jan 0001 00:00:00 +0000
      Finished:		Mon, 01 Jan 0001 00:00:00 +0000
    Ready:		False
    Restart Count:	0
    Limits:
      cpu:	600m
      memory:	1500M
    Requests:
      cpu:	600m
      memory:	1500M
    Readiness:	http-get http://:8080/healthy delay=1s timeout=1s period=10s #success=1 #failure=3
    Environment:
      XXXX
    Mounts:
      /app/config/external from volume-2 (ro)
      /data/volume-1 from volume-1 (ro)
      /var/run/secrets/kubernetes.io/serviceaccount from default-token-xxxxx (ro)
Conditions:
  Type		Status
  Initialized 	True
  Ready 	False
  PodScheduled 	True
Volumes:
  volume-1:
    Type:	Secret (a volume populated by a Secret)
    SecretName:	volume-1
    Optional:	false
  volume-2:
    Type:	ConfigMap (a volume populated by a ConfigMap)
    Name:	external
    Optional:	false
  default-token-xxxxx:
    Type:	Secret (a volume populated by a Secret)
    SecretName:	default-token-xxxxx
    Optional:	false
QoS Class:	Burstable
Node-Selectors:	<none>
```

sudo journalctl -u kubelet | grep "my-pod"
```
[...]
Sep 01 17:17:56 ip-172-16-30-204 kubelet[9619]: time="2017-09-01T17:17:56Z" level=info msg="Releasing address using workloadID" Workload=my-pod-3854038851-r1hc3
Sep 01 17:17:56 ip-172-16-30-204 kubelet[9619]: time="2017-09-01T17:17:56Z" level=info msg="Releasing all IPs with handle 'my-pod-3854038851-r1hc3'"
Sep 01 17:17:56 ip-172-16-30-204 kubelet[9619]: time="2017-09-01T17:17:56Z" level=warning msg="Asked to release address but it doesn't exist. Ignoring" Workload=my-pod-3854038851-r1hc3 workloadId=my-pod-3854038851-r1hc3
Sep 01 17:17:56 ip-172-16-30-204 kubelet[9619]: time="2017-09-01T17:17:56Z" level=info msg="Teardown processing complete." Workload=my-pod-3854038851-r1hc3 endpoint=<nil>
Sep 01 17:19:06 ip-172-16-30-204 kubelet[9619]: I0901 17:19:06.591946    9619 kubelet.go:1824] SyncLoop (DELETE, "api"):my-pod-3854038851(b8cf2ecd-8f25-11e7-ba86-0a27a44c875)"
```

sudo journalctl -u docker | grep "docker-id-for-my-pod"
```
Sep 01 17:17:55 ip-172-16-30-204 dockerd[9385]: time="2017-09-01T17:17:55.695834447Z" level=error msg="Handler for POST /v1.24/containers/docker-id-for-my-pod/stop returned error: Container docker-id-for-my-pod is already stopped"
Sep 01 17:17:56 ip-172-16-30-204 dockerd[9385]: time="2017-09-01T17:17:56.698913805Z" level=error msg="Handler for POST /v1.24/containers/docker-id-for-my-pod/stop returned error: Container docker-id-for-my-pod is already stopped"
```

**Environment**:
- Kubernetes version (use `kubectl version`):
Client Version: version.Info{Major:"1", Minor:"7", GitVersion:"v1.7.3", GitCommit:"2c2fe6e8278a5db2d15a013987b53968c743f2a1", GitTreeState:"clean", BuildDate:"2017-08-03T15:13:53Z", GoVersion:"go1.8.3", Compiler:"gc", Platform:"darwin/amd64"}
Server Version: version.Info{Major:"1", Minor:"6", GitVersion:"v1.6.6", GitCommit:"7fa1c1756d8bc963f1a389f4a6937dc71f08ada2", GitTreeState:"clean", BuildDate:"2017-06-16T18:21:54Z", GoVersion:"go1.7.6", Compiler:"gc", Platform:"linux/amd64"}

- Cloud provider or hardware configuration**:
AWS

- OS (e.g. from /etc/os-release):
NAME="CentOS Linux"
VERSION="7 (Core)"
ID="centos"
ID_LIKE="rhel fedora"
VERSION_ID="7"
PRETTY_NAME="CentOS Linux 7 (Core)"
ANSI_COLOR="0;31"
CPE_NAME="cpe:/o:centos:centos:7"
HOME_URL="https://www.centos.org/"
BUG_REPORT_URL="https://bugs.centos.org/"

CENTOS_MANTISBT_PROJECT="CentOS-7"
CENTOS_MANTISBT_PROJECT_VERSION="7"
REDHAT_SUPPORT_PRODUCT="centos"
REDHAT_SUPPORT_PRODUCT_VERSION="7"

- Kernel (e.g. `uname -a`):
Linux ip-172-16-30-204 3.10.0-327.10.1.el7.x86_64 #1 SMP Tue Feb 16 17:03:50 UTC 2016 x86_64 x86_64 x86_64 GNU/Linux

- Install tools:
Kops

- Others:
Docker version 1.12.6, build 78d1802

@kubernetes/sig-aws @kubernetes/sig-scheduling



## Curated Answers



### High Signal Answer 1

I have the same issue on Kubernetes 1.8.2 on IBM Cloud. After new pods are started the old pods are stuck in terminating. 

kubectl version
`
Server Version: version.Info{Major:"1", Minor:"8+", GitVersion:"v1.8.2-1+d150e4525193f1", GitCommit:"d150e4525193f1c79569c04efc14599d7deb5f3e", GitTreeState:"clean", BuildDate:"2017-10-27T08:15:17Z", GoVersion:"go1.8.3", Compiler:"gc", Platform:"linux/amd64"}
`


I have used `kubectl delete pod xxx --now` as well as `kubectl delete pod foo --grace-period=0 --force` to no avail.

- Author: wardhane
- Quality score: 75
- URL: https://github.com/kubernetes/kubernetes/issues/51835#issuecomment-346793299

### High Signal Answer 2

I have the same issue with Kubernetes 1.8.1 on Azure - after deployment is changed and new pods are have been started, the old pods are stuck at terminating.

- Author: tadas-subonis
- Quality score: 35
- URL: https://github.com/kubernetes/kubernetes/issues/51835#issuecomment-345757555

### High Signal Answer 3

> Usually volume and network cleanup consume more time in termination.

Correct. They are always suspect.

@igorleao You can try `kubectl delete pod xxx --now` as well.

- Author: dixudx
- Quality score: 9
- URL: https://github.com/kubernetes/kubernetes/issues/51835#issuecomment-326810204
