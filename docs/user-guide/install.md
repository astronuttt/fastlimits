You can install this library just by running:

`pip install fastlimits`


Then you can start using it! 


As we mentioned before, FastLimits supports multiple storage backends courtesy of limist library.


You can read more about different flavours of limits storage backend in their [Installation manual](https://limits.readthedocs.io/en/stable/installation.html).


But... you can take a shortcut and install those flavours directly:



=== "Async Redis"
    `pip install "fastlimits[async-redis]"`


=== "Async Memcached"
    `pip install "fastlimits[async-memcached]"`

=== "Async Mongodb"
    `pip install "fastlimits[async-mongodb]"`

=== "Async Etcd"
    `pip install "fastlimits[async-etcd]"`

Before you dive in, take a look at the next few chapters as they walk you in on how to get started.