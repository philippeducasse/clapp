from typing import Tuple

from django.core.cache import cache
from django.utils import timezone


def check_llm_rate_limit(tenant_schema: str, limit: int = 100) -> Tuple[bool, int]:
    today = timezone.now().date()
    cache_key = f"llm_limit:{tenant_schema}:{today}"

    current_count = cache.get(cache_key, 0)

    if current_count >= limit:
        return False, 0

    return True, limit - current_count


def increment_llm_call_counter(tenant_schema: str) -> int:
    today = timezone.now().date()
    cache_key = f"llm_limit:{tenant_schema}:{today}"

    current_count = cache.get(cache_key, 0)

    if current_count == 0:
        now = timezone.now()
        midnight = timezone.make_aware(
            timezone.datetime.combine(
                today + timezone.timedelta(days=1), timezone.datetime.min.time()
            )
        )
        seconds_until_midnight = int((midnight - now).total_seconds())

        cache.set(cache_key, 1, timeout=seconds_until_midnight)

    else:
        cache.incr(cache_key)

    return cache.get(cache_key)
