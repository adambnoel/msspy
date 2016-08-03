#Some code to try and evaluate the separated signals 
#and compare them to the original
#
#This code is in bad shape, and needs to be cleaned up

import numpy as np
import sounddevice as sd
import soundfile as sf

def calc_error(sig1, sig2):
	return np.abs(20*np.log10((np.inner(sig1, sig2)/np.abs(np.inner(sig1, sig1)))))

#Need to pad zeros to make the signals line up
#This may be really undesirable
#But is a product of the way music is generated
#In three_instrument_mixture.py
def padZeros(signal, targetLength):
	if (len(signal) < targetLength):
		new_zeros = np.zeros((targetLength - len(signal)))
		return np.append(signal, new_zeros)
	else:
		return signal


instrument_directory = '../stereosamplemusic'
cello_note_file = '/cello/cello.a4.aif'
violin_note_file = '/violin/violin.a4.aif'
viola_note_file = '/viola/viola.a4.aif'

max_signal_length = 0
cello_data, fs = sf.read(instrument_directory + cello_note_file)
cello_data = cello_data[:,0] + cello_data[:,1]
max_signal_length = np.max([len(cello_data), max_signal_length])
violin_data, fs = sf.read(instrument_directory + violin_note_file)
violin_data = violin_data[:,0] + violin_data[:,1]
max_signal_length = np.max([len(violin_data), max_signal_length])
viola_data, fs = sf.read(instrument_directory + viola_note_file)
viola_data = viola_data[:, 0] + viola_data[:, 1]
max_signal_length = np.max([len(viola_data), max_signal_length])

mixture_directory = '../signalseparation/a4a4a4/'
cello_mixture_file = 'Sourcenumber0.aiff'
violin_mixture_file = 'Sourcenumber1.aiff'
viola_mixture_file = 'Sourcenumber2.aiff'

s_cello_data, fs = sf.read(mixture_directory + cello_mixture_file)
max_signal_length = np.max([len(s_cello_data), max_signal_length])
s_violin_data, fs = sf.read(mixture_directory + violin_mixture_file)
max_signal_length = np.max([len(s_violin_data), max_signal_length])
s_viola_data, fs = sf.read(mixture_directory + viola_mixture_file)
max_signal_length = np.max([len(s_viola_data), max_signal_length])

cello_data = padZeros(cello_data, max_signal_length)
violin_data = padZeros(violin_data, max_signal_length)
viola_data = padZeros(viola_data, max_signal_length)
s_cello_data = padZeros(s_cello_data, max_signal_length)
s_violin_data = padZeros(s_violin_data, max_signal_length)
s_viola_data = padZeros(s_viola_data, max_signal_length)


print(calc_error(cello_data, s_cello_data))
print(calc_error(violin_data, s_violin_data))
print(calc_error(violin_data, s_viola_data))