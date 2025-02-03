locals {
  salesforce_backup_role_name = "salesforce-backup"
}

module "oidc" {
  source = "github.com/cds-snc/terraform-modules//gh_oidc_role?ref=v5.1.11"

  billing_tag_value = var.billing_code

  oidc_exists = true

  roles = [
    {
      name      = local.salesforce_backup_role_name
      repo_name = "salesforce-backup"
      claim     = "ref:refs/heads/main"
    }
  ]
}

data "aws_iam_policy_document" "write_to_bucket" {
  // this statement allows writing to the cds-salesforce-backups s3 bucket
  statement {
    effect = "Allow"
    actions = [
      "s3:PutObject",
      "s3:ListBucket",
    ]
    resources = [
      module.cds_salesforce_backups_bucket.s3_bucket_arn,
      "${module.cds_salesforce_backups_bucket.s3_bucket_arn}/*",
    ]

  }
}

resource "aws_iam_policy" "write_to_bucket" {
  name   = "write_to_salesforce_bucket"
  policy = data.aws_iam_policy_document.write_to_bucket.json
}

resource "aws_iam_role_policy_attachment" "oidc" {
  role       = local.salesforce_backup_role_name
  policy_arn = aws_iam_policy.write_to_bucket.id

  depends_on = [
    module.oidc,
  ]
}

#
# Replicate the Salesforce data to the Data Lake
#
resource "aws_iam_role" "salesforce_replicate" {
  name               = "SalesforceReplicateToDataLake"
  assume_role_policy = data.aws_iam_policy_document.salesforce_replicate_assume.json
  tags               = local.common_tags
}
resource "aws_iam_policy" "salesforce_replicate" {
  name   = "SalesforceReplicateToDataLake"
  policy = data.aws_iam_policy_document.salesforce_replicate_assume.json
  tags   = local.common_tags
}
resource "aws_iam_role_policy_attachment" "salesforce_replicate" {
  role       = aws_iam_role.salesforce_replicate.name
  policy_arn = aws_iam_policy.salesforce_replicate.arn
}

data "aws_iam_policy_document" "salesforce_replicate_assume" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals {
      type = "Service"
      identifiers = [
        "s3.amazonaws.com"
      ]
    }
  }
}

data "aws_iam_policy_document" "salesforce_replicate" {
  statement {
    effect = "Allow"
    actions = [
      "s3:GetReplicationConfiguration",
      "s3:ListBucket"
    ]
    resources = [
      module.cds_salesforce_backups_bucket.s3_bucket_arn
    ]
  }
  statement {
    effect = "Allow"
    actions = [
      "s3:GetObjectVersion",
      "s3:GetObjectVersionAcl"
    ]
    resources = [
      "${module.cds_salesforce_backups_bucket.s3_bucket_arn}/*"
    ]
  }
  statement {
    effect = "Allow"
    actions = [
      "s3:ObjectOwnerOverrideToBucketOwner",
      "s3:ReplicateObject",
      "s3:ReplicateDelete"
    ]
    resources = [
      "${local.data_lake_raw_s3_bucket_arn}/*"
    ]
  }
}