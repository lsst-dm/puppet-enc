#!/bin/env python
# Python ENC
# receives fqdn as argument

#import sys
#import re
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
    sql = "select site,datacenter,cluster,role,environment from Nodes where fqdn=?"
    c.execute( sql, (node,) )
    r = c.fetchone()
    rv = {}
    if r is not None:
        rv = { k: str(r[k]) for k in r.keys() }
    return rv


def output_yaml(enc):
    """ output_yaml renders the hash as yaml and exits cleanly
    """
    # output the ENC as yaml
    print "---"
    print yaml.dump(enc)


def run():
    args = process_cmdline()

    # basics
    classes = [ "role::default" ]
    parms = { "enc_hostname": args.fqdn }

    # Get info from DB
    db_data = sql_lookup( args.dbfilename, args.fqdn )

    # Attempt to extract environment from DB or use default value 'production'
    env = db_data.pop( 'environment', 'production' )

    # Fill in additional details from DB
    parms.update( db_data )
    try:
        role = db_data[ 'role' ]
    except ( KeyError ) as e:
        classes.append( "hostname_problem" )
    else:
        classes = [ 'role::{0}'.format( role ) ]
    
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
