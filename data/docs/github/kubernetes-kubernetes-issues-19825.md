# Container Termination Discrepancy  for Exit Code 137



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #19825

- State: closed

- Labels: sig/node, lifecycle/rotten

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/19825



## Problem



In the documentation [here](http://kubernetes.io/v1.1/docs/user-guide/compute-resources.html#my-container-is-terminated)  it shows a pod using too much memory and is promptly killed.
When this happens it shows the error reason as "OOM"  and error code as 137 in the docs. When I go through similar steps myself, the termination reason is just "Error", though I do still get the 137 error code. Is there a reason this was changed?
OOM is very clear on what happened while "Error" can send people down a wild chase trying to
figure out what happened to their pod - hence me filing this issue.

For reference the script ran in my docker image just eats memory until it the container gets killed.

```
$kubectl version
Client Version: version.Info{Major:"1", Minor:"1", GitVersion:"v1.1.1", GitCommit:"92635e23dfafb2ddc828c8ac6c03c7a7205a84d8", GitTreeState:"clean"}
Server Version: version.Info{Major:"1", Minor:"1", GitVersion:"v1.1.3", GitCommit:"6a81b50c7e97bbe0ade075de55ab4fa34f049dc2", GitTreeState:"clean"}
```

```
$ kubectl get pod -o json  memtest
{
    "kind": "Pod",
    "apiVersion": "v1",
    "metadata": {
        "name": "memtest",
        "namespace": "default",
        "selfLink": "/api/v1/namespaces/default/pods/memtest",
        "uid": "c480d1ba-bec2-11e5-ad45-062d2421a4bd",
        "resourceVersion": "21949421",
        "creationTimestamp": "2016-01-19T15:39:03Z"
    },
    "spec": {
        "containers": [
            {
                "name": "memtest",
                "image": "nyxcharon/docker-stress:latest",
                "args": [
                    "python",
                    "/scripts/mem-fill"
                ],
                "resources": {
                    "limits": {
                        "memory": "10M"
                    },
                    "requests": {
                        "memory": "10M"
                    }
                },
                "terminationMessagePath": "/dev/termination-log",
                "imagePullPolicy": "Always"
            }
        ],
        "restartPolicy": "Never",
        "terminationGracePeriodSeconds": 30,
        "dnsPolicy": "ClusterFirst",
        "nodeName": "<IP removed>"
    },
    "status": {
        "phase": "Failed",
        "conditions": [
            {
                "type": "Ready",
                "status": "False",
                "lastProbeTime": null,
                "lastTransitionTime": null
            }
        ],
        "hostIP": "<IP Removed>",
        "startTime": "2016-01-19T15:39:03Z",
        "containerStatuses": [
            {
                "name": "memtest",
                "state": {
                    "terminated": {
                        "exitCode": 137,
                        "reason": "Error",
                        "startedAt": "2016-01-19T15:39:15Z",
                        "finishedAt": "2016-01-19T15:39:16Z",
                        "containerID": "docker://3dd77f77dfd6e715c8792c625f388e0b31cbd36ccdb4a11dafbb6d381bf83943"
                    }
                },
                "lastState": {},
                "ready": false,
                "restartCount": 0,
                "image": "nyxcharon/docker-stress:latest",
                "imageID": "docker://bacbb71b34e92ed2074621d86b10ec15a856f5918537c4d75b6f16925b5b93e7",
                "containerID": "docker://3dd77f77dfd6e715c8792c625f388e0b31cbd36ccdb4a11dafbb6d381bf83943"
            }
        ]
    }
}
```

```
$ kubectl describe pod memtest
Name:               memtest
Namespace:          default
Image(s):           nyxcharon/docker-stress:latest
Node:               <IP removed>
Start Time:         Tue, 19 Jan 2016 10:39:03 -0500
Labels:             <none>
Status:             Failed
Reason:
Message:
IP:
Replication Controllers:    <none>
Containers:
  memtest:
    Container ID:   docker://3dd77f77dfd6e715c8792c625f388e0b31cbd36ccdb4a11dafbb6d381bf83943
    Image:      nyxcharon/docker-stress:latest
    Image ID:       docker://bacbb71b34e92ed2074621d86b10ec15a856f5918537c4d75b6f16925b5b93e7
    QoS Tier:
      memory:   Guaranteed
    Limits:
      memory:   10M
    Requests:
      memory:       10M
    State:      Terminated
      Reason:       Error
      Exit Code:    137
      Started:      Tue, 19 Jan 2016 10:39:15 -0500
      Finished:     Tue, 19 Jan 2016 10:39:16 -0500
    Ready:      False
    Restart Count:  0
    Environment Variables:
Conditions:
  Type      Status
  Ready     False
No volumes.
Events:
  FirstSeen LastSeen    Count   From                    SubobjectPath               Reason  Message
  ─────────   ────────    ───── ────                    ─────────────             ──────  ───────
  2m        2m      1   {kubelet <IP removed>}  implicitly required container POD   Pulled  Container image "gcr.io/google_containers/pause:0.8.0" already present on machine
  2m        2m      1   {scheduler }                                    Scheduled   Successfully assigned memtest to <IP removed>
  2m        2m      1   {kubelet <IP removed>}  implicitly required container POD   CreatedCreated with docker id 65a446677edd
  2m        2m      1   {kubelet <IP removed>}  spec.containers{memtest}        PullingPulling image "nyxcharon/docker-stress:latest"
  2m        2m      1   {kubelet <IP removed>}  implicitly required container POD   StartedStarted with docker id 65a446677edd
  2m        2m      1   {kubelet <IP removed>}  spec.containers{memtest}        Pulled  Successfully pulled image "nyxcharon/docker-stress:latest"
  2m        2m      1   {kubelet <IP removed>}  spec.containers{memtest}        CreatedCreated with docker id 3dd77f77dfd6
  2m        2m      1   {kubelet <IP removed>}  spec.containers{memtest}        StartedStarted with docker id 3dd77f77dfd6
  2m        2m      1   {kubelet <IP removed>}  implicitly required container POD   KillingKilling with docker id 65a446677edd
```

Here is the pod definition i'm using:

```
kind: Pod
apiVersion: v1
metadata:
  name: memtest
spec:
  containers:
  - name: memtest
    image: nyxcharon/docker-stress:latest
    args:
    - python
    - /scripts/mem-fill
    resources:
      limits:
        memory: 10M
  restartPolicy: Never
```



## Curated Answers



### High Signal Answer 1

Hey guys,
Sorry to bump this up after 2 years, but still the same problem here.
I am getting a `137` error code while there is no OOM issue. And yes it's because of the liveness probe not being successful. I am not even sure that this `137` should be even reserved for OOM. So my suggestion would be more about having a specific exitCode when the liveness probe is failed and the pod is running?

- Author: bakayolo
- Quality score: 15
- URL: https://github.com/kubernetes/kubernetes/issues/19825#issuecomment-616407535

### High Signal Answer 2

I suspect its because of liveliness probe failing, but not sure why it should exit with code 137 which is for OOM.

- Author: parthakom
- Quality score: 11
- URL: https://github.com/kubernetes/kubernetes/issues/19825#issuecomment-393030265

### High Signal Answer 3

I am also seeing one weird behaviour where container is using 40% the memory of the request, and it is getting restarted throwing 137 exit code. There is no logs for oom or liveliness check failures as it is set pretty high but container is getting kill repeatedly throwing 137 code. Also application in itself is not throwing any error, etc so I am guessing something from k8s is killing the pod. 

Any clue anyone on what might be going wrong.

- Author: rtudo
- Quality score: 8
- URL: https://github.com/kubernetes/kubernetes/issues/19825#issuecomment-734842639
