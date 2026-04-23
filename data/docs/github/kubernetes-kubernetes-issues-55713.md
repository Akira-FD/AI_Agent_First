# Pods are not moved when Node in NotReady state



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #55713

- State: closed

- Labels: kind/bug, sig/scheduling, sig/node, lifecycle/frozen

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/55713



## Problem



<!-- This form is for bug reports and feature requests ONLY! 

If you're looking for help check [Stack Overflow](https://stackoverflow.com/questions/tagged/kubernetes) and the [troubleshooting guide](https://kubernetes.io/docs/tasks/debug-application-cluster/troubleshooting/).
-->

**Is this a BUG REPORT or FEATURE REQUEST?**:

> Uncomment only one, leave it on its own line: 
>
/kind bug


**What happened**:

To simulate a crashed worker node I stopped the kubelet service on that node (Debian Jessie).
The node got into unknow state (resp. NotReady) as expected:
```
NAME                STATUS     ROLES         AGE       VERSION
lls-lon-db-master   Ready      master,node   7d        v1.8.0+coreos.0
lls-lon-testing01   NotReady   node          6d        v1.8.0+coreos.0
```
The pods running on the lls-lon-testing01 stay declared as running:
```
test-core-services   infrastructure-service-deployment-5cb868f49-94gh4                 1/1       Running   0          4h        10.233.96.204   lls-lon-testing01
```
But is declared as ready: false on describe:
```
Name:           infrastructure-service-deployment-5cb868f49-94gh4
Namespace:      test-core-services
Node:           lls-lon-testing01/10.100.0.5
Start Time:     Tue, 14 Nov 2017 10:31:41 +0000
Labels:         app=infrastructure-service
                pod-template-hash=176424905
Annotations:    kubernetes.io/created-by={"kind":"SerializedReference","apiVersion":"v1","reference":{"kind":"ReplicaSet","namespace":"test-core-services","name":"infrastructure-service-deployment-5cb868f49","uid":"d...
Status:         Running
IP:             10.233.96.204
Created By:     ReplicaSet/infrastructure-service-deployment-5cb868f49
Controlled By:  ReplicaSet/infrastructure-service-deployment-5cb868f49
Containers:
  infrastructure-service:
    Container ID:  docker://3b750d7cad0c24386cade1e4fedac24ab2621f4991d3302d15c30d9e68749b7b
    Image:         index.docker.io/looplinesystems/infrastructure-service:latest
    Image ID:      docker-pullable://looplinesystems/infrastructure-service@sha256:632591a86ca67f3e19718727e717b07da3b5c79251ce9deede969588b6958272
    Ports:         7110/TCP, 7111/TCP, 7112/TCP
    Command:
      /infrastructurectl
      daemon
    State:          Running
      Started:      Tue, 14 Nov 2017 10:31:48 +0000
    Ready:          True
    Restart Count:  0
    Environment Variables from:
      infrastructure-service-config  Secret  Optional: false
    Environment:                     <none>
    Mounts:
      /var/log/services from logs (rw)
      /var/run/secrets/kubernetes.io/serviceaccount from default-token-hm2hs (ro)
Conditions:
  Type           Status
  Initialized    True 
  Ready          False 
  PodScheduled   True 
Volumes:
  logs:
    Type:  HostPath (bare host directory volume)
    Path:  /var/log/services
  default-token-hm2hs:
    Type:        Secret (a volume populated by a Secret)
    SecretName:  default-token-hm2hs
    Optional:    false
QoS Class:       BestEffort
Node-Selectors:  <none>
Tolerations:     <none>
Events:          <none>
```

**What you expected to happen**:
I excpected the pods on the "crashed" node to be moved to the remaining node.

**How to reproduce it (as minimally and precisely as possible)**:
In my situtation: Having a node (A)and a master+node (B) installed with Kubespray. Running at least one pod on each node. Stopping Kubelet on A and wait

**Anything else we need to know?**:

**Environment**:
- Kubernetes version (use `kubectl version`):
```
Client Version: version.Info{Major:"1", Minor:"8", GitVersion:"v1.8.0+coreos.0", GitCommit:"a65654ef5b593ac19fbfaf33b1a1873c0320353b", GitTreeState:"clean", BuildDate:"2017-09-29T21:51:03Z", GoVersion:"go1.8.3", Compiler:"gc", Platform:"linux/amd64"}
Server Version: version.Info{Major:"1", Minor:"8", GitVersion:"v1.8.0+coreos.0", GitCommit:"a65654ef5b593ac19fbfaf33b1a1873c0320353b", GitTreeState:"clean", BuildDate:"2017-09-29T21:51:03Z", GoVersion:"go1.8.3", Compiler:"gc", Platform:"linux/amd64"}
```
- Cloud provider or hardware configuration: 
```
Intel(R) Xeon(R) CPU E5-2670
4 Cores
4 GB RAM
```
- OS (e.g. from /etc/os-release): Debian GNU/Linux 8 (jessie)
- Kernel (e.g. `uname -a`): Linux lls-lon-db-master 3.16.0-4-amd64 #1 SMP Debian 3.16.43-2+deb8u5 (2017-09-19) x86_64 GNU/Linux
- Install tools: Kubespray
- Others: -



## Curated Answers



### High Signal Answer 1

Hi, I have the same problem. No pods are evicted if a node is "NotReady" even after `--pod-eviction-timeout` set on `kube-controller-manager`. Are there any workarounds?

- Author: huyqut
- Quality score: 30
- URL: https://github.com/kubernetes/kubernetes/issues/55713#issuecomment-423493018

### High Signal Answer 2

Surely this is one of the first failure modes everyone tests?  It's the first worker-related failure I tested while evaluating Kubernetes.  I even gracefully shutdown the worker node and let all kube processes exit cleanly.  IMO it very much violates the Principle of Least Astonishment that pods assigned to NotReady nodes remain in the Running state.

(1.13.3 with a single node test cluster.)

- Author: jtackaberry
- Quality score: 24
- URL: https://github.com/kubernetes/kubernetes/issues/55713#issuecomment-460004699

### High Signal Answer 3

I wrote a script, that can be run as a cronjob:
```
#!/bin/sh

KUBECTL="/usr/local/bin/kubectl"

# Get only nodes which are not drained yet
NOT_READY_NODES=$($KUBECTL get nodes | grep -P 'NotReady(?!,SchedulingDisabled)' | awk '{print $1}' | xargs echo)
# Get only nodes which are still drained
READY_NODES=$($KUBECTL get nodes | grep '\sReady,SchedulingDisabled' | awk '{print $1}' | xargs echo)

echo "Unready nodes that are undrained: $NOT_READY_NODES"
echo "Ready nodes: $READY_NODES"


for node in $NOT_READY_NODES; do
  echo "Node $node not drained yet, draining..."
  $KUBECTL drain --ignore-daemonsets --force $node
  echo "Done"
done;

for node in $READY_NODES; do
  echo "Node $node still drained, uncordoning..."
  $KUBECTL uncordon $node
  echo "Done"
done;
```
It is actually checking if a node is down and not drained and vice versa. Hope it helps

- Author: marczahn
- Quality score: 22
- URL: https://github.com/kubernetes/kubernetes/issues/55713#issuecomment-358632214
