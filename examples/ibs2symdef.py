#!/usr/bin/env python
#
#  ibs2symdef.py - Generate symdef files from IBIS.
#
#  Copyright (C) 2012 Russ Dill <Russ.Dill@asu.edu>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

import sys
import pybis
import re 

ibs = pybis.IBSParser().parse(sys.argv[1])
for component_name, component in ibs.component.iteritems():

    # Sort pins into groups.
    groups = dict((s, dict()) for s in ["power", "gnd", "input", "output", "io", "nc", "other"])

    # Remember which pins are part of a differential pair.
    has_inv = dict()
    is_inv = set()

    for pin_name, pin in component.pin.iteritems():

        if pin.model_name is None:
            group = "nc"
        elif pin.model_name == "POWER":
            group = "power"
        elif pin.model_name == "GND":
            group = "gnd"
        else:
            # Find the model associated with this pin.
            model_name = pin.model_name
            if model_name not in ibs.model:
                # If there is a model selector, just pick the first one.
                model_name = ibs.model_selector[model_name].keys()[0]
            model = ibs.model[model_name]

            if "input" in model.model_type:
                group = "input"
            elif "i/o" in model.model_type:
                group = "io"
            elif "series" or "terminator" in model.model_type:
                group = "other"
            else:
                group = "output"

            # And store differential pair information.
            try:
                inv_name = component.diff_pin[pin_name].inv_pin
                has_inv[pin_name] = inv_name
                is_inv.add(inv_name)
            except:
                pass

        # signal_name's can be duplicated, so keep a list of pins with
        # that signal_name.
        groups[group].setdefault(pin.signal_name, list()).append(pin_name)

    sys.stdout = open(component_name + '.symdef', 'wb')

    # vmode makes the signal names across the top and bottom vertical.
    print "--vmode"

    print "[labels]"
    print component_name
    print "refdes=U?"
    print component.manufacturer
    print "! device=" + component_name
    print "! manufacturer=" + component.manufacturer

    # Reduce all numbers in a name down to ' ', this allows us to detect
    # busses.
    tr = lambda text: re.sub('([0-9]+)', ' ', text)

    # A modified sorted that sorts ['a15', 'a1', 'a2'] to ['a1', 'a2', 'a15'].
    def sorted_alphanum(l): 
        convert = lambda text: int(text) if text.isdigit() else text
        alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
        return sorted(l, key=alphanum_key)

    def dump_pins(group):
        bus = False

        # Sorted signal names, allows easy look-ahead, look-behind
        sorted_sigs = sorted_alphanum(group.keys())

        # Same list, but without numbers, used for bus detection
        trs = [ tr(pin) for pin in sorted_sigs ]

        for i, signal_name in enumerate(sorted_sigs):
            pins = group[signal_name]

            # If we are on a bus, but the last signal name doesn't match the
            # current signal name (ignoring numbers), end the bus.
            if bus and trs[i] != trs[i - 1]:
                bus = False
                print

            # If we aren't on a bus, check if we should be.
            if not bus:
                # If a number of pins have the same signal name (ignoring
                # negative diff pins), we consider it a bus.
                if reduce(lambda x, y: x + (y not in is_inv), pins, 0) > 1:
                    bus = True
                    print ".bus"
                # If the current signal name matches the next signal name, we
                # start a bus.
                elif i + 1 < len(trs) and trs[i] == trs[i + 1]:
                    bus = True
                    print ".bus"

            # Attempt a "heuristic" for inverted pins.
            mod = '!' if signal_name[-1] == '#' else ''

            # For all pins with this signal name except for neg side diff.
            for pin in filter(lambda x: x not in is_inv, pins):
                # If this is a pos side diff, make it a bus with its neg.
                if pin in has_inv:
                    print ".bus"
                print pin, mod, signal_name
                if pin in has_inv:
                    inv_name = has_inv[pin]
                    print inv_name, '!', component.pin[inv_name].signal_name
                    print

    print
    print "[left]"
    dump_pins(groups["input"])
    dump_pins(groups["other"])

    print
    print "[right]"
    dump_pins(groups["output"])
    dump_pins(groups["io"])

    print
    print "[top]"
    dump_pins(groups["power"])

    print
    print "[bottom]"
    dump_pins(groups["gnd"])

    print
    print "[nc]"
    dump_pins(groups["nc"])

