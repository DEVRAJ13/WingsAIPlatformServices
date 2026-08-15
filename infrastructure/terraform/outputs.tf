output "instance_id" {
  description = "WINGS A1 instance OCID"

  value = oci_core_instance.wings.id
}


output "public_ip" {
  description = "WINGS server public IP"

  value = oci_core_instance.wings.public_ip
}


output "private_ip" {
  description = "WINGS server private IP"

  value = oci_core_instance.wings.private_ip
}


output "availability_domain" {
  description = "A1 Availability Domain"

  value = var.a1_availability_domain
}


output "compute_shape" {
  description = "Always Free compute shape"

  value = "VM.Standard.A1.Flex"
}


output "compute_ocpus" {
  description = "Always Free OCPU allocation"

  value = 2
}


output "compute_memory_gb" {
  description = "Always Free memory allocation"

  value = 12
}


output "boot_volume_gb" {
  description = "Boot volume"

  value = 50
}


output "ssh_command" {
  description = "SSH command"

  value = format(
    "ssh -i <PRIVATE_KEY> ubuntu@%s",
    oci_core_instance.wings.public_ip
  )
}


output "docker_directory" {
  description = "Docker application directory"

  value = local.docker_project_dir
}