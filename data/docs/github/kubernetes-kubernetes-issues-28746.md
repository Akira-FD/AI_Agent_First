# kubectl logs should *not* fail while a pod is being started, because it makes for a terrible initial experience



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #28746

- State: closed

- Labels: priority/backlog, area/usability, area/kubectl, sig/node, sig/cli, lifecycle/frozen

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/28746



## Problem



Currently the following can fail:

```
$ kubectl create -f pod.yaml 
pod "foo" created
$ kubectl logs -f foo
container "build" in pod "build" is waiting to start: ContainerCreating
```

For real world cases where it may take tens of seconds to pull the image, this is intensely frustrating to users because now they have to guess when the pod is started in order to debug it.

For users who specify `kubectl logs foo`, it may be ok to return immediately (we need to debate this).  `-f` is different because the expectation is to wait to see the results of the pod execution.

We need to fix the kubelet to return errors that allow clients to make the determination (probably by improving the types of errors returned by `validateContainerLogStatus` to include structured API errors) and ensure that the pod log (and other log endpoints, like deploy logs) can properly handle surfacing that.  Then we either need to change the logs endpoint for follow to have that behavior (reasonable) or change the clients (more work, harder to justify).  The other log endpoints should be have consistently.

We need to keep backwards compatibility in account on errors - right now we always return 400 Bad Request, but we could add detail causes.  The GenericHTTPResponseChecker would probably need to be wrapped with a more powerful PossibleAPIOrGenericHTTPResponseChecker that tested for JSON output and did the right thing.



## Curated Answers



### High Signal Answer 1

Thanks @stszap.

We found the `Initialized` condition was not ready enough to be able to start watching the logs, but `ContainersReady` is.

It turns out waiting on the pod to start can be done by using the automatically provided `job-name` as the selector. I'm not sure whether that's GKE-specific though.

I haven't investigated whether running `kubectl logs --follow job/db-migrate` in the foreground is reliable enough to determine that the job has finished; so we run it in the background and kill it once the job's done. But this has the side-effect of not exiting the script if the job fails - so more investigation is required.

Here's basically what we're using to run a job - as `scripts/migrate-db` in order to have our database migrations run as a separate Buildkite pipeline step before deploying the rest of the app:

```bash
#!/bin/bash

set -Eeuo pipefail

cd $(dirname $0)/..

cleanup() {
  echo "Cleaning up..."
  kill $(jobs -p) &>/dev/null || true
}

trap cleanup EXIT

set -x

# Delete the previous job if it exists
kubectl delete -f db-migrate-job.yaml --ignore-not-found

# Run the job
kubectl apply -f db-migrate-job.yaml

# Start showing the logs
kubectl wait --for=condition=ContainersReady --timeout=60s pod --selector job-name=db-migrate
kubectl logs --follow job/db-migrate &

# Wait for completion
kubectl wait --for=condition=complete --timeout=86400s job/db-migrate
```

CC @jpaulgs, @yob, @ceralena

---

**Update: [here is our new `kube-run-pod` script](https://gist.github.com/ZimbiX/8482514298e8eca419f48fb2a52e7ae4)**. In the above, the ContainersReady waiting fails in the rare case that the cronjob hasn't yet created a pod. From that, we realised we didn't need it to be a job anyway - creating and deleting a pod is sufficient.

- Author: ZimbiX
- Quality score: 18
- URL: https://github.com/kubernetes/kubernetes/issues/28746#issuecomment-520716747

### High Signal Answer 2

Making this p2 because I can't yet justify it, but this is _intensely_ irritating to new users.

- Author: smarterclayton
- Quality score: 17
- URL: https://github.com/kubernetes/kubernetes/issues/28746#issuecomment-231618924

### High Signal Answer 3

@mfojtik @kargakis - has there been any movement on this issue?

`kubectl logs` has the `--pod-running-timeout=90s` flag but it doesn't appear to have any effect. It appears that the only workaround is an involved Python script that checks for the job status and then polls until it starts receiving logs... it feels like `kubectl logs` should support this out of the box.

This is the bad experience that @smarterclayton mentioned:
````
$ kubectl logs -f xxxx-0
Error from server (BadRequest): container "xxxx-0" in pod "xxxx-0-6cqdt" is waiting to start: ContainerCreating
```

- Author: brunobowden
- Quality score: 12
- URL: https://github.com/kubernetes/kubernetes/issues/28746#issuecomment-389035477
