# ============================================================
# WINGS AI - MONTHLY ALWAYS FREE START
# ============================================================
resource "oci_resource_scheduler_schedule" "wings_monthly_start" {
  compartment_id = var.compartment_ocid

  display_name = "wings-monthly-start"

  description = "Start WINGS AI A1 instance on the first day of every month."

  action = "START_RESOURCE"

  recurrence_type    = "CRON"
  recurrence_details = "05 00 1 * *"

  resources {
    id = oci_core_instance.wings.id
  }

  freeform_tags = merge(
    local.common_tags,
    {
      Purpose = "Always-Free-Protection"
    }
  )
}