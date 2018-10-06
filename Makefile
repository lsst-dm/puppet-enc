
configure:
	#Creates SQL file to import the configuration described in the hiera parameters.
	python3 bin/configuration.py etc/hiera_parameters.yaml config/database.sql

clean: clean_config clean_db

clean_config:
	rm -v config/database.sql

clean_db:
	rm data/puppet_enc.sqlite

import:
	sqlite3 data/puppet_enc.sqlite < config/database.sql
