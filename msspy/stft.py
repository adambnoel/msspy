# This code is informed from the discussion on:
# http://dsp.stackexchange.com/questions/2757/inverse-short-time-fourier-transform-algorithm-described-in-words
#
# Author: Adam Noel
#

import scipy as sp

#Take the short-time fourier transform
#The sample_per_frame is the length of your FFT
#The
def short_time_fourier_transform(input_data, samples_per_frame, time_window_delay, window_function = None):
	if window_function is None: 
		window_function = sp.hamming
	w = window_function(samples_per_frame)
	output_data = sp.array([sp.fft(w*input_data[i:i+samples_per_frame])
		for i in range(0, len(input_data)- samples_per_frame, time_window_delay)])
	return output_data

def inverse_short_time_fourier_transform(input_data, signal_length, samples_per_frame, time_window_delay, window_function = None):
	if window_function is None:
		window_function = sp.hamming

	w = window_function(samples_per_frame)
	output_data = sp.zeros(signal_length)
	for i in range(0, input_data.shape[0]):
		output_data[i*time_window_delay:(i*time_window_delay+(samples_per_frame-1))] += sp.real(sp.ifft(input_data[i]))*w[1:samples_per_frame]

	return output_data