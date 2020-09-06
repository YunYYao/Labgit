# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

"""
K6221-sin_wave-offset mode + SR830 to detect the dV - dI for Josephson coupling

"""

from sqm import *
import numpy as np
import matplotlib.pyplit as plt
import os
import time

ppms=PPMS()
vna=VNA()
k6221=K6221()
sr830=SR830()

TempPoints=[5,4,6]
FreqPoints=[11.8] #np.arange(10,15,0.2)
FieldPonits=[0,1020]

#set VNA
vna.set_on_off('on')
vna.spin_pumping_init(measure_type='S21',freq_cent=10e9,fspan=0.2e9,power=-25,ave=16,IF=10e3,sweep_time=300)
vna.auto_scale()

#set PPMS
Temp=5  # in K
H=1020  # in Oe
#ppms.setField(H)
#ppms.setTemperature(Temp)

#set K6221, current inmA
Is=-1e-3
Ie=1e-3
Istep=2e-5
di=2e-5

FilePath='E:\\Cai Ranran\\FMR driven Josephson Effect\\Nb(100)-Py(5)-Nb(100)\\20200818_S2\\20200901\\5K\\1020Oe'

#k6221.arm_sin(mode='sin',f=7,offset=0.000,ampl=5e-6,Range='FIX')
#k6221.set_DCoffset(offset=Is,ramp=0.2)


real_plot_another_process(plot_row_number=1,columns_list=[])

i=0
fspan=0.2e9
power=0

for freq in FreqPoints:
    i=i+1

    filename=str(i)+'th '+str(Temp)+'K '+str(H)+'Oe '+str(freq)+'GHz_S21.txt'    
    fp=os.path.join(FilePath,filename)
    vna.spin_pumping_init(freq_cent=freq*1e9,fspan=fspan,power=power,ave=16,IF=10e3,sweep_time=300)
    vna.auto_scale()
    
    k6221.set_DCoffset(Is)   # in A
    time.sleep(60)
    k6221.sweep_offset(pathfilename=fp,Istart=Is,Iend=Ie,ramp=Istep,dI=di)

    

    
    