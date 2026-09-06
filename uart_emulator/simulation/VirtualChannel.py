from collections import deque


class VirtualChannel:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, is_ideal: bool = True, bit_flip_rate: float = 0.0, baud_rate: int = 9600):
        if getattr(self, "_initialized", False):
            return

        self.is_ideal = is_ideal
        self.bit_flip_rate = bit_flip_rate
        """keep bit_flip_rate lesser than 0.01 or too many frames will be corrupted"""
        self.baud_rate = baud_rate

        # Each queue stores bits as (tick, bit).
        self.line0 = deque()
        self.line1 = deque()

        self._initialized = True

    def push(self, tick, bit, line=0):
        """Push one bit onto a line at a specific simulation tick."""
        queue = self.line0 if line == 0 else self.line1
        if self.is_ideal:
            queue.append((tick, bit))
        else:
            import random
            if random.random() < self.bit_flip_rate:
                bit = not bit # flip the bit
            queue.append((tick, bit))

    def read(self, tick, line=0):
        """Read a bit only when it has arrived by the current tick."""
        queue = self.line0 if line == 0 else self.line1

        if not queue:
            return None

        bit_tick, bit = queue[0]
        if bit_tick > tick:
            return None

        queue.popleft()
        return bit

    def reset(self):
        """Clear both communication lines."""
        self.line0.clear()
        self.line1.clear()