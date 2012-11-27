License
=======

foremanBuddy has been released under the Apache 2.0 license

Copyright 2012 (c) Jasper Poppe <jgpoppe@gmail.com>
                   eBuddy (http://www.ebuddy.com)

Disclaimer
==========

foremanBuddy can do most of the stuff you could do in Foreman, so be carefull and think before you type! The author or eBuddy will not be responsible for any loss of data.

Notes
=====

* Modifying or deleting parameters will require some patches in Foreman, soon I will post here more info about this.
* foremanBuddy is using the 'old' API, this will probably be changed when the
  new API has been finished
* There should be much more and better documentation, feel free to help ;)

Todo
====

Most of the stuff works fine, but there is lots room for improvements, feel free to help ;)

Requirements
============

Python 2.6.x or 2.7.x

When using Python 2.6 argeparse needs to be installed

    sudo apt-get install python-argparse

Configuration
=============

foremanBuddy will look to configuration files in the following order

    ~/.foremanbuddy.cfg -> /etc/foremanbuddy/foremanbuddy.cfg -> foremanbuddy.cfg

Testing notes
=============

Wipe all Foreman data when using Debian packages
------------------------------------------------

    sudo service apache2 stop
    sudo mysql --defaults-extra-file=/etc/mysql/debian.cnf -e 'DROP DATABASE foreman;'
    sudo mysql --defaults-extra-file=/etc/mysql/debian.cnf -e "CREATE DATABASE foreman;"
    sudo su - foreman -s /bin/bash -c /usr/share/foreman/extras/dbmigrate
    sudo service apache2 start
    cd /usr/share/foreman
    sudo rake puppet:import:hosts_and_facts RAILS_ENV=production
    sudo RAILS_ENV=production rake permissions:reset 
    
Wipe all Foreman data when using Foreman from source 
----------------------------------------------------

    cd ~/git/foreman
    sudo mysql --defaults-extra-file=/etc/mysql/debian.cnf -e 'DROP DATABASE foreman;'
    sudo mysql --defaults-extra-file=/etc/mysql/debian.cnf -e "CREATE DATABASE foreman;"
    sudo rake db:migrate RAILS_ENV=production
    #sudo su - foreman -s /bin/bash -c ~/git/foreman/extras/dbmigrate
    sudo rake puppet:import:hosts_and_facts RAILS_ENV=production
    sudo RAILS_ENV=production rake permissions:reset 
    ~/git/foreman/script/foreman-config -k ssl_ca_file -v /var/lib/puppet/ssl/certs/ca.pem
    ~/git/foreman/script/foreman-config -k ssl_certificate -v /var/lib/puppet/ssl/certs/overlord001.b.c.m.e.pem
    ~/git/foreman/script/foreman-config -k ssl_priv_key -v /etc/foreman-proxy/overlord001.b.c.m.e.key

Examples
========

Add a smart proxy
-----------------

    ./foremanbuddy.py -u admin -p changeme smart_proxy add --name overlord001.b.c.m.e --url https://overlord001.b.c.m.e:8443

Add a smart proxy DNS service to the b.c.m.e domain and set the full domain name

    ./foremanbuddy.py -u admin -p changeme domain modify b.c.m.e --dns_id 1 --fullname b.c.m.e

Modify the x86_64 architecture, bind related operating system
--------------------------------------------------------------

    ./foremanbuddy.py -u admin -p changeme architecture modify x86_64 --operatingsystem_ids 1

Add a subnet
------------

    ./foremanbuddy.py -u admin -p changeme subnet add --name b.c.m.e --network 192.168.21.0 --mask 255.255.255.0 --dns_id 1 --tftp_id 1 --dhcp_id 1 --domain_ids=1

Add Debian installation media
-----------------------------

    ./foremanbuddy.py -u admin -p changeme media add --name 'Debian Mirror' --path http://ftp.debian.org/debian --os_family Debian

Add a Debian PXElinux template
-----------------------------

    ./foremanbuddy.py -u admin -p changeme template add --name 'Preseed Debian PXElinux' --file_name templates/preseed_debian_pxelinux.template --template_kind 1

Add a partition table from a file
---------------------------------

    ./foremanbuddy.py -u admin -p changeme ptable add --name 'Debian Entire Disk KVM' --file_name templates/debian_entire_disk_kvm.template --os_family Debian

Bind the Preseed Default to operating system with id 1 (Debian 6.0)
-------------------------------------------------------------------

    ./foremanbuddy.py -u admin -p changeme ids -t
    ./foremanbuddy.py -u admin -p changeme template modify 5 --operatingsystem_ids 1
    ./foremanbuddy.py -u admin -p changeme template modify 6 --operatingsystem_ids 1
    ./foremanbuddy.py -u admin -p changeme template modify 23 --operatingsystem_ids 1

