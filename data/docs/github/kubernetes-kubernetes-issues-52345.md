# Re-run initContainers in a Deployment when containers exit on error



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #52345

- State: closed

- Labels: sig/node, kind/feature, needs-triage

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/52345



## Problem



**Is this a BUG REPORT or FEATURE REQUEST?**:

/kind feature


**What happened**: Container in a Deployment exits on error, container is restarted without first re-running the initContainer. 

**What you expected to happen**: Container in a Deployment exits on error, initContainer is re-run before restarting the container.

**How to reproduce it (as minimally and precisely as possible)**: 

Sample spec:
```
kind: "Deployment"
apiVersion: "extensions/v1beta1"
metadata:
  name: "test"
  labels:
    name: "test"
spec:
  replicas: 1
  selector:
    matchLabels:
      name: "test"
  template:
    metadata:
      name: "test"
      labels:
        name: "test"
    spec:
      initContainers:
        - name: sleep
          image: debian:stretch
          imagePullPolicy: IfNotPresent
          command:
            - sleep
            - 1s
      containers:
        - name: test
          image: debian:stretch
          imagePullPolicy: IfNotPresent
          command:
            - /bin/sh
            - exit 1

```

**Anything else we need to know?**:

**Environment**:
- Kubernetes version (use `kubectl version`): 
```
Client Version: version.Info{Major:"", Minor:"", GitVersion:"v0.0.0-master+$Format:%h$", GitCommit:"db809c0eb7d33fac8f54d8735211f2f3a8fc4214", GitTreeState:"clean", BuildDate:"2017-09-11T19:46:47Z", GoVersion:"go1.8.3", Compiler:"gc", Platform:"linux/amd64"}
Server Version: version.Info{Major:"", Minor:"", GitVersion:"v0.0.0-master+$Format:%h$", GitCommit:"db809c0eb7d33fac8f54d8735211f2f3a8fc4214", GitTreeState:"clean", BuildDate:"2017-09-11T19:46:47Z", GoVersion:"go1.8.3", Compiler:"gc", Platform:"linux/amd64"}
```
- OS (e.g. from /etc/os-release): 
```Debian GNU/Linux 9 (stretch)```
- Kernel (e.g. `uname -a`): 
```Linux aleinung 4.9.0-3-amd64 #1 SMP Debian 4.9.30-2+deb9u3 (2017-08-06) x86_64 GNU/Linux```

Implementation Context:

I have an initContainer that waits for a service running in `Kubernetes` to detect its existence via pod annotations, and send it an HTTP request, upon which it writes this value to disk. The main container then reads this value upon startup and "unwraps" it via another service, upon which it stores the unwrapped value in memory. 

The value that is written to disk by the initContainer is a one-time read value, in that once it is used the value is then expired. The problem is that if the main container ever restarts due to fatal error, it loses that unwrapped value and upon startup tries to unwrap the expired value again, leading to an infinite crashing loop until I manually delete the pod, upon which a new pod is created, the initContainer runs, and all is again well. 

I desire a feature that restarts the entire pod upon container error so that this workflow can function properly.



## Curated Answers



### High Signal Answer 1

@aisengard did you ever find a solution to this? We hit exactly the same issue today, we have an initContainer to read some secret data from vault and write it to an `emptyDir` volume which is shared between the `initContainer` and the first container in the pod. The first container reads this file when executing the command and then deletes it so no one can enter the pod and read the file; but if the container restarts the initContainer isn't run so the file doesn't exist

- Author: REBELinBLUE
- Quality score: 31
- URL: https://github.com/kubernetes/kubernetes/issues/52345#issuecomment-540154975

### High Signal Answer 2

Good catch, When use init container to acquire certificate or token, containers may remove it after read to cache. Then containers may re-run repeatedly after once panic.

- Author: hzxuzhonghu
- Quality score: 6
- URL: https://github.com/kubernetes/kubernetes/issues/52345#issuecomment-329040445

### High Signal Answer 3

/reopen

this is such unexpected behaviour as a long time k8s user. the proposed solution to add another value to `RestartPolicy` which forces all containers to restart seems reasonable - any thoughts from sig-node?

- Author: afirth
- Quality score: 4
- URL: https://github.com/kubernetes/kubernetes/issues/52345#issuecomment-1191187762
