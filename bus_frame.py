
class CANFrame:
    def __init__(self):
        self.sof = "0"                                                                  # 1 bit start of frame
        self.id = "00000000000"                                                         # 11 bits id
        self.dlc = "0000"                                                               # 4 bits data length code
        self.data = "0000000000000000000000000000000000000000000000000000000000000000"  # 64 bits data content 
        self.crc = "000000000000000"                                                    # 15 bits cyclic redundancy check
        self.ack = "1"                                                                  # 1 bit acknowledgement, Transmitter sends recessive (1) and any receiver can assert a dominant (0)
        self.eof = "1111111"                                                            # 7 bits of end of file
        self.ifs = "111"                                                                # 3 bits inter-frame space
        
    def make(self, id, dlc, data):
        self.id = id
        self.dlc = dlc
        self.data = data
    
    def tot_len_frame(self):
        return len(self.sof) + len(self.id) + len(self.dlc) + len(self.data) + len(self.crc) + len(self.ack) + len(self.eof) + len(self.ifs)
        
    def __str__(self):
        return f"ID={self.id}, DLC={self.dlc}, Data={self.data}, CRC={self.crc}, ACK={self.ack}, EOF={self.eof}"