Deploy the default pxe template to all smart proxies
----------------------------------------------------

    ./foremanbuddy.py -u admin -p changeme template build

Modify the Debian Operating system assign templates and various ids
-------------------------------------------------------------------

    ./foremanbuddy.py -u admin -p changeme operatingsystem modify 1 --medium_ids 6 --ptable_ids 11 --architecture_ids 1 --provision_template_id 5 --pxelinux_template_id 23 --finish_template_id 6

Add 2 hosts (minion001.b.c.m.e and minion002.b.c.m.e)
-----------------------------------------------------

    ./foremanbuddy.py -u admin -p changeme host add --name minion001.b.c.m.e --environment_id 1 --architecture_id 1 --operatingsystem_id 1 --domain_id 1 --mac 52:54:c0:a8:14:65 --ip 192.168.21.101 --ptable_id 11 --puppet_proxy_id 1 --subnet_id 1 --medium_id 6
    ./foremanbuddy.py -u admin -p changeme host add --name minion002.b.c.m.e --environment_id 1 --architecture_id 1 --operatingsystem_id 1 --domain_id 1 --mac 52:54:c0:a8:14:66 --ip 192.168.21.102 --ptable_id 11 --puppet_proxy_id 1 --subnet_id 1 --medium_id 6

Enable a host for unattended installation
-----------------------------------------

    ./foremanbuddy.py -u admin -p changeme host action --set_build minion001.b.c.m.e
    ./foremanbuddy.py -u admin -p changeme host action --set_build minion002.b.c.m.e

Disable a host for unattended installation
------------------------------------------

    ./foremanbuddy.py -u admin -p changeme host action --cancel_build minion001.b.c.m.e

Add Foreman user
----------------

    ./foremanbuddy.py -u admin -p changeme user add --login jpoppe --firstname Jasper --lastname Poppe --mail jpoppe@ebuddy.com --auth_source_id 1 --password 123 --admin True

Add a compute resource
----------------------

    ./foremanbuddy.py -u admin -p changeme compute_resource add --name astray98 --url "qemu+ssh://jpoppe@192.168.123.1/system" --provider Libvirt

Add a host group
----------------

    ./foremanbuddy.py  hostgroup add --operatingsystem_id 'Debian 6.0' --root_pass 123 --environment_id  --name backend --medium_id 6 --architecture_id 1 --ptable_id 9 --puppet_proxy_id 1 --domain_id 1

Add and remove a host group parameter to host group with id 1
-------------------------------------------------------------

    ./foremanbuddy.py hostgroup add_parameter -k dns -v 192.168.0.1 1
    ./foremanbuddy.py hostgroup delete_parameter -k dns 1

Add and remove a host parameter to host 'overlord001.b.c.m.e'
-------------------------------------------------------------

    ./foremanbuddy.py host add_parameter -k test -v 123 overlord001.b.c.m.e
    ./foremanbuddy.py host delete_parameter -k test overlord001.b.c.m.e

Query UUIDs for nodes on compute resource 1
-------------------------------------------

    ./foremanbuddy.py -d -u admin -p changeme compute_resource info -u 1

Delete node with UUID 'cf42e9ae-5d77-71a2-1af5-fd2e8bf33d32'
------------------------------------------------------------

    ./foremanbuddy.py -d compute_resource action --destroy cf42e9ae-5d77-71a2-1af5-fd2e8bf33d32 1

Start node with UUID '77a39ace-a832-d42e-94ab-02532ec1c6ca'
-----------------------------------------------------------

    ./foremanbuddy.py -d compute_resource action --power_on 77a39ace-a832-d42e-94ab-02532ec1c6ca 1

Stop a node with uuid '77a39ace-a832-d42e-94ab-02532ec1c6ca'
------------------------------------------------------------

    ./foremanbuddy.py -d compute_resource action --power_off 77a39ace-a832-d42e-94ab-02532ec1c6ca 1

Create a virtual host
---------------------

    ./foremanbuddy.py host compute_add --name minion003.b.c.m.e --environment_id 1 --architecture_id 1 --operatingsystem_id 1 --domain_id 1 --mac 52:54:c0:a8:14:68 --ip 192.168.21.14 --ptable_id 11 --puppet_proxy_id 1 --subnet_id 1 --medium_id 6 --cpus 2 --capacity 10G --format_type raw --pool_name bcme --memory 536870912 --start 1 --bridge virbr4 --compute_resource_id 1 --build 1

Delete host 'minion003.b.c.m.e'
-------------------------------------------

    ./foremanbuddy.py host delete minion003.b.c.m.e
