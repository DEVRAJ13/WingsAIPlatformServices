resource "oci_core_security_list" "wings" {
  compartment_id = var.compartment_ocid

  vcn_id = oci_core_vcn.wings.id

  display_name = "wings-security-list"


  # ============================================================
  # SSH
  # ============================================================

  ingress_security_rules {
    protocol = "6"

    source = var.ssh_source_cidr

    tcp_options {
      min = local.ssh_port
      max = local.ssh_port
    }

    description = "SSH from administrator IP only"
  }


  # ============================================================
  # HTTP
  # ============================================================

  ingress_security_rules {
    protocol = "6"

    source = "0.0.0.0/0"

    tcp_options {
      min = local.http_port
      max = local.http_port
    }

    description = "HTTP"
  }


  # ============================================================
  # HTTPS
  # ============================================================

  ingress_security_rules {
    protocol = "6"

    source = "0.0.0.0/0"

    tcp_options {
      min = local.https_port
      max = local.https_port
    }

    description = "HTTPS"
  }


  # ============================================================
  # FASTAPI - TEMPORARY TESTING
  # ============================================================

  ingress_security_rules {
    protocol = "6"

    source = var.ssh_source_cidr

    tcp_options {
      min = 8000
      max = 8000
    }

    description = "FastAPI temporary access"
  }


  # ============================================================
  # PGADMIN - TEMPORARY ADMIN ACCESS
  # ============================================================

  ingress_security_rules {
    protocol = "6"

    source = var.ssh_source_cidr

    tcp_options {
      min = 5050
      max = 5050
    }

    description = "pgAdmin temporary access"
  }

  # ============================================================
  # OUTBOUND
  # ============================================================

  egress_security_rules {
    protocol = "all"

    destination = "0.0.0.0/0"

    description = "Outbound Internet"
  }


  freeform_tags = local.common_tags
}


