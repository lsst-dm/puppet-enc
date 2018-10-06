DROP TABLE IF EXISTS Nodes;
CREATE TABLE "Nodes" (
	"node_definition"  TEXT UNIQUE NOT NULL Primary Key,
	"site"  TEXT NOT NULL,
	"datacenter"  TEXT NOT NULL,
	"cluster"  TEXT NOT NULL,
	"role"  TEXT NOT NULL,
	"environment"  TEXT NOT NULL
);
.separator ","
.import config/nodes_database.csv Nodes
DROP TABLE IF EXISTS TemporaryEnvironmentConfiguration;
CREATE TABLE "TemporaryEnvironmentConfiguration" (
	"fqdn"  TEXT UNIQUE NOT NULL,
	"environment"  TEXT NOT NULL,
	"ConfTimeStart"  TEXT NOT NULL Primary Key,
	"ConfTimeEnd"  TEXT NOT NULL
);
.separator ","
.import config/environments_database.csv TemporaryEnvironmentConfiguration
