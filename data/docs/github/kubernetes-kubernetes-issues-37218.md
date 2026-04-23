# Multiple liveness checks (feature request)



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #37218

- State: closed

- Labels: sig/node, sig/instrumentation

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/37218



## Problem



# Statement of issue

I have an application that listens on multiple ports, say 1234 and 4321. I would like to have a liveness check (and readiness check) that tests that the application is listening on both ports, and terminate it if it is not.

I know of a number of ways to do this.

- I can change the application code so that any failure leads to termination. Unfortunately, some of this application code is third party, so it's hard for me to change.

- I can just execute a script that checks all the ports. That requires that I install the script or tool in question on the container. For now, it is probably what I will have to do.

- Alternatively, I could create a probe container in the same pod that just runs a script to verify that the "real" container is listening, and terminates with an error if it does not. However, that doesn't really work, because Kubernetes restarts my probe container rather than the entire pod (and I don't think I can change this behaviour).

# Possible resolutions

I can see three possible resolutions, given in my personal order of preference.

1. Allow configuration of multiple liveness checks to be run in parallel.
2. Extend the pod spec to have a "recreate entire pod on error" option (not just options about how to restart containers), allowing use of a probe container.
3. Allow multiple ports in a TCP connection probe.

# Workaround

As a workaround, I can create a tool or script and install it on the container I want to check. That means messing about with third party images, but is plausible, and so is what I am doing for now.

# Environment

I'm running Kubernetes 1.4.3 in GKE, but I believe this applies to all versions and environments.

I am using deployments rather than replication controllers; some of the above might be implemented as extensions to the deployment or replica set configuration rather than the pod spec.



## Curated Answers



### High Signal Answer 1

Let's assume for a minute that we had nothing more significantly on fire
than this (which is NOT the case, but let's pretend)...

First, keep in mind that we have to do this 2 times - liveness and
readiness.  No, wait 3 times, because we just added startup probes.

First convert the internal field to a plural and write the conversion from
external to internal, update all the tests, validation, etc.

Now add a feature gate, because something like this has to get testing.

Add a new external field in the plural.   Write all the custom conversions
for it to handle full backwards compatibility -- remember no breaking
changes allowed!

Now spec how many are allowed - 4?  16?  64?

Now define the semantics of exactly what happens in all the corner cases -
what happens if #2 fails just as #1 starts passing - is that considered a
sustained failure?  All the API is around each probe failing for some
number of tries, so you can oscillate back-and-forth between failures and
never consider it an actual failure -- is that what we intended?  10 bucks
someone asks immediately for a global failure threshold.

Now go implement it in kubelet.  That's more state to carry around but far
from impossible.  The test cases though, uggh, my brain hurts just thinking
about it.

So, is it unreachable?  No, it's just code.  We know HOW to do it, but a) I
have 2100 open issues at the moment and over 1000 open pull requests and b)
there's a budget for complexity in any system, and we're not so flush any
more.  We have to think hard about where we spend our complexity budget.
Is this the best ROI we can get?

Consider the alternative - someone write an HTTP healthz multiplexer.  It
serves on a port (flag).  It takes a list of arguments - localhost:80,
localhost:12345, localhost:8675 - and returns 200 IFF all of the arguments
return 200.  That's like a 50 line go program, honestly.  You run that as a
sidecar in all of your pods, and use that as your probe.  Kubernetes grew 0
LOCs and you got what you wanted without that many corner cases.

I don't mean to be rude -- I love implementing cool features, but this
seems like a PERFECT use of composition.  So here's my challenge - go write
that HTTP multiplexer app.  I bet you can think of 20 features for it to
make it even more useful.  Put it up on github and I'll tweet about it.
Win-win.



On Thu, May 30, 2019 at 12:47 PM Guilherme Garnier <notifications@github.com>
wrote:

> You'd still have to handle both cases, for compatibility, only in two
> different properties. And also handle the case for both livenessProbe and
> livenessProbes defined.
>
> —
> You are receiving this because you modified the open/close state.
> Reply to this email directly, view it on GitHub
> <https://github.com/kubernetes/kubernetes/issues/37218?email_source=notifications&email_token=ABKWAVHZQCOLE6MWTMYKHZDPYAVLJA5CNFSM4CXA6QY2YY3PNVWWK3TUL52HS4DFVREXG43VMVBW63LNMVXHJKTDN5WW2ZLOORPWSZGODWTKIYI#issuecomment-497460321>,
> or mute the thread
> <https://github.com/notifications/unsubscribe-auth/ABKWAVG356YPUZCO5ZAJ2YLPYAVLJANCNFSM4CXA6QYQ>
> .
>

- Author: thockin
- Quality score: 48
- URL: https://github.com/kubernetes/kubernetes/issues/37218#issuecomment-498518291

### High Signal Answer 2

As a workaround we incorporate the GET request in the command. 
For example this 

```
livenessProbe: {
     httpGet: {
         path: "/ping",
         port: 9099
     },
     exec: {
         command: [
             "verify-correctness.sh",
         ]
     }
 }

```

Converts to something like this
```

"livenessProbe": {
             "exec": {
                "command": ["sh", "-c",
                   "reply=$(curl -s -o /dev/null -w %{http_code} http://127.0.0.1:9099/ping); if [ \"$reply\" -lt 200 -o \"$reply\" -ge 400 ]; then exit 1; fi; verify-correctness.sh;"
                ]
             }
          }
```

- Author: ahakanbaba
- Quality score: 30
- URL: https://github.com/kubernetes/kubernetes/issues/37218#issuecomment-372887460

### High Signal Answer 3

very much needeed

- Author: kilianc
- Quality score: 15
- URL: https://github.com/kubernetes/kubernetes/issues/37218#issuecomment-413108684
