locals {

  # ============================================================
  # PROJECT
  # ============================================================

  project_name = "wings-ai-platform"

  environment = "always-free"


  # ============================================================
  # LOCKED OCI ALWAYS FREE COMPUTE
  # ============================================================

  compute_shape = "VM.Standard.A1.Flex"

  compute_ocpus = 2

  compute_memory_gb = 12

  boot_volume_gb = 50


  # ============================================================
  # NETWORK
  # ============================================================

  vcn_cidr = "10.0.0.0/16"

  public_subnet_cidr = "10.0.1.0/24"


  # ============================================================
  # PUBLIC PORTS
  # ============================================================

  ssh_port = 22

  http_port = 80

  https_port = 443


  # ============================================================
  # INTERNAL DOCKER PORTS
  # ============================================================

  postgres_port = 5432

  redis_port = 6379

  ollama_port = 11434

  pgadmin_port = 5050

  fastapi_port = 8000


  # ============================================================
  # DOCKER
  # ============================================================

  docker_project_dir = "/opt/wings-ai-platform"


  # ============================================================
  # TAGS
  # ============================================================

  common_tags = {
    Project     = "WINGS AI Platform"
    Environment = "Always-Free"
    ManagedBy   = "Terraform"
    CostPolicy  = "ALWAYS-FREE-ONLY"
  }
}