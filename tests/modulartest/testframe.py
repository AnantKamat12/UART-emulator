import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from uart_emulator.protocol.Frames import Frame, Deserialise as DS
Frame1=Frame(start=0b0101,parity=0,data="A",stop=0b010,data_size=1)
Frame2=Frame(start=0b0101,parity=0,data="AB",stop=0b010,data_size=2)
Frame3=Frame(start=0b0101,parity=0,data="ABC",stop=0b010,data_size=3)
serialized_frame1 = Frame1.serialise()
serialized_frame2 = Frame2.serialise()  
serialized_frame3 = Frame3.serialise()
#print(len(serialized_frame1),len(serialized_frame2),len(serialized_frame3))
def test_data_sizes():
    assert Frame1.data_size == 1
    assert Frame2.data_size == 2    
    assert Frame3.data_size == 3
def test_serialization():
    assert len(serialized_frame1) == 2  # 1 byte for data + 1 byte for start, parity, and stop bits
    assert len(serialized_frame2) == 3  # 2 bytes for data + 1 byte for start, parity, and stop bits
    assert len(serialized_frame3) == 4  # 3 bytes for data + 1 byte for start, parity, and stop bits
def testDS():
    deserializer1 = DS(start=0b0101, parity=0, stop=0b010,data_size=1)
    deserializer2 = DS(start=0b0101, parity=0, stop=0b010,data_size=2)
    deserializer3 = DS(start=0b0101, parity=0, stop=0b010,data_size=3)

    status1, data1 = deserializer1.decode_data(int.from_bytes(serialized_frame1, byteorder='big'))
    status2, data2 = deserializer2.decode_data(int.from_bytes(serialized_frame2, byteorder='big'))
    status3, data3 = deserializer3.decode_data(int.from_bytes(serialized_frame3, byteorder='big'))
    print(data1, data2, data3)
    assert status1 == "OK" and data1 == ord("A")
    assert status2 == "OK" and data2 == int.from_bytes(b"AB", byteorder='big')
    assert status3 == "OK" and data3 == int.from_bytes(b"ABC", byteorder='big')
if __name__ == "__main__":
    test_data_sizes()
    test_serialization()
    testDS()
    print("All tests passed")