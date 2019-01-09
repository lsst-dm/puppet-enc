#!/usr/bin/env python3.6
# Python ENC
# receives fqdn as argument

from datetime import datetime
import re
import yaml
import sqlite3
import argparse

def process_cmdline():
    """Process command line arguments. It is used to parse the arguments provided from the 
    command line or puppet. This script should be executed by default only by puppet, so 
    most likely to use the default value for the database location.

    Returns
    ----------
    """
    desc = "LSST Puppet ENC"
    parser = argparse.ArgumentParser( description=desc )
    parser.add_argument( '--dbfilename', '-d', 
        help="Sqlite3 database filename [default='%(default)s]'" )
    parser.add_argument( 'fqdn', metavar='FQDN' )
    defaults = { 
        'dbfilename': '/etc/puppetlabs/code/enc/data/puppet_enc.sqlite',
    }
    parser.set_defaults( **defaults )
    args = parser.parse_args()
    if len( args.fqdn ) < 1:
        raise SystemExit( 'missing FQDN' )
    return args


# This will return the node definition that best matches 
def find_node_definition(cursor, fqdn):
    """Find the node regex/node definition withim the SQlite provided database.
    The Nodes database is filled with node definitions/regex rather than FQDN to allow grouping
    server's behavior, in that way, the database only have generic names and specifications of which
    role has to be applied to each definition, regardles of the FQDN, in that way, you don't have a long list
    of nodes but a shorter one with generic definitions. Also you don't depend on a specific naming convention
    you only need a regex that can be easily changed. This function will return the longest match found between
    the FQDN received and the nodes definition stored in the DB.

    Parameters
    ----------
        cursor: `sqlite3.Connection.cursor`
            Cursor used to interact with the database
        fqdn: `str`
            Fully Qualified Domain Name, used to determine which role must be applied.

    Returns
    ----------
        node_def: `str` or `None`
            The node definition that best match the FQDN received or `None` if none is found. 
    """
    sql = "SELECT node_definition FROM Nodes"
    node_regex = cursor.execute( sql )
    selected_definition = ""
    aux = ""
    for n in node_regex:
        aux = re.search(n[0],fqdn)
        if aux != None and len(str(aux.group(0))) > len(selected_definition):
            selected_definition = aux
    if selected_definition == "":
        return None
    else:
        return selected_definition.group(0)

def find_temporary_environment(cursor, fqdn):
    """Find if there is any temporary environment definition for a given node.
    There are situations in where you want to try a configuration in production for 
    a given and fixed time, so, there is a table in the sqlite database that has that 
    information. Ideally that Table will have only FQDN just for a given amount of nodes
    in where that new environment should be applied. If there is a FQDN in there, then 
    that environment is returned, otherwhise None is returned. The temporary environments
    configuration table also have an starting date and ending date in where that configuration
    is valid, if that start date is not met, then this function will return null, if end date
    has been reached, this function will delete that server from the environments database and
    return None as well.

    Parameters
    ----------
        cursor: `sqlite3.Connection.cursor`
            Cursor used to interact with the database
        fqdn: `str`
            Fully Qualified Domain Name, used to determine which role must be applied.

    Returns
    ----------
        environment: `str` or `None`
            If no temporary configuration was found for this given FQDN and `str` if an environment 
            stored in the DB has to be applied to that FQDN in the given period of time.
    """
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
            #print("Delete this host from the environments database")
            cursor.execute( "DELETE FROM TemporaryEnvironmentConfiguration WHERE fqdn=(?)", (fqdn,) )
            return None
        if conf_start > today:
            #print("This environment shouldn't be used yet")
            return None
        else:
            #print("This is the environment that should be used for this host during this period")
            return rv["environment"]

#TODO Improve the query in such a way that can be inferred from hiera_parameters.yaml
def sql_lookup( dbfn, node ):
    """Lookup fqdn in database and return hash of values for parameters defined in hiera
    This function will use the FQDN to find the exact match in the DB by using function:
    find_node_definition, then will try to verify if there is any temporary definition
    that should be applied to that node using function: find_temporary_environment
    Finally, based on the received information it will either look all the parameters
    related with the node definition that best fit the FQDN received and will return it
    as a hash parameter_name: value. If a temporary definition is found, then that
    environment will be replaced by the one stored by default in the Nodes database.
    Finally if no definitions were found for the received FQDN, then this function
    will return None

    Parameters
    ----------
        dbfn: `str`
            sqlite3 database filename
        node: `str`
            fully qualified domain name of a given node
    
    Returns
    ----------
        parameters_hash: `None` or `Hash`
            `None` If no definitions were found. `Hash` If a node definition was found 
            in the database. The hash has to format of db_column_name: value

    """
    conn = sqlite3.connect( dbfn )
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    node_definition = find_node_definition(c, node)
    temp_env = find_temporary_environment(c, node)

    if node_definition == None:
        return {}
    else:
        sql = "select * from Nodes where node_definition = '" + node_definition + "'"
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
    """Output_yaml renders the hash as yaml and exits cleanly
    """
    # output the ENC as yaml
    print ("---")
    print (yaml.dump(enc))


def run():
    """It will search in the DB for the right environment to be applied to the received FQDN either
    in a temporary manner or the default and production configuration to finally print it in YAML format
    """
    args = process_cmdline()

    # basics
    classes = []
    parms = { "enc_hostname": args.fqdn }

    # Get info from DB

    db_data = sql_lookup( args.dbfilename, args.fqdn )

    # Attempt to extract environment from DB or use default value 'production'
    env = db_data.pop( 'environment', 'develop' )

    # Get classes from DB if any declared, this is a semi-colon separated string in the DB
    classes_text = db_data.pop('classes', '')
    if classes_text != '' :
        for c in classes_text.split(";"):
            classes.append(c)

    # Fill in additional details from DB
    parms.update( db_data )
    try:
        role = db_data[ 'role' ]
        classes.append( role )
    except ( KeyError ) as e:
        classes.append( "role::default" )
    else:
        if len(classes) == 0:
            classes = [ "role::default" ]
    
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
