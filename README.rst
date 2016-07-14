=============================
Stream analysis
=============================

This is a toy project to study the analysis of time stream data from a sensor.

The streamanalysis folder contains the source code of three modules:

- The athlete module implements a simulated athlete and creates random position and velocity data.
- The sensor module implements a sensor that streams the data from the simulated athlete.
- The analyser module implements an analysis thread that processes the data from the sensor.

The notebooks folder contains illustrations of the individual parts of streamanalysis: 

1) ``1 Athlete.ipynb`` visualises the movement of the simulated athlete.
2) ``2 Sensor.ipynb`` shows how the sensor implementation works.
3) ``3 Analyser.ipynb`` evaluates the performance of the analysis tool.
4) ``4 Analysing multiple athletes.ipynb`` shows the results when analysing the streams from 20 sensors/athletes.

To open the notebook-visualisations in the browser simply click the .ipynb files.
