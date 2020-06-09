# -*- coding: utf-8 -*-
"""
Created on Fri 29th May 2020

T.Lawson
"""

import time
import devices as dev


meter = dev.Instrument("GPIB0::4::INSTR", can_talk=True)

while True:
    cmd = input('>> ')
    if 'q' in cmd:
        break
    reply = meter.send_cmd(cmd)
    print(reply)
    if cmd == 'TRAC:TREN:SUM?':
        lines = reply.split('\n')
        last_line = lines[-2]
        n_samples = int(last_line.split(',')[-2])
        print('n_samples = {}'.format(n_samples))
    if cmd == 'TRAC:DATA?':
        lines = reply.split('\n')
        for line in lines:
            words = line.split(',')
            if len(words) == 3:
                print('{}: R={}\t?={}'.format(words[1], words[0], words[2]))
            elif len(words) == 2:
                print('{}: R={}'.format(words[1], words[0]))
            elif len(words) == 1:
                print('R={}'.format(words[0]))
            else:
                print('_____End of buffer____')

    time.sleep(1)
    meter.send_cmd('CONF:TEST:VOLT CONT')
    print(meter.send_cmd('MEAS?'))

meter.close()
dev.RM.close()
