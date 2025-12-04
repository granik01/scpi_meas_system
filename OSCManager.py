import pyvisa # need pip install pyvisa and pyvisa-py
import time
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

class SDS1000CFL:
    def __init__(self, rm, name = ""):
        #self.rm = pyvisa.ResourceManager('C:/WINDOWS/System32/nivisa64.dll')
        self.rm = rm
        self.oscilloscope = None

    def connect(self, name = ""):
        success = False
        if name == "":
            name = "USB0::0xF4EC::0xEE3A::NEU00001141223::INSTR"
        try:
            self.oscilloscope = self.rm.open_resource(name, timeout=30000, chunk_size = 20*1024*1024)
            success = True
        except:
            success = False
        return success

    def reset(self):
        #self.oscilloscope.write_termination = '\n'
        #self.oscilloscope.read_termination = '\n' 
        self.oscilloscope.write('*RST')
        self.setCHDR("OFF")

    def requestID(self):
        """ Request the instrument's ID
        @precondition: device must be connected 
        """
        id = ""
        if self.oscilloscope != None:
            id = self.oscilloscope.query("*IDN?")
        return id

    def getDeviceList(self):
        """ Get the connected divices list. Useful to search for the resource 
        name used in pyvisa.ResourceManager().open_resource(<name>)
        """
        return self.rm.list_resources()

    def getChannelsStatus(self):
        """ Request the instrument's ID
        @precondition: device must be connected 
        """
        status = ""
        if self.oscilloscope != None:
            status = self.oscilloscope.query("TRACE?")
        return status

    def setCHDR(self, onoff):
        self.oscilloscope.write(f'CHDR {onoff}')

    def getCHDR(self):
        vdiv = self.oscilloscope.query('CHDR?')
        return vdiv
    
    def getTRDL(self):
        time = self.oscilloscope.query('TRDL?')
        return time
    
    def setTRDL(self, value):
        self.oscilloscope.write(f'TRDL {value}NS')

    def getCHDR(self):
        vdiv = self.oscilloscope.query('CHDR?')
        return vdiv

    def setChOnOff(self, ch, onoff):
        self.oscilloscope.write(f'C{ch}:TRA {onoff}')

    def getChVDIV(self,ch):
        vdiv = self.oscilloscope.query(f'C{ch}:VDIV?')
        return vdiv

    def setChVDIV(self, ch, value):
        self.oscilloscope.write(f'C{ch}:VOLT_DIV {value}V')

    def getChOffset(self,ch):
        offset = self.oscilloscope.query(f'C{ch}:OFFSET?')
        return offset

    def setChOffset(self, ch, value):
        self.oscilloscope.write(f'C{ch}:OFST {value}V')

    def getTIME_DIV(self):
        timediv = self.oscilloscope.query(f'TIME_DIV?')
        return timediv

    def setTIME_DIV(self,value):
        self.oscilloscope.write(f'TIME_DIV {value}NS')

    def setTRIG_conf(self,channel,select,level,slope): #(str(1),"EDGE",str("0.5"),"RISE")
        #self.oscilloscope.write(f'C{channel}:TRCP DC')
        #self.oscilloscope.write(f'TRSE {select},SR,C{channel},HT,TI,HV,500uS')
        self.oscilloscope.write(f'TRSE {select},SR,C{channel}')
        self.oscilloscope.write(f'C{channel}:TRLV {level}V')
        self.oscilloscope.write(f'C{channel}:TRSL {slope}')
        self.oscilloscope.write('TRIG_SLOPE {slope}')  # Фронт: RISE (можно также FALL или BOTH)
        self.oscilloscope.write(f'TRMD SINGLE')
    
    def getTRIG_conf(self):
        trig_select = self.oscilloscope.query('TRIG_SELECT?')  # Тип: EDGE, источник: C1
        trig_level = self.oscilloscope.query('TRIG_LEVEL?')  # Уровень триггера 1.0 В
        trig_slope = self.oscilloscope.query('TRIG_SLOPE?')  # Фронт: RISE (можно также FALL или BOTH) 
        trig_coupling = self.oscilloscope.query('TRIG_COUPLING?')
        trig_mode = self.oscilloscope.query('TRIG_MODE?')        
        print(f'TRIGSELECT:{trig_select}\nTRIGLEVEL:{trig_level}\nTRIG_SLOPE:{trig_slope}\nTRIG_COUPLING:{trig_coupling}\nTRIG_MODE:{trig_mode}')
        

    def getSARA(self):
        sara = self.oscilloscope.query('SARA?')
        return sara

    def getBMP(self, file_name):
        self.oscilloscope.write('SCDP')
        result_str = self.oscilloscope.read_raw()
        f = open(file_name,'wb')
        f.write(result_str)
        f.flush()
        f.close()

    def getPLT_conditions(self,ch):
        vdiv = self.getChVDIV(ch)
        ofst = self.getChOffset(ch)
        return float(vdiv),float(ofst)

    def getTIME_conditions(self):
        tdiv = self.getTIME_DIV()
        sara = self.getSARA()
        sara_unit = {'G':1E9,'M':1E6,'k':1E3}
        for unit in sara_unit.keys():
            if sara.find(unit)!=-1:
                sara = sara.split(unit)
                sara = float(sara[0])*sara_unit[unit]
                break
        return float(tdiv),float(sara)

    def plotData(self,t,ch1,ch2,tdiv,trig_level,time_shift,vdiv,filename):
        df1 = pd.DataFrame({'t': t, 'u1': ch1})
        df2 = pd.DataFrame({'t': t, 'u2': ch2})
        df_full = pd.DataFrame({'t': t, 'u1': ch1, 'u2': ch2})
        path_full = filename + "_full.csv"
        df_full.to_csv(path_full, sep='\t', index=False)

        time_shift = time_shift*1E-9 #нс
        time_shift_from_zero = tdiv*18/2 - time_shift
        filtered_df1 = df1[(df1['u1'] > trig_level)]
        puls_start = filtered_df1['t'].min()-time_shift_from_zero
        puls_end = filtered_df1['t'].max()
        filtered_df1 = df1-puls_start
        filtered_df1 = filtered_df1[(filtered_df1['t'] >= 0)&(filtered_df1['t'] <= tdiv*18)]
        filtered_df2 = df2[(df2['t'] >= puls_start)]-puls_start
        filtered_df2 = filtered_df2[(filtered_df2['t'] <= tdiv*18)]

        df_cut = pd.DataFrame({'t': filtered_df1['t'], 'u1': filtered_df1['u1'], 'u2': filtered_df2['u2']})
        path_cut = filename + "_cut.csv"
        df_cut.to_csv(path_cut, sep='\t', index=False)
        
        plt.figure(figsize=(7,5))
        plt.plot(filtered_df1['t'],filtered_df1['u1'],color='gold',markersize=2,label=u"CH1-T")
        plt.plot(filtered_df2['t'],filtered_df2['u2'],color='green',markersize=2,label=u"CH2-T")
        plt.xticks(np.arange(0, 19*tdiv, tdiv))
        plt.yticks(np.arange(-4*vdiv, 5*vdiv, vdiv))
        plt.xlabel("t, с")   
        plt.ylabel("U, В")   
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(filename+".png") 
        plt.show()

    def getWFdata(self,ch,vdiv,ofst):
        print(f'{ch}-channel data capturing..')
        self.setCHDR("OFF")
        #vdiv,ofst = self.getPLT_conditions(ch)
        print(f'\rVDIV:{vdiv}\nOFFSET:{ofst}')
        #self.oscilloscope.write("WFSU SP,50")
        self.oscilloscope.write(f"c{ch}:wf? dat2")
        #recv = self.oscilloscope.read_raw()
        #print(recv)
        #recv = list(recv)
        recv = list(self.oscilloscope.read_raw())[15:]
        #print(f'Полученные данные {recv}')
        recv.pop()
        recv.pop()
        volt_value = []
        for data in recv:
            if data > 127:
                data = data - 256
            else:
                pass
            volt_value.append(data)
        for idx in range(0,len(volt_value)):
            volt_value[idx] = volt_value[idx]/25*float(vdiv)-float(ofst) 
        return volt_value

    def calcTIME_value(self, nbofpoints,tdiv,sara):
        #tdiv,sara = self.getTIME_conditions()
        print(f'TDIV:{tdiv},\nSAMPLING:{sara}\n')
        time_value = []
        for idx in range(0,nbofpoints):
            #time_data = -(tdiv*18/2)+idx*(1/sara)
            #time_data = -(tdiv*18/2)-(600E-9)-(3000E-9)+idx*(1/sara)
            time_data = idx*(1/sara)
            #time_data = idx*tdiv*18/len(volt_value)
            time_value.append(time_data)
        return time_value


    def setup_oscilloscope_sds1000(self, onoff="ON", vdiv=2.0, offset=0, tdiv=1000.0, select="EDGE", level=0.1,time_shift=600):
        """Настройка SDS1000CFL для захвата одиночного импульса""" 

        # Настройка канала 1
        self.setChOnOff(1,"ON")
        self.setChOnOff(2,"ON")
        self.setChVDIV(1,str(vdiv))  # Масштаб 0.5 В/дел
        self.setChVDIV(2,str(vdiv))
        self.setChOffset(1,str(offset))  # Нет смещения
        self.setChOffset(2,str(offset))  # Нет смещения
        
        # Временная развертка
        self.setTIME_DIV(str(tdiv))  # 25 нс/дел
        self.setTRDL(str(time_shift))

        # Синхронизация
        self.setTRIG_conf(1,select,level,"POS")
        self.getTRIG_conf()      
   
    
    def close(self):
        self.oscilloscope.close()

if __name__ == "__main__":  

    osc = SDS1000CFL()
    devicelist = osc.getDeviceList()
    print(devicelist)

    connection = osc.connect()
    if connection: 
        print("Connection with the Oscilloscope is successfully set!")
    
    osc.read_termination = '\n'
    osc.setCHDR("OFF")  
    
    id = osc.requestID()
    print(f'Oscilloscope ID is {id}')
    
    osc.setup_oscilloscope_sds1000()

    osc.getBMP("screen.bmp")
    osc.getWFdata()

    osc.close()