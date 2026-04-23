# deleting namespace stuck at "Terminating" state



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #60807

- State: closed

- Labels: kind/bug, priority/important-soon, sig/api-machinery

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/60807



## Problem



I am using v1.8.4 and I am having the problem that deleted namespace stays at "Terminating" state forever. I did "kubectl delete namespace XXXX" already.



## Curated Answers



### High Signal Answer 1

@ManifoldFR , I had the same issue as yours and I managed to make it work by making an API call with json  file .
``kubectl get namespace annoying-namespace-to-delete -o json > tmp.json``
then edit tmp.json and remove``"kubernetes"`` 

``curl -k -H "Content-Type: application/json" -X PUT --data-binary @tmp.json https://kubernetes-cluster-ip/api/v1/namespaces/annoying-namespace-to-delete/finalize``

and it should delete your namespace,

- Author: slassh
- Quality score: 451
- URL: https://github.com/kubernetes/kubernetes/issues/60807#issuecomment-408599873

### High Signal Answer 2

Hey,

I've got this over and over again and it's most of the time some trouble with finalizers.

If a namespace is stuck, try to `kubectl get namespace XXX -o yaml` and check if there is a finalizer on it. If so, edit the namespace and remove the finalizer (by passing an empty array) and then the namespace gets deleted

- Author: xetys
- Quality score: 119
- URL: https://github.com/kubernetes/kubernetes/issues/60807#issuecomment-401039268

### High Signal Answer 3

@xetys is it safe? in my case there is only one finalizer named "kubernetes".

- Author: adampl
- Quality score: 68
- URL: https://github.com/kubernetes/kubernetes/issues/60807#issuecomment-401413463
