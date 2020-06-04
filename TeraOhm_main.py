# -*- coding: utf-8 -*-
"""
Created on Thur 4th July 2019

T.Lawson
"""


import time
import config


TOTAL_RUNTIME_PER_CHAN = 205  # 210time in s


"""
Create a configuration from info stored in
config, instruments & resistor files:
"""
setup = config.Configuration()

print('All possible channels:\n{}'.format(setup.chan_ids))
print('All available visa resources:\n{}'.format(setup.get_res_list()))

"""
Ensure meter and scanner work:
"""
setup.meter.test()  # Return id-string.
time.sleep(1)
# setup.scanner.test()  # Select each channel in sequence.
time.sleep(1)

"""
Initialise meter:
"""
setup.meter.send_cmd('SYST:VERB')
setup.meter.send_cmd('MEAS:UNIT OHMS')
setup.meter.send_cmd('TRAC:MODE CLEAR')  # Overwrite previous measurements.
setup.meter.send_cmd('TRIG:SOUR CONT')  # Continuous trigger mode.
setup.meter.send_cmd('SENS:RANG AUTO')  # Auto range mode.
setup.meter.send_cmd('SENS:POL AUTO')  # Auto-switch polarity during measurements.
# setup.meter.send_cmd('TRAC:MODE KEEP')  # Append to previous measurements.

"""
Use default measurement parameters (AUTO):
OR...
set manually, using parameters in setup for this channel:
    "MEAS:TERA:COUN 300" # Total no of samples?
    "MEAS:STAB:SIZE 100" # No of samples to use for mean & stdev?
    "SENS:OUT:VOLT 10" # Test voltage
    "SENS:MAX:VOLT 10"  # Max output voltage 
    "SENS:CAP 2700"  # Integrating cap (pF)
    "SENS:INT:THR 10" # Integrator thresold (V)
    "TRIG:DEL 5" # Delay (s) between each measurement
    "TRIG:SOAK 60"  # Additional delay between reversals/applying test-V

    Can check integration time of last measurement with:
    "SENS:INT:TIME?"  # should be {0.5 < t < 60} s (default: 5.4 s)

"""
print('System date:', setup.meter.send_cmd('SYST:DATE?'))
print('System time:', setup.meter.send_cmd('SYST:TIME?'))

# set scanner to reference channel:
# setup.scanner.send_cmd('A' + setup.ref_chan_id)

"""
Loop over scanner channels:
"""
for chan in range(setup.config['n_chans']):  # 0, 1, ...
    chan_id = setup.chan_ids[chan]  # 'A01', 'A02', ...
    setup.scanner.send_cmd(chan_id)
    R_name = setup.config[str(chan)]['resistor']
    print('Resistor: {} on scanner chan {}'.format(R_name, chan_id))
    time.sleep(1)

    setup.meter.send_cmd('MEAS ON')
    print('\nMEAS ON____________________')

    test_reading = setup.meter.send_cmd('READ:RES?')

    t_start = time.time()
    run_time = 0
    while run_time <= TOTAL_RUNTIME_PER_CHAN:
        time.sleep(15)  # Below cmd needs to be given every <= 20 s.
        setup.meter.send_cmd('CONF:TEST:VOLT CONT')  # Continue measurements
        run_time = time.time() - t_start
        countdown = TOTAL_RUNTIME_PER_CHAN - run_time
        print('{:0.1f} s to go...'.format(countdown))
    setup.meter.send_cmd('MEAS OFF')
    print('___________________MEAS OFF')

    summary_stats_dump = setup.meter.send_cmd('TRAC:TREN:SUM?')
    trace_buffer_dump = setup.meter.send_cmd('TRAC:DATA?')

    print('Trace buffer:\n', trace_buffer_dump)
    print('Summary stats:\n', summary_stats_dump)
    print('Last integration time (s):', setup.meter.send_cmd('SENS:INT:TIME?'))

# print('Single reading:', setup.meter.send_cmd('READ:RES?'))
# print('Trace elements:', setup.meter.send_cmd('TRAC:ELEM?'))
# print('Summary buffer:\n', setup.meter.send_cmd('TRAC:TREN:DATA?'))
# print('TRIG:DEL?:', setup.meter.send_cmd('TRIG:DEL?'))
# print('TRIG:SOAK?:', setup.meter.send_cmd('TRIG:SOAK?'))

setup.meter.close()
setup.scanner.close()
config.dev.RM.close()
