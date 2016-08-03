#This code uses the University of Iowa Electronic Music Database music
#To generate samples for testing the DUET algorithm
#
#To gain access please see to the music : 
#http://theremin.music.uiowa.edu/MIS.html
#
#If you wish to use this code
#Hopefully the relative paths are clear
#

import matplotlibwrapper as mplw
import numpy as np
import sounddevice as sd
import soundfile as sf

constant_instrument = 'cello'
constant_instrument_note = 'a4'
slow_changing_instrument = 'violin'
slow_changing_instrument_notes = ['a4','ab4','b4','bb4','c4','d4','db4','e4', 'eb4', 'f4','g4','gb4','a5']
fast_changing_instrument = 'viola'
fast_changing_instrument_notes = ['a4','ab4','b4','bb4','c4','d4','db4','e4', 'eb4', 'f4','g4','gb4','a5']
instrument_directory = '../stereosamplemusic/'
fs = 44100
play_samples = False
output_samples = True

def combine_samples(list_of_sample_paths):
	sampleArrays = []
	for i in range(0, len(list_of_sample_paths)):
		data, fs = sf.read(list_of_sample_paths[i])
		mplw.simple_line_plot(data)
		sampleArrays.append(data)

	maxSampleLength = 0
	for i in range(0, len(sampleArrays)):
		if (len(sampleArrays[i]) > maxSampleLength):
			maxSampleLength = len(sampleArrays[i])

	##Now combine the samples
	newArray = []
	for i in range(0, maxSampleLength):
		newSampleValue = [0, 0]
		for j in range(0, len(sampleArrays)):
			if (not(i >= len(sampleArrays[j]))):
				newSampleValue[0] += sampleArrays[j][i][0]
				newSampleValue[1] += sampleArrays[j][i][1]

		newArray.append(newSampleValue)

	return newArray

constant_instrument_path = instrument_directory + constant_instrument + '/' + constant_instrument + '.' + constant_instrument_note + '.aif'
for i in slow_changing_instrument_notes:
	current_slow_path = instrument_directory + slow_changing_instrument + '/' + slow_changing_instrument + '.' + i + '.aif'
	for j in fast_changing_instrument_notes:
		current_fast_path = instrument_directory + fast_changing_instrument + '/' + fast_changing_instrument + '.' + j + '.aif'
		sample_paths = [constant_instrument_path, current_slow_path, current_fast_path]
		data = combine_samples(sample_paths)
		if (play_samples):
			sd.play(data, fs, blocking=True)
		if (output_samples):
			output_mixture = constant_instrument_note + i + j + '.aiff'
			sf.write(output_mixture, data, fs)
		


