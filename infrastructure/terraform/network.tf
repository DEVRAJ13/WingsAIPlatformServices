resource "oci_core_vcn" "wings" {
  compartment_id = var.compartment_ocid

  display_name = "wings-vcn"

  cidr_blocks = [
    local.vcn_cidr
  ]

  dns_label = "wingsvcn"

  freeform_tags = local.common_tags
}


resource "oci_core_internet_gateway" "wings" {
  compartment_id = var.compartment_ocid

  vcn_id = oci_core_vcn.wings.id

  display_name = "wings-internet-gateway"

  enabled = true

  freeform_tags = local.common_tags
}


resource "oci_core_route_table" "public" {
  compartment_id = var.compartment_ocid

  vcn_id = oci_core_vcn.wings.id

  display_name = "wings-public-route-table"

  route_rules {
    destination = "0.0.0.0/0"

    destination_type = "CIDR_BLOCK"

    network_entity_id = oci_core_internet_gateway.wings.id
  }

  freeform_tags = local.common_tags
}


resource "oci_core_subnet" "public" {
  compartment_id = var.compartment_ocid

  vcn_id = oci_core_vcn.wings.id

  display_name = "wings-public-subnet"

  cidr_block = local.public_subnet_cidr

  route_table_id = oci_core_route_table.public.id

  security_list_ids = [
    oci_core_security_list.wings.id
  ]

  dns_label = "public"

  prohibit_public_ip_on_vnic = false

  freeform_tags = local.common_tags
}