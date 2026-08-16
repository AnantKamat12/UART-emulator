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
if __name__ == "__main__":
    sg =sg(max_segment_size=8)
    list_of_data=sg.segment_data("Anant")
    print((list_of_data))
    print("while printing by bin() it omist leading zeros, of start and stop bits, start is 4 bits and stop is 3 bits, so leading zeros are omitted")
    for segment in list_of_data:
        frame = Frame(start=0b0101, parity=0, data=segment, stop=0b010)
        serialized_frame = frame.serialise()
        print(frame)
        print(f"Serialized Frame: {serialized_frame.hex()}")
    

    