import numpy as np
import theano
import theano.tensor as T
import random
import lasagne
import warnings
warnings.filterwarnings('ignore', module='lasagne')

class SwarmNet():
	def __init__(self):
		self.initialized = False

	def buildModel(self):
		self.in_layer = lasagne.layers.InputLayer(shape=(None, 2))
		self.H1_layer = lasagne.layers.DenseLayer(in_layer, 30, b=lasagne.init.Constant(1.), nonlinearity = lasagne.nonlinearities.linear)
		self.parameter_layer = lasagne.layers.DenseLayer(H1_layer, 5, b=lasagne.init.Constant(1.), nonlinearity = lasagne.nonlinearities.linear)
		self.out_layer = lasagne.layers.DenseLayer(parameter_layer, 1, nonlinearity = lasagne.nonlinearities.linear)

		param_output = lasagne.layers.get_output(self.parameter_layer)
		net_output = lasagne.layers.get_output(self.out_layer)
		# As a loss function, we'll use Theano's squared error function.
		# This should work fairly well for regression
		true_output = T.ivector('true_output')
		loss = T.mean(lasagne.objectives.squared_error(net_output, true_output))

		# Retrieving all parameters of the network is done using get_all_params,
		# which recursively collects the parameters of all layers connected to the provided layer.
		all_params = lasagne.layers.get_all_params(self.out_layer, trainable=True)
		# Now, we'll generate updates using Lasagne's SGD function
		# Finding a good learning rate is a challenge for large numbers since the squared error will explode
		# if there is a large range, it should be processed to have a smaller range
		updates = lasagne.updates.sgd(loss, all_params, learning_rate=0.001) 
		# Finally, we can compile Theano functions for training and computing the output.
		# Note that because loss depends on the input variable of our input layer,
		# we need to retrieve it and tell Theano to use it.
		self.train_function = theano.function([in_layer.input_var, true_output], loss, updates=updates)
		self.get_output = theano.function([in_layer.input_var], net_output)
		self.get_param_fun = theano.function(self.param_output)

		self.initialized = True

	def loadModel(self):
		''' load a pickled object from a file, and use it as the current network '''
		f = open(self.filename,'rb')
		tmp_dict = cPickle.load(f)
		f.close()

		self.__dict__.update(tmp_dict) 


	def saveModel(self):
		''' save a pickled object of self'''
		f = open(self.filename,'wb')
		cPickle.dump(self.__dict__,f,2)
		f.close()

	def savePoint(self):
		''' save a datapoint to a file, for offline training later '''
		pass

	def getParameters(self, input):
		''' Forward pass through the network to generate parameter values '''
		return self.get_param_fun()

	def train(self, in_data, out):
		''' Pass in a datapoint to update the network '''
		pass

