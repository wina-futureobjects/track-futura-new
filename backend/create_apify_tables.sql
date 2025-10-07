BEGIN;
--
-- Create model ApifyConfig
--
CREATE TABLE "apify_integration_apifyconfig" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(100) NOT NULL, "platform" varchar(30) NOT NULL UNIQUE, "api_token" varchar(255) NOT NULL, "actor_id" varchar(100) NOT NULL, "is_active" bool NOT NULL, "description" text NULL, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL);
--
-- Create model ApifyWebhookEvent
--
CREATE TABLE "apify_integration_apifywebhookevent" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "event_id" varchar(255) NOT NULL UNIQUE, "run_id" varchar(255) NOT NULL, "status" varchar(20) NOT NULL, "platform" varchar(50) NOT NULL, "raw_data" text NOT NULL CHECK ((JSON_VALID("raw_data") OR "raw_data" IS NULL)), "processed_at" datetime NULL, "created_at" datetime NOT NULL);
--
-- Create model ApifyBatchJob
--
CREATE TABLE "apify_integration_apifybatchjob" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(200) NOT NULL, "source_folder_ids" text NOT NULL CHECK ((JSON_VALID("source_folder_ids") OR "source_folder_ids" IS NULL)), "platforms_to_scrape" text NOT NULL CHECK ((JSON_VALID("platforms_to_scrape") OR "platforms_to_scrape" IS NULL)), "content_types_to_scrape" text NOT NULL CHECK ((JSON_VALID("content_types_to_scrape") OR "content_types_to_scrape" IS NULL)), "num_of_posts" integer NOT NULL, "start_date" date NULL, "end_date" date NULL, "auto_create_folders" bool NOT NULL, "output_folder_pattern" varchar(200) NOT NULL, "platform_params" text NOT NULL CHECK ((JSON_VALID("platform_params") OR "platform_params" IS NULL)), "status" varchar(20) NOT NULL, "total_sources" integer NOT NULL, "processed_sources" integer NOT NULL, "successful_requests" integer NOT NULL, "failed_requests" integer NOT NULL, "job_metadata" text NOT NULL CHECK ((JSON_VALID("job_metadata") OR "job_metadata" IS NULL)), "error_log" text NULL, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL, "started_at" datetime NULL, "completed_at" datetime NULL, "project_id" bigint NOT NULL REFERENCES "users_project" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model ApifyScraperRequest
--
CREATE TABLE "apify_integration_apifyscraperrequest" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "platform" varchar(50) NOT NULL, "content_type" varchar(50) NOT NULL, "target_url" varchar(200) NOT NULL, "source_name" varchar(200) NOT NULL, "status" varchar(20) NOT NULL, "request_id" varchar(255) NULL, "error_message" text NULL, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL, "started_at" datetime NULL, "completed_at" datetime NULL, "batch_job_id" bigint NOT NULL REFERENCES "apify_integration_apifybatchjob" ("id") DEFERRABLE INITIALLY DEFERRED, "config_id" bigint NOT NULL REFERENCES "apify_integration_apifyconfig" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model ApifyNotification
--
CREATE TABLE "apify_integration_apifynotification" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "run_id" varchar(255) NOT NULL, "status" varchar(50) NOT NULL, "message" text NOT NULL, "raw_data" text NOT NULL CHECK ((JSON_VALID("raw_data") OR "raw_data" IS NULL)), "request_ip" char(39) NULL, "request_headers" text NOT NULL CHECK ((JSON_VALID("request_headers") OR "request_headers" IS NULL)), "created_at" datetime NOT NULL, "scraper_request_id" bigint NULL REFERENCES "apify_integration_apifyscraperrequest" ("id") DEFERRABLE INITIALLY DEFERRED);

CREATE INDEX "apify_integration_apifybatchjob_project_id_1e842eb2" ON "apify_integration_apifybatchjob" ("project_id");
CREATE INDEX "apify_integration_apifyscraperrequest_batch_job_id_4b86cc25" ON "apify_integration_apifyscraperrequest" ("batch_job_id");
CREATE INDEX "apify_integration_apifyscraperrequest_config_id_7ffa2da1" ON "apify_integration_apifyscraperrequest" ("config_id");
CREATE INDEX "apify_integration_apifynotification_scraper_request_id_d34f6e13" ON "apify_integration_apifynotification" ("scraper_request_id");
COMMIT;