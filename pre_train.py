import tensorflow as tf
from spatial_transformer import transformer
import numpy as np
from utils.tf_utils import weight_variable, bias_variable, dense_to_one_hot
from config import *
import sys
import os

# log_file will have output messages about loss and accuracy
log_file = ARGS.LOGFILE
sys.stdout = open(log_file, 'w')

model_dir = ARGS.MODEL_PATH

# Create directory to store model if it does not already exist
if not os.path.exists(model_dir):
    os.makedirs(model_dir)

rts_mnist = np.load(ARGS.DATA_FOLDER + '42x42_mnist.npz')
X, y = rts_mnist['distorted_x'], rts_mnist['labels']

classifier_arch = ARGS.CLASSIFIER_ARCH

if classifier_arch == 'FCN':
    X = X.reshape(X.shape[0], 42 * 42)
    x = tf.placeholder(tf.float32, [None, 42*42])
else:
    X = X.reshape(X.shape + (1, ))
    x = tf.placeholder(tf.float32, [None, 42, 42, 1])

y = tf.placeholder(tf.float32, [None, 10])

X_train = X[:10000] 
y_train = y[:10000] 
X_valid = X[10000:11000] 
y_valid = y[10000:11000]

Y_train = dense_to_one_hot(y_train, n_classes=10)
Y_valid = dense_to_one_hot(y_valid, n_classes=10) 

classifier_arch = ARGS.CLASSIFIER_ARCH

if classifier_arch == 'CNN':
    filter_size=3
    n_filters_1=16
    W_clsfr_1 = weight_variable([filter_size, filter_size, 1, n_filters_1], name='W_clsfr_1')
    b_clsfr_1 = bias_variable([n_filters_1], name='b_clsfr_1')
    clsfr_conv1 = tf.nn.relu(
                    tf.nn.conv2d(
                        input=x, 
                        filter=W_clsfr_1, 
                        strides=[1, 1, 1, 1], 
                        padding='SAME'
                    ) + b_clsfr_1
                )
    clsfr_pool1 = tf.nn.max_pool(
                    value=clsfr_conv1, 
                    ksize=[1, 2 ,2 , 1], 
                    strides=[1, 2, 2, 1], 
                    padding='SAME'
                )
    filter_size=3
    n_filters_2=32
    W_clsfr_2 = weight_variable([filter_size, filter_size, n_filters_1, n_filters_2], name='W_clsfr_2')
    b_clsfr_2 = bias_variable([n_filters_2], name='b_clsfr_2')
    clsfr_conv2 = tf.nn.relu(
                    tf.nn.conv2d(
                        input=clsfr_pool1,
                        filter=W_clsfr_2,
                        strides=[1, 1, 1, 1],
                        padding='SAME'
                    ) + b_clsfr_2
                )
    clsfr_pool2 = tf.nn.max_pool(
                    value=clsfr_conv2,
                    ksize=[1, 2, 2, 1],
                    strides=[1, 2, 2, 1],
                    padding='SAME'
                )

    # Shape of clsfr_pool2 should be (batch_size, 11, 11, n_filters_2)
    clsfr_pool2_flat = tf.reshape(clsfr_pool2, [-1, 121*n_filters_2])
    W_clsfr_3 = weight_variable([121*n_filters_2, 1024], name='W_clsfr_3')
    b_clsfr_3 = bias_variable([1024], name='b_clsfr_3')
    h_clsfr_1 = tf.nn.relu(
                    tf.matmul(clsfr_pool2_flat, W_clsfr_3) 
                    + b_clsfr_3
                )
    W_clsfr_4 = weight_variable([1024, 10], name='W_clsfr_4')
    b_clsfr_4 = bias_variable([10], name='b_clsfr_4')
    y_logits = tf.nn.relu(
                    tf.matmul(h_clsfr_1, W_clsfr_4) 
                    + b_clsfr_4
                )
    clsfr_weights=[W_clsfr_1, W_clsfr_2, W_clsfr_3, W_clsfr_4]
    clsfr_biases=[b_clsfr_1, b_clsfr_2, b_clsfr_3, b_clsfr_4]

