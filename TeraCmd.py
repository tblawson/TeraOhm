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
        print(lines)
        last_line = lines[-2]
        print(last_line)
        n_samples = int(last_line.split(',')[-2])
        print('n_samples = {}'.format(n_samples))
meter.close()
dev.RM.close()
