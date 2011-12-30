PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
DROP TABLE IF EXISTS "masar_data";
CREATE TABLE "masar_data" (
  "masar_data_id" INTEGER ,
  "service_event_id" int(11) NOT NULL DEFAULT '0',
  "pv_name" varchar(50) DEFAULT NULL,
  "value" varchar(50) DEFAULT NULL,
  "status" int(11) DEFAULT NULL,
  "severity" int(11) DEFAULT NULL,
  "ioc_timestamp" int(11)  NOT NULL,
  "ioc_timestamp_nano" int(11)  NOT NULL,
  PRIMARY KEY ("masar_data_id")
  CONSTRAINT "Ref_10" FOREIGN KEY ("service_event_id") REFERENCES "service_event" ("service_event_id") ON DELETE NO ACTION ON UPDATE NO ACTION
);
DROP TABLE IF EXISTS "pv";
CREATE TABLE "pv" (
  "pv_id" INTEGER ,
  "pv_name" varchar(128) NOT NULL,
  "description" text,
  PRIMARY KEY ("pv_id")
);
DROP TABLE IF EXISTS "pv__pvgroup";
CREATE TABLE "pv__pvgroup" (
  "pv__pvgroup_id" INTEGER ,
  "pv_id" int(11) NOT NULL DEFAULT '0',
  "pv_group_id" int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY ("pv__pvgroup_id")
  CONSTRAINT "Ref_92" FOREIGN KEY ("pv_id") REFERENCES "pv" ("pv_id") ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT "Ref_95" FOREIGN KEY ("pv_group_id") REFERENCES "pv_group" ("pv_group_id") ON DELETE NO ACTION ON UPDATE NO ACTION
);
DROP TABLE IF EXISTS "pv_group";
CREATE TABLE "pv_group" (
  "pv_group_id" INTEGER ,
  "pv_group_name" varchar(50) DEFAULT NULL,
  "pv_group_func" varchar(50) DEFAULT NULL,
  "pvg_creation_date" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "version" varchar(50) DEFAULT NULL,
  PRIMARY KEY ("pv_group_id")
);
DROP TABLE IF EXISTS "pvgroup__serviceconfig";
CREATE TABLE "pvgroup__serviceconfig" (
  "pvgroup__serviceconfig_id" INTEGER ,
  "pv_group_id" int(11) NOT NULL DEFAULT '0',
  "service_config_id" int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY ("pvgroup__serviceconfig_id")
  CONSTRAINT "Ref_09" FOREIGN KEY ("service_config_id") REFERENCES "service_config" ("service_config_id") ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT "Ref_137" FOREIGN KEY ("pv_group_id") REFERENCES "pv_group" ("pv_group_id") ON DELETE NO ACTION ON UPDATE NO ACTION
);
DROP TABLE IF EXISTS "service";
CREATE TABLE "service" (
  "service_id" INTEGER ,
  "service_name" varchar(50) DEFAULT NULL,
  "service_desc" varchar(255) DEFAULT NULL,
  PRIMARY KEY ("service_id")
);
DROP TABLE IF EXISTS "service_config";
CREATE TABLE "service_config" (
  "service_config_id" INTEGER ,
  "service_id" int(11) NOT NULL DEFAULT '0',
  "service_config_name" varchar(50) DEFAULT NULL,
  "service_config_desc" varchar(255) DEFAULT NULL,
  "service_config_version" int(11) DEFAULT NULL,
  "service_config_create_date" timestamp NOT NULL ,
  PRIMARY KEY ("service_config_id")
  CONSTRAINT "Ref_197" FOREIGN KEY ("service_id") REFERENCES "service" ("service_id") ON DELETE NO ACTION ON UPDATE NO ACTION
);
DROP TABLE IF EXISTS "service_config_prop";
CREATE TABLE "service_config_prop" (
  "service_config_prop_id" INTEGER ,
  "service_config_id" int(11) NOT NULL DEFAULT '0',
  "service_config_prop_name" varchar(2555) DEFAULT NULL,
  "service_config_prop_value" varchar(255) DEFAULT NULL,
  PRIMARY KEY ("service_config_prop_id")
  CONSTRAINT "Ref_12" FOREIGN KEY ("service_config_id") REFERENCES "service_config" ("service_config_id") ON DELETE NO ACTION ON UPDATE NO ACTION
);
DROP TABLE IF EXISTS "service_event";
CREATE TABLE "service_event" (
  "service_event_id" INTEGER ,
  "service_config_id" int(11) NOT NULL DEFAULT '0',
  "service_event_user_tag" varchar(255) DEFAULT NULL,
  "service_event_UTC_time" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  "service_event_serial_tag" varchar(50) DEFAULT NULL,
  PRIMARY KEY ("service_event_id")
  CONSTRAINT "Ref_08" FOREIGN KEY ("service_config_id") REFERENCES "service_config" ("service_config_id") ON DELETE NO ACTION ON UPDATE NO ACTION
);
DROP TABLE IF EXISTS "service_event_prop";
CREATE TABLE "service_event_prop" (
  "service_event_prop_id" INTEGER ,
  "service_event_id" int(11) NOT NULL DEFAULT '0',
  "service_event_prop_name" varchar(255) DEFAULT NULL,
  "service_event_prop_value" varchar(50) DEFAULT NULL,
  PRIMARY KEY ("service_event_prop_id")
  CONSTRAINT "Ref_11" FOREIGN KEY ("service_event_id") REFERENCES "service_event" ("service_event_id") ON DELETE NO ACTION ON UPDATE NO ACTION
);
CREATE INDEX "service_config_Ref_197" ON "service_config" ("service_id");
CREATE INDEX "service_event_Ref_08" ON "service_event" ("service_config_id");
CREATE INDEX "pv__pvgroup_idx_pv_id" ON "pv__pvgroup" ("pv_id");
CREATE INDEX "pv__pvgroup_idx_pvgroup_id" ON "pv__pvgroup" ("pv_group_id");
CREATE INDEX "pvgroup__serviceconfig_Ref_09" ON "pvgroup__serviceconfig" ("service_config_id");
CREATE INDEX "pvgroup__serviceconfig_Ref_137" ON "pvgroup__serviceconfig" ("pv_group_id");
CREATE INDEX "masar_data_Ref_10" ON "masar_data" ("service_event_id");
CREATE INDEX "service_config_prop_Ref_12" ON "service_config_prop" ("service_config_id");
CREATE INDEX "pv_idx_pv_name" ON "pv" ("pv_name");
CREATE INDEX "service_event_prop_Ref_11" ON "service_event_prop" ("service_event_id");
COMMIT;
