# Cross-namespace Ingress



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #17088

- State: closed

- Labels: none

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/17088



## Problem



As far as I can tell right now it's only possible to create an ingress to address services inside the namespace in which the Ingress resides. It would be good to be able to address services in any namespace.

It's possible that I'm missing something and this is already possible - if so it'd be great if this was documented.



## Curated Answers



### High Signal Answer 1

I would tend to imagine the use case that @paralin described is common.  I'm looking at an ingress controller as a _system_ component and a means of reflecting _any_ service in the cluster to the outside world.  Running _one_ (perhaps even in the `kube-system` namespace) that can handle ingress for all services just seems to make a lot of sense.

- Author: krancour
- Quality score: 178
- URL: https://github.com/kubernetes/kubernetes/issues/17088#issuecomment-157926226

### High Signal Answer 2

There seems to be demand for cross namespace ingress x service resolution. We should at least reconsider.

- Author: bprashanth
- Quality score: 140
- URL: https://github.com/kubernetes/kubernetes/issues/17088#issuecomment-162258789

### High Signal Answer 3

@bprashanth I'm running multiple projects on a cluster - kubernetes tests, blog, API for a project. I want to address these as subdomains on my domain using a single ingress controller because load balancers and IP addresses are expensive on GCE.

- Author: paralin
- Quality score: 83
- URL: https://github.com/kubernetes/kubernetes/issues/17088#issuecomment-155918432
