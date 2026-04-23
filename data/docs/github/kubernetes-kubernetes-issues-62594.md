# Liveness/Readiness probes are failing with getsockopt: connection refused



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #62594

- State: closed

- Labels: kind/bug, sig/network, triage/unresolved

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/62594



## Problem



**Is this a BUG REPORT or FEATURE REQUEST?**:

 /kind bug

**What happened**: Liveness/Readiness probes are failing so frequently and the failures are also inconsistent. Some of the pods in the same deployment are getting stuck in the crashLoopBackOff

```
Back-off restarting failed container
Error syncing pod, skipping: failed to "StartContainer" for "web" with CrashLoopBackOff: "Back-off 5m0s restarting failed container=web pod=web-controller-3987916996-qtfg7_micro-services(a913f25b-400a-11e8-8a2a-0252b8c4655e)"
Liveness probe failed: Get http://100.96.11.194:5000/: dial tcp 100.96.11.194:5000: getsockopt: connection refused
Failed to start container with id 0d47047e3e7a640ad6b4a6a8664bdb01a3601c95518c9e60bdb4966533fe7e6d with error: rpc error: code = 2 desc = failed to create symbolic link "/var/log/pods/a913f25b-400a-11e8-8a2a-0252b8c4655e/web_23.log" to the container log file "/var/lib/docker/containers/0d47047e3e7a640ad6b4a6a8664bdb01a3601c95518c9e60bdb4966533fe7e6d/0d47047e3e7a640ad6b4a6a8664bdb01a3601c95518c9e60bdb4966533fe7e6d-json.log" for container "0d47047e3e7a640ad6b4a6a8664bdb01a3601c95518c9e60bdb4966533fe7e6d": symlink /var/lib/docker/containers/0d47047e3e7a640ad6b4a6a8664bdb01a3601c95518c9e60bdb4966533fe7e6d/0d47047e3e7a640ad6b4a6a8664bdb01a3601c95518c9e60bdb4966533fe7e6d-json.log /var/log/pods/a913f25b-400a-11e8-8a2a-0252b8c4655e/web_23.log: file exists
```

And few more errors from other pods!
```
Error syncing pod, skipping: failed to "CreatePodSandbox" for "work-1132229878-zk00f_micro-services(897dd216-41f4-11e8-8a2a-0252b8c4655e)" 
with CreatePodSandboxError: "CreatePodSandbox for pod \"work-1132229878-zk00f_micro-services(897dd216-41f4-11e8-8a2a-0252b8c4655e)\" 
failed: rpc error: code = 2 desc = NetworkPlugin kubenet failed to set up pod \"work-1132229878-zk00f_micro-services\" 
network: Error adding container to network: failed to connect \"vethdaa54c24\" to bridge cbr0: exchange full"
```

Here is how my livenessProbe config
```
        "livenessProbe": {
          "httpGet": {
            "path": "/",
            "port": 5000,
            "scheme": "HTTP"
          },
          "initialDelaySeconds": 60,
          "timeoutSeconds": 10,
          "periodSeconds": 10,
          "successThreshold": 1,
          "failureThreshold": 3
        }
```
**What you expected to happen**:
Health checks to pass if the app is running. 

**How to reproduce it (as minimally and precisely as possible)**:

**Anything else we need to know?**:
Its a NodeJS app and its listening on port 5000 and its also exposed in dockerfile.

**Environment**:
- Kubernetes version (use `kubectl version`):
```
Client Version: version.Info{Major:"1", Minor:"8", GitVersion:"v1.8.3", GitCommit:"f0efb3cb883751c5ffdbe6d515f3cb4fbe7b7acd", GitTreeState:"clean", BuildDate:"2017-11-09T07:26:38Z", GoVersion:"go1.9.2", Compiler:"gc", Platform:"darwin/amd64"}
Server Version: version.Info{Major:"1", Minor:"6", GitVersion:"v1.6.7", GitCommit:"095136c3078ccf887b9034b7ce598a0a1faff769", GitTreeState:"clean", BuildDate:"2017-07-05T16:40:42Z", GoVersion:"go1.7.6", Compiler:"gc", Platform:"linux/amd64"}
```

- Cloud provider or hardware configuration: AWS
- OS (e.g. from /etc/os-release): Ubuntu 16.04 LTS
- Kernel (e.g. `uname -a`): 
```
Linux ip-172-20-54-255 4.4.78-k8s #1 SMP Fri Jul 28 01:28:39 UTC 2017 x86_64 GNU/Linux
```
- Install tools: `kops`
- Others:



## Curated Answers



### High Signal Answer 1

Hello all. We were experiencing this issue as well. 

Using:
```
kubectl describe pod <pod-name>
```

We also found that the Exit code was:137 and the Reason: 'Error'. 
This is the error code for both Liveness failure and Memory issues but we were fairly certain it was not due to Memory issues as we had more than enough Memory allocated and when we find error issues kill the pod we get the correct reason 'OOMKilled'.

Anyway, We found that the issue occurred when we attempted to statically apply 250m per pod CPU in  Lower Environments so to be Resource Efficient. 

We run Spring Boot Applications which have a real heavy boot period. Because of this, the 0.25 cores we applied could not boot the App in time to start running the server and pass the health checks. And, we ultimately passed our Failure deadline before the Service was Ready.

I suggest that anyone seeing this issue either could maybe solve their problems by doing 1 of 2 things:

1) **Meet the Race Condition**
Allocate Higher Quantities of CPU to your Deployments so that the boot process is faster and the pod will be up in time for Liveness and Readiness checks.

2) **Change the Race Condition**
Set a longer Initial wait time on the Live and Readiness probe and, extend the failure deadline and the test interval . This should give you plenty of time for your Service to boot up and become Ready. 

e.g
```
    readinessProbe:
      httpGet:
        scheme: http
        path: /health
        port: 8080
      initialDelaySeconds: 120
      timeoutSeconds: 3
      periodSeconds: 30
      successThreshold: 1
      failureThreshold: 5


    livenessProbe:
      httpGet:
        scheme: http
        path: /health
        port: 8080
      initialDelaySeconds: 120
      timeoutSeconds: 3
      periodSeconds: 30
      successThreshold: 1
      failureThreshold: 5
```

Obviously there could be other reasons for the probe failing and ending up with this type of Error but this is what solved it for us. 

Hope this can help.

- Author: njgibbon
- Quality score: 41
- URL: https://github.com/kubernetes/kubernetes/issues/62594#issuecomment-420685737

### High Signal Answer 2

My case was solved by changing the binding from 127.0.0.1 to 0.0.0.0.

- Author: terry90
- Quality score: 12
- URL: https://github.com/kubernetes/kubernetes/issues/62594#issuecomment-397797071

### High Signal Answer 3

Same issue here. I can get the service running continuously by disabling the readiness probe. This indicated that it's the probe failure and the subsequent shutting down that caused the connection refusal instead of the other way around. 

Things I have tried that doesn't work:
- Increasing probe timeout
- Fiddling with ports, `containerPort`, `targetPort`

- Author: voidcenter
- Quality score: 7
- URL: https://github.com/kubernetes/kubernetes/issues/62594#issuecomment-431101218
