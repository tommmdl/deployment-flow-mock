variable "region" {
  type    = string
  default = "us-east-1"
}
variable "owner" { type = string }
variable "azs" {
  type    = list(string)
  default = ["us-east-1a", "us-east-1b"]
  validation {
    condition     = length(var.azs) == 2
    error_message = "Informe exatamente duas AZs."
  }
}
variable "admin_cidrs" {
  type = list(string)
  validation {
    condition     = length(var.admin_cidrs) > 0 && !contains(var.admin_cidrs, "0.0.0.0/0")
    error_message = "Restrinja o endpoint público aos IPs dos administradores."
  }
}
variable "kubernetes_version" {
  type    = string
  default = "1.35"
}
variable "budget_email" { type = string }
variable "budget_usd" {
  type    = number
  default = 250
}
