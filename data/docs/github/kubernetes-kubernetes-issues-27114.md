# LivenessProbe should start after ReadinessProbe Succeeded if ReadinessProbe is specified



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #27114

- State: closed

- Labels: area/api, sig/node

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/27114



## Problem



Our initial understanding is that liveness probe will start to check after readiness probe was succeeded but it turn out not to be like that.

We are testing with our system that has a long boot time, an approximation of boot time is between 1-3 minutes. We specify readiness probe with same url of liveness probe and specify initial delay of liveness probe to be 30 seconds, we found that the pod is killed by failing of liveness probe while readiness probe still in a failure.

So, why don't we specify initial delay of liveness probe to be more than 3 minutes? Well, it might be a case when readiness probe succeed at first minute and after that the pod will fail to do a job before liveness probe will start. So, it will affect running service.

Another point is why we don't only put readiness probe and leave out liveness probe? When readiness probe fail again it might take out of service as well so, it don't cause any affect for running service but it won't be restarted and we have to do manual restart them.

There are some concerns we thought about, here are list:
- What if readiness probe never succeed while starting a pod, can we specify a maximum number of check will be performed and if readiness probe fail more than that number, we may consider that pod should be killed.
- What if someone want to set readiness probe to put the pod in maintenance mode, the pod might be killed by above point if readiness probe fail more than that number or liveness probe will kill it. Maybe, we add one more state of readiness probe called `Maintenance` so that liveness probe should stop working when enter this state and no number of failing readiness probe should not be considered.

What do you think?



## Curated Answers



### High Signal Answer 1

I see this is still not implemented. This would really be much appreciated and I think its a pretty logical way to think about it:

[`readinessProbe`] Is it ready? **No**
-> Okay lets wait a bit and see [still `readinessProbe`]

_Eventually..._
[`readinessProbe`] Is it ready? **Yes**
-> Okay we can serve traffic and run checks to see if it remains alive [`livenessProbe`]

Having liveness probe kill off the pod before it's ready is frustrating and counter-intuitive. As mentioned, that should be handled completely in the readiness probe - with a set limit on time to ready / check iterations. As it stands now I have to create some rough estimates about how long I should delay my liveness probe - which is not always an easy constant to track.

- Author: lostpebble
- Quality score: 79
- URL: https://github.com/kubernetes/kubernetes/issues/27114#issuecomment-293846153

### High Signal Answer 2

Understandably, this will cause unexpected behaviour because of the way people have bent their liveness probes around this at the moment.

I suggest an extra variable on `livenessProbe` perhaps? Something like `waitForReadinessProbe`.

And maybe a warning somewhere that on future versions (however far down the line) liveness probes will wait by default. Or just stick with the extra `waitForReadinessProbe` indefinitely... (it just seems like it should be default behaviour)

- Author: lostpebble
- Quality score: 73
- URL: https://github.com/kubernetes/kubernetes/issues/27114#issuecomment-294149744

### High Signal Answer 3

I  totally like this idea, my general understanding of a `livenessProbe` was that it is only run on ready containers - I was surprised to find out that this is not the case. (Actually found that out the same way as @tanapoln - when running a container with long boot time for the first time.)

I vote for making `waitForReadinessProbe` the default, as it makes so much more sense.

- Author: tobilarscheid
- Quality score: 47
- URL: https://github.com/kubernetes/kubernetes/issues/27114#issuecomment-300403981
