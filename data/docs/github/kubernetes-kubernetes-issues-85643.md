# Create ability to do zero downtime deployments when using externalTrafficPolicy: Local



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #85643

- State: closed

- Labels: kind/bug, sig/network, area/provider/gcp, kind/feature, sig/cloud-provider

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/85643



## Problem



I am using externalTrafficPolicy set to Local for my a LoadBalancer service for an ingress controller on GKE.

Right now, when a pod gets terminated, it is immediately removed from the NodePort service, which stops traffic from routing to the pod (step 5 at https://kubernetes.io/docs/concepts/workloads/pods/pod/#termination-of-pods). 

The problem is that the GCP Load Balancer doesn't update itself immediately, so it continues to send traffic to the NodePort even though Kubernetes has already removed the pod from the NodePort as part of the termination process. This results in timeouts and an inability to do zero downtime deployments when a node no longer has an active application residing on it when externalTrafficPolicy is set to Local.

I'd like to see an option where we can use Local, but allow for zero-downtime deployments. 

I'm wondering if there could be a configurable option to wait until a preStop hook has finished (or grace period hits) before removing the pod from the NodePort service? With something like this, we could make a preStop hook that can make health checks fail but have the pod continue to serve traffic normally. The preStop hook could then sleep for a certain amount of time while the load balancers gracefully stop sending traffic because the health checks start to fail. Once the preStop hook completes, then it removes the pod from the NodePort. This would allow for graceful draining of outgoing pods.

Or maybe the answer is a pre-PreStop hook that can run before termination officially begins?



## Curated Answers



### High Signal Answer 1

FYI alpha feature to fix this issue was merged for v1.22 (https://github.com/kubernetes/kubernetes/pull/97238), I would appreciate if anyone can try it out and test it. The feature gate is called ProxyTerminatingEndpoints and you're only required to enable it on kube-proxy.

- Author: andrewsykim
- Quality score: 8
- URL: https://github.com/kubernetes/kubernetes/issues/85643#issuecomment-928196372

### High Signal Answer 2

I think I and many people are suffering similar problem (LB keep send traffics to deleted pods) although it is `type: ClusterIP` and ALB `target-type: ip`.

@andrewsykim Would your PR solve following similar issues even it is not `externalTrafficPolicy: Local`?
kubernetes/kubernetes
* Pods receive traffic from load balancer whilst in terminating state for >60s #96858
* Pod lifecycle, termination can be improved around LBs and grace period #89263
* Pods in `Terminating` status receive incoming requests #88236
* Connection refused during rolling upgrade of deployment #86280
* Document recommended way to not fail requests during rolling update #20473
* and more ...
kubernetes-sigs/aws-load-balancer-controller
* 400/502/504 errors while doing rollout restart or rolling update https://github.com/kubernetes-sigs/aws-load-balancer-controller/issues/1065
* ALB sending requests to pods after ingress controller deregisters them leading to 504s https://github.com/kubernetes-sigs/aws-load-balancer-controller/issues/1064
* 502/503 During deploys and/or pod termination https://github.com/kubernetes-sigs/aws-load-balancer-controller/issues/814
* and more ...

*edit*: I've made this package to solve the problem that I've explained: https://github.com/foriequal0/pod-graceful-drain
It works for only with `aws-load-balancer-controller` and `target-type:ip` Service for now, but I'm willing to support other loadbalancers.

- Author: foriequal0
- Quality score: 7
- URL: https://github.com/kubernetes/kubernetes/issues/85643#issuecomment-763408752

### High Signal Answer 3

This is a problem with 2-hop load-balancing - the end-of-life handling of pods doesn't really have a way to describe "upstream" dependencies and sequencing.  The endpoints controller sees the pod as terminating and immediately removes it from the set.  Kube-proxy has no choice but to also remove it from the list of available backends.  As you described, the upstream LB hasn't received the news yet.

For HTTP apps, If you use Ingress and VPC-Native LB (on GCP) you will bypass this second hop (kube-proxy) and the LB goes directly to the pod.  During the terminationGracePeriod, the pod will be removed from the LB.

For apps that use Service, this remains a problem.  I'd like this to be possible.  It probably needs a KEP to cover the details, but maybe something like:

* Instead of removing a terminating endpoint, move it to NotReadyAddresses
* In kube-proxy, if a service has no viable ready endpoints, but has not-ready addresses, use those

For "local" services that would still use the terminating endpoint.  Presumably, upstream LBs would be deconfigured and incoming traffic would taper off.

That doesn't seem egregiously complicated to me, but I bet there are corner cases.  Here's one - NotReady covers both startup and teardown.  Would we want LBs to go to not-yet-initialized backends at the beginning of life?  It seems wrong but not terribly so.  Here's another - it will add a lot of endpoints writes as we have to process both states.

@freehan @robscott

- Author: thockin
- Quality score: 5
- URL: https://github.com/kubernetes/kubernetes/issues/85643#issuecomment-601415454
