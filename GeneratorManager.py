import pyvisa # need pip install pyvisa and pyvisa-py
import time

class SDG800:
    def __init__(self, rm, name = ""):
        #self.rm = pyvisa.ResourceManager('C:/WINDOWS/System32/nivisa64.dll')
        #self.rm = pyvisa.ResourceManager('@py')
        self.rm = rm
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

    def setFreq(self,freq):
        self.generator.write(f"FREQ {str(freq)}")

    def setPulsWidt(self,t):
        self.generator.write(f"PULS:WIDT {str(t)}")

    def setAmp(self,amp,offset):
        self.generator.write(f"VOLT {str(amp)}")
        self.generator.write(f"VOLT:OFFS {str(offset)}")
            
    def setSignal(self, waveform="PULS", freq = 10000, amp = 3.0, offset = 0, t = 0.00000005, ncycles =1):
        self.generator.write(f"FUNC {waveform}")
        self.setFreq(freq)
        self.setPulsWidt(t)
        #self.generator.write("PULS:TRAN 0.000000005")
        self.setAmp(amp,offset)
        self.generator.write("BURS:STAT ON")
        self.generator.write(f"BURS:NCYC {str(ncycles)}")
        self.generator.write("TRIG:SOUR BUS")
        
    
    def setPeriodicSignal(self, waveform="SQUARE", freq = 10000, amp = 3.0, offset = 0):
        self.generator.write(f"FUNC {waveform}")
        self.generator.write(f"FREQ {str(freq)}")
        self.generator.write(f"VOLT {str(amp)}")
        self.generator.write(f"VOLT:OFFS {str(offset)}")

    def close(self):
        self.generator.close()

if __name__ == "__main__":  

    gen = SDG800()
    gen.getDeviceList()
    gen.connect()
    gen.reset()
    gen.setSignal()
    time.sleep(1)
    gen.turnOn()
    gen.trig()
    time.sleep(1)
    gen.turnOff()
    # gen.setPeriodicSignal()
    # time.sleep(1)
    # gen.turnOn()
    # time.sleep(10)
    # gen.turnOff()
    gen.close()