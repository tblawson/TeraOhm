# -*- coding: utf-8 -*-
"""
Created on Fri 29th May 2020

T.Lawson
"""


import devices as dev


meter = dev.Instrument("GPIB0::4::INSTR", can_talk=True)

while True:
    cmd = input('>>')
    print(meter.send_cmd(cmd))
    if 'q' in cmd:
        break
