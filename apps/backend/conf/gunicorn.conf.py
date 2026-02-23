# Gunicorn configuration for filtering healthcheck logs

bind = "0.0.0.0:8000"
workers = 3
worker_class = "sync"
accesslog = "-"
errorlog = "-"
access_log_format = '%(h)s - - [%(t)s] "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Custom logging configuration
logconfig_dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "healthcheck": {
            "()": "conf.settings.logging_filters.HealthcheckFilter",
        },
    },
    "formatters": {
        "default": {
            "format": '%(h)s - - [%(t)s] "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"',
        },
    },
    "handlers": {
        "access": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "filters": ["healthcheck"],
        },
    },
    "loggers": {
        "gunicorn.access": {
            "handlers": ["access"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
