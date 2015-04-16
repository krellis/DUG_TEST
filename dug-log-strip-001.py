#!/usr/bin/env python3
#-*- coding: utf-8 -*-

################################################################################
#
# Usage: dug-log-strip-001.py <LOG_FILE>
#
# Version history:
#   14.11.00: -- Initial version
#   14.11.01: -- Fixes some labels on the plots & calculates the uncertainty in 
#                the processing rate correctly.
#
# Richard Goodwin
# v14.11.01
# 28-NOV-2014
#
################################################################################

import os
import sys
import re
import time
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker as mticker

#Edit these if necessary #######################################################
ffid_mb = 203                                   #Size of FFID in MB
min_time = 0                                    #Minimum left hand axis
max_time = 30000                                #Maximum left hand axis
num_tbin = 31                                   #Number of bins for Histogram
min_slag = 0                                    #Min right hand axis
max_slag = 60                                   #Max right hand axis
# num_lbin = 7
################################################################################

logname = sys.argv[1]
outname = sys.argv[1].split('.')[0] + '-strip-001.txt'

def logout(fname, comm):
    ofile = open(fname, 'a')
    ofile.write(comm + '\n')
    ofile.close()

def rem_dbl_spaces(str):
    lenstr = 0
    while len(str) != lenstr:
        lenstr = len(str)
        str = str.replace('  ', ' ')
    return str

sp = 0
proc_time_list = []
shots_behind_list = []
parsing_ten_list = []
proc_ten_list = []
with open(logname, 'r') as log:
    for line in log:
        line = rem_dbl_spaces(line)
        sline = line.strip().split(' ')
        
        if re.search('Processing shot', line):
            sp = int(sline[3])
            ptime = float(sline[5].replace(',',''))
            proc_time_list.append((sp, ptime))
        
        if re.search(r'shotsBehind', line):
            shot_lag = sline[3].split('=')
            if len(shot_lag) == 2 and sp > 0:
                if shot_lag[1].isdigit():
                    shots_behind_list.append((sp, int(shot_lag[1])))

        if re.search('Parsing 10 files took average', line):
            parse_ten_time = float(sline[7].replace(',',''))
            # print(parse_ten_time)
            parsing_ten_list.append((sp, float(parse_ten_time)))
            # time.sleep(0.2)
            
        if re.search('Processing 10 shots took average', line):
            proc_ten_time = float(sline[7].replace(',',''))
            # print(proc_ten_time)
            proc_ten_list.append((sp, float(proc_ten_time)))
            # time.sleep(0.2)
            
# print(proc_time_list)
# print(shots_behind_list)
# print(parsing_ten_list)
# print(proc_ten_list)
# for i in proc_time:
    # print(i)
    # time.sleep(0.2)
# for i in shots_behind_list:
    # print(i)
    # time.sleep(0.1)

proc_time = np.array(proc_time_list, dtype=[('sp', int), ('val', float)])#.sort(order='sp')
shots_behind = np.array(shots_behind_list, dtype=[('sp', int), ('val', int)])#.sort('sp')
parsing_ten = np.array(parsing_ten_list, dtype=[('sp', int), ('val', float)])#.sort('sp')
proc_ten = np.array(proc_ten_list, dtype=[('sp', int), ('val', float)])#.sort('sp')

proc_time.sort(order='sp')
shots_behind.sort(order='sp')
parsing_ten.sort(order='sp')
proc_ten.sort(order='sp')

################################################################################

# fig1 = plt.figure(figsize=(15,10), facecolor='w')
# gs11 = gridspec.GridSpec(2,2)
# ax11 = fig1.add_subplot(gs11[0])
# ax12 = fig1.add_subplot(gs11[1])
# ax13 = fig1.add_subplot(gs11[2])
# ax14 = fig1.add_subplot(gs11[3])

# ax11.set_title('Single Shot Processing Time')
# ax12.set_title('Shots Behind Production')
# ax13.set_title('Mean Time to Parse Files')
# ax14.set_title('Mean Time to Process Files')

