from collections import deque


class VirtualChannel:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, is_ideal: int = 0, baud_rate: int = 9600):
        # Singleton: don't reinitialize on every VC() call
        if getattr(self, "_initialized", False):
            return

        self.is_ideal = is_ideal
        self.baud_rate = baud_rate

        # Store (tick, bit)
        self.line0 = deque()
        self.line1 = deque()

        self._initialized = True

    def push(self, tick, bit, line=0):
        """
        Put a bit onto the virtual channel at a specific simulation tick.
        """
        queue = self.line0 if line == 0 else self.line1
        queue.append((tick, bit))

    def read(self, tick, line=0):
        """
        Read a bit that has arrived at or before the current simulation tick.

        Returns:
            bit (0/1) if available
            None if no bit is available
        """
        queue = self.line0 if line == 0 else self.line1

        if not queue:
            return None

        bit_tick, bit = queue[0]

        # Bit has not arrived yet
        if bit_tick > tick:
            return None

        queue.popleft()
        return bit

    def reset(self):
        """
        Clear both communication lines.
        """
        self.line0.clear()
        self.line1.clear()