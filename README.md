# puppet-enc
External Node Classifier for Puppet Master

# Installation
1. Edit `puppet.conf`
```
node_terminus = exec
external_nodes = /etc/puppetlabs/code/config/scripts/lsst_enc.py
```
1. Edit `puppet_enc_sqlite_source.csv`
1. `import_csv`

# Usage
* View contents of entire database
  * `lsdb.sh`
* View settings for nodes matching a (sub)string
  * `lsnode.sh` _<STRING>_
  * Example: Show all nodes with the string _test_ anywhere in their FQDN
    * `lsnode.sh test`
* Update a node
  * `chnode.sh` _<FQDN> <KEY> <VALUE>_
  * Example: Move node to test environment
    * `chnode.sh my_test_node.vm.dev.lsst.org environment test`
* Update a node (alternative)
  * Edit `puppet_enc_sqlite_source.csv`
  * `import_csv`

# Testing
1. Run it from the cmdline
```
/etc/puppetlabs/code/config/scripts/lsst_enc.py my_test_node.vm.dev.lsst.org
---
classes: ['role::default']
environment: test
parameters: {cluster: default, datacenter: npcf, enc_hostname: my_test_node.vm.dev.lsst.org, role: default, site: ncsa}
```
