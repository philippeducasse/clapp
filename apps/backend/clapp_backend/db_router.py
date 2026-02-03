from threading import local

_thread_locals = local()


def set_tenant_schema(schema_name):
    _thread_locals.schema = schema_name


def get_tenant_schema():
    return getattr(_thread_locals, "schema", "public")


class TenantRouter:
    def db_for_read(self, model, **hints):
        return "default"

    def db_for_write(self, model, **hints):
        return "default"

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return db == "default"
