# -*- coding: utf-8 -*-
"""
Created on Fri 29th May 2020

T.Lawson
"""


import devices as dev


meter = dev.Instrument("GPIB0::4::INSTR", can_talk=True)

while True:
    cmd = input('>>')
    reply = meter.send_cmd(cmd)
    print(reply)
    if 'q' in cmd:
        break
    if cmd == 'TRAC:TREN:SUM?':
        lines = reply.split('\n')
        last_line = lines[-2]
        n_samples = int(last_line.split(',')[-2])
        print('n_samples = {}'.format(n_samples))
    if cmd == 'TRAC:DATA?':
        lines = reply.split('\n')
        for line in lines:
            words = line.split(',')
            print('\t{}: R={}\t?={}'.format(words[1], words[0], words[2]))

meter.close()
dev.RM.close()
