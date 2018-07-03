#!/usr/bin/bash

DB_CMD=/usr/bin/sqlite3
PATH=$( /bin/readlink -e $0 )
PGM=$( /bin/basename $PATH )
DIR=$( /bin/dirname $PATH )
DB=${DIR}/puppet_enc.sqlite

function usage() {
    /bin/cat <<ENDHERE

Usage: $PGM <NODENAME>

Print row from DB matching nodename.

ENDHERE
}

if [[ $# -ne 1 ]] ; then
    usage
    exit 1
fi

SQL="SELECT * FROM Nodes WHERE fqdn LIKE \"%$1%\";"

$DB_CMD $DB -header -column "$SQL"
