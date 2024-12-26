
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
    
    # forse conviene utilizzare un metodo del tipo send_broadcast per inviare il messaggio si al CAN bus che 
    # agli altri nodi in modo che l'attaccante possa poi sviluppare l'attacco controllando quel frame e costruendo il suo in base a quello
    # Method takes: can bus that receive the frame, a list of others nodes
    def send_broadcast(self, can_bus, frame1, nodes, frame2=None, n_senders=1):#TODO qui ci vorrebbe un qualcosa per capire quanti stanno inviando contemporaneamente i frame (tipo un parametro: n_senders)
        if n_senders == 1:
            if can_bus.is_idle():
                print(f"{self.name} is sending frame to CAN bus...")
                for attr in frame1.__dict__:
                    frame1_bits = getattr(frame1, attr)
                    for b1 in frame1_bits:
                        can_bus.receive_frames(b1=int(b1), attr=attr, node1=self)
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
                        can_bus.receive_frames(int(b1), int(b2), attr, node1=self, node2=nodes[0])

            print(nodes[0]) # adversary
            print(self)  # victime
        
        return 0
    
    # TODO qui il nodo attaccante dovrebbe fabbricare il frame per poi effettuare il busoff attack
    def receive_broadcast(self, frame):
        print(f"{self.name} received broadcast frame: {frame}")
        return 0
    
    # active error: the victim experiences bit error, transmits an active error ﬂag, and increases its TEC by 8
    # TODO i don't know if i have to send also the error flags
    def error_detected(self):
        
        # error active status
        if self.status == self.stat[0]:
            self.tec += 8
            
            if self.tec >= 128:
                self.status = self.stat[1]
                print("Node switch to status: ", self.status)

        # error passive status
        elif self.status == self.stat[1]:
        
            if (self.tec >= 128 and self.tec <= 255) or (self.rec >= 128):  # TODO non mi convince la parte relativa al rec
                self.tec += 8   # +8 for the bit error
                self.tec -= 1   # -1 for the successful retrasmission

            if self.tec > 255 or self.rec >= 128:
                self.status = self.stat[2]
                print("Node switch to status: ", self.status)
                self.reset_node()
            
    def reset_node(self):
        self.tec = 0
        self.rec = 0
        self.status = self.stat[0]
        print("The node excedeed TEC 255. Node is shutted down.")
        raise Exception

    def __str__(self):
        return f"Node:{self.name}, TEC={self.tec}, REC={self.rec}, Status={self.status}"
    
