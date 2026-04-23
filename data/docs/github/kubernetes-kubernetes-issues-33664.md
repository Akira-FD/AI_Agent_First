# Force pods to re-pull an image without changing the image tag



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #33664

- State: closed

- Labels: priority/important-soon, sig/apps

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/33664



## Problem



### Problem

A frequent question that comes up on Slack and Stack Overflow is how to trigger an update to a Deployment/RS/RC when the image tag hasn't changed but the underlying image has.

Consider:
1. There is an existing Deployment with image `foo:latest`
2. User builds a new image `foo:latest` 
3. User pushes `foo:latest` to their registry
4. User wants to do something here to tell the Deployment to pull the new image and do a rolling-update of existing pods

The problem is that there is no existing Kubernetes mechanism which properly covers this.
### Current Workarounds
- Always change the image tag when deploying a new version
- Refer to the image hash instead of tag, e.g. `localhost:5000/andy/busybox@sha256:2aac5e7514fbc77125bd315abe9e7b0257db05fe498af01a58e239ebaccf82a8`
- Use `latest` tag or `imagePullPolicy: Always` and delete the pods. New pods will pull the new image. This approach doesn't do a rolling update and will result in downtime.
- Fake a change to the Deployment by changing something other than the image
### Possible Solutions
- https://github.com/kubernetes/kubernetes/issues/13488 If rolling restart were implemented, users could do a rolling-restart to pull the new image.
- Have a controller that watches the image registry and automatically updates the Deployment to use the latest image hash for a given tag. See https://github.com/kubernetes/kubernetes/issues/1697#issuecomment-202631815

cc @justinsb



## Curated Answers



### High Signal Answer 1

@yujuhong  Sometimes it's very useful to be able to do this. For instance, we run a testing cluster that should run a build from the latest commit on the master branch of our repository. There aren't tags or branches for every commit, so ':latest' is the logical and most practical name for it.

Wouldn't it make more sense if Kubernetes stored and checked the hash of the deployed container instead of its (mutable) name anyway, though?

- Author: Arachnid
- Quality score: 228
- URL: https://github.com/kubernetes/kubernetes/issues/33664#issuecomment-253876444

### High Signal Answer 2

For people like me, finding this issue via Google: A solution to force the re-pull of the image is to change the pod-template hash during each build. This can be achieved by adding an environment variable that is altered during build:

**deployment.yaml**
```yaml
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: demo
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: demo
    spec:
      containers:
      - name: demo
        image: registry.example.com/apps/demo:master
        imagePullPolicy: Always
        env:
        - name: FOR_GODS_SAKE_PLEASE_REDEPLOY
          value: 'THIS_STRING_IS_REPLACED_DURING_BUILD'
```

**Deploy:**
```bash
sed -ie "s/THIS_STRING_IS_REPLACED_DURING_BUILD/$(date)/g" deployment.yml
kubectl apply -f deployment.yml
```

- Author: max-vogler
- Quality score: 217
- URL: https://github.com/kubernetes/kubernetes/issues/33664#issuecomment-292895327

### High Signal Answer 3

if `kubectl apply -f for-god-sake-update-latest-image.yaml ` can update latest image we should really happy. (with `ImagePullPollicy: Always`)

- Author: alizdavoodi
- Quality score: 144
- URL: https://github.com/kubernetes/kubernetes/issues/33664#issuecomment-271227282
