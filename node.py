
from bus_frame import CANFrame
from exception_classes import *

class Node:
    stat = ['error active', 'error passive', 'bus off']
    
    def __init__(self, name):
        self.tec = 0
        self.rec = 0
        self.status = self.stat[0]
        self.name = name
        self.tec_history = [0]
        
    def make_frame(self, id, dlc, data):
        self.can_frame = CANFrame()
        self.can_frame.make(id=id, dlc=dlc, data=data)
        print(self.can_frame)
        
        return self.can_frame
    
    # method to send via broadcast the frame to the CAN bus and other nodes
    def send_broadcast(self, can_bus, frame1, nodes, frame2=None, n_senders=1):
        
        if n_senders == 1:
            if can_bus.is_idle():
                print(f"{self.name} is sending frame to CAN bus...")
                
                for attr in frame1.__dict__:
                    frame1_bits = getattr(frame1, attr)
                    
                    for b1 in frame1_bits:
                        can_bus.receive_frames(b1=int(b1), attr=attr, node1=self)
                
                can_bus.set_status(can_bus.status[0])
                print(f"{self.name} finished sending frame.")
            
            for node in nodes:
                if node.name != self.name:
                    node.receive_broadcast(frame1)
        
        else:
            print("\n")
            
            if can_bus.is_idle():
            
                for attr in frame1.__dict__:
                    frame1_bits = getattr(frame1, attr)
                    frame2_bits = getattr(frame2, attr)
            
                    for b1, b2 in zip(frame1_bits, frame2_bits):
            
                        try:
                            can_bus.receive_frames(int(b1), int(b2), attr, node1=self, node2=nodes[0])
            
                        except BitErrorException:
                            return 0
                        except FrameElaborated:
                            return 0
                        
            print(nodes[0]) # adversary
            print(self)  # victim
        
        return 0
    
    # each node receive the frame sent via broadcast
    def receive_broadcast(self, frame):
        print(f"{self.name} received broadcast frame: {frame}")
        
        if self.name == "adversary":
            self.fabricate_frame(frame)
        
        return 0
    
    # Chapter 4.2: Empty msg filter. Since an adversary can read contents only from accepted messages, meeting C1 depends on how the filter 
    # is set at the compromised ECU.
    
    # method for the attacker to fabricate victim's frame with Empty Message Filter situation
    def fabricate_frame(self, frame):
        # In order to cause a bit error, it should happen in the control (dlc) or data frame segment
        
        # Chapter 4.1: Since CAN messages normally have DLC set to at least 1 and non-zero data values, one simple 
        # but most deﬁnite way for the adversary to cause a mismatch is to set the attack message’s DLC or DATA values to all 0s
        fabricated_dlc = "0000"
        fabricated_data = "0000000000000000000000000000000000000000000000000000000000000000"
        
        self.make_frame(frame.id, fabricated_dlc, fabricated_data)
        
        return 0
    
    def error_detected(self):
        
        # error active status
        if self.status == self.stat[0]:
            self.tec += 8
            self.tec_history.append(self.tec)
            
            if self.tec >= 128:
                self.status = self.stat[1]
                print("Node switch to status: ", self.status)

        # error passive status
        elif self.status == self.stat[1]:
        
            if (self.tec >= 128 and self.tec <= 255) or (self.rec >= 128):
                self.tec += 8   # +8 for the bit error
                self.tec_history.append(self.tec)
                
                self.tec -= 1   # -1 for the successful retrasmission
                self.tec_history.append(self.tec)
            

            if self.tec > 255:
                self.status = self.stat[2]
                print("Node switch to status: ", self.status)
                
                self.reset_node()
            
    def reset_node(self):
        self.tec = 0
        self.rec = 0
        self.status = self.stat[0]
        
        print("The node excedeed TEC 255. Node is shutted down.")
        
        raise BusOffException

    def __str__(self):
        return f"Node:{self.name}, TEC={self.tec}, REC={self.rec}, Status={self.status}"
    
