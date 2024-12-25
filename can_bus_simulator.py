from bus_frame import CANFrame
from node import Node


class CANBus:
    frame_segments = ['sof', 'id', 'dlc', 'data', 'crc', 'ack', 'eof']
    status = ['idle', 'non-idle']
    
    def __init__(self):
        self.stat = self.status[0]
        self.frame = ""
        
    def is_idle(self):
        return True if self.stat == self.status[0] else False
    
    def set_status(self, s):
        self.stat = s
    
    def elaborate_frame(self, node):
        global count
        if count == 0:
            self.set_status(self.status[1])
            print(node.name + " frame in elaboration. CAN bus status: ", self.stat)
        elif count == 105:
            self.set_status(self.status[0])
            print(node.name + " frame elaborated. CAN bus status: ", self.stat)

    def receive_frames(self, b1=None, b2=None, attr="", node1=None, node2=None):
        global count
        
        if b1 == None or b2 == None:
            x = (lambda x, y: x if y is None else y)(node1, node2)
            self.elaborate_frame(x)
            count += 1
            return 0
        
        
        ''' BITWISE AND-GATE '''
        if attr == self.frame_segments[0]:      # "sof"
            self.frame += str(b1 & b2)
            return 0
            
        elif attr == self.frame_segments[1]:    # "id - arbitration phase"
            if count == 0:
                print("Start of Arbitration.")

            if b1 & b2:
                
                self.frame += str(b1 & b2)
                
            else:
                
                if b1 == 0 and b2 == 1:
                    print("Arbitration winner: ", node1.name)           #TODO ora dovrei usare il metodo dei nodi per il rilevamento degli errori
                    self.elaborate_frame(node1)
                    return True                                         #TODO non so se forse è meglio lanciare un'eccezione
                
                elif b1 == 1 and b2 == 0:
                    print("Arbitration winner: ", node2.name)
                    self.elaborate_frame(node2)
                    return True
                    
                else:
                    self.frame += str(b1 & b2)
                    
            count += 1
            return 0
        
        elif attr == self.frame_segments[2]:    # "dlc - bit error starts here"
            if count == 11:
                count += 1
                print("Two arbitration winners.")
                
            self.check_bit_error(b1, b2, node1, node2)
            # self.frame += str(b1 & b2)
            return 0
        
        elif attr == self.frame_segments[3]:    # "data"
            self.frame += str(b1 & b2)
            return 0
        
        elif attr == self.frame_segments[4]:    # "crc"
            self.frame += str(b1 & b2)
            return 0
        
        elif attr == self.frame_segments[5]:    # "ack"
            self.frame += str(b1 & b2)
            return 0
        
        elif attr == self.frame_segments[6]:    # "eof"
            self.frame += str(b1 & b2)
            return 0
        
        self.print_out_sequence()
        self.frame = ""
        # return 0
        
    def check_bit_error(self, b1, b2, node1, node2):
        if b1 & b2:
                
            self.frame += str(b1 & b2)
                
        else:
            # Here if there is a mismatch will be raise the error to the corresponding node
            if b1 == 0 and b2 == 1:
                print("Bit-error detected, recessive bit from: ", node2.name)   # recessive (1) from node2
                node2.error_detected()
                return True
                
            elif b1 == 1 and b2 == 0:
                print("Bit-error detected, recessive bit from: ", node1.name)   # recessive (1) from node1
                node1.error_detected()
                return True
                    
            else:
                self.frame += str(b1 & b2)

    
    def print_out_sequence(self):
        if self.frame == "":
            print("No bitwise AND-gate output frame.")
        else:
            print("Bitwise AND-gate output frame: ", self.frame)
    

### MAIN ###

if __name__ == "__main__":
    global count
    count = 0
    
    can_bus = CANBus()
    
    victime_ecu = Node("victime")
    print(victime_ecu)
    
    adversary_ecu = Node("adversary")
    print(adversary_ecu)
    
    frame1_victime = victime_ecu.make_frame(id="01000100001", dlc="0100", data="0000000100000010000000110000010000000001000000100000001100000100")
    frame2_adversary = adversary_ecu.make_frame(id="01000000001", dlc="0000", data="0000000100000010000000110000010011111111111111111111111100000000")
        
    print("victime " + "".join(getattr(frame1_victime, attribute) for attribute in frame1_victime.__dict__))
    print("adversary " + "".join(getattr(frame2_adversary, attribute) for attribute in frame2_adversary.__dict__))
    
    print("\n")
        
    if can_bus.is_idle():
        for attr in frame1_victime.__dict__:
            frame1_bits = getattr(frame1_victime, attr)
            for b1 in frame1_bits:
                can_bus.receive_frames(b1=int(b1), attr=attr, node1=victime_ecu)

    can_bus.print_out_sequence()
    
    count = 0
    
    print("\n")
    
    if can_bus.is_idle():
        for attr in frame1_victime.__dict__:
            frame1_bits = getattr(frame1_victime, attr)
            frame2_bits = getattr(frame2_adversary, attr)
            for b1, b2 in zip(frame1_bits, frame2_bits):
                can_bus.receive_frames(int(b1), int(b2), attr, node1=victime_ecu, node2=adversary_ecu)
              
    # TODO la prima volta entrambi i nodi dovrebbero entrare in error passive, poi l'attaccante dovrebbe tornare in error active  
    try:
        for i in range(1, 40):
            print("\n")
            print("loop n: ", i)
            if can_bus.is_idle():
                for attr in frame1_victime.__dict__:
                    frame1_bits = getattr(frame1_victime, attr)
                    frame2_bits = getattr(frame2_adversary, attr)
                    for b1, b2 in zip(frame1_bits, frame2_bits):
                        can_bus.receive_frames(int(b1), int(b2), attr, node1=victime_ecu, node2=adversary_ecu)

            # can_bus.print_out_sequence()
            print(adversary_ecu)
            print(victime_ecu)

    except:
        print("\n******** System-Off ********\n")
    