DROP TABLE IF EXISTS Nodes;


CREATE TABLE "Nodes" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "fqdn" TEXT UNIQUE NOT NULL,
  "site" TEXT NOT NULL,
  "datacenter" TEXT NOT NULL,
  "cluster" TEXT NOT NULL,
  "role" TEXT NOT NULL,
  "environment" TEXT NOT NULL
);


.separator ","
.import puppet_enc_sqlite_source.csv Nodes
