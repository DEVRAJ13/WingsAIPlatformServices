data "oci_core_images" "ubuntu_arm64" {
  compartment_id = var.compartment_ocid

  operating_system = "Canonical Ubuntu"

  shape = local.compute_shape

  state = "AVAILABLE"

  sort_by = "TIMECREATED"

  sort_order = "DESC"
}