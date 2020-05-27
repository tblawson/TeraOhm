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

# Ensure meter and scanner work:
setup.meter.test()  # Return id-string.
time.sleep(1)
setup.scanner.test()  # Select each channel in sequence.
time.sleep(1)

# Initialise meter
setup.meter.send_cmd('SYST:VERB')
setup.meter.send_cmd('MEAS:UNIT OHMS')
setup.meter.send_cmd('TRAC:MODE CLEAR')  # Clear old measurements.
setup.meter.send_cmd('TRAC:MODE KEEP')  # Keep new measurements.
setup.meter.send_cmd('TRIG:SOUR CONT')  # Continuous trigger mode.
setup.meter.send_cmd('SENS:RANG AUTO')  # Auto range mode.
setup.meter.send_cmd('SENS:POL AUTO')  # Auto-switch polarity during measurements.

# Loop over channels in config file:
for chan in range(setup['n_chans']):  # 0, 1, ...
    chan_id = setup.chan_ids[chan]  # 'A01', 'A02', ...
    setup.scanner.send_cmd(chan_id)

"""
Use default measurement parameters (AUTO):

OR set manually, using parameters in setup for this channel:
    "MEAS:TERA:COUN 300" # Total no of samples
    "MEAS:STAB:SIZE 100" # No of samples to use for mean & stdev
    "SENS:OUT:VOLT 10" # Test voltage
    "SENS:MAX:VOLT 10"  # Max output voltage 
    "SENS:CAP 2700"  # Integrating cap (pF)
    "SENS:INT 10" # Integrator thresold (V)
    "TRIG:DEL 5" # Delay (s) between each measurement
    "TRIG:SOAK 60"  # Additional delay between reversals/applying test-V

    Can check integration time of last measurement with:
    "SENS:INT:TIME?"  # should be {0.5 < t < 60} s (default: 5.4 s)

"""




# set scanner to reference channel:
# setup.scanner.send_cmd('A' + setup.ref_chan_id)

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