# ax11.set_ylabel('Time (ms)')
# ax12.set_ylabel('Number Shots')
# ax13.set_ylabel('Time (ms)')
# ax14.set_ylabel('Time (ms)')

# ax11.set_xlabel('Shot Point')
# ax12.set_xlabel('Shot Point')
# ax13.set_xlabel('Shot Point')
# ax14.set_xlabel('Shot Point')

# ax11.set_ylim(ymin=min_time, ymax=max_time)
# ax12.set_ylim(ymin=min_time, ymax=10)
# ax13.set_ylim(ymin=min_time, ymax=max_time)
# ax14.set_ylim(ymin=min_time, ymax=max_time)

# cax11 = ax11.plot(proc_time['sp'], proc_time['val'], 'b-', linewidth=3)
# cax12 = ax12.plot(shots_behind['sp'], shots_behind['val'], 'r-', linewidth=3)
# cax13 = ax13.plot(parsing_ten['sp'], parsing_ten['val'], 'g-', linewidth=3)
# cax14 = ax14.plot(proc_ten['sp'], proc_ten['val'], 'y-', linewidth=3)

# ax11.xaxis.set_major_locator(mpl.ticker.MultipleLocator(1000))
# ax11.xaxis.set_minor_locator(mpl.ticker.MultipleLocator(100))
# ax11.yaxis.set_major_locator(mpl.ticker.MultipleLocator(5000))
# ax11.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(1000))
# ax11.xaxis.grid(True, 'major', linestyle='-', linewidth=0.3)
# ax11.xaxis.grid(True, 'minor', linestyle='-', linewidth=0.1)
# ax11.yaxis.grid(True, 'major', linestyle='-', linewidth=0.3)
# ax11.yaxis.grid(True, 'minor', linestyle='-', linewidth=0.1)

# ax12.xaxis.set_major_locator(mpl.ticker.MultipleLocator(1000))
# ax12.xaxis.set_minor_locator(mpl.ticker.MultipleLocator(100))
# ax12.yaxis.set_major_locator(mpl.ticker.MultipleLocator(5))
# ax12.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(1))
# ax12.xaxis.grid(True, 'major', linestyle='-', linewidth=0.3)
# ax12.xaxis.grid(True, 'minor', linestyle='-', linewidth=0.1)
# ax12.yaxis.grid(True, 'major', linestyle='-', linewidth=0.3)
# ax12.yaxis.grid(True, 'minor', linestyle='-', linewidth=0.1)

# ax13.xaxis.set_major_locator(mpl.ticker.MultipleLocator(1000))
# ax13.xaxis.set_minor_locator(mpl.ticker.MultipleLocator(100))
# ax13.yaxis.set_major_locator(mpl.ticker.MultipleLocator(5000))
# ax13.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(1000))
# ax13.xaxis.grid(True, 'major', linestyle='-', linewidth=0.3)
# ax13.xaxis.grid(True, 'minor', linestyle='-', linewidth=0.1)
# ax13.yaxis.grid(True, 'major', linestyle='-', linewidth=0.3)
# ax13.yaxis.grid(True, 'minor', linestyle='-', linewidth=0.1)

# ax14.xaxis.set_major_locator(mpl.ticker.MultipleLocator(1000))
# ax14.xaxis.set_minor_locator(mpl.ticker.MultipleLocator(100))
# ax14.yaxis.set_major_locator(mpl.ticker.MultipleLocator(5000))
# ax14.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(1000))
# ax14.xaxis.grid(True, 'major', linestyle='-', linewidth=0.3)
# ax14.xaxis.grid(True, 'minor', linestyle='-', linewidth=0.1)
# ax14.yaxis.grid(True, 'major', linestyle='-', linewidth=0.3)
# ax14.yaxis.grid(True, 'minor', linestyle='-', linewidth=0.1)

