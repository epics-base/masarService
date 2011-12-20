PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
DROP TABLE IF EXISTS "alias";
CREATE TABLE "alias" (
  "alias_id" INTEGER ,
  "pv_id" int(11) NOT NULL DEFAULT '0',
  "alias" varchar(50) DEFAULT NULL,
  PRIMARY KEY ("alias_id")
  CONSTRAINT "Ref_185" FOREIGN KEY ("pv_id") REFERENCES "pv" ("pv_id") ON DELETE NO ACTION ON UPDATE NO ACTION
);
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
DROP TABLE IF EXISTS "pv_attr";
CREATE TABLE "pv_attr" (
  "pv_attr_id" INTEGER ,
  "pv_id" int(11) NOT NULL DEFAULT '0',
  "pv_attrtype_id" int(11) DEFAULT NULL,
  "pv_attr" varchar(255) DEFAULT NULL,
  PRIMARY KEY ("pv_attr_id")
  CONSTRAINT "Ref_151" FOREIGN KEY ("pv_id") REFERENCES "pv" ("pv_id") ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT "Ref_118" FOREIGN KEY ("pv_attrtype_id") REFERENCES "pv_attrtype" ("pv_attrtype_id") ON DELETE NO ACTION ON UPDATE NO ACTION
);
DROP TABLE IF EXISTS "pv_attrtype";
CREATE TABLE "pv_attrtype" (
  "pv_attrtype_id" INTEGER ,
  "pv_attrtype_name" varchar(50) DEFAULT NULL,
  "pv_attrtype_desc" varchar(255) DEFAULT NULL,
  PRIMARY KEY ("pv_attrtype_id")
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
DROP TABLE IF EXISTS "pv_rel";
CREATE TABLE "pv_rel" (
  "pv_rel_id" INTEGER ,
  "rel_type" varchar(50) DEFAULT NULL,
  "parent_pv_id" int(11) NOT NULL DEFAULT '0',
  "child_pv_id" int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY ("pv_rel_id")
  CONSTRAINT "Ref_154" FOREIGN KEY ("parent_pv_id") REFERENCES "pv" ("pv_id") ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT "Ref_155" FOREIGN KEY ("child_pv_id") REFERENCES "pv" ("pv_id") ON DELETE NO ACTION ON UPDATE NO ACTION
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
DROP TABLE IF EXISTS "renamed_pv";
CREATE TABLE "renamed_pv" (
  "renamed_pv_id" INTEGER ,
  "pv_id" int(11) DEFAULT '0',
  "new_pv_name" varchar(50) DEFAULT NULL,
  "old_pv_name" varchar(50) DEFAULT NULL,
  "old_pv_desc" varchar(255) DEFAULT NULL,
  "old_pv_end_date" datetime DEFAULT NULL,
  PRIMARY KEY ("renamed_pv_id")
  CONSTRAINT "Ref_195" FOREIGN KEY ("pv_id") REFERENCES "pv" ("pv_id") ON DELETE NO ACTION ON UPDATE NO ACTION
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
CREATE INDEX "renamed_pv_Ref_195" ON "renamed_pv" ("pv_id");
CREATE INDEX "pv__pvgroup_idx_pv_id" ON "pv__pvgroup" ("pv_id");
CREATE INDEX "pv__pvgroup_idx_pvgroup_id" ON "pv__pvgroup" ("pv_group_id");
CREATE INDEX "pvgroup__serviceconfig_Ref_09" ON "pvgroup__serviceconfig" ("service_config_id");
CREATE INDEX "pvgroup__serviceconfig_Ref_137" ON "pvgroup__serviceconfig" ("pv_group_id");
CREATE INDEX "pv_rel_Ref_154" ON "pv_rel" ("parent_pv_id");
CREATE INDEX "pv_rel_Ref_155" ON "pv_rel" ("child_pv_id");
CREATE INDEX "masar_data_Ref_10" ON "masar_data" ("service_event_id");
CREATE INDEX "service_config_prop_Ref_12" ON "service_config_prop" ("service_config_id");
CREATE INDEX "pv_attr_Ref_151" ON "pv_attr" ("pv_id");
CREATE INDEX "pv_attr_Ref_118" ON "pv_attr" ("pv_attrtype_id");
CREATE INDEX "pv_idx_pv_name" ON "pv" ("pv_name");
CREATE INDEX "alias_Ref_185" ON "alias" ("pv_id");
CREATE INDEX "service_event_prop_Ref_11" ON "service_event_prop" ("service_event_id");
COMMIT;
