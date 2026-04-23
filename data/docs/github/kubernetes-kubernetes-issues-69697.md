# PV is stuck at terminating after PVC is deleted



## GitHub Provenance



- Repository: kubernetes/kubernetes

- Issue: #69697

- State: closed

- Labels: kind/bug, sig/storage, lifecycle/rotten

- Repository stars: 121862

- URL: https://github.com/kubernetes/kubernetes/issues/69697



## Problem



<!-- This form is for bug reports and feature requests ONLY!

If you're looking for help check [Stack Overflow](https://stackoverflow.com/questions/tagged/kubernetes) and the [troubleshooting guide](https://kubernetes.io/docs/tasks/debug-application-cluster/troubleshooting/).

If the matter is security related, please disclose it privately via https://kubernetes.io/security/.
-->

**Is this a BUG REPORT or FEATURE REQUEST?**:

> Uncomment only one, leave it on its own line:
>
/kind bug
> /kind feature

**What happened**:
I was testing EBS CSI driver. I created a PV using PVC. Then I deleted the PVC. However, PV deletion is stuck in `Terminating` state. Both PVC and volume is deleted without any issue. CSI driver is kept being called with `DeleteVolume` even if it returns success when volume not found (because it is already gone). 

CSI Driver log:
```
I1011 20:37:29.778380       1 controller.go:175] ControllerGetCapabilities: called with args &csi.ControllerGetCapabilitiesRequest{XXX_NoUnkeyedLiteral:struct {}{}, XXX_unrecognized:[]uint8(nil), XXX_sizecache:0}
I1011 20:37:29.780575       1 controller.go:91] DeleteVolume: called with args: &csi.DeleteVolumeRequest{VolumeId:"vol-0ea6117ddb69e78fb", ControllerDeleteSecrets:map[string]string(nil), XXX_NoUnkeyedLiteral:struct {}{}, XXX_unrecognized:[]uint8(nil), XXX_sizecache:0}
I1011 20:37:29.930091       1 controller.go:99] DeleteVolume: volume not found, returning with success
```
external attacher log:
```
I1011 19:15:14.931769       1 controller.go:167] Started VA processing "csi-3b15269e725f727786c5aec3b4da3f2eebc2477dec53d3480a3fe1dd01adea53"
I1011 19:15:14.931794       1 csi_handler.go:76] CSIHandler: processing VA "csi-3b15269e725f727786c5aec3b4da3f2eebc2477dec53d3480a3fe1dd01adea53"
I1011 19:15:14.931808       1 csi_handler.go:103] Attaching "csi-3b15269e725f727786c5aec3b4da3f2eebc2477dec53d3480a3fe1dd01adea53"
I1011 19:15:14.931823       1 csi_handler.go:208] Starting attach operation for "csi-3b15269e725f727786c5aec3b4da3f2eebc2477dec53d3480a3fe1dd01adea53"
I1011 19:15:14.931905       1 csi_handler.go:179] PV finalizer is already set on "pvc-069128c6ccdc11e8"
I1011 19:15:14.931947       1 csi_handler.go:156] VA finalizer is already set on "csi-3b15269e725f727786c5aec3b4da3f2eebc2477dec53d3480a3fe1dd01adea53"
I1011 19:15:14.931962       1 connection.go:235] GRPC call: /csi.v0.Controller/ControllerPublishVolume
I1011 19:15:14.931966       1 connection.go:236] GRPC request: volume_id:"vol-0ea6117ddb69e78fb" node_id:"i-06d0e08c9565c4db7" volume_capability:<mount:<fs_type:"ext4" > access_mode:<mode:SINGLE_NODE_WRITER > > volume_attributes:<key:"storage.kubernetes.io/csiProvisionerIdentity" value:"1539123546345-8081-com.amazon.aws.csi.ebs" >
I1011 19:15:14.935053       1 controller.go:197] Started PV processing "pvc-069128c6ccdc11e8"
I1011 19:15:14.935072       1 csi_handler.go:350] CSIHandler: processing PV "pvc-069128c6ccdc11e8"
I1011 19:15:14.935106       1 csi_handler.go:386] CSIHandler: processing PV "pvc-069128c6ccdc11e8": VA "csi-3b15269e725f727786c5aec3b4da3f2eebc2477dec53d3480a3fe1dd01adea53" found
I1011 19:15:14.952590       1 controller.go:197] Started PV processing "pvc-069128c6ccdc11e8"
I1011 19:15:14.952613       1 csi_handler.go:350] CSIHandler: processing PV "pvc-069128c6ccdc11e8"
I1011 19:15:14.952654       1 csi_handler.go:386] CSIHandler: processing PV "pvc-069128c6ccdc11e8": VA "csi-3b15269e725f727786c5aec3b4da3f2eebc2477dec53d3480a3fe1dd01adea53" found
I1011 19:15:15.048026       1 controller.go:197] Started PV processing "pvc-069128c6ccdc11e8"
I1011 19:15:15.048048       1 csi_handler.go:350] CSIHandler: processing PV "pvc-069128c6ccdc11e8"
I1011 19:15:15.048167       1 csi_handler.go:386] CSIHandler: processing PV "pvc-069128c6ccdc11e8": VA "csi-3b15269e725f727786c5aec3b4da3f2eebc2477dec53d3480a3fe1dd01adea53" found
I1011 19:15:15.269955       1 connection.go:238] GRPC response:
I1011 19:15:15.269986       1 connection.go:239] GRPC error: rpc error: code = Internal desc = Could not attach volume "vol-0ea6117ddb69e78fb" to node "i-06d0e08c9565c4db7": could not attach volume "vol-0ea6117ddb69e78fb" to node "i-06d0e08c9565c4db7": InvalidVolume.NotFound: The volume 'vol-0ea6117ddb69e78fb' does not exist.
        status code: 400, request id: 634b33d1-71cb-4901-8ee0-98933d2a5b47
I1011 19:15:15.269998       1 csi_handler.go:320] Saving attach error to "csi-3b15269e725f727786c5aec3b4da3f2eebc2477dec53d3480a3fe1dd01adea53"
I1011 19:15:15.274440       1 csi_handler.go:330] Saved attach error to "csi-3b15269e725f727786c5aec3b4da3f2eebc2477dec53d3480a3fe1dd01adea53"
I1011 19:15:15.274464       1 csi_handler.go:86] Error processing "csi-3b15269e725f727786c5aec3b4da3f2eebc2477dec53d3480a3fe1dd01adea53": failed to attach: rpc error: code = Internal desc = Could not attach volume "vol-0ea6117ddb69e78fb" to node "i-06d0e08c9565c4db7": could not attach volume "vol-0ea6117ddb69e78fb" to node "i-06d0e08c9565c4db7": InvalidVolume.NotFound: The volume 'vol-0ea6117ddb69e78fb' does not exist.
        status code: 400, request id: 634b33d1-71cb-4901-8ee0-98933d2a5b47
I1011 19:15:15.274505       1 controller.go:167] Started VA processing "csi-3b15269e725f727786c5aec3b4da3f2eebc2477dec53d3480a3fe1dd01adea53"
I1011 19:15:15.274516       1 csi_handler.go:76] CSIHandler: processing VA "csi-3b15269e725f727786c5aec3b4da3f2eebc2477dec53d3480a3fe1dd01adea53"
I1011 19:15:15.274522       1 csi_handler.go:103] Attaching "csi-3b15269e725f727786c5aec3b4da3f2eebc2477dec53d3480a3fe1dd01adea53"
I1011 19:15:15.274528       1 csi_handler.go:208] Starting attach operation for "csi-3b15269e725f727786c5aec3b4da3f2eebc2477dec53d3480a3fe1dd01adea53"
I1011 19:15:15.274536       1 csi_handler.go:320] Saving attach error to "csi-3b15269e725f727786c5aec3b4da3f2eebc2477dec53d3480a3fe1dd01adea53"
I1011 19:15:15.278318       1 csi_handler.go:330] Saved attach error to "csi-3b15269e725f727786c5aec3b4da3f2eebc2477dec53d3480a3fe1dd01adea53"
I1011 19:15:15.278339       1 csi_handler.go:86] Error processing "csi-3b15269e725f727786c5aec3b4da3f2eebc2477dec53d3480a3fe1dd01adea53": failed to attach: PersistentVolume "pvc-069128c6ccdc11e8" is marked for deletion
```
```
I1011 20:37:23.328696       1 controller.go:167] Started VA processing "csi-3b15269e725f727786c5aec3b4da3f2eebc2477dec53d3480a3fe1dd01adea53"
I1011 20:37:23.328709       1 csi_handler.go:76] CSIHandler: processing VA "csi-3b15269e725f727786c5aec3b4da3f2eebc2477dec53d3480a3fe1dd01adea53"
I1011 20:37:23.328715       1 csi_handler.go:103] Attaching "csi-3b15269e725f727786c5aec3b4da3f2eebc2477dec53d3480a3fe1dd01adea53"
I1011 20:37:23.328721       1 csi_handler.go:208] Starting attach operation for "csi-3b15269e725f727786c5aec3b4da3f2eebc2477dec53d3480a3fe1dd01adea53"
I1011 20:37:23.328730       1 csi_handler.go:320] Saving attach error to "csi-3b15269e725f727786c5aec3b4da3f2eebc2477dec53d3480a3fe1dd01adea53"
I1011 20:37:23.330919       1 reflector.go:286] github.com/kubernetes-csi/external-attacher/vendor/k8s.io/client-go/informers/factory.go:87: forcing resync
I1011 20:37:23.330975       1 controller.go:197] Started PV processing "pvc-069128c6ccdc11e8"
I1011 20:37:23.330990       1 csi_handler.go:350] CSIHandler: processing PV "pvc-069128c6ccdc11e8"
I1011 20:37:23.331030       1 csi_handler.go:386] CSIHandler: processing PV "pvc-069128c6ccdc11e8": VA "csi-3b15269e725f727786c5aec3b4da3f2eebc2477dec53d3480a3fe1dd01adea53" found
I1011 20:37:23.346007       1 csi_handler.go:330] Saved attach error to "csi-3b15269e725f727786c5aec3b4da3f2eebc2477dec53d3480a3fe1dd01adea53"
I1011 20:37:23.346033       1 csi_handler.go:86] Error processing "csi-3b15269e725f727786c5aec3b4da3f2eebc2477dec53d3480a3fe1dd01adea53": failed to attach: PersistentVolume "pvc-069128c6ccdc11e8" is marked for deletion
I1011 20:37:23.346069       1 controller.go:167] Started VA processing "csi-3b15269e725f727786c5aec3b4da3f2eebc2477dec53d3480a3fe1dd01adea53"
I1011 20:37:23.346077       1 csi_handler.go:76] CSIHandler: processing VA "csi-3b15269e725f727786c5aec3b4da3f2eebc2477dec53d3480a3fe1dd01adea53"
I1011 20:37:23.346082       1 csi_handler.go:103] Attaching "csi-3b15269e725f727786c5aec3b4da3f2eebc2477dec53d3480a3fe1dd01adea53"
I1011 20:37:23.346088       1 csi_handler.go:208] Starting attach operation for "csi-3b15269e725f727786c5aec3b4da3f2eebc2477dec53d3480a3fe1dd01adea53"
I1011 20:37:23.346096       1 csi_handler.go:320] Saving attach error to "csi-3b15269e725f727786c5aec3b4da3f2eebc2477dec53d3480a3fe1dd01adea53"
I1011 20:37:23.351068       1 csi_handler.go:330] Saved attach error to "csi-3b15269e725f727786c5aec3b4da3f2eebc2477dec53d3480a3fe1dd01adea53"
I1011 20:37:23.351090       1 csi_handler.go:86] Error processing "csi-3b15269e725f727786c5aec3b4da3f2eebc2477dec53d3480a3fe1dd01adea53": failed to attach: PersistentVolume "pvc-069128c6ccdc11e8" is marked for deletion
```

