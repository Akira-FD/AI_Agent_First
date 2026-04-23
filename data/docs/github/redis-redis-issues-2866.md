# Added authentication to cluster redis-trib.rb



## GitHub Provenance



- Repository: redis/redis

- Issue: #2866

- State: closed

- Labels: none

- Repository stars: 73959

- URL: https://github.com/redis/redis/issues/2866



## Problem



redis-trib.rb

line 51:
..................... 
 def initialize(addr)
        s = addr.split(":")
        if s.length < 2
           puts "Invalid IP or Port (given as #{addr}) - use IP:Port format"
           exit 1
        end
    pwd =nil
        if s.length==3
           pwd = s.pop
        end
        port = s.pop # removes port from split array
        ip = s.join(":") # if s.length > 1 here, it's IPv6, so restore address
        @r = nil
        @info = {}
        @info[:host] = ip
        @info[:port] = port
        @info[:slots] = {}
        @info[:migrating] = {}
        @info[:importing] = {}
        @info[:replicate] = false
    @info[:password] = pwd
        @dirty = false # True if we need to flush slots info into node.
        @friends = []
    end

```
def friends
    @friends
end

def slots
    @info[:slots]
end

def has_flag?(flag)
    @info[:flags].index(flag)
end

def to_s
    "#{@info[:host]}:#{@info[:port]}"
end

def connect(o={})
    return if @r
    print "Connecting to node #{self}: "
    STDOUT.flush
    begin
   if @info[:password] != nil
           @r = Redis.new(:host => @info[:host], :port => @info[:port], :timeout => 60,:password=>@info[:password])
           @r.ping
   else
         @r = Redis.new(:host => @info[:host], :port => @info[:port], :timeout => 60)
             @r.ping
   end
    rescue
        xputs "[ERR] Sorry, can't connect to node #{self}"
        exit 1 if o[:abort]
        @r = nil
    end
    xputs "OK"
end
```

.......
.......
COMMANDS={
    "create"  => ["create_cluster_cmd", -2, "host1:port1:<  password   >  ......  hostN:portN:<  password  >"],
    "check"   => ["check_cluster_cmd", 2, "host:port"],
    "fix"     => ["fix_cluster_cmd", 2, "host:port"],
    "reshard" => ["reshard_cluster_cmd", 2, "host:port"],
    "add-node" => ["addnode_cluster_cmd", 3, "new_host:new_port existing_host:existing_port"],
    "del-node" => ["delnode_cluster_cmd", 3, "host:port node_id"],
    "set-timeout" => ["set_timeout_cluster_cmd", 3, "host:port milliseconds"],
    "call" =>    ["call_cluster_cmd", -3, "host:port command arg arg .. arg"],
    "import" =>  ["import_cluster_cmd", 2, "host:port"],
    "help"    => ["help_cluster_cmd", 1, "(show this help)"]
}



## Curated Answers



### High Signal Answer 1

as noted in https://github.com/redis/redis/pull/4288, redis-trib is now replaced by redis-cli, which does solve this issues.

- Author: oranagra
- Quality score: 4
- URL: https://github.com/redis/redis/issues/2866#issuecomment-700214261
