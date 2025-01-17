import pickle
import numpy as np
from scipy.optimize import minimize
from scipy.io import loadmat
from math import sqrt
import re


def initializeWeights(n_in,n_out):
    """
    # initializeWeights return the random weights for Neural Network given the
    # number of node in the input layer and output layer

    # Input:
    # n_in: number of nodes of the input layer
    # n_out: number of nodes of the output layer

    # Output:
    # W: matrix of random initial weights with size (n_out x (n_in + 1))"""

    epsilon = sqrt(6) / sqrt(n_in + n_out + 1);
    W = (np.random.rand(n_out, n_in + 1)*2* epsilon) - epsilon;
    return W

def sigmoid(z):

    """# Notice that z can be a scalar, a vector or a matrix
    # return the sigmoid of input z"""

    return 1 / (1 + np.exp(-z))

def preprocess():
    """ Input:
     Although this function doesn't have any input, you are required to load
     the MNIST data set from file 'mnist_all.mat'.

     Output:
     train_data: matrix of training set. Each row of train_data contains
       feature vector of a image
     train_label: vector of label corresponding to each image in the training
       set
     validation_data: matrix of training set. Each row of validation_data
       contains feature vector of a image
     validation_label: vector of label corresponding to each image in the
       training set
     test_data: matrix of training set. Each row of test_data contains
       feature vector of a image
     test_label: vector of label corresponding to each image in the testing
       set

     Some suggestions for preprocessing step:
     - divide the original data set to training, validation and testing set
           with corresponding labels
     - convert original data set from integer to double by using double()
           function
     - normalize the data to [0, 1]
     - feature selection"""

    mat = loadmat('mnist_all.mat') #loads the MAT object as a Dictionary

    train_data_temp = np.array([[0]*784])
    train_label_temp = np.array([])
    train_data = np.array([[0]*784])
    train_label = np.array([])
    validation_data = np.array([])
    validation_label = np.array([])
    test_data = np.array([[0]*784])
    test_label = np.array([])

    for key in mat:
        digData = re.findall(r'\d+', key)

        if len(digData) == 0:
                continue

        val = int(digData[0])

        value = mat.get(key)
        if key[:5] == 'train':
                train_label_temp = np.append(train_label_temp, [val]*len(mat.get(key)), axis=1)
                train_data_temp = np.vstack((train_data_temp, value/255.0))
        else:
                test_label = np.append(test_label, [val]*len(mat.get(key)), axis=1)
                test_data = np.vstack((test_data, value/255.0))

    #remove the extra entry added during array initialization
    train_data_temp = np.delete(train_data_temp, 0, axis=0)
    test_data = np.delete(test_data, 0, axis=0)
    
    # now split train_data and train_label
    indices = np.random.permutation(60000)
    training_idx, validation_idx = indices[:50000], indices[50000:]

    train_data, train_label = np.array([train_data_temp[i] for i in training_idx]), np.array([train_label_temp[j] for j in training_idx])
    validation_data, validation_label = np.array([train_data_temp[i] for i in validation_idx]), np.array([train_label_temp[j] for j in validation_idx])
    return train_data, train_label, validation_data, validation_label, test_data, test_label


def nnObjFunction(params, *args):
    """% nnObjFunction computes the value of objective function (negative log
    %   likelihood error function with regularization) given the parameters
    %   of Neural Networks, the training data, their corresponding training
    %   labels and lambda - regularization hyper-parameter.

    % Input:
    % params: vector of weights of 2 matrices w1 (weights of connections from
    %     input layer to hidden layer) and w2 (weights of connections from
    %     hidden layer to output layer) where all of the weights are contained
    %     in a single vector.
    % n_input: number of node in input layer (not include the bias node)
    % n_hidden: number of node in hidden layer (not include the bias node)
    % n_class: number of node in output layer (number of classes in
    %     classification problem
    % training_data: matrix of training data. Each row of this matrix
    %     represents the feature vector of a particular image
    % training_label: the vector of truth label of training images. Each entry
    %     in the vector represents the truth label of its corresponding image.
    % lambda: regularization hyper-parameter. This value is used for fixing the
    %     overfitting problem.

    % Output:
    % obj_val: a scalar value representing value of error function
    % obj_grad: a SINGLE vector of gradient value of error function
    % NOTE: how to compute obj_grad
    % Use backpropagation algorithm to compute the gradient of error function
    % for each weights in weight matrices.

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    % reshape 'params' vector into 2 matrices of weight w1 and w2
    % w1: matrix of weights of connections from input layer to hidden layers.
    %     w1(i, j) represents the weight of connection from unit j in input
    %     layer to unit i in hidden layer.
    % w2: matrix of weights of connections from hidden layer to output layers.
    %     w2(i, j) represents the weight of connection from unit j in hidden
    %     layer to unit i in output layer."""

    n_input, n_hidden, n_class, training_data, training_label, lambdaval = args

    w1 = params[0:n_hidden * (n_input + 1)].reshape( (n_hidden, (n_input + 1)))
    w2 = params[(n_hidden * (n_input + 1)):].reshape((n_class, (n_hidden + 1)))
    obj_val = 0
    dell_L = np.array([])

    grad_w2 = np.array([[0.0]*(n_hidden+1)]*(n_class))
    grad_w1 = np.array([[0.0]*(n_input+1)]*(n_hidden))

    index_columns = [i for i in range(len(w2.T)-1)]
    w2_temp = w2[:, index_columns]

    for i in range(len(training_data)):
        value = training_data[i]
        value = np.append(value, 1)
        a1 = value.dot(w1.T)
        z1 = sigmoid(a1)
        z1_bias = np.append(z1, 1)

        a2 = z1_bias.dot(w2.T)
        z2 = sigmoid(a2)

        y = np.array([0]*n_class)
        label = training_label[i]
        y[int(label)] = 1

        error = (y-z2)**2
        obj_val += np.sum(error);

        #output to hidden
        dell_L = (y-z2)*(1-z2)*(z2)
        grad_w2_temp = np.array([])
        grad_w2_temp = -1*dell_L[:,None]*z1_bias
        grad_w2 += grad_w2_temp 

        #hidden to input
        part1 = (1-z1)*(z1) 
        part2 = -1*dell_L.dot(w2_temp)
        part3 = part1*part2

        grad_w1_temp = part3[:,None]*value
        grad_w1 += grad_w1_temp

    grad_w2 = (grad_w2 + (lambdaval*w2))/len(training_data)
    grad_w1 = (grad_w1 + (lambdaval*w1))/len(training_data)

    obj_val = obj_val/(2*len(training_data))
    obj_val += (np.sum(w1**2) + np.sum(w2**2))*(lambdaval/len(training_data))

    #Make sure you reshape the gradient matrices to a 1D array. for instance if your gradient matrices are grad_w1 and grad_w2
    #you would use code similar to the one below to create a flat array
    obj_grad = np.concatenate((grad_w1.flatten(), grad_w2.flatten()),0)
    
    # nnObjVal function returns two outputs. One is a scalar which equals to your loss function value.
    #Second is a vector that denotes the gradient of the loss function with respect to all of your weights.

    return (obj_val,obj_grad)



