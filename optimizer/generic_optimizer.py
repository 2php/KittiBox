from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging
import sys
import tensorflow as tf


def get_learning_rate(hypes, step):
    if "learning_rates" not in hypes['solver']:
        lr = hypes['solver']['learning_rate']
        lr_step = hypes['solver']['learning_rate_step']
        if lr_step is not None:
            adjusted_lr = (lr * 0.5 ** max(0, (step / lr_step) - 2))
            return adjusted_lr
        else:
            return lr

    for i, num in enumerate(hypes['solver']['steps']):
        if step < num:
            return hypes['solver']['learning_rates'][i]


def training(hypes, total_loss, global_step, learning_rate):
    """Sets up the training Ops.

    Creates a summarizer to track the loss over time in TensorBoard.

    Creates an optimizer and applies the gradients to all trainable variables.

    The Op returned by this function is what must be passed to the
    `sess.run()` call to cause the model to train.

    Args:
      loss: Loss tensor, from loss().
      global_step: Integer Variable counting the number of training steps
        processed.
      learning_rate: The learning rate to use for gradient descent.

    Returns:
      train_op: The Op for training.
    """
    # Add a scalar summary for the snapshot loss.''
    sol = hypes["solver"]
    hypes['tensors'] = {}
    hypes['tensors']['global_step'] = global_step
    with tf.name_scope('training'):

        tvars = tf.trainable_variables()
        if hypes['clip_norm'] <= 0:
            grads = tf.gradients(total_loss, tvars)
        else:
            grads, norm = tf.clip_by_global_norm(tf.gradients(total_loss,
                                                 tvars), hypes['clip_norm'])

        to_opt = zip(grads, tvars)

        if sol['opt'] == 'RMS':
            opt = tf.train.RMSPropOptimizer(learning_rate=learning_rate,
                                            decay=0.9, epsilon=sol['epsilon'])
        elif sol['opt'] == 'Adam':
            opt = tf.train.AdamOptimizer(learning_rate=learning_rate,
                                         epsilon=sol['epsilon'])
        elif sol['opt'] == 'SGD':
            lr = learning_rate
            opt = tf.train.GradientDescentOptimizer(learning_rate=lr)
        else:
            raise ValueError('Unrecognized opt type')

        train_op = opt.apply_gradients(to_opt, global_step=global_step)

    return train_op
