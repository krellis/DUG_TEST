#!/usr/bin/env python

"""
Creates a PLCS standard directory structure for use with insight.

The project will be placed in /<VESSEL>/contracts/ (assuming that your host name
is made up of your vessel name and four digits,e.g. naila0153).

The project directory named will be like: 

  -- <PLCS_PROJECT_NUMBER>-<CLIENT>-<SURVEY_NAME>
  -- All spaces will be replaced with '_'
  -- All characters will be changed to lower case

Inside the insight project directory the following structure will be created:
    -- <PLCS_PROJECT_NUMBER>-PROD/
    -- <PLCS_PROJECT_NUMBER>-RTQC/
    -- survey-data/
        -- survey-data/edit/            -- survey-data/p190.nav/
        -- survey-data/segd.segd/       -- survey-data/segy/
        -- survey-data/tidal/           -- survey-data/vel/

This is intended to be ran before creating the insight project.  For the 
fast-track insight project select "<PLCS_PROJECT_NUMBER>-PROD" and convert this
to a DUG Insight project.  For the RTQC insight project select 
"<PLCS_PROJECT_NUMBER>-RTQC" and convert this to a DUG Insight project.

  However, should run on python 2.7 & 3 however, you will
need to set the correct python version in the she-bang line on *nix systems.

Usage:  {sname} [OPTION]
   
Arguments:
    None            Run script to create project directory structure.
    -h, --help      Display this help and exit.

--------------------------------------------------------------------------------
Author:   Richard Goodwin (richard.goodwin@polarcus.com)
Date:     13-APR-2015
Version:  15.04.00
--------------------------------------------------------------------------------
Written for:    python 2.6, 
Tested on:      python 2.7, 3.2, 3.3, 3.4
Current:        python {pver}
(N.B. You may need to change the she-bang on the first line to use different 
versions of python.)
"""

################################################################################
# Version History:
#   15.02.03    -- Original release
#   15.03.01    -- Updated to match new project path (14-FEB-2015)
#   15.04.00    -- Doc string set up for use as help.
#
################################################################################

import os
import sys
import socket

def clear_screen():
    """Clear the terminal window"""
    if os.name == 'posix':
        #Unix & unix like
        os.system('clear')
        root_dir = '/'
    elif os.name in ('nt', 'dos', 'ce'):
        #Microsoft, Windows, DOS, etc
        os.system('CLS')
        root_dir = get_info('Enter the drive letter to use')[0] + ':'
    else:
        #Fallback for any other operating systems
        # print('\n'*500)
        shady_rest('Only *nix & windows file systems are supported - Exiting')
    return root_dir
        
def shady_rest(msg):
    """Exit with optional message"""
    print('\n' + '='*80 )
    print(msg)
    print('='*80)
    sys.exit()

def add_dir(dname):
    """Test if a directory exists & create if it doesn't"""
    if os.path.exists(dname):
        print('{d}: already exists.'.format(d=dname))
    else:
        try:
            os.makedirs(dname)
            print('{d:<72} created'.format(d=dname))
        except:
            shady_rest('An error occured creating {d} - exiting'.format(dname))

def get_info(msg):
    """Get information from the user"""
    if sys.version[0] == '2':
        rval = raw_input('{m:<58}: '.format(m=msg))
    elif sys.version[0] == '3':
        rval = input('{m:<58}: '.format(m=msg))
    else:
        shady_rest('Cannot work out which version of python is being used - exiting')
    return rval
                
hostname = socket.gethostname()
# print(hostname,sys.version[0])
rdir = clear_screen()

if len(sys.argv) != 1:
    if len(sys.argv) == 2 and (sys.argv[1] == '-h' or sys.argv[1] == '--help'):
        shady_rest(__doc__.format(sname=os.path.basename(sys.argv[0]), pver=sys.version.split(' ')[0]))
    else:
        shady_rest('Invalid option {o}\nTry\n\t"{c} -h"\nor\n\t"{c} --help"\nfor more information.'.format(o=sys.argv[1:], c=os.path.basename(sys.argv[0])))
        

proj_num = get_info('What is the Polarcus job ID?').lower().replace(' ', '_')
client = get_info('Who is the client?').lower().replace(' ', '_')
surv_name = get_info('What is the survey name?').lower().replace(' ', '_')

proj_dir = os.path.join(rdir, '{h}'.format(h=hostname[:-4]), 'contracts', '{p}-{c}-{s}'.format(p=proj_num.strip(), c=client.strip(), s=surv_name.strip()))

print('\nThe following project will be created:')
print('\n\t{d}'.format(d=proj_dir))

carry_on = get_info('\nContinue (y/Y)?')

if carry_on.strip().lower() == 'y':
    print('\nCreating project directories:\n')
    add_dir(proj_dir)
    
    ldir = proj_dir
    ndir = os.path.join(ldir, '{pn}-RTQC'.format(pn=proj_num))
    add_dir(ndir)
    
    ndir = os.path.join(ldir, '{pn}-PROD'.format(pn=proj_num))
    add_dir(ndir)
    
    ndir = os.path.join(ldir, 'survey-data')
    add_dir(ndir)
    ldir = ndir
    ndir = os.path.join(ldir, 'segd.segd')
    add_dir(ndir)
    ndir = os.path.join(ldir, 'p190.nav')
    add_dir(ndir)
    ndir = os.path.join(ldir, 'edit')
    add_dir(ndir)
    ndir = os.path.join(ldir, 'vel')
    add_dir(ndir)
    ndir = os.path.join(ldir, 'tidal')
    add_dir(ndir)
    ndir = os.path.join(ldir, 'segy')
    add_dir(ndir)
    
    #ldir = ndir
    #ndir = os.path.join(ldir, '')
    #add_dir(ndir)
    
else:
    shady_rest('Aborted - Exiting...')

shady_rest('Complete')
