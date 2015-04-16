#!/usr/bin/env python

"""
DUG SEGD dump file rename from header FFID values.

Extracts the FFID or expanded FFID number from the SEGD general header blocks
one and two, respectively.  This is used to rename the file to the correct file
number.

The files extracted from tape are expected to be kept in a directory structure
like: /.../<line_name>/REEL0001, /.../<line_name>/REEL0002, etc.

The script should be ran from the parent directory holding each individual line
directories.

Usage:  {sname} linename [chksum_type]

Arguments:
    None
        -- Display this help and exit.
    linename
        -- Required
        -- Name of the directory containing the individual REELXXXX directories.
    chksum_type
        -- Optional - if omitted the default checksum is used
        -- Type of checksum to be used to verify source & destination files are 
           the same: 
            -- none
            -- md5
            -- sha1
            -- sha256 [default if argument omitted or incorrectly typed]

--------------------------------------------------------------------------------
Author:   Richard Goodwin (richard.goodwin@polarcus.com)
Date:     13-APR-2015
Version:  v15.04.03
--------------------------------------------------------------------------------
Written for:    python 2.6, 
Tested on:      python 2.7, 3.2, 3.3, 3.4
Current:        python {pver}
(N.B. You may need to change the she-bang on the first line to use different 
versions of python.)
"""

import sys
import os
import struct
import shutil
import hashlib
from datetime import datetime

def clear_screen():
    """Clear the terminal window"""
    if os.name == 'posix':
        #Unix & unix like
        os.system('clear')
    elif os.name in ('nt', 'dos', 'ce'):
        #Microsoft, Windows, DOS, etc
        os.system('CLS')
    else:
        #Fallback for any other operating systems
        print('\n'*500)

def shady_rest(msg):
    """Exit with optional message"""
    print('\n' + '='*80 )
    print(msg)
    print('='*80)
    sys.exit()

def decode_ffid(bin_data):
    """Decode FFID number in General Header Block 1"""
    hdr = ''
    for byteloc in range(0, len(bin_data)):
            hdr = hdr + str(hex(struct.unpack('B', bin_data[byteloc])[0])[2:]).rjust(2, '0')
    return hdr

def decode_effid(bin_data):
    """Decode expanded FFID number in General Header Block 2"""
    upack = struct.unpack(str(len(bin_data)) + 'B', bin_data)
    hdr = ''
    for i in range(0, len(upack)):
        hdr = hdr + (hex(upack[i])[2:]).zfill(2)
    ival = int(hdr,16)
    return ival

def feedback(comment):
    """Send feedback to screen and a log file"""
    print(comment)
    logfile = open(logfname, 'a')
    logfile.write('{c}\n'.format(c=comment))
    logfile.close()

clear_screen()
chksum_type = 'sha256'
chksum_types = ['none', 'md5', 'sha1', 'sha256']
if len(sys.argv) == 2:
    ok_to_continue = True
elif len(sys.argv) == 3:
    ok_to_continue = True
    chksum_type = sys.argv[2].lower()
else:
    ok_to_continue = False

if ok_to_continue and os.path.isdir(os.path.join(os.getcwd(), sys.argv[1])) and chksum_type in chksum_types:
    linename = sys.argv[1]
    line_dir = os.path.join(os.getcwd(), linename)
else:
    shady_rest(__doc__.format(sname=os.path.basename(sys.argv[0]), pver=sys.version.split(' ')[0]))

ncols = 80
cwd = os.getcwd()
logfname = os.path.join(cwd, linename + '.dug-dump.log')
if os.path.exists(logfname):
    shady_rest('Log file exists - rename or delete manually & re-run script')
