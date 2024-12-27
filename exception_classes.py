class BitErrorException(Exception):
    """
    Exception raised when a bit error is detected in the CAN message.
    """
    def __init__(self):
        self.message = "A bit error has occurred in the CAN message."
        super().__init__(self.message)


class BusOffException(Exception):
    """
    Exception raised when the system is shut down due to critical errors like TEC overflow.
    """
    def __init__(self):
        self.message = "The system is turned off due to a critical error."
        super().__init__(self.message)

class FrameElaborated(Exception):
    '''
    Exception raised when the CAN bus has elaborated the frame of the arbitration winner.
    '''
    def __init__(self):
        self.message = "The frame has been elaborated."
        super().__init__(self.message)