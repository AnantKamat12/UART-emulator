from uart_emulator.protocol.Frames import Deserialise as DS,Frame
from uart_emulator.protocol.Segmenter import segmenter as sg
class Reassembler:
    def __init__(self, data_type: int = 1):
        # data_type:
        # 0 = int
        # 1 = string
        # 2 = bytes

        if data_type not in (0, 1, 2):
            raise ValueError("data_type must be 0 (int), 1 (string), or 2 (bytes)")

        self.data_type = data_type
        self.rcvd_data = []

    def decode(self, frame, non_ideal_vc=False,data_size:int=1):
        status,raw_data = DS(data_size=data_size).decode_frame(frame)
        if not non_ideal_vc:
            if status!="OK":
                #frame will be not decoded at all,data lost,so return None

                return None
            else:
                if self.data_type == 0:
                    data = raw_data

                elif self.data_type == 1:
                    data = raw_data.to_bytes(data_size, byteorder='big').decode('ascii')

                else:
                    data = raw_data.to_bytes(data_size, byteorder='big')

                self.rcvd_data.append(data)
                return data
        else:
            if status!="OK":
                return f"Corrupted Frame due to {status},data lost"

            else:
                if self.data_type == 0:
                    data = raw_data

                elif self.data_type == 1:
                    data = raw_data.to_bytes(data_size, byteorder='big').decode('ascii')

                else:
                    data = raw_data.to_bytes(data_size, byteorder='big')

                self.rcvd_data.append(data)
                return data

    def get_data(self):
        return self.rcvd_data
    def rcvd_data_comb(self):
        if self.data_type == 0:
            return self.rcvd_data
        elif self.data_type == 1:
            return ''.join(self.rcvd_data)
        else:
            return b''.join(self.rcvd_data) 
    
if __name__ == "__main__":
    sg = sg(max_segment_size=8)
    rs=Reassembler(1);
    list_of_data = sg.segment_data("ANANT")

    print(list_of_data)
    print(
        "while printing by bin() it omits leading zeros of start and stop bits; "
        "start is 4 bits and stop is 3 bits."
    )

    deserializer = DS(
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
            data = rs.decode(serialized_frame)

            print(f"Decoded Data: {data}")
        except ValueError as error:
            print(f"Frame Error: {error}")
    print(rs.rcvd_data)
    