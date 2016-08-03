# This is just a silly wrapper around matplotlib
# So I can avoid all the annoying gruntwork when creating a plot

import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.ticker import LinearLocator, FormatStrFormatter
from matplotlib import cm

def simple_line_plot(data):
	data_range = range(0, len(data))
	plt.plot(data_range, data)
	plt.show()

def simple_surface_plot(data, num_x_bins, num_y_bins, alpha_cutoff, delay_cutoff):
	fig = plt.figure()
	ax = fig.gca(projection='3d')
	X = np.arange(-alpha_cutoff, alpha_cutoff, 2*alpha_cutoff/float(num_x_bins))
	Y = np.arange(-delay_cutoff, delay_cutoff, (2*delay_cutoff)/float(num_y_bins))
	X, Y = np.meshgrid(X, Y)

	surf = ax.plot_surface(X, Y, data.reshape(X.shape), rstride=1, cstride=1)
	ax.set_xlabel(r'$\alpha$')
	ax.set_ylabel(r'$\delta$')

	plt.show()
