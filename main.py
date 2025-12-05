import pyvisa
from OSCManager import SDS1000CFL
from GeneratorManager import SDG800
import time


if __name__ == "__main__":
    rm = pyvisa.ResourceManager('C:/WINDOWS/System32/nivisa64.dll')
    print(rm.list_resources())
    osc = SDS1000CFL(rm)
    gen = SDG800(rm)

    puls_width = 0.000001 #c
    puls_amp = 3 #В
    trig_level = 1 #В
    time_shift = 600 #нс
    time_div = 100 #нс
    vdiv = 2.0 #В
    filename = "data"


    osc_connection = osc.connect()
    if osc_connection: 
        print("Connection with the Oscilloscope is successfully set!")
        print(f'Oscilloscope ID is {osc.requestID()}')
    
    gen_connection = gen.connect()
    if gen_connection: 
        print("Connection with the Generator is successfully set!")

    gen.reset()
    osc.reset()

    gen.setSignal(t=puls_width,amp=puls_amp)
    time.sleep(1) 
    
     
    osc.setup_oscilloscope_sds1000(vdiv=vdiv, tdiv=time_div, level=trig_level, time_shift=time_shift)
    vdiv1,ofst1 = osc.getPLT_conditions(1)
    vdiv2,ofst2 = osc.getPLT_conditions(2)
    tdiv,sara = osc.getTIME_conditions()

   
    gen.turnOn()
    gen.trig()
    #time.sleep(1)
    gen.turnOff()

    #while osc.oscilloscope.query('INR?') != '1': pass
 
    volt_value2 = osc.getWFdata(2,vdiv2,ofst2)
    volt_value1 = osc.getWFdata(1,vdiv1,ofst1)
    
    time_value = osc.calcTIME_value(len(volt_value2),tdiv,sara)

    print("Plotting..")
    osc.plotData(time_value,volt_value1,volt_value2,tdiv,trig_level,time_shift,vdiv1,filename)
    osc.getBMP("screen.bmp")

    osc.close()
    gen.close()