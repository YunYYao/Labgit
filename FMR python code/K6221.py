# -*- coding: utf-8 -*-
"""
Created on Wed Sep 04 16:57:40 2019

@author: Yunyan Yao
"""

import visa
import numpy as np
import sys
import time
import matplotlib.pyplot as plt
import clr
import pyqtgraph as pg
import os
import threading as td

import QuantumDesign.QDInstrument as QDInstrument

DATA=''
COLUMNS=''

rm=visa.ResourceManger()

class K6221():                                                    
    """Just in delta mode 20190904"""
    
    def __init__(self,k6221_address='GPIB0::23::INSTR'):
        self.k6221=rm.open_resource(k6221_address)
    def A2182_connect(self):
        self.k6221.write('SOUR:DELT:NVPR')
        
            
    def set_I_HIGH(self,I_HIGH=1e-3):
        self.k6221.write('SOUR:DELT:HIGH {}'.format(str(I_HIGH)))
    def set_I_LOW(self,I_LOW=-1e-3):
        self.k6221.write('SOUR:DELT:LOW '+ str(I_LOW))
    def set_delay(self,delay=0.002):
        self.k6221.write('SOUR:DELT:DELAY {}'.format(str(delay)))
    def set_delta_count(self, delta_count='INF'):
        self.k6221.write('SOUR:DELT:COUNt {}'.format(str(delta_count)))    # 1 to 65536 and inifinte
    def arm(self):
        self.k6221.write('SOUR:DELT:ARM')
    def read_buffer(self):
       # self.k6221.query(':SENS:DATA?')
      # time.sleep(0.10)
        return self.k6221.query_ascii_values('SENS:DATA:FRESh?')[0]
    
    def set_unit(self,unit='OHMS'):
        self.k6221.write('UNIT {}'.format(str(unit)))  #specify reading units
    def stop_meas(self):
        self.k6221.write('SOUR:SWE:ABOR')
        
    def ARM_Delta(self,I_resource=1e-3,delay=0.002,delta_count='INF'):
        if not self.ask_delta_mode():
            self.set_I_HIGH(I_resource)
            self.set_delta_count(delta_count)
            self.set_delay(delay)
            self.k6221.write('SOUR:DELT:CAB on')
            self.arm
            time.sleep(5)
            while not self.ask_delta_mode():
                self.arm
                time.sleep(1)

            self.k6221.write(':INIT:IMM')      # start delta measurement
            time.sleep(1)
            print 'Delta mode is running'
            
    def ask_delta_mode(self):
        return int(self.k6221.query('SOUR:DELT:ARM?'))
        
    def R_T_text_init(self,pathfilename):
        global COLUMNS
        COLUMNS='T(K), R(ohms)\n'
        print COLUMNS
        if not os.path.exists(pathfilename):
            f1=open(pathfilename,'a')
            f1.write(COLUMNS)
            f1.close()
           
    def RUN_Delta(self,pathfilename,set_Temp,Temp_speed):
        global DATA
        self.R_T_text_init(pathfilename)
        ppms=PPMS()
        ppms.setTemperature(set_Temp,Temp_speed,stable=0)
        temperature=float(ppms.getTemperature()[0])
        data_last=DATA
        self.ARM_Delta(I_resource=1e-6,delay=0.002,delta_count='INF')
        #self.set_unit()
        while abs(temperature-set_Temp)>0.02:
            #self.set_unit()
            R=self.read_buffer()
            temperature=float(ppms.getTemperature()[0])
            DATA=str(temperature)+','+str(R) +'\n'
            if not DATA==data_last:
                f1=open(pathfilename,'a')
                f1.write(DATA)
                f1.close()
                data_last=DATA
                print temperature
                time.sleep(0.5)
    
    def set_DCoffset(self,offset=-1e-3,ramp=2e-5):
        '''offset: [-0.105 , 0.105] in A. but in Amps for SCPI
           ramp: 
        '''
        dcoffset=self.read_DCoffset()
        print('the start offset is '+str(dcoffset*1E3)+'mA')
        delta_offset=offset - dcoffset
        
        while abs(delta_offset) != 0:
            
            if delta_offset < 0:
                k=-1
            if delta_offset == 0:
                k=0
            if delta_offset > 0:
                k=1
                
            set_offset=dcoffset + k*min(abs(delta_offset),ramp)
            self.k6221.write('SOUR:WAVE:OFFS '+str(set_offset))
            
            dcoffset=self.read_DCoffset()
            delta_offset=offset - dcoffset
            time.sleep(1)
            
        dcoffset=self.read_DCoffset()
        
        print('Isd is '+str(dcoffset*1e3)+'mA')
                   
        
    def read_DCoffset(self):
        Isd=self.k6221.query('SOUR:WAVE:OFFS?')
        '''unit in A'''
        return float(Isd)
        
    def dvdi_text_init(self,pathfilename):
        global COLUMNS
    
        COLUMNS='Isd(mA),dV(V),dR(Ω)\n'
        print(COLUMNS)
        if not os.path.exists(pathfilename):
            f1=open(pathfilename,'a')        
            f1.write(COLUMNS)
            f1.close()
            
    def sweep_offset(self, pathfilename,Istart=-4e-3,Iend=4e-3,ramp=2e-5,dI=2e-5):
        # ALL current in mA in set-up
        global DATA
        self.dvdi_text_init(pathfilename)
        
        sr830=SR830()
        data_last=DATA
        
        self.set_DCoffset(Istart)
        dcoffset=self.read_DCoffset()   # in mA
        delta_offset=Iend - dcoffset
        
        while abs(delta_offset) != 0:
            
            if delta_offset < 0:
                k=-1
            if delta_offset == 0:
                k=0
            if delta_offset > 0:
                k=1
                
            dV=sr830.GetVoltageAverage(n=10,amplifier=1.0).split(',')[0]
            dR=float(dV)/float(dI)
            DATA=str(dcoffset)+','+str(dV) +','+str(dR)+'\n'
            if not DATA==data_last:
                f1=open(pathfilename,'a')
                f1.write(DATA)
                f1.close()
                data_last=DATA
                print('Isd is '+str(dcoffset*1e3)+'mA')
                time.sleep(0.5)   
                
            set_offset=dcoffset + k*min(abs(delta_offset),ramp)
            self.k6221.write('SOUR:WAVE:OFFS '+str(set_offset))
            
            dcoffset=self.read_DCoffset()
            delta_offset=Iend - dcoffset
            time.sleep(1)


        Istart=-Istart
        Iend=-Iend
        self.set_DCoffset(Istart)
        dcoffset=self.read_DCoffset()   
        delta_offset=Iend - dcoffset

        while abs(delta_offset) != 0:
            
            if delta_offset < 0:
                k=-1
            if delta_offset == 0:
                k=0
            if delta_offset > 0:
                k=1
                
            dV=sr830.GetVoltageAverage(n=10,amplifier=1.0).split(',')[0]
            dR=float(dV)/float(dI)
            DATA=str(dcoffset)+','+str(dV) +','+str(dR)+'\n'
            if not DATA==data_last:
                f1=open(pathfilename,'a')
                f1.write(DATA)
                f1.close()
                data_last=DATA
                print('Isd is '+str(dcoffset*1e3)+'mA')
                time.sleep(0.5)   
                
            set_offset=dcoffset + k*min(abs(delta_offset),ramp)
            self.k6221.write('SOUR:WAVE:OFFS '+str(set_offset))
            
            dcoffset=self.read_DCoffset()
            delta_offset=Iend - dcoffset
            time.sleep(1)
        

    

         
