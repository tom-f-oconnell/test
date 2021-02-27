#!/usr/bin/env python3.6

import atexit
import time

from serial.tools import list_ports
from alicat import FlowController


def main():
    ports = list_ports.comports()

    to_print = ['device', 'name', 'description', 'hwid', 'vid', 'pid',
        'serial_number', 'location', 'manufacturer', 'product', 'interface'
    ]
    flow_controllers = []

    def close_flow_controllers():
        print('closing flow controllers: ', end='')
        for i, f in enumerate(flow_controllers):
            print(i, end=' ', flush=True)
            f.close()
        print('done')
    atexit.register(close_flow_controllers)

    # TODO TODO is there any reason we'd want to find a solution that doesn't
    # require setting these (i.e. are these disabling something that the MFCs
    # would otherwise be trying to use)?
    #serial_kwargs = {'rtscts': True, 'dsrdtr': True}
    serial_kwargs = dict()

    # Checking against these to not accidentally write stuff to devices that
    # would react badly to that.
    startech_adapter_vid = 5296
    startech_adapter_pid = 13328

    devices = []
    could_read_from = []
    working_controllers = []
    for p in sorted(ports):
        if not (p.vid == startech_adapter_vid and
            p.pid == startech_adapter_pid):

            continue

        devices.append(p.device)

        #for f in to_print:
        #    print(f + ':', getattr(p, f))
        #print()

        print(f'opening flow controller on port {p.device}...', end='',
            flush=True
        )

        try:
            # serial_kwargs was something i added in my fork
            #c = FlowController(port=p.device, serial_kwargs=serial_kwargs)
            # NOTE: to open them this way, it seems that each device must have
            # it's software-configurable "Device ID" set to "A" (the default)
            c = FlowController(port=p.device)
        except OSError as e:
            print(e)
            print('INVALID ARGS. COULD NOT OPEN FLOW CONTROLLER!\n')
            continue

        print('done')
        flow_controllers.append(c)

        try:
            # TODO TODO how am i getting
            # {..., 'control_point': None} for COM13 device (not COM14 one)?
            # matter?
            print(c.get())
            could_read_from.append(p.device)
            working_controllers.append(c)

        except OSError as e:
            print(e)

    #print(f'{len(devices)} devices:', devices)
    print()
    print('Could read from:', could_read_from)

    # TODO TODO TODO possible to set volumetric setpoint?
    # either on the hardware or here? (docs say just mass flow / pressure, but
    # idk how to select those, and maybe loop var on hardware affects things?)
    def set_flow_rates(r):
        print(f'setting flow rates to: {r:.1f} ...', end='', flush=True)
        t0 = time.time()
        for c in working_controllers:
            c.set_flow_rate(r)
        took_s = time.time() - t0
        print(f'done ({took_s:.3fs})', flush=True)

    set_flow_rates(10.0)
    time.sleep(8)
    set_flow_rates(0.0)

    # NOTE: trying things this way led to the following error on the downstairs 2p
    # windows 7 (and on further inspection the docs seem to indicate this is
    # just if multiple MFCs are on the SAME port somehow, so i don't think that
    # applies with the usb-to-rs232 adapter i'm using)
    #$ python alicat_test.py
    #opening flow controller A...Traceback (most recent call last):
    #  File "alicat_test.py", line 98, in <module>
    #    main()
    #  File "alicat_test.py", line 84, in main
    #    c = FlowController(address=x)
    #  File "C:\Users\User\AppData\Local\Programs\Python\Python38\lib\site-packages\alicat\serial.py", line 234, in __init__
    #    FlowMeter.__init__(self, port, address)
    #  File "C:\Users\User\AppData\Local\Programs\Python\Python38\lib\site-packages\alicat\serial.py", line 40, in __init__
    #    self.connection = serial.Serial(port, 19200, timeout=1.0)
    #  File "C:\Users\User\AppData\Local\Programs\Python\Python38\lib\site-packages\serial\serialwin32.py", line 33, in __init__
    #    super(Serial, self).__init__(*args, **kwargs)
    #  File "C:\Users\User\AppData\Local\Programs\Python\Python38\lib\site-packages\serial\serialutil.py", line 244, in __init__
    #    self.open()
    #  File "C:\Users\User\AppData\Local\Programs\Python\Python38\lib\site-packages\serial\serialwin32.py", line 64, in open
    #    raise SerialException("could not open port {!r}: {!r}".format(self.portstr, ctypes.WinError()))
    #serial.serialutil.SerialException: could not open port '/dev/ttyUSB0': FileNotFoundError(2, 'The system cannot find the path specified.', None, 3)
    '''
    for x in ['A', 'B']:
        print(f'opening flow controller {x}...', end='', flush=True)
        c = FlowController(address=x)
        print('done')
        flow_controllers.append(c)

        print(c.get())
    '''


if __name__ == '__main__':
    main()

