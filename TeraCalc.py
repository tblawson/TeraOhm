# -*- coding: utf-8 -*-
"""
Created on Thur 19th June 2020

T.Lawson

Analyse raw data captured during run of TeraOhm_main.py
"""

import config
import GTC

calc_setup = config.Configuration('calc')  # Analysis configuration


"""
Import the raw measurements file to a dict:
"""
meas_data = calc_setup.load_file('T-Ohm_Measurements.json')

"""
Gather reference resistor info:
"""
ref_chan = calc_setup.init['ref_chan']  # NOTE: This info needed for both sections
ref_chan_label = calc_setup.channel_num_to_label(ref_chan)

Rs_name = meas_data[ref_chan_label]['R_name']
Rs_Vtest = meas_data[ref_chan_label]['V_test']

Rs_meas = {'chan_no': ref_chan,
           'reference': True,
           'name': Rs_name,
           'value': GTC.ta.estimate(meas_data[ref_chan_label]['R_vals']),  # ureal
           'Temp': GTC.ta.estimate(meas_data[ref_chan_label]['temperatures']),  # ureal
           'V_test': Rs_Vtest,
           'time': calc_setup.t_mean(meas_data[ref_chan_label]['times'])
           }

# Choose reference value of Rs based on nearest test-voltage:
V0_LV = calc_setup.res_data[Rs_name]['VRef_LV']  # calc_setup.dict_to_ureal(calc_setup.res_data[Rs_name]['VRef_LV'])
print('V0_LV:',V0_LV)
V0_HV = calc_setup.res_data[Rs_name]['VRef_HV']  # calc_setup.dict_to_ureal(calc_setup.res_data[Rs_name]['VRef_HV'])
if abs(V0_LV - Rs_Vtest) >= abs(V0_HV - Rs_Vtest):
    V_suffix = '_HV'
else:
    V_suffix = '_LV'
Rs_0 = calc_setup.res_data[Rs_name]['R0' + V_suffix]  # calc_setup.dict_to_ureal(calc_setup.res_data[Rs_name]['R0' + V_suffix])
Rs_T0 = calc_setup.res_data[Rs_name]['TRef' + V_suffix]  # calc_setup.dict_to_ureal(calc_setup.res_data[Rs_name]['TRef' + V_suffix])
Rs_V0 = calc_setup.res_data[Rs_name]['VRef' + V_suffix]  # calc_setup.dict_to_ureal(calc_setup.res_data[Rs_name]['VRef' + V_suffix])


# Calculate corrected true value of Rs:
Rs_alpha = calc_setup.res_data[Rs_name]['alpha']  # calc_setup.dict_to_ureal(calc_setup.res_data[Rs_name]['alpha'])
Rs_beta = calc_setup.res_data[Rs_name]['beta']  # calc_setup.dict_to_ureal(calc_setup.res_data[Rs_name]['beta'])
Rs_gamma = calc_setup.res_data[Rs_name]['gamma']  # calc_setup.dict_to_ureal(calc_setup.res_data[Rs_name]['gamma'])
Rs_dT = Rs_meas['Temp'] - Rs_T0
Rs_dV = Rs_meas['V_test'] - Rs_V0
Rs = Rs_0*(1 + Rs_alpha*Rs_dT + Rs_beta*Rs_dT*Rs_dT + Rs_gamma*Rs_dV)

"""
Calculate values of all non-reference resistors:
"""

analysed_results = {ref_chan_label: Rs_meas}

for chan_label in meas_data.keys():  # 'A01', 'A02'...
    chan = calc_setup.channel_label_to_num(chan_label)
    if chan == ref_chan:
        continue

    Rx_meas = {'chan_no': chan,
               'name': meas_data[chan_label]['R_name'],
               'value': GTC.ta.estimate(meas_data[chan_label]['R_vals']),
               'Temp': GTC.ta.estimate(meas_data[chan_label]['temperatures']),
               'V_test': meas_data[chan_label]['V_test'],
               'time': calc_setup.t_mean(meas_data[chan_label]['times'])}

    Rx_calc = Rx_meas
    Rx_spec = GTC.ureal(0, calc_setup.spec(Rx_meas['value'].x))
    Rs_spec = GTC.ureal(0, calc_setup.spec(Rs_meas['value'].x))
    spec = max(Rx_spec.u, Rs_spec.u)

    Rx_calc['value'] = Rs*Rx_meas['value']/Rs_meas['value'] + spec  # calc_setup.ureal_to_dict(Rs*Rx_meas['value']/Rs_meas['value'] + spec)

    analysed_results.update({chan_label: Rx_calc})
    calc_setup.save_file(analysed_results, filename=config.RESULTS_FILENAME)
