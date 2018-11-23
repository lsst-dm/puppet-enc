#!/bin/env python
# Python Database quick Nodes administrator

from prettytable import PrettyTable
import argparse
import sqlite3
import re

def process_cmdline():
    """Process command line arguments. It is used to parse the arguments provided from the 
    command line.

    Returns
    ----------
    args
    """
    desc = "LSST Nodes DB administrator"
    parser = argparse.ArgumentParser( description=desc )
    parser.add_argument( '--dbfilename', '-d', help="Sqlite3 database filename [default='%(default)s]'" )
    parser.add_argument('--listdb', '-l', help="Lists all the Nodes and all the temporary configuration within the given DB", action='store_true')
    parser.add_argument('--list-node', '-L', help="Lists all the parameters for a given Node and the temporary configuration if any", action='store_true')
    parser.add_argument('--update','-u', help="Update an attribute of a given Node definition", action='store_true')
    parser.add_argument('--attribute','-a', help="attribute to be updated to a given FQDN as key=value", action='append')
    parser.add_argument( '-fqdn', metavar='FQDN' )
    parser.add_argument( '--node-def', metavar='NODE-DEF' )
    parser.add_argument( '--assign-env', help="Assign an environment to a given FQDN, use -a to indicate environments and dates. You can use as many as you need", action='store_true')
    parser.add_argument( '--new-temp-node', help="Assign a temporary environment to a new node", action='store_true')
    defaults = { 
        'dbfilename': '/etc/puppetlabs/code/enc/data/puppet_enc.sqlite',
    }
    parser.set_defaults( **defaults )
    args = parser.parse_args()
    return args

def db_print(column_names, data):
    """Prints in a nice format, using prettytable the content in data

    Parameters
    ----------
        column_names: `list`
            A list of string that represents the header of the table
        data: `list`
            Each row of the query
    """
    x = PrettyTable(column_names)
    x.align = "r"
    x.align[column_names[0]] = "l"
    x.padding_width = 1
    for row in data:
        x.add_row(row)
    print(x)

def list_db(cursor):
    """List the content of the Data Base

    Parameters
    ----------
        cursor: `sqlite3.Connection.cursor`
            Cursor used to interact with the database
    """
    for tables in ["Nodes", "TemporaryEnvironmentConfiguration"]:
        print("Displaying", tables, "content")
        rows = cursor.execute( "SELECT * FROM " + tables  )
        col_names = [cn[0] for cn in cursor.description]
        db_print(col_names, rows)

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


def list_node(cursor, fqdn, node_def):
    """List all the details of a given node by either FQDN or Node Definition. It will print
    either the information in Node or in TemporaryEnvironmentConfiguration.

    Parameters
    ----------
        cursor: `sqlite3.Connection.cursor`
            Cursor used to interact with the database
        fqdn: `str`
            The fully qualified domain name in case specified in the command line
        node_def: `str`
            An string to match the node definition in the Nodes db
    """
    node_definition = ""
    if fqdn == None and node_def != None:
        node_definition = node_def
    elif fqdn != None and node_def ==  None:
        node_definition = find_node_definition(cursor,fqdn)
    rows = cursor.execute( "SELECT * FROM Nodes WHERE node_definition=?", (node_definition,) )
    col_names = [cn[0] for cn in cursor.description]
    db_print(col_names, rows)

    if fqdn != None:
        rows = cursor.execute( "SELECT * FROM TemporaryEnvironmentConfiguration WHERE fqdn=?", (fqdn,) )
        col_names = [cn[0] for cn in cursor.description]
        db_print(col_names, rows)

def update(cursor, table, pk, node_def, parameter_list):
    """Update the parameters of a given FQDN in the TemporaryEnvironmentConfiguration

    Parameters
    ----------
        cursor: `sqlite3.Connection.cursor`
            Cursor used to interact with the database
        table: `str`
            The table name in where the data should be updated
        node_def: `str`
            In case node definition is specified, that string is used to get data.
        parameter_list: `list`
            A list of parameters to update within the DB
    """
    for parameter in parameter_list:
        parsed_param = parameter.split("=")
        key = parsed_param[0]
        value = parsed_param[1]
        ows = cursor.execute( "UPDATE "+table+" SET " + key + " = '" + value + "' WHERE "+pk+"=?", (node_def,))

def insert_new_temp_node(cursor, parameter_list):
    """Insert a new node in the TemporaryEnvironmentConfiguration table.

    Parameters
    ----------
        cursor: `sqlite3.Connection.cursor`
            Cursor used to interact with the database
        parameter_list: `list`
            A list of parameters to update within the DB
    """
    keys = []
    values = []
    for parameter in parameter_list:
        parsed_param = parameter.split("=")
        keys.append(parsed_param[0])
        values.append("'"+parsed_param[1]+"'")

    sql = "INSERT INTO TemporaryEnvironmentConfiguration ("+",".join(keys)+") VALUES (" + ",".join(values) + ")"
    cursor.execute(sql)

def run():
    args = process_cmdline()
    conn = sqlite3.connect( args.dbfilename )
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    if args.listdb :
        list_db(c)
    elif args.list_node:
        list_node(c, args.fqdn, args.node_def)
    elif args.update:
        update(c,"Nodes", "node_definition",args.node_def, args.attribute)
    elif args.assign_env:
        update(c,"TemporaryEnvironmentConfiguration", "fqdn",args.fqdn, args.attribute)
    elif args.new_temp_node:
        insert_new_temp_node(c, args.attribute)
    conn.commit()
    c.close()

if __name__ == "__main__":
    run()

