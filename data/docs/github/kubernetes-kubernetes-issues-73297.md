# Support TLS termination with AWS NLB



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #73297

- State: closed

- Labels: kind/feature

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/73297



## Problem



<!-- Please only use this template for submitting enhancement requests -->

**What would you like to be added**:

AWS has announced TLS termination for network load balancers: https://aws.amazon.com/blogs/aws/new-tls-termination-for-network-load-balancers/

It would be amazing if Kuberentes could support this! The annotations are all defined, we would need to hook up the cloud provisioner.

```yaml
service.beta.kubernetes.io/aws-load-balancer-type: nlb
service.beta.kubernetes.io/aws-load-balancer-ssl-cert: `arn:...`
```

**Why is this needed**:

ACM can only be used with AWS Load balancers, so supporting TLS with NLBs means we will be able to leverage ACM and support http2 and WebSockets without using alb-ingress. This would resolve my need for ALBs in Kubernetes: https://github.com/kubernetes/kubernetes/issues/30518. For example it would make running nginx-ingress with http2 and WebSocket support possible with ACM.



## Curated Answers



### High Signal Answer 1

In addition to certificate ARN on the listener, we need ssl security policy.  Also TLS protocol should be applied to the target group. Without this last part, [API GW (using PrivateLink)](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/vpc-endpoints.html) will throw errors.

Perhaps a more complete implementation would look like this:

```yaml
apiVersion: v1
kind: Service
metadata:
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: nlb
    service.beta.kubernetes.io/aws-load-balancer-cross-zone-load-balancing-enabled: "true"
    service.beta.kubernetes.io/aws-load-balancer-ssl-cert: arn: ...
    service.beta.kubernetes.io/aws-load-balancer-ssl-negotiation-policy: ELBSecurityPolicy-TLS-1-1-2017-01
    service.beta.kubernetes.io/aws-load-balancer-backend-protocol: TLS
    service.beta.kubernetes.io/aws-load-balancer-ssl-ports: "443"
```

- Author: davidxjohnson
- Quality score: 25
- URL: https://github.com/kubernetes/kubernetes/issues/73297#issuecomment-464391502

### High Signal Answer 2

will provide support for this in early next week

- Author: M00nF1sh
- Quality score: 22
- URL: https://github.com/kubernetes/kubernetes/issues/73297#issuecomment-468756436

### High Signal Answer 3

Hi, sorry for late update, I will push some ppl to get this merged :D

- Author: M00nF1sh
- Quality score: 11
- URL: https://github.com/kubernetes/kubernetes/issues/73297#issuecomment-480431601
