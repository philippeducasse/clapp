import logging

from django.conf import settings
from django.db import connection

from .db_router import set_tenant_schema

logger = logging.getLogger(__name__)


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

        self.use_tenant_partitioning = settings.ENVIRONMENT == "prod"

    def __call__(self, request):
        if request.user.is_authenticated and self.use_tenant_partitioning:
            schema = f"user_{request.user.id}"
            set_tenant_schema(schema)

            # switch Postgres schema
            try:
                with connection.cursor() as cursor:
                    quoted_schema = connection.ops.quote_name(schema)
                    cursor.execute(f"SET search_path TO {quoted_schema}, public")
            except Exception as e:
                logger.error(f"Failed to set schema for user {request.user.id}: {e}")
                raise

        return self.get_response(request)
