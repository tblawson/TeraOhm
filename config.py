# -*- coding: utf-8 -*-

"""
config.py
Gathers together info for configuring experimental setup.
"""
import os
import json
import devices as dev

# working_dir = os.path.dirname(os.path.realpath(__file__))
working_dir = input('Working directory? ')
CONFIG_FILENAME = os.path.join(working_dir, 'T-Ohm_Config.json')  # os.getcwd()
INSTR_FILENAME = os.path.join(working_dir, 'T-Ohm_Instruments.json')
RES_FILENAME = os.path.join(working_dir, 'T-Ohm_Resistors.json')
OUT_FILENAME = os.path.join(working_dir, 'T-Ohm_Measurements.json')


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
    """
    def __init__(self):
        self.chan_ids = []
        # Build list of channel labels: 'A01', 'A02', ...'A15', 'A16':
        for c in range(dev.MAX_CHANNELS):
            self.chan_ids.append('A' + str(c + 1).zfill(2))

        #  Load default config, instrument & resistor info:
        self.config = self.load_file(CONFIG_FILENAME)  # Resistor & T-sensor assignments for each channel.
        self.instr_data = self.load_file(INSTR_FILENAME)
        self.res_data = self.load_file(RES_FILENAME)

        """
        Check that gmh probes listed in CONFIG_FILENAME
        can be found in CONFIG_FILENAME:
        """
        self.check_gmh_validity()

        # Create meter and scanner instruments:
        addr_6530 = self.instr_data['G6530']['str_addr']  # "GPIB0::4::INSTR"
        addr_6564 = self.instr_data['G6564']['str_addr']  # "GPIB0::5::INSTR"
        self.meter = dev.Instrument(addr_6530, can_talk=True)
        self.scanner = dev.Instrument(addr_6564)

        # Assign reference channel label:
        self.ref_chan_id = self.chan_ids[self.init['ref_chan']]

    def check_gmh_validity(self):
        for ch in range(self.init['n_chans']):
            probe = self.init[str(ch)]['gmh_probe']
            if probe in self.instr_data:
                print('{}: OK.'.format(probe))
                continue
            else:
                print('Unknown temperature probe {} specified for channel {}!'.format(probe, ch))

    def load_file(self, filename):
        """
        Attempt to load setup info from default file.
        Returns a dictionary (empty, on failure).
        """
        try:
            with open(filename, 'r') as fp:
                json_str = self.strip_chars(fp.read(), '\t\n')
            return json.loads(json_str)  # A dict
        except (FileNotFoundError, IOError) as e:
            print("Can't open file {}: {}".format(filename, e))
            return {}  # An empty dict

    @staticmethod
    def save_data(data, filename=OUT_FILENAME):
        """
        Write raw measurement data.
        """
        json_str = json.dumps(data, indent=4)
        try:
            with open(filename, 'w') as fp:
                fp.write(json_str)
            return 1
        except IOError as e:
            print("Can't open file {}: {}".format(filename, e))
            return -1

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
    def get_res_list():
        return dev.RM.list_resources()

    # def refresh_params(directory):
    #     """
    #     Refreshes state-of-knowledge of resistors and instruments.
    #     Returns:
    #     RES_DATA: Dictionary of known resistance standards.
    #     INSTR_DATA: Dictionary of instrument parameter dictionaries,
    #     both keyed by description.
    #     """
    #     with open(os.path.join(directory, resistor_file), 'r') as new_resistor_fp:
    #         resistor_str = strip_chars(new_resistor_fp.read(), '\t\n')  # Remove tabs & newlines
    #     res_data = json.loads(resistor_str)
    #
    #     with open(os.path.join(directory, instrument_file), 'r') as new_instr_fp:
    #         instr_str = strip_chars(new_instr_fp.read(), '\t\n')
    #     instr_data = json.loads(instr_str)
    #
    #     return res_data, instr_data


# class Channel:
#     def __init__(self, chan_no, t_sensor, res):
#         """
#         param chan_no (int): Scanner channel
#         param t_sensor (GMHSensor): A GMHSensor object.
#         param res (str): A description string of resistor.
#         """
#         self.chan_no = chan_no
#         self.temp_sensor = t_sensor
#         self.resistor = res
