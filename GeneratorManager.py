import pyvisa # need pip install pyvisa and pyvisa-py
import time

class SDG800():
    def __init__(self, name = ""):
        self.rm = pyvisa.ResourceManager('C:/WINDOWS/System32/nivisa64.dll')
        #self.rm = pyvisa.ResourceManager('@py')
        self.generator = None

    def connect(self, name = ""):
        success = False
        if name == "":
            name = "USB0::0x164E::0x0FA1::TW00016073::INSTR"
        try:
            self.generator = self.rm.open_resource(name, timeout=50000, chunk_size=24*1024*1024)
            success = True
        except:
            success = False
        
        #if self.requestID()[0:4] == "*IDN":
        #    success = True

        return success

    def reset(self):
        self.generator.write_termination = '\n'
        self.generator.read_termination = '\n'
        self.generator.write('*RST')

    def requestID(self):
        """ Request the instrument's ID
        @precondition: device must be connected 
        """
        id = ""
        if self.generator != None:
            id = self.generator.query("*IDN?")
        return id

    def getDeviceList(self):
        """ Get the connected divices list. Useful to search for the resource 
        name used in pyvisa.ResourceManager().open_resource(<name>)
        """
        return self.rm.list_resources()
    
    def turnOff(self):
        self.generator.write("OUTP OFF")

    def turnOn(self):
        self.generator.write("OUTP ON")

    def trig(self):
        self.generator.write("TRIG")
        
    def setSignal(self, waveform="PULS", freq = 1000, amp = 0.1, offset = 0, t = 0.001, ncycles =1):

        self.generator.write(f"FUNC {waveform}")
        self.generator.write(f"PULS:WIDT {str(t)}")
        self.generator.write(f"VOLT {str(amp)}")
        self.generator.write(f"VOLT:OFFS {str(offset)}")
        self.generator.write("BURS:STAT ON")
        self.generator.write(f"BURS:NCYC {str(ncycles)}")
        self.generator.write("TRIG:EXT")
       

if __name__ == "__main__":

    gen = SDG800()
    gen.getDeviceList()
    gen.connect()
    # #gen.setSignal(freq = 13560000, amp = 0.1, modShape = "ARB", arbWfName = "HLO", modFreq = 1000, turnOn = False)
    gen.setSignal()
    # #gen.setSignal(freq = 13560000, amp = 0.1, modShape = None, turnOn = True)
    time.sleep(5)
    
    gen.turnOn()
    gen.trig()
    time.sleep(5)
    gen.turnOff()
