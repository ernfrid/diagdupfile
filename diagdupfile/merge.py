#!/usr/bin/python

import DupFile
import DupFilePlotter

import sys

if __name__ == "__main__":
    files = list()
    for file in sys.argv[1:]:
        files.append(DupFile.DupFile(file))

    final = files[0]
    final.merge(files[1:])
    
    plotter = DupFilePlotter.DupFilePlotter()
    plotter.plot(final, 'TestPlot.png')