# Initialise counters
rcount = 0
fcount = 0
good_chksum = 0
bad_chksum = 0
not_copied = 0
unexpected_file = 0
feedback('='*ncols)
feedback('LINE:            \t{l}'.format(l=linename))
feedback('CHKSUM ALGORITHM:\t{l}'.format(l=chksum_type.upper()))
feedback('PYTHON VERSION:  \t{l}'.format(l=sys.version.split()[0]))
feedback('='*ncols)
stime = datetime.now()
for dir in os.listdir(line_dir):
    if len(dir) == 8 and dir.startswith('REEL') and os.path.isdir(os.path.join(cwd, linename, dir)):
        rcount += 1
        rtime = datetime.now()
        feedback('PROCESSING: {d}'.format(d=dir))
        feedback('-'*ncols)
        last_fnum = 0
        for fname in os.listdir(os.path.join(linename, dir)):
            dfname = os.path.join(line_dir, dir, fname)
            fnum = fname.split('.')[0]
            try:
                fnum = int(fnum)
            except:
                fnum = -1
            fsize = os.path.getsize(dfname)
            #print(fnum, len(fname) == 13 , fname.endswith('.dump') , fnum > 0 , (fnum-last_fnum) == 1 , fsize > 0  , fsize !=16384)
            #if len(fname) == 13 and fname.endswith('.dump') and fnum > 0 and (fnum-last_fnum) == 1 and fsize > 0  and fsize !=16384:
            if len(fname) == 13 and fname.endswith('.dump') and fnum > 0 and fsize > 0  and fsize !=16384:
                fcount += 1
                # Grab the first 35 bytes (as this contains the FFID and 
                # the expanded FFID).  Decode & use the select which one to use.
                with open(dfname, 'rb') as f:
                    bdata = f.read(35)
                try:
                    ffid = decode_ffid(bdata[0:2])
                except:
                    ffid = 'ffff'
                try:
                    effid = decode_effid(bdata[32:35])
                except:
                    effid = -99
                # ffid = 'ffff'
                # effid = -99
                if ffid.lower() != 'ffff':
                    newfname = '{f:0>8}.ffid'.format(f=ffid)
                    newdfname = os.path.join(line_dir, '{f:0>8}.ffid'.format(f=ffid))
                    ftype = '   '
                elif effid != -99:
                    newfname = '{f:0>8}.ffid'.format(f=effid)
                    newdfname = os.path.join(line_dir, '{f:0>8}.ffid'.format(f=effid))
                    ftype = '(e)'
                else:
                    feedback('R{r:0>2}/F{f:0>5}:{oldf:>14}                        CANNOT DECODE FFID FROM HEADER'.format(r=rcount, f=fcount, oldf=fname, fid=ffid, efid=effid))
                    continue
                # Do not overwrite if destination file exists
                if os.path.exists(newdfname):
                    feedback('R{r:0>2}/F{f:0>5}:{oldf:>14} => {newf:<14} {ft}  FILE EXISTS - NOT COPIED'.format(r=rcount, f=fcount, oldf=fname, newf=newfname, fid=ffid, efid=effid, ft=ftype))
                    not_copied += 1
                else:
                    # Try to copy & compare checksum of source and destination files
                    try:
                        ltime = datetime.now()
                        shutil.copy2(dfname, newdfname)
                        cptime = (datetime.now() - ltime).seconds
                        ltime = datetime.now()
                        if chksum_type == 'none':
                            src_chksum = 1
                            dst_chksum = 1
                        elif chksum_type == 'md5':
                            src_chksum = hashlib.md5(open(dfname, 'rb').read()).hexdigest()
                            dst_chksum = hashlib.md5(open(newdfname, 'rb').read()).hexdigest()
                        elif chksum_type == 'sha1':
                            src_chksum = hashlib.sha1(open(dfname, 'rb').read()).hexdigest()
                            dst_chksum = hashlib.sha1(open(newdfname, 'rb').read()).hexdigest()
                        else:
                            src_chksum = hashlib.sha256(open(dfname, 'rb').read()).hexdigest()
                            dst_chksum = hashlib.sha256(open(newdfname, 'rb').read()).hexdigest()
                        cktime = (datetime.now() - ltime).seconds
                        if src_chksum == dst_chksum:
                            good_chksum += 1
                            feedback('R{r:0>2}-F{f:0>5}:{oldf:>14} => {newf:<14} {ft} COPIED ({cp:>3}s)\tCHKSUM OK ({ck:>3}s)'.format(r=rcount, f=fcount, oldf=fname, newf=newfname, fid=ffid, efid=effid, cp=cptime, ck=cktime, ft=ftype))
                        else:
                            bad_chksum += 1
                            feedback('R{r:0>2}-F{f:0>5}:{oldf:>14} => {newf:<14} {ft} COPIED\t CHKSUM ***ERROR'.format(r=rcount, f=fcount, oldf=fname, newf=newfname, fid=ffid, efid=effid, ft=ftype))
                    except:
                        not_copied += 1
                        feedback('R{r:0>2}-F{f:0>5}:{oldf:>14} => {newf:<14} {ft} ERROR DURING COPY'.format(r=rcount, f=fcount, oldf=fname, newf=newfname, fid=ffid, efid=effid, ft=ftype))
                last_fnum = fnum
            else:
                unexpected_file += 1
                feedback('           {oldf:>14} SKIPPED - UNEXPECTED FILE'.format(oldf=fname))
        feedback('-'*ncols)
        feedback('{d} COMPLETE IN\t{t:<}s'.format(d=dir, t=(datetime.now()-rtime).seconds))
        feedback('='*ncols)
# Give feedback on counters
feedback('COMPLETE:')
feedback('          -- #REELS:            {r:>5}'.format(r=rcount))
feedback('          -- #FILES:            {f:>5}'.format(f=fcount))
feedback('          -- #CHECK SUM GOOD:   {cnt:>5}'.format(cnt=good_chksum))
feedback('          -- #CHECK SUM BAD:    {cnt:>5}'.format(cnt=bad_chksum))
feedback('          -- #FILES NOT COPIED: {cnt:>5}'.format(cnt=not_copied))
feedback('          -- #UNEXPECTED FILE:  {cnt:>5}'.format(cnt=unexpected_file))
feedback('-'*ncols)
feedback('TOTAL TIME:\t\t{t:<}s'.format(t=(datetime.now()-stime).seconds))
feedback('='*ncols)

