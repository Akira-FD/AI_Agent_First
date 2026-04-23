# How to run a redis docker instance with a different port rather than 6379



## GitHub Provenance



- Repository: redis/redis

- Issue: #3842

- State: closed

- Labels: none

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/3842



## Problem



I am using the redis docker image to run redis. But I found the image is very weird. There is even no way to configure another port. 

I run redis with:
docker run -d --name shareredis redis:latest

docker ps said this instance exposes 6379 port. I would like to use a higher port since the firewall of our server blocks access to 6379 port.



## Curated Answers



### High Signal Answer 1

@yliu120 - You simply need to run the container with a different -p directive:

docker run -d -p <PORT_OF_YOUR_CHOICE>:6379 redis

- Author: ushachar
- Quality score: 105
- URL: https://github.com/redis/redis/issues/3842#issuecomment-283385521

### High Signal Answer 2

@DavideDyrecta expanding on @ushachar's reply, here's what I use but YMMV

```bash
docker run -d -p 7777:7777 redis --port 7777
redis-cli -p 7777
```

- Author: itamarhaber
- Quality score: 24
- URL: https://github.com/redis/redis/issues/3842#issuecomment-318841276

### High Signal Answer 3

@yliu120 - By default, all docker containers running on the same host can connect to each other via the EXPOSED port - the other containers should access redis via redis:6379 (and not via the PUBLISHed port).
I suggest you take a look at the Docker Networking page here:
https://docs.docker.com/engine/userguide/networking/

- Author: ushachar
- Quality score: 6
- URL: https://github.com/redis/redis/issues/3842#issuecomment-283581802