# fig1.savefig('{fn}-sep-plt.png'.format(fn=sys.argv[1]))


fig2 = plt.figure(figsize=(15,10), facecolor='w')
gs21 = gridspec.GridSpec(2,2, height_ratios=[90,10], width_ratios=[80,20])
ax21 = fig2.add_subplot(gs21[0])
# ax21 = fig2.add_subplot(111)
ax22 = ax21.twinx()
ax23 = fig2.add_subplot(gs21[1])
# ax24 = ax23.twinx()

cax21 = ax21.plot(proc_time['sp'], proc_time['val'], 'b-', linewidth=1, label='Single shot processing time')
cax22 = ax22.plot(shots_behind['sp'], shots_behind['val'], 'r-', linewidth=3, label='shotsBehind')
cax23 = ax21.plot(parsing_ten['sp'], parsing_ten['val'], 'g-', linewidth=3, label='Mean(10) file parsing time')
cax24 = ax21.plot(proc_ten['sp'], proc_ten['val'], 'y-', linewidth=3, label='Mean(10) processing time')
cax25 = ax22.plot(proc_ten['sp'], (ffid_mb*1000)/proc_ten['val'], 'm--.', linewidth=3, label='Processing Rate')

# cax21 = ax21.plot(proc_time['sp'], proc_time['val'], 'b.', linewidth=1, label='Single shot processing time')
# cax22 = ax22.plot(shots_behind['sp'], shots_behind['val'], 'r.', linewidth=3, label='Shots behind production')
# cax23 = ax21.plot(parsing_ten['sp'], parsing_ten['val'], 'g.', linewidth=3, label='Mean(10) file parsing time')
# cax24 = ax21.plot(proc_ten['sp'], proc_ten['val'], 'y.', linewidth=3, label='Mean(10) processing time')
# cax25 = ax22.plot(proc_ten['sp'], (ffid_mb*1000)/proc_ten['val'], 'm.', linewidth=3, label='Processing Rate')

hist_tbin = np.linspace(min_time, max_time, num_tbin)
# hist_lbin = np.linspace(min_slag, max_slag, num_lbin)

cax26 = ax23.hist(proc_time['val']/1000, hist_tbin/1000, align='left')
# cax27 = ax24.hist(shots_behind['val'], hist_lbin)
# cax28 = ax23.hist(parsing_ten['val'], hist_tbin)
# cax29 = ax23.hist(proc_ten['val'], hist_tbin)

ax21.set_title('DUG RTQC Log: SEGD File Processing Speed ({f})'.format(f=logname))

ax21.set_xlabel('Shot Point')
ax21.set_ylabel('Time (ms)')
ax22.set_ylabel('Number Shots / Processing Rate (MB/s)')
ax23.set_xlabel('Time (s)')
ax23.set_ylabel('Count')

ax21.set_ylim(ymin=min_time, ymax=max_time)
ax22.set_ylim(ymin=min_slag, ymax=max_slag)

# legend = fig2.legend(loc='lower left')
legend21 = ax21.legend(loc='upper left', bbox_to_anchor=[-0.1,-0.05], ncol=1, frameon=False)
legend22 = ax22.legend(loc='upper left', bbox_to_anchor=[0.3,-0.05], frameon=False)

ax21.xaxis.set_major_locator(mpl.ticker.MultipleLocator(500))
ax21.xaxis.set_minor_locator(mpl.ticker.MultipleLocator(100))
ax21.yaxis.set_major_locator(mpl.ticker.MultipleLocator(5000))
ax21.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(1000))
ax21.xaxis.grid(True, 'major', linestyle='-', linewidth=0.3)
ax21.xaxis.grid(True, 'minor', linestyle='-', linewidth=0.1)
ax21.yaxis.grid(True, 'major', linestyle='-', linewidth=0.3)
ax21.yaxis.grid(True, 'minor', linestyle='-', linewidth=0.1)

