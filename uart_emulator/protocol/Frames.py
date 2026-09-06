import struct as st
from uart_emulator.protocol.Segmenter import segmenter as sg
from uart_emulator.protocol.ACK import ACK
class Frame():
    #8bit data frame with parity bit and start bit
    #parity = 0(even) or 1(odd)
    #1401 frame format: start bit(4 bit) + data(8 bits) + parity bit(1 bit)+ stop bit(3 bits)
    def __init__(self,start=0b0101, parity=0,data=None,stop=0b010,data_size:int=1): 
        self.start = start
        self.parity = parity & 0x01 #ensure parity is 1 bit
        self.data_size=data_size #in bytes
        self.data = self.encode_data(data,data_size)#encode_data ensures data is 8 bits
        self.stop = stop & 0x7 #ensure stop is 3 bits
        self.parity_bit = None #parity bit will be calculated during serialisation
    def encode_data(self, data, data_size=1):
    # Accept int, bytes/bytearray, str, or None and return value masked to data_size bits
        if data is None:
            return 0
        if isinstance(data, int):
            mask = (1 << (data_size * 8)) - 1
            return data & mask
        if isinstance(data, str):
            b = data.encode('ascii', 'ignore')
        elif isinstance(data, (bytes, bytearray)):
            b = bytes(data)
        else:
            raise TypeError("data must be int, str, bytes, or None")
        
        # Extract bytes based on data_size
        val = 0
        for i in range(min(len(b), data_size)):
            val = (val << 8) | b[i] #one asci is 8 bit long so shift by 8
             # big-endian: most significant byte first
        
        # Mask to the correct size
        mask = (1 << (data_size * 8)) - 1
        return val & mask
    def serialise(self):
        #pack the data into a binary format
        countbits = bin(self.data).count('1')
        if self.parity == 0: #even parity
            if countbits % 2 != 0: #if odd number of bits, flip parity bit
                parity_bit = 1
            else:
                parity_bit = 0  
        else: #odd parity
            if countbits % 2 == 0: #if even number of bits, flip parity bit
                parity_bit = 1
            else:
                parity_bit = 0
        
        # Frame structure: start(4) + data(data_size*8) + parity(1) + stop(3)
        pkd_frame = self.start << (self.data_size * 8 + 4)
        pkd_frame |= self.data << 4
        pkd_frame |= parity_bit << 3
        pkd_frame |= self.stop
        
        # Pack to correct number of bytes: total bits = 4+data_size*8+1+3
        total_bits = self.data_size * 8 + 8
        total_bytes = (total_bits + 7) // 8
        
        if total_bytes == 1:
            return st.pack('>B', pkd_frame)
        elif total_bytes == 2:
            return st.pack('>H', pkd_frame)
        elif total_bytes == 3:
            return st.pack('>I', pkd_frame)[1:]  # Take last 3 bytes from 4-byte int
        elif total_bytes == 4:
            return st.pack('>I', pkd_frame)
        else:
            raise ValueError(f"Unsupported frame size: {total_bytes} bytes")
    @classmethod
    def gen_ack_nack_frame(cls, ack_nck:int=0, start=0b0101, parity=0, stop=0b010, data_size=1):
        """ack_nck=0 for ACK, ack_nck=1 for NACK"""
        if ack_nck == 0:
            data = ACK.ACK.value
        elif ack_nck == 1:
            data = ACK.NACK.value
        else:
            raise ValueError("ack_nck must be 0 (ACK) or 1 (NACK)")
        
        return cls(start=start, parity=parity, data=data, stop=stop, data_size=data_size)


    
    def __str__(self):
        return f"Frame(start={bin(self.start)}, parity={self.parity}, data={bin(self.data)}, stop={bin(self.stop)})"
class Deserialise:
    def __init__(self, start=0b0101, parity=0, stop=0b010,data_size=1):
        self.start = start & 0xF
        self.parity = parity & 0x01
        self.stop = stop & 0x7
        self.data_size=data_size

    def decode_data(self, frame):
        # Extract fields based on data_size
        # Frame structure: start(4) + data(data_size*8) + parity(1) + stop(3)
        start = (frame >> (self.data_size * 8 + 4)) & 0xF
        data_mask = (1 << (self.data_size * 8)) - 1
        data = (frame >> 4) & data_mask
        parity_bit = (frame >> 3) & 0x01
        stop = frame & 0x7
        status="OK"
        #FS=false start,PE=parity error,FE=framing error
        if start != self.start:
            status="FS"
        count = bin(data).count("1")
        expected_parity = count % 2 if self.parity == 0 else 1 - (count % 2)

        if parity_bit != expected_parity:
            status="PE"
           

        if stop != self.stop:
            status="FE"
        return status, data

    def decode_frame(self, frame_bytes):
        """
        Decode a serialized frame.

        Input:
            bytes produced by Frame.serialise()
        """

        # Expected frame size: (data_size * 8 + 8) bits = (data_size + 1) bytes
        expected_bytes = self.data_size + 1
        if len(frame_bytes) != expected_bytes:
            raise ValueError(
                f"UART frame must contain exactly {expected_bytes} bytes "
                f"for data_size={self.data_size}; got {len(frame_bytes)}"
            )

        # Unpack based on frame size
        if expected_bytes == 1:
            frame = st.unpack(">B", frame_bytes)[0]
        elif expected_bytes == 2:
            frame = st.unpack(">H", frame_bytes)[0]
        elif expected_bytes == 3:
            frame = st.unpack(">I", b'\x00' + frame_bytes)[0]  # Pad to 4 bytes
        elif expected_bytes == 4:
            frame = st.unpack(">I", frame_bytes)[0]
        else:
            raise ValueError(f"Unsupported frame size: {expected_bytes} bytes")

        return self.decode_data(frame)

        
# TODO:
# Instead of raising ValueError for FS, PE and FE, update the
# receiver FSM state/error status so that the FSM can handle
# the error and trigger a frame re-request/retransmission.
#
# FS → False Start
# PE → Parity Error
# FE → Framing Error
#
# Future flow:
# RX FSM → detect error → set error state → request retransmission
#        → discard corrupted frame → receive retransmitted frame
    
if __name__ == "__main__":
    sg = sg(max_segment_size=8)

    list_of_data = sg.segment_data("ANANT")

    print(list_of_data)
    print(
        "while printing by bin() it omits leading zeros of start and stop bits; "
        "start is 4 bits and stop is 3 bits."
    )

    deserializer = Deserialise(
        start=0b0101,
        parity=0,
        stop=0b010
    )

    for segment in list_of_data:

        frame = Frame(
            start=0b0101,
            parity=0,
            data=segment,
            stop=0b010
        )

        serialized_frame = frame.serialise()

        print("\nOriginal Frame:")
        print(frame)

        print(f"Serialized Frame: {serialized_frame.hex()}")

        try:
            _,decoded_data = deserializer.decode_frame(serialized_frame)

            print(f"Decoded Data: {decoded_data}")
            print(f"Decoded Data (char): {chr(decoded_data)}")

        except ValueError as error:
            print(f"Frame Error: {error}")
    