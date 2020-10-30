# -*- coding: utf-8 -*-

"""
config.py
Gathers together info for configuring experimental setup.
"""

import math
import datetime as dt
import time
import os
import json
import devices as dev
import GTC as gtc

# working_dir = os.path.dirname(os.path.realpath(__file__))
working_dir = input('Working directory? ')
CONFIG_FILENAME = os.path.join(working_dir, 'T-Ohm_Config.json')  # os.getcwd()
INSTR_FILENAME = os.path.join(working_dir, 'T-Ohm_Instruments.json')
RES_FILENAME = os.path.join(working_dir, 'T-Ohm_Resistors.json')
DATA_FILENAME = os.path.join(working_dir, 'T-Ohm_Measurements.json')
RESULTS_FILENAME = os.path.join(working_dir, 'T-Ohm_Results.json')
# _____________________________________________________ #


class Configuration:
    """
    Class to create a configuration object.
    This holds all info about the experimental setup
    (eg: instrument assignments, which resistors and
    which temperature probes are associated with each channel).

    Creating an instance of this class causes data to be read from
    instrument and resistor files, detailing useful operating and
    calibration parameters. This information is stored in the dictionaries:
        * self.instr_data and
        * self.res_data.

    The info in self.instr_data is used to instantiate two Instrument objects,
    representing the tera-ohmmeter and scanner.

    The info in self.res_data is used in the calculation of results.
    """
    def __init__(self, mode):
        self.chan_ids = []
        # Build list of channel labels: 'A01', 'A02', ...'A15', 'A16':
        for c in range(dev.MAX_CHANNELS):
            self.chan_ids.append(self.channel_num_to_label(c))

        #  Load default config, instrument & resistor info:
        self.init = self.load_file(CONFIG_FILENAME)  # Resistor & T-sensor assignments for each channel.
        self.instr_data = self.load_file(INSTR_FILENAME)
        if mode == 'calc':
            self.res_data = self.load_file(RES_FILENAME)

        self.check_gmh_validity()

        # Create meter and scanner instruments:
        addr_6530 = self.instr_data['G6530']['str_addr']  # "GPIB0::4::INSTR"
        addr_6564 = self.instr_data['G6564']['str_addr']  # "GPIB0::5::INSTR"
        self.meter = dev.Instrument(addr_6530, can_talk=True)
        self.scanner = dev.Instrument(addr_6564)

        # Create ambient conditions GMH sensor:
        descr = self.init['ambient_probe']  # Usually 'GMH:s/n367'
        port = self.instr_data[descr]['addr']
        self.ambient_probe = dev.GMHSensor(descr, port)  # GMH probe for room temp & RH

        # Assign reference channel label:
        self.ref_chan_id = self.chan_ids[self.init['ref_chan']]

    @staticmethod
    def channel_num_to_label(n):
        """
        Convert channel number to channel label.
        :param n: (int) channel number (0, 1,..., 15).
        :return: label (str) channel label ('A01', 'A02',...,'A16').
        """
        return 'A' + str(n + 1).zfill(2)

    @staticmethod
    def channel_label_to_num(lab):
        """
        Convert channel label to channel number.
        :param lab: (str) channel label ('A01', 'A02',...,'A16').
        :return: n (int) channel number (0, 1,..., 15).
        """
        return int(lab.lstrip('A0')) - 1

    def check_gmh_validity(self):
        """
        Check that gmh probes listed in CONFIG_FILENAME
        can be found in INSTRUMENTS_FILENAME:
        """
        for ch in range(self.init['n_chans_in_use']):
            probe = self.init[str(ch)]['gmh_probe']
            if probe in self.instr_data:
                print(f'{probe}: OK - Known instrument.')
                continue
            else:
                print(f'Unknown temperature probe {probe} specified for channel {ch}!')

    @staticmethod
    def t_mean(t_str_list):
        """
        Accept a list of times (as strings), eg:
        ['2020/06/10 14:42:59',...]
        calculate mean time and return mean time (as string).
        :param t_str_list: list of timestamps (as strings).
        :return: single timestamp (as string).
        """
        throwaway = dt.datetime.strptime('20110101', '%Y%m%d')  # known bug fix
        fmt = '%Y/%m/%d %H:%M:%S'
        n = float(len(t_str_list))
        t_av = 0.0
        for s in t_str_list:
            t_dt = dt.datetime.strptime(s, fmt)
            t_tup = dt.datetime.timetuple(t_dt)
            t_av += time.mktime(t_tup)
        t_av /= n  # av. time as float (seconds from epoch)
        t_av_fl = dt.datetime.fromtimestamp(t_av)
        return t_av_fl.strftime(fmt)  # av. time as string

    @staticmethod
    def spec(res):
        """
        Return the meter specification.
        :param res: (float) Nominal resistance (Ohms).
        :return: (float) Specified uncertainty (Ohms).
        """
        if 9e4 < res <= 2e5:
            return 4e-5*res
        elif 2e5 < res <= 2e9:
            return 8e-6*res
        elif 2e9 < res <= 2e10:
            return 1e-5*res
        elif 2e10 < res <= 2e11:
            return 1.5e-5*res
        elif 2e11 < res <= 2e12:
            return 5e-5
        elif 2e12 < res <= 2e13:
            return 1.2e-4*res
        elif 2e13 < res <= 2e14:
            return 2e-4*res
        elif 2e14 < res <= 2e15:
            return 8e-4*res
        elif 2e15 < res <= 2e16:
            return 2e-3*res
        else:
            print('Unknown meter specification!')
            return 1

    def load_file(self, filename):
        """
        Attempt to load setup info from default file.
        Returns a dictionary (empty, on failure).
        """
        try:
            with open(filename, 'r') as fp:
                json_str = self.strip_chars(fp.read(), '\t\n')
            return json.loads(json_str, object_hook=self.decode_ureal)  # A dict
        except (FileNotFoundError, IOError) as e:
            print("Can't open file {}: {}".format(filename, e))
            return {}  # An empty dict

    @staticmethod
    def strip_chars(oldstr, charlist=''):
        """
        Strip characters from oldstr and return newstr that does not
        contain any of the characters in charlist.
        Note that the built-in str.strip() only removes characters from
        the start and end (not throughout).
        """
        newstr = ''
        for ch in charlist:
            newstr = ''.join(oldstr.split(ch))
            oldstr = newstr
        return newstr

    @staticmethod
    def decode_ureal(d):
        """
        Ensures gtc.ureals are reconstructed from json source string.
        This removes the need for a dict_to_ureal() fn.
        :param d: A dictionary representing a ureal
        :return: a gtc.ureal (if '__ureal__' item is True); or the original dictionary.
        """
        if '__ureal__' in d:
            dof = d['dof']
            if d['dof'] == 'inf':
                dof = math.inf  # (>= 1e6)
            return gtc.ureal(d['value'], d['uncert'], dof, d['label'])
        return d

    @staticmethod
    def save_file(data, filename=DATA_FILENAME):
        """
        Write raw measurement data.
        """
        json_str = json.dumps(data, indent=4, cls=UrealEncoder)
        try:
            with open(filename, 'w') as fp:
                fp.write(json_str)
            return 1
        except IOError as e:
            print("Can't open file {}: {}".format(filename, e))
            return -1

    @staticmethod
    def get_res_list():
        return dev.RM.list_resources()

# _____________________________________________________ #


class UrealEncoder(json.JSONEncoder):
    """
    Over-writing default json encoder to deal with ureals.
    This removes the need for a ureal_to_dict() fn.
    """
    def default(self, obj):
        if isinstance(obj, gtc.type_a.UncertainReal):  # gtc.type_a
            return {'__ureal__': True,
                    'value': obj.x,
                    'uncert': obj.u,
                    'dof': obj.df,
                    'label': obj.label}
        else:
            return super().default(obj)