```
>> kk get pv
NAME                   CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS        CLAIM            STORAGECLASS   REASON   AGE
pvc-069128c6ccdc11e8   4Gi        RWO            Delete           Terminating   default/claim1   late-sc                 22h

>> kk describe pv
Name:            pvc-069128c6ccdc11e8
Labels:          <none>
Annotations:     pv.kubernetes.io/provisioned-by: com.amazon.aws.csi.ebs
Finalizers:      [external-attacher/com-amazon-aws-csi-ebs]
StorageClass:    late-sc
Status:          Terminating (lasts <invalid>)
Claim:           default/claim1
Reclaim Policy:  Delete
Access Modes:    RWO
Capacity:        4Gi
Node Affinity:   <none>
Message:
Source:
    Type:              CSI (a Container Storage Interface (CSI) volume source)
    Driver:            com.amazon.aws.csi.ebs
    VolumeHandle:      vol-0ea6117ddb69e78fb
    ReadOnly:          false
    VolumeAttributes:      storage.kubernetes.io/csiProvisionerIdentity=1539123546345-8081-com.amazon.aws.csi.ebs
Events:                <none>
```

Storageclass:
```
kind: StorageClass
apiVersion: storage.k8s.io/v1                                                                                                                                                                                                                             metadata:
  name: late-sc
provisioner: com.amazon.aws.csi.ebs
volumeBindingMode: WaitForFirstConsumer
```

