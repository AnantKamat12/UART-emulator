import enum
class ACK(enum.Enum):
    """Defining ACK/NCK values for the protocol."""
    ACK = 0b0001
    NACK = 0b0010
    """same structure header,payload(ACK/NACK),parity and stop bits"""