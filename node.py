# STATUS["error active", "error passive", "bus off"]

from bus_frame import CANFrame

class Node:
    stat = ['error active', 'error passive', 'bus off']
    
    def __init__(self, name):
        self.tec = 0
        self.rec = 0
        self.status = self.stat[0]
        self.name = name
        
    def make_frame(self, id, dlc, data):
        self.can_frame = CANFrame()
        self.can_frame.make(id=id, dlc=dlc, data=data)
        print(self.can_frame)
        
        return self.can_frame
    
    # active error: the victim experiences bit error, transmits an active error ﬂag, and increases its TEC by 8
    # TODO i don't know if i have to send also the error flags
    def error_detected(self):
        
        if self.status == self.stat[0]:
            self.tec += 8
            
        elif self.status == self.stat[1]:
        
            if self.tec >= 128 or self.rec >= 128:
                self.status = self.stat[1]
                
            if self.tec > 255 or self.rec >= 128:
                self.status = self.stat[2]
                self.reset_node()
            
    def reset_node(self):
        self.tec = 0
        self.rec = 0
        self.status = self.stat[0]
        print("The node excedeed TEC 255. Node is shutted down.")

    def __str__(self):
        return f"Node:{self.name}, TEC={self.tec}, REC={self.rec}, Status={self.status}"
    
