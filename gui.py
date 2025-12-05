import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from datetime import datetime
import os
from OSCManager import SDS1000CFL
from GeneratorManager import SDG800
import pyvisa
import time

class MeasurementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Измерительная система")
        self.root.geometry("1200x700")
        self.rm = pyvisa.ResourceManager('C:/WINDOWS/System32/nivisa64.dll')
        print(self.rm.list_resources())
        self.osc = SDS1000CFL(self.rm)
        self.gen = SDG800(self.rm)

        
        # Стиль ttkbootstrap
        self.style = tb.Style("darkly")
        
        # Создаем основную структуру
        self.create_widgets()
        
    def create_widgets(self):
        # Основной контейнер
        main_container = tk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Левая панель (элементы управления)
        left_panel = tk.Frame(main_container)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))
        
        # Правая панель (график)
        right_panel = tk.Frame(main_container)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # === Группа: Управление генератором ===
        gen_frame = tb.Labelframe(left_panel, text="Управление генератором", bootstyle=INFO)
        gen_frame.pack(fill=tk.X, pady=(0, 10), ipadx=5, ipady=5)
        
        # Поле: Амплитуда импульса
        self.create_labeled_entry(gen_frame, "Амплитуда имп., В:", "amplitude", "3")
        
        # Поле: Длительность импульса
        self.create_labeled_entry(gen_frame, "Длительность имп., с:", "duration", "0.000001")
        
        # === Группа: Управление осциллографом ===
        osc_frame = tb.Labelframe(left_panel, text="Управление осциллографом", bootstyle=WARNING)
        osc_frame.pack(fill=tk.X, pady=(0, 10), ipadx=5, ipady=5)
        
        # Поля осциллографа
        self.create_labeled_entry(osc_frame, "Шаг сетки по времени, нс:", "time_step", "100")
        self.create_labeled_entry(osc_frame, "Сдвиг по времени, нс:", "time_shift", "600")
        self.create_labeled_entry(osc_frame, "Шаг сетки по напряжению, В:", "voltage_step", "2.0")
        
        # === Поля для сохранения данных ===
        save_frame = tk.Frame(left_panel)
        save_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Директория
        self.create_labeled_entry(save_frame, "Директория:", "directory", "./measurements")
        
        # Имя файла
        self.create_labeled_entry(save_frame, "Имя файла:", "filename", f"measurement_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        # === Кнопка Измерение ===
        self.measure_btn = tb.Button(
            left_panel, 
            text="ИЗМЕРЕНИЕ", 
            command=self.on_measurement,
            bootstyle=SUCCESS,
            width=20
        )
        self.measure_btn.pack(pady=10)
        
        # Добавляем статус бар
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к измерению")
        status_bar = tb.Label(left_panel, textvariable=self.status_var, bootstyle=SECONDARY)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        
        # === Создание графика ===
        self.create_plot(right_panel)
        
    def create_labeled_entry(self, parent, label_text, var_name, default_value=""):
        """Создает метку и поле ввода"""
        frame = tk.Frame(parent)
        frame.pack(fill=tk.X, pady=2)
        
        label = tb.Label(frame, text=label_text, width=25, anchor="w")
        label.pack(side=tk.LEFT)
        
        var = tk.StringVar(value=default_value)
        setattr(self, f"{var_name}_var", var)
        
        entry = tb.Entry(frame, textvariable=var, width=15)
        entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
    def create_plot(self, parent):
        """Создает область для графика matplotlib"""
        # Создаем фигуру matplotlib
        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Осциллограмма сигналов")
        self.ax.set_xlabel("Время, с")
        self.ax.set_ylabel("Напряжение, В")
        self.ax.grid(True, linestyle='--', alpha=0.7)
        # Инициализируем пустой график
        self.line, = self.ax.plot([], [], 'b-', linewidth=2)
        
        # Создаем холст для встраивания в tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        
    def on_measurement(self):
        """Обработчик нажатия кнопки Измерение"""
        try:
            # Обновляем статус
            self.status_var.set("Выполняется измерение...")
            self.root.update()
            
            # Получаем значения из полей ввода
            params = self.get_parameters()
            
            # Имитация измерения (генерируем тестовые данные)
            data = self.simulate_measurement(params)
            
            # Обновляем график
            self.update_plot(data, params)
            
            # Сохраняем данные
            self.save_measurement(data, params)
            
            # Обновляем статус
            self.status_var.set(f"Измерение завершено: {datetime.now().strftime('%H:%M:%S')}")
            
        except Exception as e:
            self.status_var.set(f"Ошибка: {str(e)}")
    
    def get_parameters(self):
        """Получает все параметры из полей ввода"""
        params = {
            'amplitude': float(self.amplitude_var.get()),
            'duration': float(self.duration_var.get()),
            'time_step': float(self.time_step_var.get()),
            'time_shift': float(self.time_shift_var.get()),
            'voltage_step': float(self.voltage_step_var.get()),
            'directory': self.directory_var.get(),
            'filename': self.filename_var.get()
        }
        return params
    
    def simulate_measurement(self, params):
        trig_level = 0.1 #В
        puls_width = float(params['duration']) #c
        puls_amp = float(params['amplitude']) #В
        time_shift = float(params['time_shift']) #нс
        time_div = float(params['time_step']) #нс
        vdiv = float(params['voltage_step']) #В
        
        directory = params['directory'] 
        filename = params['filename'] 

        osc_connection = self.osc.connect()
        if osc_connection: 
            print("Connection with the Oscilloscope is successfully set!")
            print(f'Oscilloscope ID is {self.osc.requestID()}')
        
        gen_connection = self.gen.connect()
        if gen_connection: 
            print("Connection with the Generator is successfully set!")

        self.gen.reset()
        self.osc.reset()

        self.gen.setSignal(t=puls_width,amp=puls_amp)
        time.sleep(1) 
        
         
        self.osc.setup_oscilloscope_sds1000(vdiv=vdiv, tdiv=time_div, level=trig_level, time_shift=time_shift)
        vdiv1,ofst1 = osc.getPLT_conditions(1)
        vdiv2,ofst2 = osc.getPLT_conditions(2)
        tdiv,sara = osc.getTIME_conditions()

       
        self.gen.turnOn()
        self.gen.trig()
        #time.sleep(1)
        self.gen.turnOff()

        #while osc.oscilloscope.query('INR?') != '1': pass
     
        volt_value2 = self.osc.getWFdata(2,vdiv2,ofst2)
        volt_value1 = self.osc.getWFdata(1,vdiv1,ofst1)
        
        time_value = self.osc.calcTIME_value(len(volt_value2),tdiv,sara)

        print("Plotting..")
        self.osc.plotData(time_value,volt_value1,volt_value2,tdiv,trig_level,time_shift,vdiv1,filename)
        bmpfile = filename + ".bmp"
        self.osc.getBMP("screen.bmp")

        self.osc.close()
        self.gen.close()
                
        return {
            'time': t,
            'signal': signal_with_noise,
            'clean_signal': signal
        }
    
    def update_plot(self, data, params):
        """Обновляет график с новыми данными"""
        # Очищаем график
        self.ax.clear()
        
        # Обновляем данные
        self.ax.plot(data['time'], data['signal'], 'b-', linewidth=2, label='Измеренный сигнал')
        self.ax.plot(data['time'], data['clean_signal'], 'r--', linewidth=1, alpha=0.7, label='Идеальный сигнал')
        
        # Настраиваем график
        self.ax.set_title(f"Осциллограмма сигнала (Амплитуда: {params['amplitude']} В)")
        self.ax.set_xlabel("Время, с")
        self.ax.set_ylabel("Напряжение, В")
        self.ax.grid(True, alpha=0.3)
        self.ax.legend()
        
        # # Настраиваем сетку согласно параметрам
        # if params['time_step'] > 0:
        #     self.ax.xaxis.set_major_locator(plt.MultipleLocator(params['time_step'] * 1e-9))
        #
        # if params['voltage_step'] > 0:
        #     self.ax.yaxis.set_major_locator(plt.MultipleLocator(params['voltage_step']))
        #
        # # Применяем сдвиг по времени
        # if params['time_shift'] != 0:
        #     current_xlim = self.ax.get_xlim()
        #     self.ax.set_xlim(current_xlim[0] + params['time_shift'] * 1e-9,
        #                    current_xlim[1] + params['time_shift'] * 1e-9)


        # Перерисовываем график
        self.fig.tight_layout()
        self.canvas.draw()
    
    def save_measurement(self, data, params):
        """Сохраняет данные измерения в файл"""
        # Создаем директорию, если её нет
        os.makedirs(params['directory'], exist_ok=True)
        
        # Полный путь к файлу
        filepath = os.path.join(params['directory'], f"{params['filename']}.txt")
        
        # Сохраняем данные
        with open(filepath, 'w') as f:
            # Записываем параметры
            f.write("# Параметры измерения\n")
            for key, value in params.items():
                if key not in ['directory', 'filename']:
                    f.write(f"# {key}: {value}\n")
            
            # Записываем данные
            f.write("\n# Время(с)\tНапряжение(В)\n")
            for t, v in zip(data['time'], data['signal']):
                f.write(f"{t:.9f}\t{v:.6f}\n")
        
        print(f"Данные сохранены в: {filepath}")

def main():
    root = tb.Window(themename="darkly")
    app = MeasurementApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
