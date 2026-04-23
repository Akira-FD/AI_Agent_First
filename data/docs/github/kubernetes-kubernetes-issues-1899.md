# Allow users to wait for conditions from kubectl and using the API



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #1899

- State: closed

- Labels: priority/important-soon, area/usability, area/kubectl, sig/api-machinery, sig/cli, lifecycle/frozen

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/1899



## Problem



Spawned from #1325 

It should be easy for users do two things:
- Create new resources
- Determine when they are "ready"

Readiness (#620) is a complex topic, and readiness can mean different things in different contexts.  The Kubernetes client CLI and client library (see `pkg/client/conditions.go`) should provide tools for common readiness conditions and enable developers and administrators to easily script more complex readiness.  This issue _only_ covers client side readiness - server side readiness should be handled elsewhere.

Readiness must have an explicit upper bound (the system may never converge) - probably manifested as a maximum timeout.  Certain errors may be transient (network, server) and some fatal (resource deleted?).  It should be possible for end users to understand the ways that readiness can fail and work through those conditions.

Most resources are likely to have an implicit "ready" state:
- pods - when the state is "Running", "Succeeded", or "Failed", depending on the restart policy
- replicationControllers - when there are enough pods in running state to satisfy the label query
- services - when at least one pod is running and reachable via the service?

However, readiness can vary in infinitely complex ways
- services - user must wait for 2 pods to be running for HA, or pods must be running in X zones
- two services must be running and serving requests (web frontend and database tier) AND the backend database must have its schema created and at the latest version

It should be possible for users to define their own client ready conditions via scripting (potentially outside of kubectl), as long as the tools kubectl provide a common layer for behavior.

Possible CLI examples:

```
$ kubectl create -c foo.json --wait
$ kubectl create -c foo.json --wait=1m
$ kubectl get pod my-pod --wait --wait-for="pod-running"
$ kubectl get pod my-pod --wait --wait-for --format-template='{{ if .Status.Condition == "Running" }}1{{ else }}0{{ end }}'
```

Things I'd like to avoid end users doing:
- Bash `for | grep` loops on output as much as possible
- Implementing bash timeout logic
- Describing common yet complex conditions (replication controller at desired state) in template logic



## Curated Answers



### High Signal Answer 1

I wonder if this can be broken out into its own command instead of building it into create, get, etc. It may not be _quite_ as convenient but I think the wins in simplifying the kubectl interface, the implementation, and providing more cohesive building blocks for people's scripts may be worth it.

```
kubectl wait <condition> [<param1> <param2> ...]
```

```
$ kubectl wait pod-running my-pod
$ kubectl wait pod-running @my-pod-id
$ kubectl create -c foo.json | kubectl wait pod-running -  # accept from pod name/ID from stdin
$ kubectl wait pod-template my-pod --format-template='{{ if .Status.Condition == "Running" }}1{{ else }}0{{ end }}'
```

Maybe you could also define custom <condition>s in plugins or config files. WDYT?

- Author: ghodss
- Quality score: 17
- URL: https://github.com/kubernetes/kubernetes/issues/1899#issuecomment-60032014
