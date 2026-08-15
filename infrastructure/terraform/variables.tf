variable "tenancy_ocid" {
  description = "OCI tenancy OCID"
  type        = string
  sensitive   = true
}

variable "user_ocid" {
  description = "OCI Terraform user OCID"
  type        = string
  sensitive   = true
}

variable "fingerprint" {
  description = "OCI API key fingerprint"
  type        = string
  sensitive   = true
}

variable "private_key_path" {
  description = "OCI API private key path"
  type        = string
}

variable "region" {
  description = "OCI home region"
  type        = string

  validation {
    condition     = trimspace(var.region) != ""
    error_message = "OCI home region is required."
  }
}

variable "compartment_ocid" {
  description = "OCI compartment OCID"
  type        = string
}

variable "a1_availability_domain" {
  description = "Availability Domain for the Always Free A1 VM"
  type        = string
}

variable "ssh_public_key" {
  description = "SSH public key"
  type        = string
}

variable "ssh_source_cidr" {
  description = "CIDR allowed to SSH to the server, normally your-public-ip/32"
  type        = string

  validation {
    condition     = can(cidrhost(var.ssh_source_cidr, 0))
    error_message = "ssh_source_cidr must be a valid CIDR, for example 49.36.100.25/32."
  }
}