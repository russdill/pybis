#!/usr/bin/env python

import sys
import pybis
import matplotlib.pyplot as plt

output = pybis.IBSParser().parse(sys.argv[1])

try:
    model = output.model[sys.argv[2]]

except:
    for name, model in output.model.iteritems():
        print name, model.model_type
    exit()

plt.suptitle(sys.argv[2])
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
            labels = [ None, None, None ]
        ymin, ymax = plt.ylim()
        extra = (ymax - ymin) * 0.01
        plt.ylim(ymin-extra, ymax+extra)
    plt.title(plot)
    plt.xlabel('Time (s)')
    if not n & 1:
        plt.ylabel('Volts')
        plt.legend(loc=4)
    else:
        plt.legend()
    plt.grid()

plt.show()

