# -*- coding: utf-8 -*-
"""
Created on Wed May 25 11:15:44 2016

@author: ppms
"""

"""Module containing a class to interface with a Quantum Dynamics PPMS DynaCool"""

# requires Python for .NET
# can be installed with 'pip install pythonnet'

import clr
import time
# load the C# .dll supplied by Quantum Design
try:
    clr.AddReference('QDInstrument')
except:
    if clr.FindAssembly('QDInstrument') is None:
        print('Could not find QDInstrument.dll')
    else:
        print('Found QDInstrument.dll at {}'.format(clr.FindAssembly('QDInstrument')))
        print('Try right-clicking the .dll, selecting "Properties", and then clicking "Unblock"')

# import the C# classes for interfacing with the PPMS
from QuantumDesign.QDInstrument import *

    
ip_address='127.0.0.1'
QDI_DYNACOOL_TYPE = QDInstrumentBase.QDInstrumentType.DynaCool
QDI_PPMS_TYPE=QDInstrumentBase.QDInstrumentType.PPMS
DEFAULT_PORT = 11000
QDI_FIELD_STATUS = ['MagnetUnknown',
      'StablePersistent',
      'WarmingSwitch',
      'CoolingSwitch',
      'StableDriven',
      'Iterating',
      'Charging',
      'Discharging',
      'CurrentError',
      'Unused9',
      'Unused10',
      'Unused11',
      'Unused12',
      'Unused13',
      'Unused14',
      'MagnetFailure']
QDI_TEMP_STATUS = ['TemperatureUnknown',
      'Stable',
      'Tracking',
      'Unused3',
      'Unused4',
      'Near',
      'Chasing',
      'Filling',
      'Unused8',
      'Unused9',
      'Standby',
      'Unused11',
      'Unused12',
      'Disabled',
      'ImpedanceNotFunction',
      'TempFailure']



class PPMS():
    """Thin wrapper around the QuantumDesign.QDInstrument.QDInstrumentBase class"""

    def __init__(self):
       self.qdi_instrument = QDInstrumentFactory.GetQDInstrument(QDI_PPMS_TYPE, False, ip_address, DEFAULT_PORT)
       self.TstatusDict={0:'unknown',1:'stable',2:'tracking',6:'chasing',5:'near'}
       self.FieldStatusDict={6:'charging',4:'holding',3:'sw-cool',1:'persistent'}

    def getTemperature(self):
        """Return the current temperature, in Kelvin."""
        Tstatus=self.qdi_instrument.GetTemperature(0,0)
        return Tstatus[1],self.TstatusDict[Tstatus[2]]

    def setTemperature(self, temp, rate, stable=1):
        """Set the temperature.
            Keyword arguments:
            temp -- the temperature in Kelvin
            rate -- the cooling / heating rate, in K / min
            """
        self.qdi_instrument.SetTemperature(temp, rate, 0)
        
        if stable==1:
            time.sleep(10)
            Tstatus=self.getTemperature()
            while not Tstatus[1]=='stable':
                Tstatus=self.getTemperature()
                time.sleep(10)
                print 'Temperature is ' +Tstatus[0]+'K'
        

    def waitForTemperature(self, delay=5, timeout=600):
        """Pause execution until the PPMS reaches the temperature setpoint."""
        return self.qdi_instrument.WaitFor(True, False, False, False, delay, timeout)

    def getField(self):
        """Return the current field, in gauss."""
        FieldStatus=self.qdi_instrument.GetField(0,0)
        return FieldStatus[1],self.FieldStatusDict[FieldStatus[2]]

    def setField(self, field, rate,holdingornot=1,stable=1):
        """Set the field.
            Keyword arguments:
            field -- the field, in gauss
            rate  -- the field sweep rate, in gauss / second
            """
        self.qdi_instrument.SetField(field, rate, 0,holdingornot )
        if stable==1:
            time.sleep(10)
            FieldStatus=self.getField()
            while not (FieldStatus[1]=='holding' or FieldStatus[1]=='persistent'):
                FieldStatus=self.getField()
                time.sleep(5)
                print 'Magnetic field is '+FieldStatus[0]+'Oe'
        
    def waitForField(self, delay=5, timeout=600):
        """Pause execution until the PPMS reaches the field setpoint."""
        return self.qdi_instrument.WaitFor(False, True, False, False, delay, timeout)