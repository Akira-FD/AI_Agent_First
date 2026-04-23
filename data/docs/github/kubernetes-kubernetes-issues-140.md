# PreStart and PostStop event hooks



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #140

- State: closed

- Labels: area/docker, area/kubelet, priority/awaiting-more-evidence, sig/node, kind/feature, lifecycle/frozen

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/140



## Problem



Many systems support event hooks for extensions. A few examples:
https://developers.google.com/appengine/docs/java/javadoc/com/google/appengine/api/LifecycleManager
http://developer.android.com/guide/components/activities.html
http://upstart.ubuntu.com/cookbook/#event
https://coreos.com/docs/launching-containers/launching/getting-started-with-systemd/
http://elasticbox.com/documentation/configuring-and-managing-boxes/start-stop-and-upgrade-boxes/
http://git-scm.com/docs/githooks.html

docker stop and restart currently send SIGTERM followed by SIGKILL, similar to many other systems (e.g., Heroku: https://devcenter.heroku.com/articles/dynos#graceful-shutdown-with-sigterm), which provides an opportunity for applications to cleanly shut down, but lacks the ability to communicate the grace period duration or termination reason and doesn't directly provide support for notifying other processes or services.

As described in the (liveness probe issue)[https://github.com/GoogleCloudPlatform/kubernetes/issues/66], it would be useful to support multiple types of hook execution/notification mechanisms. It would also be useful to pass arguments from clients, such as "reason" (e.g., "cancel", "restart", "reload", "resize", "reboot", "move", "host_update", "probe_failure"). Another way "reason" could be handled is with user-defined events.

In addition to pre-termination notification, we should define other lifecycle hook points, probably at least pre- and post- start and terminate. 

It would be useful for post-terminate to be passed the (termination reason)[https://github.com/GoogleCloudPlatform/kubernetes/issues/137], which could either be successful completion, a client-provided stop reason (see above), or detailed failure reason (exit, signal, OOM, container creation error, docker crash, machine crash, lost/ghost). 

If the application generated an assertion failure or exception message, a post-termination hook could copy it to (/run/status.txt)[https://github.com/GoogleCloudPlatform/kubernetes/issues/139].

It would also be useful to be able to control (restart behavior)[https://github.com/GoogleCloudPlatform/kubernetes/issues/127] from a hook. We'd need a convenient way to carry over state from a previous execution. The simplest starting point would be for the user to keep it in a (volume)[https://github.com/GoogleCloudPlatform/kubernetes/issues/97].



## Curated Answers



### High Signal Answer 1

@bgrant0607 This issue is open since long is it ok if we close this?

- Author: n4j
- Quality score: 4
- URL: https://github.com/kubernetes/kubernetes/issues/140#issuecomment-867307769
