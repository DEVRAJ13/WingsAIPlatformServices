resource "oci_functions_application" "wings_quota" {
  compartment_id = var.compartment_ocid

  display_name = "wings-quota-protection"

  # ARM application for the ARM64 Docker image
  shape = "GENERIC_ARM"

  subnet_ids = [
    oci_core_subnet.private.id
  ]

  freeform_tags = merge(
    local.common_tags,
    {
      Purpose = "Quota-Protection"
    }
  )
}

resource "oci_functions_function" "wings_quota" {
  application_id = oci_functions_application.wings_quota.id

  display_name = "wings-quota-check"

  # ARM64 image stored in OCIR
  image = "bom.ocir.io/bmg2z11z8ndj/wings-quota-protection:1.0"

  memory_in_mbs = 256

  timeout_in_seconds = 60

  freeform_tags = merge(
    local.common_tags,
    {
      Purpose = "Quota-Protection"
    }
  )
}

