#!/usr/bin/env python3
#
#  models.py - Display waveform data from IBIS file.
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
import matplotlib.pyplot as plt

output = pybis.IBSParser().parse(sys.argv[1])

try:
    model = output.model[sys.argv[2]]

except:
    # If they didn't supply a model or the model wasn't found, print a list.
    for name, model in output.model.items():
        print(name, model.model_type)
    exit()

# Name the plot after the model
plt.suptitle(sys.argv[2])

# Try to avoid text overlap
plt.subplots_adjust(hspace=0.5)

for n, plot in enumerate([ "Pullup", "Power Clamp", "Pulldown", "GND Clamp" ]):
    plt.subplot(3, 2, n + 1)
    if plot in model:
        plt.plot(*model[plot].typ, color="green", label="typ")
        plt.plot(*model[plot].min, color="blue", label="min")
        plt.plot(*model[plot].max, color="red", label="max")
        ymin, ymax = plt.ylim()
        extra = (ymax - ymin) * 0.01
        plt.ylim(ymin-extra, ymax+extra)
    plt.title(plot)

    # A little complex logic to put legend and axis in sane places.
    if n > 1:
        plt.xlabel('Volts')
        plt.legend(loc=4)
    else:
        plt.legend()
    if not n & 1:
        plt.ylabel('Amps')
    plt.grid()

for n, plot in enumerate([ "Rising Waveform", "Falling Waveform" ]):
    plt.subplot(3, 2, n + 5)
    if plot in model:
        labels = [ "typ", "min", "max" ]
        for w in model[plot]:
            plt.plot(*w.waveform.typ, color="green", label=labels[0])
            plt.plot(*w.waveform.min, color="blue", label=labels[1])
            plt.plot(*w.waveform.max, color="red", label=labels[2])
            # Don't make duplicate labels for subsequent waveforms.
            labels = [ None, None, None ]
        ymin, ymax = plt.ylim()
        extra = (ymax - ymin) * 0.01
        plt.ylim(ymin-extra, ymax+extra)
    plt.title(plot)
    plt.xlabel('Time (s)')

    # A little complex logic to put legend and axis in sane places.
    if not n & 1:
        plt.ylabel('Volts')
        plt.legend(loc=4)
    else:
        plt.legend()
    plt.grid()

plt.show()

