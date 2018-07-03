#!/usr/bin/bash

DB_CMD=/usr/bin/sqlite3
PATH=$( /bin/readlink -e $0 )
PGM=$( /bin/basename $PATH )
DIR=$( /bin/dirname $PATH )
DB=${DIR}/puppet_enc.sqlite


function usage() {
    /bin/cat <<ENDHERE

USAGE:

$PGM <NODENAME> <ATTRIBUTE> <VALUE>

Change value of attribute in DB for specified node.


ENDHERE
}

if [[ $# -ne 3 ]] ; then
    usage
    exit 1
fi

node="$1"
attr="$2"
val="$3"

SQL=" UPDATE Nodes SET $attr = \"$val\" WHERE fqdn=\"$node\";
      SELECT changes() FROM Nodes;"

rv=$( $DB_CMD $DB "$SQL" | /bin/head -1 )
echo "Num Rows Affected: $rv"
echo "New DB record(s) ..."
${DIR}/lsnode.sh $node


