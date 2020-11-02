# -*- coding: utf-8 -*-
"""
Created on Thur 4th July 2019

T.Lawson
"""


import time
import config


# total_runtime_per_ch = 205  # 210time in s


"""
Create a configuration from info stored in
init, instruments & resistor files:
"""
setup = config.Configuration('meas')  # Measurement configuration

print('All possible channel labels:\n{}'.format(setup.chan_ids))
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
trace_mode = input('Trace mode (KEEP or CLEAR)? ')
setup.meter.send_cmd(f'TRAC:MODE {trace_mode}')  # Overwrite or append to previous measurements.
setup.meter.send_cmd('TRIG:SOUR CONT')  # Continuous trigger mode.
setup.meter.send_cmd('SENS:RANG AUTO')  # Auto range mode.
setup.meter.send_cmd('SENS:POL AUTO')  # Auto-switch polarity during measurements.

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
total_runtime_per_ch = int(input('Run-time per channel (s)? '))
meas_results = {}
room_temps = []
room_RHs = []
for chan in range(setup.init['n_chans_in_use']):  # 0, 1, ...
    chan_lab = setup.chan_ids[chan]  # 'A01', 'A02', ...
    setup.scanner.send_cmd('A00')  # Prime scanner for a change of channel.
    time.sleep(0.2)
    setup.scanner.send_cmd(chan_lab)
    R_name = setup.init[str(chan)]['resistor']  # json keys are always str-type.
    print(f'Resistor: {R_name} on scanner chan {chan_lab}')
    time.sleep(1)

    """
    Set up GMH probe object for this scanner channel:
    """
    # T_role = R_name + '_' + chan_id
    T_descr = setup.init[str(chan)]['gmh_probe']
    T_port = setup.instr_data[T_descr]['addr']
    T_corrn = setup.instr_data[T_descr]['T_correction']  # ureal
    T_probe = config.dev.GMHSensor(T_descr, T_port)

    setup.meter.send_cmd('MEAS ON')
    print('\nMEAS ON____________________')

    # test_reading = setup.meter.send_cmd('READ:RES?')
    setup.meter.send_cmd('TRACe:CLEar')  # Clear previous data.

    temps = []
    t_start = time.time()
    run_time = 0
    while run_time <= total_runtime_per_ch:
        time.sleep(15)  # Below cmd needs to be given every <= 20 s to keep V_test on.
        setup.meter.send_cmd('CONF:TEST:VOLT CONT')  # Continue measurements.
        temps.append(T_probe.measure('T')[0] + T_corrn + config.T_DEF)  # Only need value, not unit-string
        room_temps.append(setup.ambient_probe.measure('T')[0] + setup.ambient_T_corrn)
        room_RHs.append(setup.ambient_probe.measure('RH')[0] + setup.ambient_RH_corrn)
        run_time = time.time() - t_start
        countdown = total_runtime_per_ch - run_time
        print('{:0.1f} s to go...'.format(countdown))
    setup.meter.send_cmd('MEAS OFF')
    print('___________________MEAS OFF')

    summary_stats_dump = setup.meter.send_cmd('TRAC:TREN:SUM?')
    # n_samples = int(summary_stats_dump.split()[-1])
    # print(n_samples)
    trace_buffer_dump = setup.meter.send_cmd('TRAC:DATA?')
    V_test_reply = setup.meter.send_cmd('SENS:OUT:VOLT?')
    print('SENS:OUT:VOLT?: {}'.format(V_test_reply))
    V_test = float(V_test_reply.split()[1])

    print('Trace buffer:\n', trace_buffer_dump)
    print('Summary stats:\n', summary_stats_dump)
    print('Last integration time (s):', setup.meter.send_cmd('SENS:INT:TIME?'))

    """
    Extract data from trace buffer:
    """
    times = []
    R_vals = []
    mystery_nums = []
    lines = trace_buffer_dump.split('\n')
    for line in lines:
        words = line.split(',')
        if len(words) < 3:
            break  # Last line is blank
        R_vals.append(float(words[0]))
        times.append(words[1])
        mystery_nums.append(words[2])

    """
    Get number of samples from summary statistics:
    """
    lines = summary_stats_dump.split('\n')
    last_line = lines[-2]  # Last line is blank, so we want 2nd-to-last.
    n_samples = int(last_line.split(',')[-2])

    meas_result = {'R_name': R_name,
                   'times': times,
                   'R_vals': R_vals,
                   'temperatures': temps,
                   'V_test': V_test}
    meas_results.update({chan_lab: meas_result})

meas_results.update({'ambient_T': room_temps, 'ambient_RH': room_RHs})

"""
Write out raw measurement data - 
Note that the number of temperature measurements
will NOT match the number of resistance measurements...
"""
setup.save_file(meas_results)

"""
... and tidy up:
"""
setup.meter.close()
setup.scanner.close()
config.dev.RM.close()
