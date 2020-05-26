# -*- coding: utf-8 -*-
"""
Created on Thur 4th July 2019

T.Lawson
"""


import time
import config


SAMPLE_TIME = 10  # 210time in s

"""
Create a configuration from info stored in config, instruments & resistor files:
"""
setup = config.Configuration()

print('All possible channels:\n{}'.format(setup.chan_ids))
print('All available visa resources:\n{}'.format(setup.get_res_list()))

setup.meter.test()
time.sleep(1)
setup.scanner.test()
time.sleep(1)

setup.meter.send_cmd('SYST:VERB')
setup.meter.send_cmd('MEAS:UNITS OHMS')

# set scanner to reference channel:
setup.scanner.send_cmd('A' + setup.ref_chan_id)

print('Trace mode:', setup.meter.send_cmd('TRAC:MODE?'))
print('Calibration threshold V:', setup.meter.send_cmd('CAL:THR:VOLT?'))

print('Integrator threshold:', setup.meter.send_cmd('SENS:INT:THRESH?'))
print('Output V:', setup.meter.send_cmd('SENS:OUT:VOLT?'))
print('Polarity mode:', setup.meter.send_cmd('SENS:POL?'))
print('Range mode:', setup.meter.send_cmd('SENS:RANG?'))

setup.meter.send_cmd('MEAS ON')
print('\nMEAS ON____________________')

t_start = time.time()
run_time = 0

while run_time <= SAMPLE_TIME:
    setup.meter.send_cmd('CONF:TEST:VOLT CONT')  # Continue measurements
    time.sleep(15)  # Above cmd needs to be given at least every 20 s.
    run_time = time.time() - t_start
    countdown = SAMPLE_TIME - run_time
    print('{:0.1f} s to go...'.format(countdown))
    print('Output V:', setup.meter.send_cmd('SENS:OUT:VOLT?'))

setup.meter.send_cmd('MEAS OFF')
print(setup.meter.send_cmd('MEAS?'))
print('___________________MEAS OFF')
print('Single reading:\n', setup.meter.send_cmd('READ:RES?'))
print('Trace buffer:\n', setup.meter.send_cmd('TRAC:DATA?'))
print('Summary buffer:\n', setup.meter.send_cmd('TRAC:TREN:DATA?'))
print('Summary stats:\n', setup.meter.send_cmd('TRAC:TREN:SUM?'))

setup.meter.close()
setup.scanner.close()
config.dev.RM.close()
