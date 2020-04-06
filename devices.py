# -*- coding: utf-8 -*-
"""
Created on Tues 1st July 2019

T.lawson
"""

import pyvisa as visa
import time


RM = visa.ResourceManager()

"""
Build list of channel labels: '01', '02', ...'15', '16'
"""
CHANS = []
for c in range(16):
    CHANS.append(str(c+1).zfill(2))


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
    def __init__(self, str_addr, demo=True, can_talk=False):  # Default to demo mode, can't talk
        self.demo = demo
        self.is_open = False
        self.can_talk = can_talk
        self.delay = 0.2 # In seconds
        self.instr = None

        self.str_addr = str_addr  # e.g.: 'GPIB0::4::INSTR'
        self.addr = int(str_addr.strip('GPIB0::INSTR'))  # e.g.: 4

        self.open()

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
        demo_reply = 'Instrument in demo mode (addr {})'.format(self.addr)
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
            except visa.VisaIOError as err:
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
        print('Running scanner test...')
        try:
            for ch in CHANS:
                print(ch, end=' ')
                self.instr.write('A00')
                time.sleep(self.delay)
                self.instr.write('A' + ch)
                time.sleep(self.delay)
            self.instr.write('A00')
            time.sleep(self.delay)
            print('')
        except visa.VisaIOError as err:
            print(err)

    def get_id(self):
        try:
            return self.instr.query('*IDN?')
        except AttributeError as msg:  # self.instr is None so it has no query() method.
            print(msg, '- No physical instrument present.')
            return 'NONE_INSTR'
