import time
import random


class SnowflakeIdGenerator:
    def __init__(self, worker_id, datacenter_id):
        self.worker_id = worker_id
        self.datacenter_id = datacenter_id
        self.sequence = random.randint(0, 4095)
        self.last_timestamp = -1

    def _current_time(self):
        return int(round(time.time() * 1000))

    def _wait_for_next_millisecond(self, last_timestamp):
        timestamp = self._current_time()
        while timestamp <= last_timestamp:
            timestamp = self._current_time()
        return timestamp

    def generate(self):
        timestamp = self._current_time()

        if timestamp < self.last_timestamp:
            raise Exception("Invalid system clock")

        if timestamp == self.last_timestamp:
            self.sequence = (self.sequence + 1) & 4095
            if self.sequence == 0:
                timestamp = self._wait_for_next_millisecond(self.last_timestamp)
        else:
            self.sequence = 0

        self.last_timestamp = timestamp

        return ((timestamp & 0x1FFFFFFFFFF) << 22) | (self.datacenter_id << 17) | (self.worker_id << 12) | self.sequence

