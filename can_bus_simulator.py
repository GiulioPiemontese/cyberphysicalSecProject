import time
from matplotlib import pyplot as plt
from exception_classes import *
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
        print("CAN bus status: ", self.stat)
    
    def elaborate_frame(self, node):
        global count
        if count == 0:
            print(node.name + " frame in elaboration: " + str(node.can_frame))
            self.set_status(self.status[1])
                    
        count += 1
        return 0


    '''
    The mismatch in C3 must occur in either the control or the data ﬁeld. Note that this is infeasible in other
    ﬁelds such as CRC and ACK, because they are determined by the CAN controller
    '''
    def receive_frames(self, b1=None, b2=None, attr="", node1=None, node2=None):
        global count
        
        if b1 == None or b2 == None:
            if count == 0:
                print("*** No Arbitration ***")
            x = (lambda x, y: x if y is None else y)(node1, node2)
            self.elaborate_frame(x)
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
                    print("Arbitration winner: ", node1.name)
                    self.elaborate_frame(node1)
                    raise FrameElaborated
                
                elif b1 == 1 and b2 == 0:
                    print("Arbitration winner: ", node2.name)
                    self.elaborate_frame(node2)
                    raise FrameElaborated
                    
                else:
                    self.frame += str(b1 & b2)
                    
            count += 1
            return 0
        
        elif attr == self.frame_segments[2]:    # "dlc - bit error check"
            if count == 11:
                count += 1
                print("Two arbitration winners.")
                
            self.check_bit_error(b1, b2, node1, node2)
            return 0
        
        elif attr == self.frame_segments[3]:    # "data - bit error check"
            self.frame += str(b1 & b2)
            self.check_bit_error(b1, b2, node1, node2)

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
        
    def check_bit_error(self, b1, b2, node1, node2):
        if b1 & b2:
                
            self.frame += str(b1 & b2)
                
        else:
            # Here if there is a mismatch will be raise the error to the corresponding node
            if b1 == 0 and b2 == 1:
                print("Bit-error detected, recessive bit from: ", node2.name)   # recessive (1) from node2
                node2.error_detected()
                self.set_status(self.status[0])
                raise BitErrorException
                
            elif b1 == 1 and b2 == 0:
                print("Bit-error detected, recessive bit from: ", node1.name)   # recessive (1) from node1
                node1.error_detected()
                self.set_status(self.status[0])
                raise BitErrorException
                    
            else:
                self.frame += str(b1 & b2)
                
        return 0

    
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
    
    print("\n********** Start of Simulation **********\n")
    print("Initial State:")
    victim_ecu = Node("victim")
    print(victim_ecu)
    
    adversary_ecu = Node("adversary")
    print(adversary_ecu)
    
    frame1_victim = victim_ecu.make_frame(id="01000000001", dlc="0100", data="0000000100000010000000110000010000000001000000100000001100000100")
    
    # this adversary frame is just to show that it will be changed by the sniffing of the victim's frame
    frame2_adversary = adversary_ecu.make_frame(id="01000111101", dlc="0000", data="0000000100000010000000110000010011111111111111111111111100000000")
        
    print("victim " + "".join(getattr(frame1_victim, attribute) for attribute in frame1_victim.__dict__))
    print("adversary " + "".join(getattr(frame2_adversary, attribute) for attribute in frame2_adversary.__dict__))
    
    print("\n")
        
    victim_tec_values = []
    adversary_tec_values = []
            
    ''' broadcast non concurrent send  '''
    nodes = [adversary_ecu, victim_ecu]
    for i in range(1, 6):
        time.sleep(1)
        victim_ecu.send_broadcast(can_bus, frame1_victim, nodes)

        can_bus.print_out_sequence()
        print("\n")
                
    count = 0
    
    print("********** Start of Bus-off attack **********\n")

    print("Old victim's frame sent: ", victim_ecu.can_frame)
    print("Fabricated adversary's frame: ", adversary_ecu.can_frame)

    try:
        for i in range(1, 41):
            print("\nIteration n ", i)
            victim_ecu.send_broadcast(can_bus, frame1_victim, nodes, adversary_ecu.can_frame, 2)
            
            print(victim_ecu)
            print(adversary_ecu)
            
            # Update TEC history for plotting
            victim_tec_values = victim_ecu.tec_history
    
    except BusOffException:
        print("\n******** System-Off ********\n")
    
    # After the simulation, plot TEC values
    plt.plot(victim_tec_values, label="Victim TEC")
    plt.xlabel('Time (Simulation Steps)')
    plt.ylabel('TEC (Transmission Error Counter)')
    plt.legend()
    plt.title('TEC Over Time for Victim')
    plt.show()
    