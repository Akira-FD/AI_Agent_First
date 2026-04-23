# Enable redis stream in redis helm chart bitnami with terraform



## GitHub Provenance



- Repository: redis/redis

- Issue: #13253

- State: closed

- Labels: state:to-be-closed

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/13253



## Problem



I am trying to deploy a standalone redis with bitnami helm chart and activate the redis stream and set the stream-db-max-len to 100

I have this tf file:

```
resource "helm_release" "redis" {
  timeout    = 120
  name       = "redis-stream"
  namespace  = var.namespace
  chart      = "oci://registry-1.docker.io/bitnamicharts/redis"
  version    = "18.19.2"
  values = [templatefile("manifests/redis-values.yaml", {
    redis_deployment_name = var.redis_deployment_name
    redis_affinity      = var.redis_affinity
    redis_nodeSelector  = var.redis_nodeSelector
    redis_tolerations   = var.redis_default_tolerations
  })]
}
```
and my redis-values.yaml file with this content:

```
architecture: standalone

fullnameOverride: ${redis_deployment_name}
auth:
  password: "redis"

master:
  ${ indent(2, redis_affinity) }
  ${ indent(2, redis_nodeSelector) }
  ${ indent(2, redis_tolerations) }
  persistence:
    enabled: false
  resources:
    limits:
      cpu: 350m
      memory: 700Mi
    requests:
      cpu: 100m
      memory: 256Mi
  extraFlags:
    - stream-db-max-len 100

pdb:
  enabled: true

# Eexplicit Activation of Redis Stream
redisStreamEnabled: true
```
The problem is that this piece of code:

```
extraFlags:
    - stream-db-max-len 100
```
is causing the pod to CrashLoopBackOff and the logs of the pod are this:

```
*** FATAL CONFIG FILE ERROR (Redis 7.2.4) ***
Reading the configuration file, at line 6
>>> 'include "/opt/bitnami/redis/etc/master.conf" "stream-db-max-len 100"'

Bad directive or wrong number of arguments
```
because when i remove this:

```
extraFlags:
    - stream-db-max-len 100
```
I get the pod to run but the stream-db-max-len will be set to (empty array).
![image](https://github.com/redis/redis/assets/29490363/6b2ca891-1146-4f43-bbd4-7d7b6f843e77)



## Curated Answers



### High Signal Answer 1

@Marwen-TAALLAH `stream-db-max-len` is not a valiable config for Redis, do you mean `stream-node-max-entries`?

- Author: sundb
- Quality score: 4
- URL: https://github.com/redis/redis/issues/13253#issuecomment-2101805893
