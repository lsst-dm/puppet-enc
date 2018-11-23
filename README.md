# puppet-enc
External Node Classifier for Puppet Master

# Installation
1. `cd /etc/puppetlabs/code/enc/`
1. `git clone https://github.com/lsst-dm/puppet-enc.git`
1. Edit `/etc/puppetlabs/puppet/puppet.conf`
   ```
   node_terminus = exec
   external_nodes = /etc/puppetlabs/code/enc/bin/lsst_enc.py
   ```
1. Edit `config/nodes_database.csv`
1. `make configure import`

# Usage

* Help for admin script
  * `python3 admin.py -h`
* Help for lsst_enc.py
  * `python3 lsst_enc.py -h`
* View contents of entire database
  * `python3 admin.py -d ../data/puppet_enc.sqlite -l`
* View settings for nodes matching a (sub)string
  * `python3 admin.py -d ../data/puppet_enc.sqlite -L --node-def <NODE_DEF_STRING>`
  * `python3 admin.py -d ../data/puppet_enc.sqlite -L -fqdn <FQDN>`
* Update a node
  * `python3 admin.py -d ../data/puppet_enc.sqlite -u --node-def <NODE_DEF> -a key1=value1 -a key2=value2 ...` 
  * Example: Move node to test environment
    * `python3 admin.py -d ../data/puppet_enc.sqlite -u --node-def graylog -a environment=test`
* Update a node (alternative)
  * Edit `/etc/puppetlabs/code/enc/nodes_database.csv`
  * `make import`
* Export data to CSV
  * `make export`

# Testing
1. Run it from the cmdline
   ```
   # Example:
   python3 admin.py -d ../data/puppet_enc.sqlite -L -fqdn gs-grafana-node-01.cl.cp.lsst.org
   +-----------------+------+------------+---------+-------------------+-------------+
   | node_definition | site | datacenter | cluster |              role | environment |
   +-----------------+------+------------+---------+-------------------+-------------+
   | grafana         |   cp |         cp |      gs | role::it::grafana |     develop |
   +-----------------+------+------------+---------+-------------------+-------------+
   +------+-------------+---------------+-------------+
   | fqdn | environment | ConfTimeStart | ConfTimeEnd |
   +------+-------------+---------------+-------------+
   +------+-------------+---------------+-------------+
   ```
