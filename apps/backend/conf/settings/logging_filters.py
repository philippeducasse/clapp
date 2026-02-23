import logging


class HealthcheckFilter(logging.Filter):
    """Filter out healthcheck requests from logs."""

    def filter(self, record):
        return "/health/" not in record.getMessage()
