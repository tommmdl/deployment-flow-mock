terraform {
  required_version = "= 1.16.5"
  required_providers {
    aws = { source = "hashicorp/aws", version = "= 6.68.0" }
  }
  backend "s3" {}
}
provider "aws" {
  region = var.region
  default_tags {
    tags = { Project = "deployment-flow", Environment = "production", Owner = var.owner, CostCenter = "portfolio", ManagedBy = "terraform" }
  }
}
