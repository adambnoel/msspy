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

import duet as duet
import matplotlibwrapper as mplw
import numpy as np
import stft as stft
import soundfile as sf
import sounddevice as sd

#Input values are defined here
window_length= 1024 #In the DUET paper this was found to be the optimal window length for the STFT
delay_size = 512 #In the DUET paper this was chosen as the delay spacing
output_plots = True #Defines whether this will just be for use or analysis
output_sounds = True #Defines whether the separated sources are output
p = 0.5 #Both of these can be tuned depending on the MLE
q = 0 #Both of these can be tuned depending on the MLE
alpha_cutoff = 1
number_alpha_bins = 50
delta_cutoff = 4
number_delta_bins = 50
number_of_sources = 3

data, fs = sf.read('../stereomixtures/a4bb4b4.aiff') #Read in the sample music

#Get the relevant left and right channel data
l_data = data[:,0]
r_data = data[:,1]

#Get l and r stft for each dataset
l_stft_data = stft.short_time_fourier_transform(l_data, window_length, delay_size)
r_stft_data = stft.short_time_fourier_transform(r_data, window_length, delay_size)

#Remove the dc component of the data since this causes problems for when w = 0 for 1/w
l_stft_data = np.delete(l_stft_data, 0, 1)
r_stft_data = np.delete(r_stft_data, 0, 1)

#Estimate mixing parameters
symmetric_attenuation_estimation, delay_estimation = duet.estimate_parameters(l_stft_data, r_stft_data, window_length)
weighted_data = duet.generate_weighted_data(l_stft_data, r_stft_data, window_length, p, q)

filtered_weighted_data, filtered_attenutation_data, filtered_delay_data = duet.filter_data(weighted_data, symmetric_attenuation_estimation, delay_estimation, alpha_cutoff, delta_cutoff)
histogram_data = duet.generate_histogram(filtered_weighted_data, filtered_attenutation_data, filtered_delay_data, number_alpha_bins, number_delta_bins)
smoothed_histogram_data = duet.smooth_histogram(histogram_data, 4)

if (output_plots):
	mplw.simple_surface_plot(histogram_data, number_alpha_bins, number_delta_bins, alpha_cutoff, delta_cutoff)
	mplw.simple_surface_plot(smoothed_histogram_data, number_alpha_bins, number_delta_bins, alpha_cutoff, delta_cutoff)

#Ideally, we'd have an effective peak-picking algorithm here
#Alas, for now, we do not
peak_alphas = np.array([-0.478, -0.2, 0.123])
peak_deltas = np.array([-0.600, -1.18, 1.32])

stft_sources = duet.separate_sources(l_stft_data, r_stft_data, duet.compute_w(window_length), duet.compute_a(peak_alphas), peak_deltas, number_of_sources)

#Lastly, convert back to the time domain
td_sources = []
for i in range(len(stft_sources)):
	td_sources.append(stft.inverse_short_time_fourier_transform(stft_sources[i], len(l_data), window_length, delay_size))


#Finally, save the separated sources
if (output_sounds):
	for i in range(0, len(td_sources)):
		#mplw.simple_line_plot(td_sources[i])
		sf.write("Sourcenumber" + str(i) + ".aiff", td_sources[i], fs)