def nnPredict(w1,w2,data):

    """% nnPredict predicts the label of data given the parameter w1, w2 of Neural
    % Network.

    % Input:
    % w1: matrix of weights of connections from input layer to hidden layers.
    %     w1(i, j) represents the weight of connection from unit i in input
    %     layer to unit j in hidden layer.
    % w2: matrix of weights of connections from hidden layer to output layers.
    %     w2(i, j) represents the weight of connection from unit i in input
    %     layer to unit j in hidden layer.
    % data: matrix of data. Each row of this matrix represents the feature
    %       vector of a particular image

    % Output:
    % label: a column vector of predicted labels"""

    labels = np.array([])
    for i in range(len(data)):
        value = data[i]

        value = np.append(value, 1)
        a1 = w1.dot(value.T)
        z1 = sigmoid(a1)
        z1 = np.append(z1, 1)

        a2 = w2.dot(z1.T)
        z2 = sigmoid(a2)
        # following call returns the indices of the maximum argument. The index works as the true label.
        labels = np.append(labels, np.argmax(z2))
    return labels




"""**************Neural Network Script Starts here********************************"""
train_data, train_label, validation_data,validation_label, test_data, test_label = preprocess();

#  Train Neural Network

# set the number of nodes in input unit (not including bias unit)
#rohin n_input = train_data.shape[1];
n_input = np.shape(train_data)[1];

# set the number of nodes in hidden unit (not including bias unit)
n_hidden = 88;

# set the regularization hyper-parameter
lambdaval = 0.4;

# set the number of nodes in output unit
n_class = 10;

# initialize the weights into some random matrices
initial_w1 = initializeWeights(n_input, n_hidden);
initial_w2 = initializeWeights(n_hidden, n_class);

# unroll 2 weight matrices into single column vector
initialWeights = np.concatenate((initial_w1.flatten(), initial_w2.flatten()),0)

args = (n_input, n_hidden, n_class, train_data, train_label, lambdaval)

#Train Neural Network using fmin_cg or minimize from scipy,optimize module. Check documentation for a working example

opts = {'maxiter' : 50}    # Preferred value.
nn_params = minimize(nnObjFunction, initialWeights, jac=True, args=args,method='CG', options=opts)

#In Case you want to use fmin_cg, you may have to split the nnObjectFunction to two functions nnObjFunctionVal
#and nnObjGradient. Check documentation for this function before you proceed.
#nn_params, cost = fmin_cg(nnObjFunctionVal, initialWeights, nnObjGradient,args = args, maxiter = 50)

#Reshape nnParams from 1D vector into w1 and w2 matrices
w1 = nn_params.x[0:n_hidden * (n_input + 1)].reshape( (n_hidden, (n_input + 1)))
w2 = nn_params.x[(n_hidden * (n_input + 1)):].reshape((n_class, (n_hidden + 1)))

#Test the computed parameters
predicted_label = nnPredict(w1,w2,train_data)

#find the accuracy on Training Dataset
predicted_label = np.array(predicted_label)
train_label = np.array(train_label)
validation_label = np.array(validation_label)
test_label = np.array(test_label)

print('\n Training set Accuracy:' + str(100*np.mean((predicted_label == train_label).astype(float))) + '%')

predicted_label = nnPredict(w1,w2,validation_data)
#find the accuracy on Validation Dataset
print('\n Validation set Accuracy:' + str(100*np.mean((predicted_label == validation_label).astype(float))) + '%')

predicted_label = nnPredict(w1,w2,test_data)
#find the accuracy on Validation Dataset
print('\n Test set Accuracy:' + str(100*np.mean((predicted_label == test_label).astype(float))) + '%')

#generate params.pickle
pickle.dump([n_hidden,w1,w2,lambdaval],open('params.pickle','wb'))
