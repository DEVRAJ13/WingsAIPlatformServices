resource "oci_core_instance" "wings" {
  compartment_id = var.compartment_ocid

  display_name = "wings-server"

  availability_domain = var.a1_availability_domain


  # ============================================================
  # LOCKED ALWAYS FREE SHAPE
  # ============================================================

  shape = "VM.Standard.A1.Flex"


  shape_config {
    # ALWAYS FREE
    ocpus = 2

    # ALWAYS FREE
    memory_in_gbs = 12
  }


  # ============================================================
  # UBUNTU ARM64
  # ============================================================

  source_details {
    source_type = "image"

    source_id = data.oci_core_images.ubuntu_arm64.images[0].id

    # 50 GB
    boot_volume_size_in_gbs = 50
  }


  # ============================================================
  # NETWORK
  # ============================================================

  create_vnic_details {
    subnet_id = oci_core_subnet.public.id

    assign_public_ip = true

    display_name = "wings-vnic"

    hostname_label = "wings-server"
  }


  # ============================================================
  # SSH
  # ============================================================

  metadata = {
    ssh_authorized_keys = var.ssh_public_key

    user_data = base64encode(
      file("${path.module}/cloud-init.yaml")
    )
  }


  # ============================================================
  # TAGS
  # ============================================================

  freeform_tags = local.common_tags


  # ============================================================
  # SAFETY
  # ============================================================

  lifecycle {
    prevent_destroy = true
  }
}