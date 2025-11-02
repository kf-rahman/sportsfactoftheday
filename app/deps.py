import time
from collections import deque, defaultdict
from typing import Callable, Deque, Dict, Set
from fastapi import HTTPException

class RateLimiter:
    """Simple token bucket per IP: allow `rate` requests every `per` seconds."""
    def __init__(self, rate: int = 10, per: int = 60):
        self.rate = rate
        self.per = per
        self._hits: Dict[str, Deque[float]] = defaultdict(deque)

    def check(self, ip: str):
        now = time.time()
        hits = self._hits[ip]
        # drop old timestamps
        while hits and (now - hits[0]) > self.per:
            hits.popleft()
        if len(hits) >= self.rate:
            # too many requests
            raise HTTPException(status_code=429, detail="Too many requests, please slow down.")
        hits.append(now)

class RecentFactsCache:
    """Keep last N facts per sport and avoid repeats for a few generations."""
    def __init__(self, maxlen: int = 15):
        self.maxlen = maxlen
        self._cache: Dict[str, Deque[str]] = defaultdict(lambda: deque(maxlen=self.maxlen))
        self._set: Dict[str, Set[str]] = defaultdict(set)

    def remember(self, sport: str, fact: str):
        q = self._cache[sport]
        s = self._set[sport]
        if len(q) == q.maxlen and q:
            old = q.popleft()
            s.discard(old)
        q.append(fact)
        s.add(fact)

    def unique_generate(self, sport: str, make: Callable[[], str], attempts: int = 6) -> str:
        seen = self._set[sport]
        fact = ""
        for _ in range(max(1, attempts)):
            fact = make()
            if fact not in seen:
                break
        self.remember(sport, fact)
        return fact
