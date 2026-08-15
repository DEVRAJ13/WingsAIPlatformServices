# ============================================================
# WINGS AI PLATFORM
# ALWAYS-FREE SAFETY CHECKS
# ============================================================

check "always_free_compute" {
  assert {
    condition = (
      local.compute_shape == "VM.Standard.A1.Flex" &&
      local.compute_ocpus == 2 &&
      local.compute_memory_gb == 12 &&
      local.boot_volume_gb == 50
    )

    error_message = <<-EOT
      BLOCKED.

      WINGS is restricted to:

      Shape  : VM.Standard.A1.Flex
      OCPU   : 2
      Memory : 12 GB
      Disk   : 50 GB
    EOT
  }
}


check "always_free_network" {
  assert {
    condition = (
      local.vcn_cidr == "10.0.0.0/16" &&
      local.public_subnet_cidr == "10.0.1.0/24"
    )

    error_message = "BLOCKED: Network configuration does not match the locked WINGS design."
  }
}