Claim:
```
apiVersion: v1                                                                                                                                                                                                                                            kind: PersistentVolumeClaim
metadata:
  name: claim1
spec:                                                                                                                                                                                                                                                       accessModes:
    - ReadWriteOnce
  storageClassName: late-sc
  resources:                                                                                                                                                                                                                                                  requests:
      storage: 4Gi
```
**What you expected to happen**:
After PVC is deleted, PV should be deleted along with the EBS volume (since my Reclaim Policy is delete)

**How to reproduce it (as minimally and precisely as possible)**:
Non-deterministic so far

**Anything else we need to know?**:

**Environment**:
- Kubernetes version (use `kubectl version`): client: v1.12.0 server: v1.12.1
- Cloud provider or hardware configuration: aws
- OS (e.g. from /etc/os-release): 
- Kernel (e.g. `uname -a`):
- Install tools: cluster is set up using kops
- Others:



## Curated Answers



### High Signal Answer 1

I got rid of this issue by performing the following actions:
```Chandras-MacBook-Pro:kubernetes-kafka chandra$ kubectl get pv | grep "kafka/"
pvc-5124cf7a-e9dc-11e8-93a1-02551748eea0   1Gi        RWO            Retain           Bound         kafka/data-pzoo-0                                         kafka-zookeeper             21h
pvc-639023b2-e9dc-11e8-93a1-02551748eea0   1Gi        RWO            Retain           Bound         kafka/data-pzoo-1                                         kafka-zookeeper             21h
pvc-7d88b184-e9dc-11e8-93a1-02551748eea0   1Gi        RWO            Retain           Bound         kafka/data-pzoo-2                                         kafka-zookeeper             21h
pvc-9ea68541-e9dc-11e8-93a1-02551748eea0   100Gi      RWO            Delete           Terminating   kafka/data-kafka-0                                        kafka-broker                21h
pvc-ae795177-e9dc-11e8-93a1-02551748eea0   100Gi      RWO            Delete           Terminating   kafka/data-kafka-1                                        kafka-broker                21h
```
Then I manually edited the `pv` individually and then removing the `finalizers` which looked something like this:
```finalizers:
  - kubernetes.io/pv-protection```

Once done, the PVs those were in Terminating condition were all gone!!!

- Author: chandraprakash1392
- Quality score: 285
- URL: https://github.com/kubernetes/kubernetes/issues/69697#issuecomment-439635888

### High Signal Answer 2

examples removing for finalizers 

`kubectl patch pvc db-pv-claim -p '{"metadata":{"finalizers":null}}'`
`kubectl patch pod db-74755f6698-8td72 -p '{"metadata":{"finalizers":null}}'`

then you can delete them

!!! IMPORTANT !!!:
Read also https://github.com/kubernetes/kubernetes/issues/78106
The patch commands are a workaround and something is not working properly. 
Ther volumes are still attached: kubectl get volumeattachments!

- Author: murdav
- Quality score: 227
- URL: https://github.com/kubernetes/kubernetes/issues/69697#issuecomment-448541618

### High Signal Answer 3

Answer of @chandraprakash1392  is still valid when `pvc` stucks also in `Terminating` status.
You just need to edit the pvc object and remove `finalizers` object.

- Author: abdennour
- Quality score: 39
- URL: https://github.com/kubernetes/kubernetes/issues/69697#issuecomment-447201890
