# "WARNING you have Transparent Huge Pages (THP) support enabled in your kernel"



## GitHub Provenance



- Repository: redis/redis

- Issue: #3176

- State: closed

- Labels: state:to-be-closed

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/3176



## Problem



Redis server's log issues this warning on startup:

```
WARNING you have Transparent Huge Pages (THP) support enabled in your kernel
```

along with instructions for how to change this. However, when adding the necessary configuration edits to the `rc.local` file it seems that redis manages to launch before `rc.local` is executed. (Since it gives the same warning, but the settings have indeed been changed and if restarting redis, then the warning goes away...)

So what I've done instead is add this:

```
if test -f /sys/kernel/mm/transparent_hugepage/enabled; then
  echo never > /sys/kernel/mm/transparent_hugepage/enabled
fi

if test -f /sys/kernel/mm/transparent_hugepage/defrag; then
  echo never > /sys/kernel/mm/transparent_hugepage/defrag
fi
```

to the beginning of the /etc/init.d/redis_6379 file, which seems to do the trick.

Any problems with this approach?

Thanks.



## Curated Answers



### High Signal Answer 1

We solved this on Ubuntu 14 LTS and 16 LTS by adding a directive to grub, so this will be activated before services are started and it will survive a reboot.

Create the file `/etc/default/grub.d/no_thp.cfg` and add:

```
GRUB_CMDLINE_LINUX_DEFAULT="$GRUB_CMDLINE_LINUX_DEFAULT transparent_hugepage=never"
```

Run `sudo update-grub` to activate it.

- Author: tsoldaat
- Quality score: 14
- URL: https://github.com/redis/redis/issues/3176#issuecomment-302073232

### High Signal Answer 2

Actually with newer Jemalloc versions (4.5.0) which I hope to upgrade to
ASAP, there is directly a build option to avoid using THP automatically.
This could be the best way to address the problem in the future.

On Wed, May 17, 2017 at 2:22 PM, Tjalling Soldaat <notifications@github.com>
wrote:

> We solved this on Ubuntu 14 LTS and 16 LTS by adding a directive to grub,
> so this will be activated before services are started and it will survive a
> reboot.
>
> Create the file /etc/default/grub.d/no_thp.cfg and add:
>
> GRUB_CMDLINE_LINUX_DEFAULT="$GRUB_CMDLINE_LINUX_DEFAULT transparent_hugepage=never"
>
> Run sudo update-grub to activate it.
>
> —
> You are receiving this because you are subscribed to this thread.
> Reply to this email directly, view it on GitHub
> <https://github.com/antirez/redis/issues/3176#issuecomment-302073232>, or mute
> the thread
> <https://github.com/notifications/unsubscribe-auth/AAEAYKOLisaltuFix0sAaC9GO2bNeWswks5r6uZqgaJpZM4IJ3Cx>
> .
>



-- 
Salvatore 'antirez' Sanfilippo
open source developer - Redis Labs https://redislabs.com

"If a system is to have conceptual integrity, someone must control the
concepts."
       — Fred Brooks, "The Mythical Man-Month", 1975.

- Author: antirez
- Quality score: 13
- URL: https://github.com/redis/redis/issues/3176#issuecomment-302104279

### High Signal Answer 3

http://antirez.com/news/84

- Author: badboy
- Quality score: 11
- URL: https://github.com/redis/redis/issues/3176#issuecomment-211522873
