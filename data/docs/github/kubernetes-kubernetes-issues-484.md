# Service scale-to-zero (fka "Socket activation")



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #484

- State: closed

- Labels: sig/network, priority/awaiting-more-evidence, sig/node, kind/feature, lifecycle/rotten

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/484



## Problem



I want to start this issue to drum up support for adding socket activation support to Kubernetes. My CTO at the last place I worked at, @davidstrauss, invented this technique.

Normally for a service to be available, its daemon has to be running and listening on a socket. With socket activation, another service, generally SystemD, listens for all incoming traffic and on an incoming request, passes the request to its service, waking it if necessary.

By idling inactive containers, there can be significant savings on memory. At Pantheon which hosts Drupal and Wordpress sites, at any time some ~80-90% of containers are idled waiting for traffic. This means they can proportionally increase the density of containers resulting in significant operations and server cost savings.

This is of course not a technique for everyone. You need to have services which won't get any use for significant periods of time and you can accept a few second delay from the initial waking time. But for many people, especially those running multi-tenant architectures, this would be a very valuable feature if baked in and easy to use and help Kubernetes be even more elastic.

Some more information on socket activation:
- http://0pointer.de/blog/projects/socket-activated-containers.html
- http://www.slideshare.net/warpforge/php-at-density-and-scale



## Curated Answers



### High Signal Answer 1

any progress?

would really be great to socket activate pods to use them for webhooks/serverless services.

- Author: Zetanova
- Quality score: 11
- URL: https://github.com/kubernetes/kubernetes/issues/484#issuecomment-620762699
