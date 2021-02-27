#!/usr/bin/env python3.6

import atexit

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

    #'''
    for p in sorted(ports):
        for f in to_print:
            print(f + ':', getattr(p, f))
        print()

        print(f'opening flow controller on port {p.device}...', end='',
            flush=True
        )

        try:
            c = FlowController(port=p.device, serial_kwargs=serial_kwargs)
        except OSError:
            print('INVALID ARGS. COULD NOT OPEN FLOW CONTROLLER!\n')
            continue

        print('done')
        flow_controllers.append(c)

        try:
            print(c.get())
        except OSError:
            print('COULD NOT READ FROM THIS PORT!\n')
    #'''

    '''
    for x in ['A', 'B']:
        print(f'opening flow controller {x}...', end='', flush=True)
        c = FlowController(address=x, serial_kwargs=serial_kwargs)
        print('done')
        flow_controllers.append(c)

        print(c.get())
    '''

    import ipdb; ipdb.set_trace()


if __name__ == '__main__':
    main()