else:
    W_clsfr_1 = weight_variable([42*42, 1024], name='W_clsfr_1')
    b_clsfr_1 = bias_variable([1024], name='b_clsfr_1')
    h_clsfr_1 = tf.nn.relu(
                    tf.matmul(h_trans_flat, x) + b_clsfr_1
                )
    W_clsfr_2 = weight_variable([1024, 256], name='W_clsfr_2')
    b_clsfr_2 = bias_variable([256], name='b_clsfr_2')
    h_clsfr_2 = tf.nn.relu(
                    tf.matmul(h_clsfr_1, W_clsfr_2) + b_clsfr_2
                )
    W_clsfr_3 = weight_variable([256, 10], name='W_clsfr_3')
    b_clsfr_3 = bias_variable([10], name='b_clsfr_3')
    y_logits  = tf.nn.relu(
                    tf.matmul(h_clsfr_2, W_clsfr_3) + b_clsfr_3
                )
    clsfr_weights=[W_clsfr_1, W_clsfr_2, W_clsfr_3]
    clsfr_biases=[b_clsfr_1, b_clsfr_2, b_clsfr_3]
    filter_size=3
    n_filters_1=16
    W_clsfr_1 = weight_variable([filter_size, filter_size, 1, n_filters_1], name='W_clsfr_1')
    b_clsfr_1 = bias_variable([n_filters_1], name='b_clsfr_1')
    clsfr_conv1 = tf.nn.relu(
                    tf.nn.conv2d(
                        input=h_trans, 
                        filter=W_clsfr_1, 
                        strides=[1, 1, 1, 1], 
                        padding='SAME'
                    ) + b_clsfr_1
                )
    clsfr_pool1 = tf.nn.max_pool(
                    value=clsfr_conv1, 
                    ksize=[1, 2 ,2 , 1], 
                    strides=[1, 2, 2, 1], 
                    padding='SAME'
                )
    filter_size=3
    n_filters_2=32
    W_clsfr_2 = weight_variable([filter_size, filter_size, n_filters_1, n_filters_2], name='W_clsfr_2')
    b_clsfr_2 = bias_variable([n_filters_2], name='b_clsfr_2')
    clsfr_conv2 = tf.nn.relu(
                    tf.nn.conv2d(
                        input=clsfr_pool1,
                        filter=W_clsfr_2,
                        strides=[1, 1, 1, 1],
                        padding='SAME'
                    ) + b_clsfr_2
                )
    clsfr_pool2 = tf.nn.max_pool(
                    value=clsfr_conv2,
                    ksize=[1, 2, 2, 1],
                    strides=[1, 2, 2, 1],
                    padding='SAME'
                )
    # Shape of clsfr_pool2 should be (batch_size, 11, 11, n_filters_2)
    clsfr_pool2_flat = tf.reshape(clsfr_pool2, [-1, 121*n_filters_2])
    W_clsfr_3 = weight_variable([121*n_filters_2, 1024], name='W_clsfr_3')
    b_clsfr_3 = bias_variable([1024], name='b_clsfr_3')
    h_clsfr_1 = tf.nn.relu(
                    tf.matmul(clsfr_pool2_flat, W_clsfr_3) 
                    + b_clsfr_3
                )
    W_clsfr_4 = weight_variable([1024, 10], name='W_clsfr_4')
    b_clsfr_4 = bias_variable([10], name='b_clsfr_4')
    y_logits = tf.matmul(h_clsfr_1, W_clsfr_4) + b_clsfr_4

    clsfr_weights=[W_clsfr_1, W_clsfr_2, W_clsfr_3, W_clsfr_4]
    clsfr_biases=[b_clsfr_1, b_clsfr_2, b_clsfr_3, b_clsfr_4]

else:
    h_trans_flat = tf.reshape(h_trans, [-1, 42*42])
    W_clsfr_1 = weight_variable([42*42, 1024], name='W_clsfr_1')
    b_clsfr_1 = bias_variable([1024], name='b_clsfr_1')
    h_clsfr_1 = tf.nn.relu(
                    tf.matmul(h_trans_flat, W_clsfr_1) + b_clsfr_1
                )
    W_clsfr_2 = weight_variable([1024, 256], name='W_clsfr_2')
    b_clsfr_2 = bias_variable([256], name='b_clsfr_2')
    h_clsfr_2 = tf.nn.relu(
                    tf.matmul(h_clsfr_1, W_clsfr_2) + b_clsfr_2
                )
    W_clsfr_3 = weight_variable([256, 10], name='W_clsfr_3')
    b_clsfr_3 = bias_variable([10], name='b_clsfr_3')
    y_logits = tf.matmul(h_clsfr_2, W_clsfr_3) + b_clsfr_3

    clsfr_weights=[W_clsfr_1, W_clsfr_2, W_clsfr_3]
    clsfr_biases=[b_clsfr_1, b_clsfr_2, b_clsfr_3]

beta = ARGS.BETA
if ARGS.REG == 'L1':
    regularizer = tf.contrib.layers.l1_regularizer(scale=beta, scope=None)
elif ARGS.REG == 'L2':
    regularizer = tf.contrib.layers.l2_regularizer(scale=beta, scope=None)

reg_weights = clsfr_weights
if ARGS.reg=='None':
    reg_penalty = 0
else:
    reg_penalty = tf.contrib.layers.apply_regularization(regularizer, reg_weights)
 
cross_entropy = tf.reduce_mean(
                    tf.nn.softmax_cross_entropy_with_logits(y_logits, y)
                )
learning_rate = ARGS.LEARNING_RATE
opt = tf.train.AdamOptimizer(learning_rate=learning_rate)
optimizer = opt.minimize(cross_entropy + reg_penalty)

store_layers = {}
clsfr_params = clsfr_weights + clsfr_biases
for param in clsfr_params:
    store_layers[param.name] = param
saver = tf.train.Saver(store_layers)

iter_per_epoch=100
n_epochs=ARGS.N_EPOCHS

indices=np.linspace(0, 10000-1, iter_per_epoch)
indices=indices.astype('int')

for epoch_i in range(n_epochs):
    for iter_i in range(iter_per_epoch-1):
        batch_xs=X_train[indices[iter_i]:indices[iter_i+1]]
        batch_ys=Y_train[indices[iter_i]:indices[iter_i+1]]

        if iter_i%10 == 0:
            loss = sess.run(
                                cross_entropy,
                                feed_dict = {
                                x:batch_xs,
                                y:batch_ys
                                }
                            )
            print('Iteration: ' + str(iter_i) + ' Loss: ' + str(loss))

        sess.run(
                    optimizer, 
                    feed_dict={
                        x:batch_xs,
                        y:batch_ys
                    }
                )

    acc = str(sess.run(
                        accuracy, 
                        feed_dict={
                            x:X_valid,
                            y:Y_valid
                        }
                    ))
    print('Accuracy (%d): %s' % (epoch_i, acc))
