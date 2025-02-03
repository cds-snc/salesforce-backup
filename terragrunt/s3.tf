module "cds_salesforce_backups_bucket" {
  source = "github.com/cds-snc/terraform-modules//S3?ref=v5.1.11"
  replication_configuration = {
    role = aws_iam_role.salesforce_replicate.arn

    rules = [
      {
        id       = "send-to-data-lake"
        priority = 10
        destination = {
          bucket = local.data_lake_raw_s3_bucket_arn
        }
      }
    ]
  }

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
  source = "github.com/cds-snc/terraform-modules//S3?ref=v5.1.11"

  bucket_name       = "cds-salesforce-backups-access-logs"
  billing_tag_value = var.billing_code

}