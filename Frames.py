import struct as st
from Segmenter import segmenter as sg
class Frame():
    #8bit data frame with parity bit and start bit
    #parity = 0(even) or 1(odd)
    #1401 frame format: start bit(4 bit) + data(8 bits) + parity bit(1 bit)+ stop bit(3 bits)
    def __init__(self,start=0b0101, parity=0,data=None,stop=0b010): 
        self.start = start
        self.parity = parity & 0x01 #ensure parity is 1 bit
        self.data = self.encode_data(data)#encode_data ensures data is 8 bits
        self.stop = stop & 0x7 #ensure stop is 3 bits
        self.parity_bit = None #parity bit will be calculated during serialisation
    def encode_data(self, data):
    # Accept int, bytes/bytearray, str, or None and return 8-bit int
        if data is None:
            return 0
        if isinstance(data, int):
            return data & 0x0FF
        if isinstance(data, str):
            b = data.encode('ascii', 'ignore')
        elif isinstance(data, (bytes, bytearray)):
            b = bytes(data)
        else:
            raise TypeError("data must be int, str, bytes, or None")
        # use struct to get a 16-bit value from up to two bytes, then mask to 8 bits
        if len(b) >= 2:
            val = st.unpack('>H', b[:2])[0] #unsigned short, big-endian(Msb first) #keep only the first
            #two bytes and return value as an integer
        elif len(b) == 1:
            val = b[0]
        else:
            val = 0
        return val & 0x0FF #only keep the lower 8 bits
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
                
        pkd_frame= self.start << 12 | self.data << 4 | parity_bit<<3 | self.stop 
        return st.pack('>H', pkd_frame) #big-endian unsigned short
    
    def __str__(self):
        return f"Frame(start={bin(self.start)}, parity={self.parity}, data={bin(self.data)}, stop={bin(self.stop)})"
class Deserialise:
    def __init__(self, start=0b0101, parity=0, stop=0b010):
        self.start = start & 0xF
        self.parity = parity & 0x01
        self.stop = stop & 0x7

    def decode_data(self, frame):
        start = (frame >> 12) & 0xF
        data = (frame >> 4) & 0xFF
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
        return status,data
    def decode_frame(self, frame_bytes):
        """
        Decode a serialized frame.

        Input:
            bytes produced by Frame.serialise()
        """

        if len(frame_bytes) != 2:
            raise ValueError("UART frame must contain exactly 2 bytes")

        frame = st.unpack(">H", frame_bytes)[0]

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
    