import time
from collections import defaultdict


class TimerManager:
    def __init__(self):
        self.timers = defaultdict(float)
        self.starts = {}

    def start(self, timer_name: str):
        self.starts[timer_name] = time.time()

    def stop(self, timer_name: str):
        if timer_name in self.starts:
            elapsed = time.time() - self.starts[timer_name]
            self.timers[timer_name] += elapsed
            del self.starts[timer_name]

    def get_report(self):
        total = sum(self.timers.values())
        report = ["\n=== ТАЙМИНГИ ==="]
        for name, elapsed in sorted(self.timers.items(), key=lambda x: x[1], reverse=True):
            percentage = (elapsed / total) * 100 if total > 0 else 0
            report.append(f"{name}: {elapsed:.2f}с ({percentage:.1f}%)")
        report.append(f"Общее время: {total:.2f}с")
        return "\n".join(report)