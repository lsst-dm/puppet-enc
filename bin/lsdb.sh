#!/bin/bash

DB_CMD=/usr/bin/sqlite3
PATH=$( /bin/readlink -e $0 )
DIR=$( /bin/dirname $PATH )
DB=${DIR}/puppet_enc.sqlite

$DB_CMD -header $DB 'select * from Nodes' | /usr/bin/column -t -s '|'
