resource "oci_identity_dynamic_group" "wings_quota_function" {
  compartment_id = var.tenancy_ocid

  name        = "wings-quota-function-dg"
  description = "Allows WINGS AI quota protection Function to manage usage and stop the WINGS instance."

  matching_rule = "ALL {resource.type = 'fnfunc', resource.id = '${oci_functions_function.wings_quota.id}'}"
}


resource "oci_identity_policy" "wings_quota_function" {
  compartment_id = var.tenancy_ocid

  name        = "wings-quota-function-policy"
  description = "Permissions for WINGS AI quota protection."

  statements = [
    "Allow dynamic-group wings-quota-function-dg to read usage-reports in tenancy",
    "Allow dynamic-group wings-quota-function-dg to read instances in tenancy",
    "Allow dynamic-group wings-quota-function-dg to use instance-family in tenancy"
  ]
}