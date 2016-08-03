# This code is based off the DUET algorithm presented in:
# O. Yilmaz and S. Rickard, "Blind separation of speech mixtures via time-frequency masking."
# S. Rickard, "The DUET Blind Source Separation Algorithm"
#
# At this time, the algorithm is not working when returning to the time domain
# and, to be honest, I haven't yet figured out why. At a later time I'll try
# and add code implementing the below algorithms
#
# A. S. Master, "Bayesian two source modeling for separation of N sources from stereo signals."
# J. Woodruff and B. Pardo, "Active source estimation for improved signal estimation"
#
# 

import numpy as np
import numpy.ma as ma
import sys
from scipy import signal

#This function could probably go somewhere else
#But is just the centralization of a function for
#calculating omega as is needed in this code
def compute_w(stft_window_length):
	w_range = [i for j in (range(1, stft_window_length/2+1), range(-stft_window_length/2 + 1, 0)) for i in j]
	w = np.array([2*np.pi*i/(stft_window_length)
		for i in w_range
		if i is not 0]) #Remove the DC component -> division by 0

	return w

#Calculate the alpha and delta terms
def estimate_parameters(left_stft, right_stft, stft_window_length):
	#List comprehensions are amazing!
	w_range = [i for j in (range(1, stft_window_length/2+1), range(-stft_window_length/2 + 1, 0)) for i in j]
	w = np.array([2*np.pi*i/(stft_window_length)
		for i in w_range
		if i is not 0])
	delay_estimation = -1/w * np.angle((right_stft + np.spacing(1))/(left_stft + np.spacing(1)))
	attenuation_estimation = np.absolute(right_stft/left_stft) - np.absolute(left_stft/right_stft)
	return attenuation_estimation, delay_estimation

#Generate weighted data
def generate_weighted_data(left_stft, right_stft, stft_window_length, p, q):
	weighted_data = np.power((np.absolute(left_stft*right_stft)),p)*np.power(compute_w(stft_window_length), q)
	return weighted_data

#Cutoff data in preparation for histogram
def filter_data(weighted_data, input_attenutation_data, input_delay_data, attentuation_threshold, delay_threshold):
	check_attenuation = lambda x: True if np.abs(x) < attentuation_threshold else False
	check_delay = lambda x: True if np.abs(x) < delay_threshold else False

	#Generate the mask array
	check_attenuation_matrix_function = np.vectorize(check_attenuation, otypes=[np.ndarray])
	check_delay_matrix_function = np.vectorize(check_delay, otypes=[np.ndarray])
	attenuation_delay_matrix = np.logical_and(check_attenuation_matrix_function(input_attenutation_data), check_delay_matrix_function(input_delay_data))
	mask = ma.masked_equal(attenuation_delay_matrix, 0) #Note - cannot just use a boolean in python as mask values are represented by 1

	#With the values masked, removed the non-mask values
	filtered_data = (ma.array(weighted_data, mask=mask.mask)).compressed()
	filtered_attenuation_data = (ma.array(input_attenutation_data, mask=mask.mask)).compressed()
	filtered_delay_data = (ma.array(input_delay_data, mask=mask.mask)).compressed()
	return filtered_data, filtered_attenuation_data, filtered_delay_data

#Use numpy to generate 2d histogram
def generate_histogram(filtered_weighted_data, filtered_attenuation_data, filtered_delay_data, number_attenuation_bins, number_delay_bins):
	H, xedges, yedges = np.histogram2d(filtered_attenuation_data, filtered_delay_data, bins=[number_attenuation_bins,number_delay_bins], weights=filtered_weighted_data)
	return H

#Smooth histogram using a 2d averager
def smooth_histogram(histogram_data, averager_size = 2):
	filter_array = np.full((averager_size, averager_size), 1.0/(averager_size*averager_size))
	return signal.convolve2d(histogram_data, filter_array, boundary='symm', mode='same')

#Straight-forward calculation of a from the symmetric attenutation
def compute_a(peak_alphas):
	return ((peak_alphas+np.sqrt(peak_alphas*peak_alphas + 4))/2)

#Given an attenutation and delay, find the mask value. Ideally, would be 0!
def compute_source_mask(x1, x2, w, a, delta):
	#As an aside, we have to use np.power instead np.square - cannot be returned otherwise
	#Why? I have no idea!
	return np.power((a*x1*np.exp(-1j*w*delta) - x2),2)/(1+a*a)

#Use the mask to find the source
def compute_source(x1, x2, w, a, delta):
	return (x1 + a*np.exp(1j*w*delta)*x2)/(1+a*a)

#Basically, find the mask that best dominates the power
#In each frame. Once found, use each of these N makes
#To separate the sources
def separate_sources(left_stft, right_stft, w, peak_as, peak_deltas, num_sources):
	smallest_source_residual = np.zeros(left_stft.shape)
	dominant_source_indices = np.zeros(left_stft.shape)

	#Find argmin of the mask
	for i in range(0, num_sources):
		if (i == 0): #For i=0 -> all of the above will be set
			smallest_source_residual = compute_source_mask(left_stft, right_stft, w, peak_as[i], peak_deltas[i])
			dominant_source_indices.fill(i)
		else:
			source_residuals = compute_source_mask(left_stft, right_stft, w, peak_as[i], peak_deltas[i])
			update_indices = np.less(source_residuals, smallest_source_residual)
			for j in range(0, update_indices.shape[0]):
				for k in range(0, update_indices.shape[1]):
					if (update_indices[j][k] == True):
						smallest_source_residual[j][k] = source_residuals[j][k]
						dominant_source_indices[j][k] = i

	#With mask ind
	estimated_source_array = []
	for i in range(0, num_sources):
		new_source_estimate = np.zeros(left_stft.shape, dtype=complex)
		for j in range(0, dominant_source_indices.shape[0]):
			for k in range(0, dominant_source_indices.shape[1]):
				if (dominant_source_indices[j][k] == i):
					new_source_estimate[j][k] = compute_source(left_stft[j][k], right_stft[j][k], w[j], peak_as[i], peak_deltas[i])
		estimated_source_array.append(new_source_estimate)

	return estimated_source_array


