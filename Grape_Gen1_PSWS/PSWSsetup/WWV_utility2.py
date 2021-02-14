# -*- coding: utf-8 -*-
"""
20 February 2020
WWV utility file
Routines and classes used in WWV file management and graphing
David Kazdan, AD8Y
John Gibbons, N8OBJ - mods to plot header 2/3/20

"""

#%% utility function needed here to convert ISO time into decimal hours
def time_string_to_decimals(time_string): #returns float decimal hours
    
    #print('Input time string=',time_string)
#    if (NewHdr = 'New'):   # if new header strip off date and Zulu stuff
#        time_string = time_string[11:-1]  # Hack off date 'YYYY-MM-DDT' and ending 'Z'
    time_string = time_string[11:-1]  # Hack off date 'YYYY-MM-DDT' and ending 'Z'
    #print('Used Time_String=',time_string)
    fields=time_string.split(":")
    hours=float(fields[0]) if len(fields)>0 else 0.0
    minutes=float(fields[1])/60. if len(fields)>0 else 0.0
    seconds=float(fields[2])/3600. if len(fields)>0 else 0.0
    #print('Hr=',hours, '  Min=',minutes, '  Sec=',seconds, '\n')
    return (hours + minutes + seconds)

#%
#%% modified from "Double-y axis plot,
# http://kitchingroup.cheme.cmu.edu/blog/2013/09/13/Plotting-two-datasets-with-very-different-scales/
#import matplotlib.pyplot as plt
#from matplotlib.pyplot import plot, legend, show, grid, figure, savefig

def graph_Doppler_and_power_data():
    fig = plt.figure(figsize=(19,10)) # inches x, y with 72 dots per inch
    ax1 = fig.add_subplot(111)
    ax1.plot(hours, filtDoppler, 'k') # color k for black

    ax1.set_ylabel('Doppler shift, Hz')
    ax1.set_xlim(0,24) # UTC day
    ax1.set_ylim([-1, 1]) # -1 to 1 Hz for Doppler shift
    #
    ax2 = ax1.twinx()
    ax2.plot(hours, filtPower, 'r-')  # NOTE: Set for filtered version
    ax2.set_ylabel('Power in relative dB', color='r')
    ax2.set_ylim(min_power, max_power) #as determined above for this data set
    for tl in ax2.get_yticklabels():
        tl.set_color('r')
    #
#    plt.title('HF Beacon Doppler Shift Plot for:     ' + OrgName + ' \nLat= ' + Lat + '    Long=' + Lon + '    Elv= ' + Alt + ' M\n WWV 5 MHz   ' + PlotDate)
#    plt.savefig(DATADIR+ 'two-scales-5.png', dpi=250, orientation='landscape')

#&
