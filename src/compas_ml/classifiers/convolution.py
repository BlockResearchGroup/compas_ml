
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf

from numpy import asarray
from numpy import float32
from numpy.random import choice


__author__    = ['Andrew Liew <liew@arch.ethz.ch>']
__copyright__ = 'Copyright 2018, BLOCK Research Group - ETH Zurich'
__license__   = 'MIT License'
__email__     = 'liew@arch.ethz.ch'


__all__ = [
    'convolution',
]


def weight_variable(shape):
    return tf.Variable(tf.truncated_normal(shape, stddev=0.1))


def bias_variable(shape):
    return tf.Variable(tf.constant(0.1, shape=shape))


def conv2d(x, W):
    return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')


def max_pool_2x2(x):
    return tf.nn.max_pool(x, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')


def conv_layer(input, shape):
    W = weight_variable(shape)
    b = bias_variable([shape[-1]])
    return tf.nn.relu(conv2d(input, W) + b)


def full_layer(input, size):
    in_size = int(input.get_shape()[1])
    W = weight_variable([in_size, size])
    b = bias_variable([size])
    return tf.matmul(input, W) + b


def convolution(training_data, training_labels, testing_data, testing_labels, fdim, features, classes, dimx, dimy,
                channels, steps, batch, neurons):

    """ Convolution Neural Network.

    Parameters
    ----------
    training_data : array
        Training data of size (m x length).
    training_labels : array
        Training labels of size (m x classes).
    testing_data : array
        Testing data of size (n x length).
    testing_labels : array
        Testing labels of size (n x classes).
    fdim : int
        Filter size in x and y.
    features : int
        Number of features per convolution layer.
    classes : int
        Number of classes.
    dimx : int
        Number of pixels in x.
    dimy : int
        Number of pixels in y.
    channels : int
        Grey: 1, RGB: 3.
    steps : int
        Number of analysis steps.
    batch : int
        Batch size of images per step.
    neurons : int
        Number of neurons.

    Returns
    -------
    None

    """

    print('***** Session started *****')

    training_data = asarray(training_data, dtype=float32)
    training_labels = asarray(training_labels, dtype=float32)

    x_ = tf.placeholder(tf.float32, [None, dimx, dimy, channels])
    y_ = tf.placeholder(tf.float32, [None, classes])
    m = training_data.shape[0]

    conv1 = conv_layer(x_, shape=[fdim, fdim, channels, features])
    conv1_pool = max_pool_2x2(conv1)

    conv2 = conv_layer(conv1_pool, shape=[fdim, fdim, features, 2 * features])
    conv2_pool = max_pool_2x2(conv2)

    conv2_flat = tf.reshape(conv2_pool, [-1, int(0.25 * 0.25 * dimx * dimy * 2 * features)])
    full_1 = tf.nn.relu(full_layer(conv2_flat, neurons))

    keep_prob = tf.placeholder(tf.float32)
    full1_drop = tf.nn.dropout(full_1, keep_prob=keep_prob)

    y_conv = full_layer(full1_drop, classes)

    diff = tf.nn.softmax_cross_entropy_with_logits(logits=y_conv, labels=y_)
    cross_entropy = tf.reduce_mean(diff)
    train_step = tf.train.AdamOptimizer(0.0001).minimize(cross_entropy)

    correct_prediction = tf.equal(tf.argmax(y_conv, 1), tf.argmax(y_, 1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

    with tf.Session() as session:

        session.run(tf.global_variables_initializer())

        for i in range(steps):

            select = choice(m, batch, replace=False)
            x_batch = training_data[select, :, :, :]
            y_batch = training_labels[select, :]

            if (i + 1) % 10 == 0:
                acc = session.run(accuracy, feed_dict={x_: x_batch, y_: y_batch, keep_prob: 1.0})
                print('Step: {0}: Accuracy: {1:.1f}'.format(i + 1, 100 * acc))

            session.run(train_step, feed_dict={x_: x_batch, y_: y_batch, keep_prob: 0.5})

        acc = session.run(accuracy, feed_dict={x_: testing_data, y_: testing_labels, keep_prob: 1.0})
        print('Testing accuracy: {1:.1f}'.format(i + 1, 100 * acc))

    print('***** Session finished *****')


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":

    from matplotlib import pyplot as plt
    from numpy import array
    from numpy import newaxis
    from scipy.misc import imread
    from os import listdir


    path = '/home/al/compas_ml/data/mnist/'

    training_data   = []
    testing_data    = []
    training_labels = []
    testing_labels  = []

    for j in ['testing', 'training']:
        for i in range(10):
            files = listdir('{0}/{1}/{2}'.format(path, j, i))
            for file in files:
                image = imread('{0}/{1}/{2}/{3}'.format(path, j, i, file))
                dimx, dimy = image.shape
                binary = [0] * 10
                binary[i] = 1
                if j == 'training':
                    training_data.append(image)
                    training_labels.append(binary)
                else:
                    testing_data.append(image)
                    testing_labels.append(binary)

    training_data = array(training_data)[:, :, :, newaxis]
    testing_data = array(testing_data)[:, :, :, newaxis]

    # plt.imshow(training_data[0, :, :])
    # plt.show()

    convolution(training_data, training_labels, testing_data, testing_labels, fdim=5, features=32, classes=10,
                dimx=dimx, dimy=dimy, channels=1, steps=500, batch=100, neurons=1024)