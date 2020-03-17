# -*- coding: utf-8 -*-
"""
Created on Thur 4th July 2019

T.Lawson
"""

import time
import devices as dev

SAMPLE_TIME = 210  # time in s
print(dev.RM.list_resources())

G6530 = dev.Instrument("GPIB0::4::INSTR", can_talk=True)

G6564 = dev.Instrument("GPIB0::5::INSTR")

G6530.test()
time.sleep(1)
# G6564.test()
time.sleep(1)

G6530.send_cmd('SYST:VERB')
G6530.send_cmd('MEAS:UNITS OHMS')
G6564.send_cmd('A01')

print('Trace mode:', G6530.send_cmd('TRAC:MODE?'))
print('Calibration threshold V:', G6530.send_cmd('CAL:THR:VOLT?'))

print('Integrator threshold:', G6530.send_cmd('SENS:INT:THRESH?'))
print('Output V:', G6530.send_cmd('SENS:OUT:VOLT?'))
print('Polarity mode:', G6530.send_cmd('SENS:POL?'))
print('Range mode:', G6530.send_cmd('SENS:RANG?'))

G6530.send_cmd('MEAS ON')
print('\nMEAS ON____________________')

t_start = time.time()
run_time = 0

while run_time <= SAMPLE_TIME:
    G6530.send_cmd('CONF:TEST:VOLT CONT')  # Continue measurements
    time.sleep(15)
    run_time = time.time() - t_start
    countdown = SAMPLE_TIME - run_time
    print('{:0.1f} s to go...'.format(countdown))
    print('Output V:', G6530.send_cmd('SENS:OUT:VOLT?'))

G6530.send_cmd('MEAS OFF')
print(G6530.send_cmd('MEAS?'))
print('___________________MEAS OFF')
print('Single reading:\n', G6530.send_cmd('READ:RES?'))
print('Trace buffer:\n', G6530.send_cmd('TRAC:DATA?'))
print('Summary buffer:\n', G6530.send_cmd('TRAC:TREN:DATA?'))
print('Summary stats:\n', G6530.send_cmd('TRAC:TREN:SUM?'))

G6530.close()
G6564.close()
dev.RM.close()
