
configure:
	#Creates SQL file to import the configuration described in the hiera parameters.
	python3.6 bin/configuration.py confi/hiera_parameters.yaml config/database.sql

clean: clean_config clean_db

clean_config:
	rm -v config/database.sql

clean_db:
	rm data/puppet_enc.sqlite

import:
	sqlite3 data/puppet_enc.sqlite < config/database.sql

export:
	if [ ! -d "data/backup" ]; then mkdir data/backup ; fi
	sqlite3 -header -csv data/puppet_enc.sqlite "select * from Nodes" > data/backup/nodes_database.csv
	sqlite3 -header -csv data/puppet_enc.sqlite "select * from TemporaryEnvironmentConfiguration" > data/backup/environments_database.csv