'''
meaurement below
'''

'''
""" R-T meas via K6221+2182A delta mode """
ppms=PPMS()
k6221=K6221()

init_T=150
set_T=150
T_ramp=3
I_resource=1e-6
delta_count='INF'

FilePath='E:\\YYY\\20190301\\YBCO-YIG\\3rd\\R-T\\#4'
if not os.path.exists(FilePath):
    os.makedirs(FilePath)
    filename='S3-4 '+ str(init_T)+'k to '+str(set_T)+'k '+str(T_ramp)+'K-min '+'I='+str(I_resource)+' A'+'.txt'
    fp=os.path.join(FilePath,filename)

    k6221.ARM_Delta(I_resource,delay=0.002,delta_count='INF')
    real_plot_another_process(plot_row_number=1,columns_list=[])

    #k6221.R_T_text_init(fp)
    k6221.RUN_Delta(fp,set_T,T_ramp)
'''
       
     
    
"""
K6221-sin_wave-offset mode + SR830 to detect the dV - dI for Josephson coupling

"""

from sqm import *
import numpy as np
import matplotlib.pyplit as plt
import os


ppms=PPMS()
vna=VNA()
k6221=K6221()
sr830=sr830()

TempPoints=[300,10]
FreqPoints=[]
FieldPonits=[]

"""set VNA"""
vna.power_on_off('on')
vna.fmr_init()
vna.auto_scale()

"""set K6221"""


FilePath='E:\\YYY\\FGT\\NO_1\\damping'

real_plot_another_process(plot_row_number=1,columns_list=[])

i=0
for freq in FreqPoints:
    i=i+1
    Temp=5  # in K
    H=1000  # in Oe
    filename=str(i)+'th '+str(Temp)+'K '+str(H)+'Oe '+str(freq/1e9)'GHz_S21.txt'
    fp=os.path.join(FilePath,filename)
    
    k6221.
    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
       
        
        