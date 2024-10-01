You can install this library just by running:

`pip install fastlimiter`


Then you can start using it! 


As we mentioned before, FastLimiter supports multiple storage backends courtesy of limist library.


You can read more about different flavours of limits storage backend in their [Installation manual](https://limits.readthedocs.io/en/stable/installation.html).


But... you can take a shortcut and install those flavours directly:



=== "Async Redis"
    `pip install "fastlimiter[async-redis]"`


=== "Async Memcached"
    `pip install "fastlimiter[async-memcached]"`

=== "Async Mongodb"
    `pip install "fastlimiter[async-mongodb]"`

=== "Async Etcd"
    `pip install "fastlimiter[async-etcd]"`

Before you dive in, take a look at the next few chapters as they walk you in on how to get started.