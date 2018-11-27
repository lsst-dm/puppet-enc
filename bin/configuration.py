#!/usr/bin/env python3.6

import sys 
import os.path
import yaml

# This function return a list of columns and its parameters
def create_columns_definition(database_definition):
    columns_definition = []
    for item in database_definition:
        attribute = ""
        for attr in database_definition[item]:
            attribute += " " + attr
        columns_definition.append( "\"" + item + "\" " + attribute)
    return columns_definition

def create_db_definitions(db_conf_definition):
    db_dic_definition = dict()
    db_dic_definition["table_name"] = db_conf_definition["table_name"]
    db_dic_definition["drop_if_exists"] = db_conf_definition["drop_if_exists"]
    db_dic_definition["csv_filepath"] = db_conf_definition["csv_filepath"]
    db_dic_definition["csv_separator"] = db_conf_definition["csv_separator"]
    database_definition = db_conf_definition["database_definition"]
    db_dic_definition["columns"] = create_columns_definition(database_definition)
    return db_dic_definition

def create_sql_file(databases_list, output_filename):
    output_file = open(output_filename, "w+")
    for db in databases_list:
        if db["drop_if_exists"]:
            output_file.write("DROP TABLE IF EXISTS " + db["table_name"] +";\n")
        output_file.write("CREATE TABLE \"" + db["table_name"] + "\" (\n" )
        columns = ",\n\t".join(db["columns"])
        output_file.write("\t"+ columns + "\n")
        output_file.write(");\n")
        output_file.write(".separator \""+db["csv_separator"]+"\"\n")
        output_file.write(".import " + db["csv_filepath"] + " " + db["table_name"] +"\n")

if len(sys.argv) < 1:
    print("You must give a hiera file to import the configuration and create the sql file")
elif not os.path.isfile(sys.argv[1]):
    print("File",sys.argv[1],"doesn't exists")
else:
    conf_file = yaml.load(open(sys.argv[1]))
    databases_list = []
    output_filename = sys.argv[2]
    for Databases in conf_file:
        databases_list.append(create_db_definitions(conf_file[Databases]))
    
    create_sql_file(databases_list, output_filename)
    