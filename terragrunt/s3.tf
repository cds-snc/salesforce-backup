module "cds_salesforce_backups_bucket" {
  source = "github.com/cds-snc/terraform-modules?ref=v6.0.2//S3"

  bucket_name        = "cds-salesforce-backups"
  billing_tag_value  = var.billing_code
  critical_tag_value = "true"

  logging = {
    target_bucket = module.cds_salesforce_backups_logs_bucket.s3_bucket_id
  }

  versioning = {
    enabled = true
  }

}

module "cds_salesforce_backups_logs_bucket" {
  source = "github.com/cds-snc/terraform-modules?ref=v6.0.2//S3_log_bucket"

  bucket_name       = "cds-salesforce-backups-access-logs"
  billing_tag_value = var.billing_code

}