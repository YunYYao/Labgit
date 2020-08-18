# -*- coding: utf-8 -*-
"""
Created on Thu Jan 10 16:13:10 2013

@author: weijian-office
"""
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import rc 
import os, shutil 
from BTK_fit_P import BTK_IV


#path=os.getcwd() + r'\file'
#print('Data file direction is '+path)
#namelist=os.listdir(path) 
#rc('lines',markersize=4)# default is 6
subdir='Fiure_20150901' 
if  os.path.isdir(subdir): 
    shutil.rmtree(subdir) 
os.mkdir(subdir) 
os.chdir(subdir) 
#from find_tableau import load_data
#from find_tableau import load_data
#from matplotlib import rc
mpl.rcParams['text.latex.unicode']=True

IV=BTK_IV(0.2,1,0.0,0.00,5,0.0) #def BTK_IV(T,delta,Z,gamma,Vrange,P):
IV1=BTK_IV(0.2,1,0.0,0.00,5,0.2)
IV2=BTK_IV(0.2,1,0.0,0.00,5,0.5) 
IV3=BTK_IV(0.2,1,0.0,0.00,5,0.8) 
IV4=BTK_IV(0.2,1,0.0,0.00,5,1.0) 


fig=plt.figure(figsize=(8,6))
plt.axes([0.18,0.18,0.75,0.7])




plt.plot(IV[:,0],IV[:,1],'-k')
plt.plot(IV1[:,0],IV1[:,1],'-b')
plt.plot(IV2[:,0],IV2[:,1],'-r')
plt.plot(IV3[:,0],IV3[:,1],'-m')
plt.plot(IV4[:,0],IV4[:,1],'-c')

plt.xlabel('Bias Voltage (mV)')
plt.ylabel('($\mathit{dI/dV}$)$_{\mathdefault{n}}$')
plt.legend(('P=0','P=0.2','P=0.5','P=0.8','P=1'),loc=0,frameon=False,prop={'size':12})
plt.xlim(-5,5)
plt.ylim(0,2.1)
plt.text(-4.8,1.8,r'T=0.2 K;Z=0',ha='left',color='r')
plt.text(-4.8,1.6,r'$\Delta$=1 meV',ha='left',color='r')
#plt.ylim(0.87,1.08)$\Delta$=1 meV

fname = 'S2.pdf'

plt.savefig(fname,format='pdf')

plt.show()