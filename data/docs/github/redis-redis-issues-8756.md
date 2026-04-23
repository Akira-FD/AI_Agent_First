# [BUG] Redis Does Not Automatically Reload Certificates When Certificate File Updates



## GitHub Provenance



- Repository: redis/redis

- Issue: #8756

- State: closed

- Labels: none

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/8756



## Problem



**Describe the bug**

We have short lived certificates (30 days). We also have a background process that runs and updates the cert and key files within that time period so they remain valid. It looks like redis does not notice the file has changed and does not use the new certificate.

**To reproduce**

Start redis-server in TLS mode with a cert/key
Using something like, `openssl s_client -connect <redishost>:<redisport> 2>/dev/null | openssl x509 -noout -dates`, note the expiry dates.
Now without restarting redis-server, update the file to a cert with newer expiry dates.
Using openssl again will still show the old expiry dates.

**Expected behavior**

Either redis has a file watcher on the cert/key/ca files such that if they change it will reload or add a command that will force a reload of the cert/key/ca files when requested.

**Additional information**

If the redis-server is restarted, the new cert/key/ca files will be read.

Sample Traceback
```
'cache.redis', {'exception_module': 'redis.exceptions', 'exception_class': 'ConnectionError', 'exception_msg': 'Error 1 connecting to <host>:<port>. [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: certificate has expired (_ssl.c:1076).'}
```



## Curated Answers



### High Signal Answer 1

@rjduffner You should be able to trigger a re-load by issuing a `CONFIG SET` and touch a TLS configuration option (e.g. `tls-cert-file`).

As for automatic reload - I think this is more of a feature request than a bug. I'm not inclined to address that for several reasons:

* Redis doesn't watch and auto-reload any other configuration file.
* Auto reloading may not always be the desired action. For example, if you're replacing both your key and cert files, you'd want to do that atomically.

- Author: yossigo
- Quality score: 4
- URL: https://github.com/redis/redis/issues/8756#issuecomment-817180713