# ax22.xaxis.set_major_locator(mpl.ticker.MultipleLocator(1000))
# ax22.xaxis.set_minor_locator(mpl.ticker.MultipleLocator(100))
ax22.yaxis.set_major_locator(mpl.ticker.MultipleLocator(10))
ax22.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(1))
# ax22.xaxis.grid(True, 'major', linestyle='-', linewidth=0.3)
# ax22.xaxis.grid(True, 'minor', linestyle='-', linewidth=0.1)
ax22.yaxis.grid(True, 'major', linestyle='-', linewidth=0.3)
ax22.yaxis.grid(True, 'minor', linestyle='-', linewidth=0.1)

# print(hist_tbin)
# ax23.set_xticklabels(hist_tbin[:-1], rotation=90)
ax23.xaxis.set_major_locator(mpl.ticker.MultipleLocator(5))
ax23.xaxis.set_minor_locator(mpl.ticker.MultipleLocator(1))
# ax23.yaxis.set_major_locator(mpl.ticker.MultipleLocator(5000))
# ax23.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(1000))
ax23.xaxis.grid(True, 'major', linestyle='-', linewidth=0.3)
ax23.xaxis.grid(True, 'minor', linestyle='-', linewidth=0.1)
ax23.yaxis.grid(True, 'major', linestyle='-', linewidth=0.3)
ax23.yaxis.grid(True, 'minor', linestyle='-', linewidth=0.1)

comm1 = 'Single Proc Time:{mi:>8.1f} to {ma:>8.1f}, {me:>8.1f} +/- {sd:>8.1f}ms'.format(mi=proc_time['val'].min(), ma=proc_time['val'].max(), me=proc_time['val'].mean(), sd=proc_time['val'].std())
comm2 = 'shotsBehind     :{mi:>8.1f} to {ma:>8.1f}, {me:>8.1f} +/- {sd:>8.1f}'.format(mi=shots_behind['val'].min(), ma=shots_behind['val'].max(), me=shots_behind['val'].mean(), sd=shots_behind['val'].std())
comm3 = 'Mean Parse File :{mi:>8.1f} to {ma:>8.1f}, {me:>8.1f} +/- {sd:>8.1f}ms'.format(mi=parsing_ten['val'].min(), ma=parsing_ten['val'].max(), me=parsing_ten['val'].mean(), sd=parsing_ten['val'].std())
comm4 = 'Mean Proc Time  :{mi:>8.1f} to {ma:>8.1f}, {me:>8.1f} +/- {sd:>8.1f}ms'.format(mi=proc_ten['val'].min(), ma=proc_ten['val'].max(), me=proc_ten['val'].mean(), sd=proc_ten['val'].std())
comm5 = 'Proc Rate       :{mi:>8.1f} to {ma:>8.1f}, {me:>8.1f} +/- {sd:>8.1f}MB/s'.format(mi=(ffid_mb*1000)/proc_time['val'].max(), ma=(ffid_mb*1000)/proc_time['val'].min(), me=(ffid_mb*1000)/proc_time['val'].mean(), sd=(proc_time['val'].std()/proc_time['val'].mean())*((ffid_mb*1000)/proc_time['val'].mean()))
fig2.text(0.55, 0.09, comm1)
fig2.text(0.55, 0.075, comm2)
fig2.text(0.55, 0.06, comm3)
fig2.text(0.55, 0.045, comm4)
fig2.text(0.55, 0.03, comm5)

# print(proc_time['val'].max(), (ffid_mb*1000)/proc_time['val'].max())
# print(proc_time['val'].min(), (ffid_mb*1000)/proc_time['val'].min())
# print(proc_time['val'].mean(), (ffid_mb*1000)/proc_time['val'].mean())
# print(proc_time['val'].std(), (proc_time['val'].std()/proc_time['val'].mean()))


################################################################################

fig2.savefig('{fn}-one-plt.png'.format(fn=sys.argv[1]))
plt.tight_layout()
plt.show()
