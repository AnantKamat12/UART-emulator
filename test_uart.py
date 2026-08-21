from Host import Host
from Segmenter import segmenter
from Frames import Frame
from Reassembler import Reassembler


# ============================================================
# CONFIGURATION
# ============================================================

BAUD_RATE = 9600
MAX_SEGMENT_SIZE = 8
TEST_MESSAGE = "ANANT has created this"


# ============================================================
# CREATE HOSTS
# ============================================================

print("\n" + "=" * 70)
print("CREATING HOSTS")
print("=" * 70)

# Host A:
#   TX -> line 0
#   RX <- line 1
hostA = Host(
    host_type=2,
    baud_rate=BAUD_RATE,
    data_type=1,
    host_transmit_lane=0
)

# Host B:
#   TX -> line 1
#   RX <- line 0
hostB = Host(
    host_type=2,
    baud_rate=BAUD_RATE,
    data_type=1,
    host_transmit_lane=1
)

hostA.setuphost()
hostB.setuphost()

# Both hosts use the singleton clock
clock = hostA.clk

print(f"Baud rate          : {BAUD_RATE}")
print(f"Ticks per bit      : {clock.no_of_ticks_per_bit}")
print(f"Initial clock tick : {clock.curr_tick()}")


# ============================================================
# CREATE SEGMENTER + REASSEMBLER
# ============================================================

print("\n" + "=" * 70)
print("APPLICATION DATA")
print("=" * 70)

segmenter_obj = segmenter(
    max_segment_size=MAX_SEGMENT_SIZE
)

receiver_reassembler = Reassembler(
    data_type=1
)

print(f"Original message : {TEST_MESSAGE}")

segments = segmenter_obj.segment_data(TEST_MESSAGE)

print(f"Segments         : {segments}")
print(f"Number segments  : {len(segments)}")


# ============================================================
# TRANSMIT EACH SEGMENT
# ============================================================

START_TICK = 100

for segment_index, segment in enumerate(segments):

    print("\n")
    print("=" * 70)
    print(f"SEGMENT {segment_index + 1}/{len(segments)}")
    print("=" * 70)

    print(f"Segment bytes : {segment}")
    print(f"Segment char  : {segment.decode('ascii', errors='replace')}")


    # --------------------------------------------------------
    # CREATE ACTUAL FRAME OBJECT
    # --------------------------------------------------------

    frame = Frame(
        start=0b0101,
        parity=0,
        data=segment,
        stop=0b010
    )

    print("\n[FRAME OBJECT]")
    print(f"Frame        : {frame}")
    print(f"Frame data   : {frame.data}")
    print(f"Frame binary : {frame.data:08b}")


    # --------------------------------------------------------
    # SERIALISE FRAME
    # --------------------------------------------------------

    serialized_frame = frame.serialise()

    # TX currently works with an integer frame.
    frame_int = int.from_bytes(
        serialized_frame,
        byteorder="big"
    )

    print("\n[SERIALISATION]")
    print(f"Serialized bytes : {serialized_frame.hex()}")
    print(f"Serialized int   : {frame_int:016b}")
    print(f"Serialized value : {frame_int}")


    # --------------------------------------------------------
    # SCHEDULE TRANSMISSION
    # --------------------------------------------------------

    current_start_tick = START_TICK + (
        segment_index * 1800
    )

    print("\n[TRANSMISSION SETUP]")
    print(f"Start tick : {current_start_tick}")
    print(f"TX lane    : {hostA.host_transmit_lane}")
    print(f"RX lane    : {hostB.host_receive_lane}")

    hostA.tx.start_transmission(
        frame=frame_int,
        start_tick=current_start_tick,
        line=hostA.host_transmit_lane
    )


    # --------------------------------------------------------
    # RUN SIMULATION UNTIL FRAME IS RECEIVED
    # --------------------------------------------------------

    received_frame = None

    print("\n[SIMULATION]")

    while received_frame is None:

        current_tick = clock.curr_tick()

        # Print only important ticks to avoid thousands of lines
        if current_tick % 100 == 0:
            print(
                f"\n--- BIT BOUNDARY : tick {current_tick} ---"
            )

        # ----------------------------------------------------
        # HOST A TX
        # ----------------------------------------------------

        hostA.tx.step(current_tick)

        # ----------------------------------------------------
        # HOST B RX
        # ----------------------------------------------------

        received_frame = hostB.rx.step(
            current_tick,
            hostB.host_receive_lane
        )

        # ----------------------------------------------------
        # SHOW RECEIVED FRAME
        # ----------------------------------------------------

        if received_frame is not None:

            print("\n" + "-" * 70)
            print("FRAME RECEIVED")
            print("-" * 70)

            print(
                f"Received integer : {received_frame}"
            )

            print(
                f"Received binary  : "
                f"{received_frame:016b}"
            )

            # ------------------------------------------------
            # Convert integer back to serialized bytes
            # ------------------------------------------------

            received_bytes = received_frame.to_bytes(
                2,
                byteorder="big"
            )

            print(
                f"Received bytes   : "
                f"{received_bytes.hex()}"
            )

            # ------------------------------------------------
            # REASSEMBLER
            # ------------------------------------------------

            print("\n[REASSEMBLER]")

            decoded_data = receiver_reassembler.decode(
                received_bytes
            )

            print(
                f"Decoded data     : {decoded_data}"
            )

            print(
                f"Accumulated data : "
                f"{receiver_reassembler.rcvd_data}"
            )

            # ------------------------------------------------
            # VERIFY
            # ------------------------------------------------

            expected_char = segment.decode(
                "ascii",
                errors="replace"
            )

            print(
                f"Expected         : {expected_char}"
            )

            print(
                f"Match            : "
                f"{decoded_data == expected_char}"
            )

        # ----------------------------------------------------
        # ADVANCE SINGLE SIMULATION CLOCK
        # ----------------------------------------------------

        clock.tick()


# ============================================================
# FINAL RESULT
# ============================================================

print("\n")
print("=" * 70)
print("FINAL RESULT")
print("=" * 70)

print(
    f"Original message : {TEST_MESSAGE}"
)

print(
    f"Received data    : "
    f"{''.join(receiver_reassembler.rcvd_data)}"
)

print(
    f"Expected         : {TEST_MESSAGE}"
)

print(
    f"SUCCESS          : "
    f"{''.join(receiver_reassembler.rcvd_data) == TEST_MESSAGE}"
)

print("=" * 70)