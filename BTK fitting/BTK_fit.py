# -*- coding: utf-8 -*-
"""
Created on Thu Jan 10 10:54:51 2013

@author: weijian-office

convert to py from MATLAB BTK codes written in NWU at around 2010 
"""

import numpy as np


def fermi(E,T):
# E,T are energy (mV) and temperature (K).
# one problem is that when E is an array, 
# it is incorrect in MATLAB for the T==0 case
    E=np.float(E); T=np.float(T)
    T=0.08617*T; # from K to mV. in MATLAB use .* for array
    if T == 0:
        if E<0: f = 1
        elif E>0: f = 0
        else : f=0.5
    else : f=1./(1.+np.exp(E/T)) 
    return f

def deriv_fermi(E,T):
    E=np.float(E); T=np.float(T)
    small_fact=0.00 # in case need to calculate T=0.
    T=0.08617*T # from K to meV.
    T_prime=T+small_fact # add a small number to get rid of zero temp sigularity 
    expo_fact = np.exp(E/T_prime) # in M code use double()
    df=expo_fact/(T_prime*(1.+expo_fact)**2)
    return df

def BTK_AB(E,delta,Z,gamma):
# gamma, added 20100427, make complex E, using i*gamma, life time effect, unit is mV
# E is energy (unit is mV, but unit is not important since only ratio between E and delta, gamma matters).
# Z is the interface barrier parameter.
# calculate the A parameter of the BTK theory, given the energy and the gap delta    
    E=np.float(E); delta=np.float(delta);Z=np.float(Z);gamma=np.float(gamma)
    E=E+1j*gamma # this is the capital gamma in PRB 49, 10016, Plecenik1994prb, life time effect
    # not sure + or - will make any difference, 
    # gamma should be nonzero to prevent DOS singularity at E=delta
    E_2=E*E
    delta_2=delta**2 # delta,Z, should be real
    Z_2=Z**2
    u0_2=0.5*(1.+np.sqrt((E_2-delta_2)/E_2)) # u0_2 can be complex, PRB 49, 10016, Plecenik1994prb
    # to get sqrt(-1) has to use np.sqrt(-1+0j) 
    # the square in Plecenik1994prb in fact means amplitude
    v0_2= 1.- u0_2
    gamma_s=u0_2+(u0_2-v0_2)*Z_2 # this is the small gamma in BTK paper, see also Plecenik1994prb
    BTK_A=abs(u0_2)*abs(v0_2)/(np.abs(gamma_s))**2
    a1=np.real(u0_2) # this is alpha
    a2=1.-a1 # this is beta
    a3=np.imag(u0_2) # this is yita
    BTK_B=Z_2*(((a1-a2)*Z-2*a3)**2+(2*a3*Z+(a1-a2))**2)/(np.abs(gamma_s))**2  
    return [BTK_A,BTK_B]

def BTK_IV(T,delta,Z,gamma,Vrange):
# 20130110 convert to py from \MATLAB\BTK\BTK_IV_tabulated.m
#
# 20100423, add the depairing gamma for input, since sometimes in one file need to fit junctions with different gamma 
# which was inside N_S.m (so also added input parameter gamma for N_S.m)
# Changed the unit of the input parameters. So for T, Tc0 the unit is K, Z is unitless, for delta, gamma,  
# and range, unit is mV (will calculate from -range to +range).
# if give Tc0, then gap parameter delta=0.08617*1.76*Tc0*(1-((T/Tc0)^3))**(0.5), unit is mV.
# this approximate formula is from old IDL program, see also Tinkham P63
# Output [volt_array;GofV;IofV];   
# 
    T=np.float(T); delta=np.float(delta);Z=np.float(Z);gamma=np.float(gamma); Vrange=np.float(Vrange)
    energy_range=3*Vrange # the range over which we want to find G(E), unit is mV.
    nenergy_vals=301 # the number of different energy values, related to the resolution of integration.
    energy_step=energy_range/nenergy_vals
    volt_range=Vrange 
    nvolts=601 # the number of voltage steps
    volt_step=volt_range/nvolts 
# Declare arrays to hold the integration results
    Energy_vals=np.zeros(nenergy_vals)
    IntegrandofE=np.zeros(nenergy_vals)
    IntegrandofE2=np.zeros(nenergy_vals)
# Define variable arrays 
    energy_vals_array=np.linspace(1,nenergy_vals,num=nenergy_vals)
    Energy_vals=(energy_vals_array*energy_step)-energy_range/2.
    volt_array=np.zeros(nvolts)
    IofV=np.zeros(nvolts)
    GofV=np.zeros(nvolts)
    for j1 in range(nvolts):
        volt_array[j1]=j1*volt_step
        for k in range(nenergy_vals):
            E=Energy_vals[k]    
            IntegrandofE2[k]=(1.+Z**2)*deriv_fermi(E-volt_array[j1], T)*(1.+BTK_AB(E, delta, Z,gamma)[0]-BTK_AB(E, delta, Z,gamma)[1])
            IntegrandofE[k]=(1.+Z**2)*(fermi(E-volt_array[j1], T)-fermi(E, T))*(1.+BTK_AB(E, delta, Z,gamma)[0]-BTK_AB(E, delta, Z,gamma)[1])
        GofV[j1]=np.trapz(IntegrandofE2,x=Energy_vals)
        IofV[j1]=np.trapz(IntegrandofE,x=Energy_vals)
    volt_array=np.append(volt_array[::-1]*(-1),volt_array[1:])
    GofV=np.append(GofV[::-1],GofV[1:])
    IofV=np.append(IofV[::-1]*(-1),IofV[1:])
    return np.transpose([volt_array,GofV,IofV])    