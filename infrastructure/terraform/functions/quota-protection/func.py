import json
import logging
import os
from datetime import datetime, timezone

import oci

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


TENANT_ID = os.environ["TENANT_ID"]
INSTANCE_ID = os.environ["INSTANCE_ID"]

OCPU_LIMIT = float(os.getenv("OCPU_LIMIT", "1125"))
MEMORY_LIMIT = float(os.getenv("MEMORY_LIMIT", "6750"))


def current_month_range():
    now = datetime.now(timezone.utc)

    start = datetime(
        now.year,
        now.month,
        1,
        tzinfo=timezone.utc,
    )

    if now.month == 12:
        end = datetime(
            now.year + 1,
            1,
            1,
            tzinfo=timezone.utc,
        )
    else:
        end = datetime(
            now.year,
            now.month + 1,
            1,
            tzinfo=timezone.utc,
        )

    return start, end


def get_usage():

    config = {
        "region": os.environ["OCI_REGION"],
    }

    signer = oci.auth.signers.get_resource_principals_signer()

    usage_client = oci.usage_api.UsageapiClient(
        config=config,
        signer=signer,
    )

    start, end = current_month_range()

    request = oci.usage_api.models.RequestSummarizedUsagesDetails(
        tenant_id=TENANT_ID,
        time_usage_started=start,
        time_usage_ended=end,
        granularity="MONTHLY",
        query_type="USAGE_ONLY",
        is_aggregate_by_time=True,
        group_by=[
            "service",
            "skuName",
            "unit",
            "resourceId",
        ],
    )

    response = usage_client.request_summarized_usages(
        request
    )

    ocpu = 0.0
    memory = 0.0

    for item in response.data.items:

        if item.resource_id != INSTANCE_ID:
            continue

        if item.service != "Compute":
            continue

        if (
            item.sku_name == "Standard - A1"
            and item.unit == "OCPU Per Hour"
        ):
            ocpu += float(item.computed_quantity or 0)

        elif (
            item.sku_name == "Standard - A1 - Memory"
            and item.unit == "Gigabyte Per Hour"
        ):
            memory += float(item.computed_quantity or 0)

    return ocpu, memory


def stop_instance():

    signer = oci.auth.signers.get_resource_principals_signer()

    compute_client = oci.core.ComputeClient(
        config={
            "region": os.environ["OCI_REGION"],
        },
        signer=signer,
    )

    response = compute_client.instance_action(
        instance_id=INSTANCE_ID,
        action="STOP",
    )

    logger.warning(
        "WINGS AI instance STOP requested: %s",
        response.status,
    )


def handler(ctx, data=None):

    logger.info("WINGS AI quota protection started")

    ocpu, memory = get_usage()

    logger.info(
        "Current usage: OCPU=%.4f / %.4f, Memory=%.4f / %.4f",
        ocpu,
        OCPU_LIMIT,
        memory,
        MEMORY_LIMIT,
    )

    threshold_reached = (
        ocpu >= OCPU_LIMIT
        or memory >= MEMORY_LIMIT
    )

    if threshold_reached:

        logger.warning(
            "75%% quota threshold reached. "
            "OCPU=%.4f Memory=%.4f",
            ocpu,
            memory,
        )

        stop_instance()

        result = {
            "action": "STOP",
            "ocpu_usage": ocpu,
            "memory_usage": memory,
            "ocpu_limit": OCPU_LIMIT,
            "memory_limit": MEMORY_LIMIT,
        }

    else:

        logger.info(
            "Quota safe. WINGS AI remains running."
        )

        result = {
            "action": "KEEP_RUNNING",
            "ocpu_usage": ocpu,
            "memory_usage": memory,
            "ocpu_limit": OCPU_LIMIT,
            "memory_limit": MEMORY_LIMIT,
        }

    return json.dumps(result)
