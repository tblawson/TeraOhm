# -*- coding: utf-8 -*-
"""
Created on Tues 1st July 2019

T.lawson
"""

import pyvisa as visa
import time
import GMHstuff as GMH

RM = visa.ResourceManager()
MAX_CHANNELS = 16


class GMHSensor(GMH.GMHSensor):
    """
    A derived class of GMHstuff.GMHSensor with additional functionality.
    On creation, an instance needs:
        * A description string 'descr' eg: 'GMHs/n628',
        * A 'role' - this could be a scanner channel number,
        * A 'port' - the sensor's COM port number.
    """
    def __init__(self, descr, role, port):
        self.descr = descr
        self.role = role
        self.port = port
        # self.port = int(INSTR_DATA[self.descr]['addr'])
        super().__init__(self.port)
        self.demo = True
        self.set_power_off_time(120)  # Ensure sensor stays on during whole run.

    def test(self, meas):
        """
        Test that the device is functioning.
        :argument meas (str) - an alias for the measurement type:
            'T', 'P', 'RH', 'T_dew', 't_wb', 'H_atm' or 'H_abs'.
        :returns measurement tuple: (<value>, <unit string>)
        """
        print('\ndevices.GMH_Sensor.Test()...')
        self.open_port()
        reply = self.measure(meas)
        self.close()
        return reply

    def init(self):
        pass


class Resistor:
    """
    A combined resistor / temperature-sensor object.
    """
    def __init__(self, name, nom_val, temp_sensor):
        """
        parameters:
            name (str) - decription of resistor, eg: 'H100M 1G'.
            nom_val (int) - nominal resistance, eg: 1e9.
            temp_sensor (GMHSensor object) - an instance of class GMHSensor.
        """
        self.name = name
        self.nom_val = nom_val
        self.temp_sensor = temp_sensor


class Channel:
    """
    A configuration object that combines a scanner channel number,
    and a Resistor object.
    """
    def __init__(self, index, resistor=None):
        """
        index = channel number on 6564 scanner.
        resistor is a Resistor object, representing a resistor assigned to this channel.
        """
        self.index = index
        assert index <= MAX_CHANNELS, 'Channel index too large!'
        self.resistor = resistor


class Device(object):
    """
    A generic external device or instrument
    """
    def __init__(self, demo=True):
        self.demo = demo

    def open(self):
        pass

    def close(self):
        pass


class Instrument(Device):
    """
    A class for representing a Guildline 6530 TeraOhmmeter or 6564 Scanner
    """
    def __init__(self, str_addr, chans=MAX_CHANNELS, demo=True, can_talk=False):  # Default to demo mode, can't talk
        self.demo = demo
        self.is_open = False
        self.can_talk = can_talk
        self.delay = 0.2  # In seconds
        self.instr = None
        self.n_chans = chans

        self.str_addr = str_addr  # e.g.: 'GPIB0::4::INSTR'
        self.addr = int(str_addr.strip('GPIB0::INSTR'))  # e.g.: 4

        self.open()  # Open physical instrument on instantiation.

    def open(self):
        """
        Attempt to open a visa session.
        Return visa instrument object if successful or None if it fails.
        """
        if self.str_addr in RM.list_resources():
            try:
                self.instr = RM.open_resource(self.str_addr)
            except visa.VisaIOError as err:
                print(err)
                print('Failed to open visa session to {}.'.format(self.str_addr))
                return None
            else:
                self.is_open = True
                self.demo = False
                print('Opened session {} to {}.'.format(self.instr.session, self.str_addr))
                return self.instr
        else:
            print('No instrument found at bus address {}!'.format(self.addr))
            return None

    def close(self):
        if self.demo is True:
            print('In demo mode - nothing to close')
        elif self.instr is not None:
            print('Closing visa session {} to address {}'.format(self.instr.session, self.str_addr))
            self.instr.close()
            self.demo = True
            self.is_open = False
        else:
            print('Instrument is "None" or already closed')
        return 1

    def send_cmd(self, s):
        demo_reply = 'Demo Instrument reply (addr {})'.format(self.addr)
        default_reply = ''
        if self.demo or not self.is_open:
            return demo_reply

        if s.endswith('?'):  # A query
            if self.can_talk:
                try:
                    reply = self.instr.query(s)
                except visa.VisaIOError as err:
                    print(err)
                    reply = ''
                time.sleep(self.delay)
                return reply
            else:
                print('Instrument does not support queries!')
                return default_reply
        else:  # A command - no reply expected
            try:
                self.instr.write(s)
            except (visa.VisaIOError, AttributeError) as err:
                print(err)
            time.sleep(self.delay)
            return default_reply

    def test(self):
        """
        Run test routine determined by can_talk status:
        - If can_talk is True return response to the standard GPIB command '*IDN?'
        - If can_talk is False, assume we're dealing with the scanner and run a
        full channel scan.
        """
        if self.can_talk:
            print(self.get_id())
        else:
            self.scan_test()

    def scan_test(self):
        """
        Default test-method for model 6564 scanner.
        """
        print('Running scanner test...')
        try:
            for ch in range(MAX_CHANNELS):
                print(ch, end=' ')
                self.send_cmd('A00')
                time.sleep(self.delay)
                self.send_cmd('A' + str(ch))
                time.sleep(self.delay)
            self.send_cmd('A00')
            time.sleep(self.delay)
            print('')
        except visa.VisaIOError as err:
            print(err)

    def get_id(self):
        """
        Default test-method for model 6530 teraohmmeter.
        """
        print('Attempting to get meter ID...')
        try:
            return self.instr.query('*IDN?')
        except AttributeError as msg:  # self.instr is None so it has no query() method.
            print(msg, '- No physical instrument present.')
            return 'NONE_INSTR'
