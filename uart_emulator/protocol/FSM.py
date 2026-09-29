from enum import Enum, auto
from abc import ABC


class SenderState(Enum):
    IDLE = auto()
    SENDING = auto()
    WAITING_FOR_FEEDBACK = auto()
    RESEND = auto()
    SUCCESS = auto()
    FAILED = auto()


class ReceiverState(Enum):
    IDLE = auto()
    RECEIVING = auto()
    VALIDATING = auto()
    SENDING_ACK_NACK = auto()


class Event(Enum):
    DATA_READY = auto()
    FRAME_SENT = auto()
    ACK_RECEIVED = auto()
    NACK_RECEIVED = auto()
    FEEDBACK_CORRUPT = auto()
    NO_VALID_FEEDBACK = auto()
    NEXT_PACKET = auto()
    NO_MORE_DATA = auto()
    FRAME_RECEIVED = auto()
    FRAME_COMPLETE = auto()
    VALID_FRAME = auto()
    INVALID_FRAME = auto()
    FEEDBACK_SENT = auto()


class FSM(ABC):
    def __init__(self, initial_state, transition_table):
        self.state = initial_state
        self.transition_table = transition_table

    def handle(self, event):
        if self.state not in self.transition_table.table:
            raise ValueError(f"State {self.state} is not defined in the FSM table")
        if event not in self.transition_table.table[self.state]:
            raise ValueError(
                f"No transition for state={self.state.name}, event={event.name}"
            )
        self.state = self.transition_table.table[self.state][event]
        return self.state

    def get_state(self):
        return self.state


class SenderTransitionTable:
    def __init__(self):
        self.table = {
            SenderState.IDLE: {
                Event.DATA_READY: SenderState.SENDING,
            },
            SenderState.SENDING: {
                Event.FRAME_SENT: SenderState.WAITING_FOR_FEEDBACK,
            },
            SenderState.WAITING_FOR_FEEDBACK: {
                Event.ACK_RECEIVED: SenderState.SUCCESS,
                Event.NACK_RECEIVED: SenderState.RESEND,
                Event.FEEDBACK_CORRUPT: SenderState.RESEND,
                Event.NO_VALID_FEEDBACK: SenderState.RESEND,
            },
            SenderState.RESEND: {
                Event.FRAME_SENT: SenderState.WAITING_FOR_FEEDBACK,
            },
            SenderState.SUCCESS: {
                Event.NEXT_PACKET: SenderState.SENDING,
                Event.NO_MORE_DATA: SenderState.IDLE,
            },
            SenderState.FAILED: {},
        }

    def next_state(self, current_state, event):
        return self.table[current_state][event]


class ReceiverTransitionTable:
    def __init__(self):
        self.table = {
            ReceiverState.IDLE: {
                Event.FRAME_RECEIVED: ReceiverState.RECEIVING,
            },
            ReceiverState.RECEIVING: {
                Event.FRAME_COMPLETE: ReceiverState.VALIDATING,
            },
            ReceiverState.VALIDATING: {
                Event.VALID_FRAME: ReceiverState.SENDING_ACK_NACK,
                Event.INVALID_FRAME: ReceiverState.SENDING_ACK_NACK,
            },
            ReceiverState.SENDING_ACK_NACK: {
                Event.FEEDBACK_SENT: ReceiverState.IDLE,
            },
        }

    def next_state(self, current_state, event):
        return self.table[current_state][event]


class SenderFSM(FSM):
    def __init__(self):
        super().__init__(SenderState.IDLE, SenderTransitionTable())


class ReceiverFSM(FSM):
    def __init__(self):
        super().__init__(ReceiverState.IDLE, ReceiverTransitionTable())


if __name__ == "__main__":
    sender = SenderFSM()
    receiver = ReceiverFSM()

    print("start sender:", sender.get_state().name)
    sender.handle(Event.DATA_READY)
    print("after data ready:", sender.get_state().name)
    sender.handle(Event.FRAME_SENT)
    print("after frame sent:", sender.get_state().name)
    sender.handle(Event.ACK_RECEIVED)
    print("after ack received:", sender.get_state().name)

    print("start receiver:", receiver.get_state().name)
    receiver.handle(Event.FRAME_RECEIVED)
    print("after frame received:", receiver.get_state().name)
    receiver.handle(Event.FRAME_COMPLETE)
    print("after frame complete:", receiver.get_state().name)
    receiver.handle(Event.VALID_FRAME)
    print("after valid frame:", receiver.get_state().name)
    receiver.handle(Event.FEEDBACK_SENT)
    print("after feedback sent:", receiver.get_state().name)

