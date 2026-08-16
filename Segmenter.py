import struct as st
class segmenter:
    def __init__(self, max_segment_size=8):
        self.max_segment_size = max_segment_size
    def segment_data(self, data):
        # Accept str, bytes/bytearray, or None and return list of segments
        if data is None:
            return []
        if isinstance(data, str):
            b = data.encode('ascii', 'ignore')
            #print(f"Encoded string to bytes: {b}")
        elif isinstance(data, (bytes, bytearray)):
            b = bytes(data)
        else:
            raise TypeError("data must be str, bytes, or None")
        len_of_data = len(b)
        bytes_per_segment = self.max_segment_size // 8
        segments = []
        for i in range(0, len_of_data, bytes_per_segment):
            segment = b[i:i+bytes_per_segment]
            segments.append(segment)

        

        return segments
if __name__ == "__main__":
    sg = segmenter(max_segment_size=8)
    list_of_data=sg.segment_data("anant-s-kamat")
    print((list_of_data))