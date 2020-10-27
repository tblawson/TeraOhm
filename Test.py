# -*- coding: utf-8 -*-
"""
Created on Mon 24th June 2019

t.lawson
"""

import time
import sys
import visa

DELAY = 0.2

CHANS = []
# Build channel list: '01', '02', ...'15', '16'
for c in range(16):
    CHANS.append(str(c+1).zfill(2))

RM = visa.ResourceManager()
print(RM.list_resources())

scanner_addr = input('Scanner address? >>')
if scanner_addr == 'q':
    RM.close()
    sys.exit()


def create_instr(addr):
    try:
        instr = RM.open_resource(addr)
    except visa.VisaIOError as err:
        print(err)
        print('STOPPING at Create_Instr({})...'.format(addr))
        sys.exit()
    print('Opened session', instr.session, 'to', addr, '\n')
    return instr


meter = create_instr('GPIB0::04::INSTR')  # 'GPIB0::04::INSTR'
scanner = create_instr(scanner_addr)  # 'GPIB0::07::INSTR'
instr_list = {'m': meter, 's': scanner}


def scantest():
    print('Running scan test...')
    try:
        for ch in CHANS:
            print(ch, end = ' ')
            instr_list['s'].write('A00')
            time.sleep(DELAY)
            instr_list['s'].write('A'+ch)
            time.sleep(DELAY)
        instr_list['s'].write('A00')
        time.sleep(DELAY)
        print('')
    except visa.VisaIOError as err:
        print(err)


scantest()


def end_session():
    for i in instr_list.values():
        if i is not None:
            i.close()
    RM.close()
    sys.exit()


def process(cmd):
    [i, msg] = cmd.split('_')
    try:
        if '?' in msg:
            rtn = instr_list[i].query(msg)  # Write cmd to instrument i, then read from i.
        else:
            instr_list[i].write(msg)  # Write msg to instrument i.
            rtn = 'Write {} (No reply)'.format(msg)
        time.sleep(DELAY)
        print(rtn)
    except visa.VisaIOError as err:
        print(err)
        print('STOPPING...')
        end_session()


# Main program loop follows...
# ----------------------------
print('Enter "m" (meter) or "s" (scanner), followed by "_" then command '
      'or "q" to quit.\n')

while True:
    cmd = input('>> ')
    if cmd == 'q':
        break
    elif cmd == 'scantest':
        scantest()
        continue
    elif '_' not in cmd:
        print('Invalid command!')
        continue
    else:
        process(cmd)

end_session()

