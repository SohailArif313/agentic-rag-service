import time
from collections import defaultdict, deque
from threading import Lock

GLOBAL_KEY = "__global__"


class RateLimiter:
    def __init__(self, per_minute: int, daily_cap: int):
        self.per_minute = per_minute
        self.daily_cap = daily_cap
        self.hits: dict[str, deque] = defaultdict(deque)
        self.lock = Lock()

    def _recent(self, key: str, window_seconds: int, now: float) -> deque:
        hits = self.hits[key]
        while hits and now - hits[0] > window_seconds:
            hits.popleft()
        return hits

    def check(self, client_id: str) -> str | None:
        now = time.monotonic()
        with self.lock:
            client_hits = self._recent(client_id, 60, now)
            day_hits = self._recent(GLOBAL_KEY, 86400, now)

            if len(day_hits) >= self.daily_cap:
                return "Daily demo limit reached. Please try again tomorrow."
            if len(client_hits) >= self.per_minute:
                return "Too many requests. Please wait a minute."

            client_hits.append(now)
            day_hits.append(now)
        return None