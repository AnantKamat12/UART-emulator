# ============================================================
# REUSABLE LOGGER
# ============================================================

import enum
import os

# ============================================================
# HOST TYPE
# ============================================================

class HostType(enum.Enum):
    TxHost = 1
    RxHost = 2
    DuplexHost=3
# always do from Logger import logger,HostType

# ============================================================
# LOGGER
# ============================================================

class logger:

    def __init__(self, log_id, hostname, start_tick, host_type):
        self.log_id = log_id
        self.hostname = hostname
        self.start_tick = start_tick
        self.host_type = host_type

        # ----------------------------------------------------
        # Tick tracking
        # ----------------------------------------------------

        self.prev = start_tick
        self.curr = start_tick

        # ----------------------------------------------------
        # Create a log file for this logger
        # ----------------------------------------------------

        self.filename = (
            f"{self.hostname}_{self.log_id}.log"
        )
        os.makedirs("UARTlogs", exist_ok=True)
        self.file = open(
            f"UARTlogs/{self.filename}",
            "w",
            encoding="utf-8"
        )

        # ----------------------------------------------------
        # Write logger information
        # ----------------------------------------------------

        self.file.write(
            f"Host is      : {self.hostname}\n"
            f"Host type    : {self.host_type.name}\n"
            f"start_tick   : {self.start_tick}\n"
            f"\n"
        )

        self.file.flush()

    # --------------------------------------------------------
    # WRITE LOG
    # --------------------------------------------------------

    def write(self, log_statement, current_tick=None):

        # If a new tick is provided,
        # move current tick to previous tick
        if current_tick is not None:
            self.prev = self.curr
            self.curr = current_tick

        # If no tick is provided,
        # use the most recently known current tick
        else:
            current_tick = self.curr

        log_entry = (
            f"[TICK {current_tick}] :: "
            f"{log_statement}\n"
        )

        self.file.write(log_entry)
        self.file.flush()

    # --------------------------------------------------------
    # CLOSE LOG FILE
    # --------------------------------------------------------

    def close(self):
        if not self.file.closed:
            self.file.close()

    # --------------------------------------------------------
    # CONTEXT MANAGER SUPPORT
    # --------------------------------------------------------

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


# ============================================================
# TEST LOGGER
# ============================================================

if __name__ == "__main__":

    log = logger(
        log_id=1,
        hostname="HostA",
        start_tick=0,
        host_type=HostType.TxHost
    )

    log.write("Transmission started", 100)
    log.write("Sending bit 1", 101)
    log.write("Sending bit 0")
    log.write("Frame transmitted", 103)

    log.close()