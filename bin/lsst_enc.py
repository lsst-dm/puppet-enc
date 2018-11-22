#!/bin/env python
# Python ENC
# receives fqdn as argument

from datetime import datetime
import re
import yaml
import sqlite3
import argparse


def process_cmdline():
    desc = "LSST Puppet ENC"
    parser = argparse.ArgumentParser( description=desc )
    parser.add_argument( '--dbfilename', '-d', 
        help="Sqlite3 database filename [default='%(default)s]'" )
    parser.add_argument( 'fqdn', metavar='FQDN' )
    defaults = { 
        'dbfilename': '/etc/puppetlabs/code/config/scripts/puppet_enc.sqlite',
    }
    parser.set_defaults( **defaults )
    args = parser.parse_args()
    if len( args.fqdn ) < 1:
        raise SystemExit( 'missing FQDN' )
    return args


# This will return the node definition that best matches 
def find_node_definition(cursor, fqdn):
    sql = "SELECT node_definition FROM Nodes"
    node_regex = cursor.execute( sql )
    selected_definition = None
    aux = ""
    for n in node_regex:
        pattern = re.compile(n[0])
        aux = re.search(pattern,fqdn)
        if aux != None and len(str(aux)) > len(str(selected_definition)):
            selected_definition = aux
    if selected_definition == None:
        return None
    else:
        return selected_definition.group(0)

def find_temporary_environment(cursor, fqdn):
    sql = "SELECT environment, ConfTimeStart, ConfTimeEnd FROM TemporaryEnvironmentConfiguration WHERE fqdn=?"
    cursor.execute( sql, (fqdn,) )
    r = cursor.fetchone()
    rv = {}
    if r is not None:
        rv = { k: str(r[k]) for k in r.keys() }
    
    if len(rv) == 0:
        return None
    else:
        conf_start = datetime.strptime(rv["ConfTimeStart"], '%Y-%m-%d %H:%M:%S')
        conf_end = datetime.strptime(rv["ConfTimeEnd"], '%Y-%m-%d %H:%M:%S')

        today = datetime.today()
        if conf_end < today:
            print("Delete this host from the environments database")
            cursor.execute( "DELETE FROM TemporaryEnvironmentConfiguration WHERE fqdn=(?)", (fqdn,) )
            return None
        if conf_start > today:
            print("This environment shouldn't be used yet")
            return None
        else:
            print("This is the environment that should be used for this host during this period")
            return rv["environment"]

#TODO Improve the query in such a way that can be inferred from hiera_parameters.yaml
def sql_lookup( dbfn, node ):
    """ def sql_lookup( dbfn, node ):
        Lookup fqdn in database and return hash of values for
        site,datacenter,cluster,role
        PARAMETERS:
            dbfn - string - sqlite3 database filename
            node - string - fully qualified domain name
    """
    conn = sqlite3.connect( dbfn )
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    node_definition = find_node_definition(c, node)
    temp_env = find_temporary_environment(c, node)

    if node_definition == None:
        return {}
    else:
        sql = "select site,datacenter,cluster,role,environment from Nodes where node_definition = '" + node_definition + "'"
        c.execute( sql )
        r = c.fetchone()
        rv = {}
        if r is not None:
            rv = { k: str(r[k]) for k in r.keys() }
        
        if temp_env != None:
            rv["environment"] = temp_env

        conn.commit()
        c.close()
        return rv


def output_yaml(enc):
    """ output_yaml renders the hash as yaml and exits cleanly
    """
    # output the ENC as yaml
    print ("---")
    print (yaml.dump(enc))


def run():
    args = process_cmdline()

    # basics
    classes = []
    parms = { "enc_hostname": args.fqdn }

    # Get info from DB
    db_data = sql_lookup( args.dbfilename, args.fqdn )

    # Attempt to extract environment from DB or use default value 'production'
    env = db_data.pop( 'environment', 'develop' )

    # Fill in additional details from DB
    parms.update( db_data )
    try:
        role = db_data[ 'role' ]
    except ( KeyError ) as e:
        classes.append( "role::default" )
    else:
        classes = [ '{0}'.format( role ) ]
    
    # build hash for yaml
    enc = { 
        "classes": classes,
        "parameters": parms,
        "environment": env,
    }

    # Return formatted yaml data
    output_yaml( enc )


if __name__ == "__main__":
    run()
