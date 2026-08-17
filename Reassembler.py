from Frames import Deserialise as DS

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

    def decode(self, frame):
        status,raw_data = DS().decode_frame(frame)
        if status!="OK":
            #send nack
            pass
        else:
            if self.data_type == 0:
                data = raw_data

            elif self.data_type == 1:
                data = chr(raw_data)

            else:
                data = bytes([raw_data])

            self.rcvd_data.append(data)
        return data