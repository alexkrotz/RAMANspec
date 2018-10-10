import time
import math
import random
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib
import numpy as np
import io
import binascii
import codecs
import serial
import itertools
ser = serial.Serial('/dev/ttyUSB0')
averages = b'A1\r\n'
integration_time=b'I1000`\r\n'
integration_time_original = integration_time
n=0
if ser.isOpen():
    print(ser.name + ' is open')
    cmd = b'a\r\n'
    cmd2 = b'S\r\n'
    cmd3 = b'Q\r\n'
    print('Resetting Spectrometer')
    ser.write(cmd3)
    time.sleep(.1)
    print('switching to ascii')
    ser.write(cmd)
    time.sleep(.1)
    print('Setting Integration to: '+str(integration_time))
    ser.write(integration_time)
    time.sleep(.1)
    print('Setting Averages to: '+str(averages))
    ser.write(averages)
    time.sleep(.1)
    print('flushing terminal')
    ser.flush()
    time.sleep(.1)
def get_scan():
    n=0
    while True:
        m = 0
        if n==0:
            print('initiating scan')
            ser.flush()
            ser.write(cmd2)
            scan_start = time.perf_counter()
            n = 1
            m = 5
            data_list = []
            #print(ser.inWaiting())
        #while ser.inWaiting()<3000 and m==5:
         #   print(ser.inWaiting())
          #  print(ser.read(ser.inWaiting()+5))
        if ser.inWaiting()>0:
            spec_raw = ser.read(ser.inWaiting())
            spec_raw2 = str(spec_raw).split("\r\n")[0]
            spec_list = spec_raw2.split("\\r\\n")
            del spec_list[0]
#        del spec_list[-1]
            spec_data = []
            for i in spec_list:
                if len(i)==5 and i[0]=='0':
                    if "'" not in i:
                        spec_data.append(int(i))
            data_list.append(spec_data)
            ser.flush()
            time.sleep(1)
        #print('term refreshed')
            m=m+1
            n =n+1
        if n == 18:
            n=0
            full_spec = list(itertools.chain.from_iterable(data_list))
            #print(full_spec)
            scan_finished = time.perf_counter()
            x = range(0,len(full_spec))
            print(str(len(full_spec))+' data points received after '+str(scan_finished-scan_start)+' seconds')
            #plt.plot(x,full_spec)
            #plt.draw()
            #plt.pause(0.0001)
            #plt.clf()
            return full_spec
    
drk_scan = []
bkg_scan = []
exp_scan = []
drk_scale = 1
bkg_scale = 1
exp_scale = 1
proc_spec=[]
plt.ion()
scale_var=0
plt_var=0
x=range(0,len(proc_spec))
#plt.legend(bbox_to_anchor=(1.05,1),loc=2, borderaxespad=0.)
bkg_plotvar = 0
drk_plotvar = 0
exp_plotvar = 0
while True:
    cmd_input = input("Enter command or 'exit': ")
    if cmd_input=='exit':
        ser.close()
        print(ser.name+' is closed')
        exit()
    if cmd_input == 'drk':
        drk_scan = get_scan()
    if cmd_input == 'bkg':
        bkg_scan = get_scan()
    if cmd_input == 'exp':
        exp_scan = get_scan()
    if cmd_input == 'autoscan':
       # if integration_time!=b'I1\r\n':
       #     print('setting Integration time to 10')
       #     integration_time=b'I10\r\n'
       #     ser.write(integration_time)
       #     time.sleep(1)
       #     ser.flush()
       # else:
       #     integration_time=integration_time_original
        print('acquiring drk')
        drk_scan = get_scan()
        print('acquiring bkg')
        bkg_scan = get_scan()
        print('acquiring exp')
        exp_scan = get_scan()
    if cmd_input == 'drk_scale':
        drk_scale = float(input('Enter scaling for dark scan: '))
    if cmd_input == 'bkg_scale':
        bkg_scale = float(input('Enter scaling for background scan: '))
    if cmd_input == 'exp_scale':
        exp_scale=float(input('Enter scaling for experiment scan: '))
    if cmd_input =='scale_plot':
        if scale_var==0:
            scale_var=1
        else:
            scale_var=0
    #if cmd_input == 'plt':
    if len(drk_scan)>0 and len(bkg_scan)>0 and len(exp_scan)>0:
        min_length = min([len(drk_scan),len(bkg_scan),len(exp_scan)])
        drk_scan=drk_scan[:min_length]
        bkg_scan=bkg_scan[:min_length]
        exp_scan=exp_scan[:min_length]
            #proc_spec=[exp_i*exp_scale-(drk_i*drk_scale+bkg_i*bkg_scale) for exp_i, drk_i, bkg_i in zip(exp_scan, drk_scan, bkg_scan)]
        proc_spec=[((exp_i-min(exp_scan))/(max(exp_scan)-min(exp_scan)))*exp_scale-(((drk_i-min(drk_scan))/(max(drk_scan)-min(drk_scan)))*drk_scale+((bkg_i-min(bkg_scan))/(max(bkg_scan)-min(bkg_scan)))*bkg_scale) for exp_i, drk_i, bkg_i in zip(exp_scan, drk_scan, bkg_scan)]
        x=range(0,len(proc_spec))
        plt.clf()
        if drk_plotvar==0:
            plt.plot(range(0,len(drk_scan)),[((drk_i-min(drk_scan))/(max(drk_scan)-min(drk_scan)))*drk_scale for drk_i in drk_scan],label='drk_scan')
        if bkg_plotvar ==0:
            plt.plot(range(0,len(bkg_scan)),[((bkg_i-min(bkg_scan))/(max(bkg_scan)-min(bkg_scan)))*bkg_scale for bkg_i in bkg_scan],label='bkg_scan')
        if exp_plotvar == 0:
            plt.plot(range(0,len(exp_scan)),[((exp_i-min(exp_scan))/(max(exp_scan)-min(exp_scan)))*exp_scale for exp_i in exp_scan],label='exp_scan')
        plt.plot(x, proc_spec, label='proc_spec')
        plt.legend(bbox_to_anchor=(1.05,1),loc=2, borderaxespad=0.)
        plt.plot(x,proc_spec)
       # plt.set_xlabel('Raman Shift (cm$^{-1}$)')
       # plt.set_ylabel('Normalized Intensity')
        plt.draw()
        plt.pause(0.001)
        #else:
         #   print('missing scan: dark has '+str(len(drk_scan))+' points background has '+str(len(bkg_scan))+' points experiment has '+str(len(exp_scan))+' points')
    if cmd_input=='drk_toggle':
        if drk_plotvar==0:
            drk_plotvar=1
        else:
            drk_plotvar=0
    if cmd_input=='bkg_toggle':
        if bkg_plotvar==0:
            bkg_plotvar = 1
        else:
            bkg_plotvar = 0
    if cmd_input=='exp_toggle':
        if exp_plotvar==0:
            exp_plotvar=1
        else:
            exp_plotvar=0
    #plt.plot(x,proc_spec)
    #plt.draw()
    #plt.pause(0.001)
    









