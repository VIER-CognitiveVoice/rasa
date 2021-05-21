import tensorflow as tf
from tensorflow import Tensor, TensorShape
from typing import Union


def random_indices(batch_size: Tensor, n: Tensor, n_max: Tensor) -> Tensor:
    """Creates batch_size * n random indices that run from 0 to n_max.

    Args:
        batch_size: Number of items in each batch
        n: Number of random indices in each example
        n_max: Maximum index

    Returns:
        A uniformly distributed integer tensor of indices
    """
    return (
        tf.random.uniform(shape=(batch_size, n), maxval=n_max, dtype=tf.int32)
        if n_max > 0
        else tf.zeros((batch_size, n))
    )


def batch_flatten(x: Tensor) -> Tensor:
    """Flattens all but last dimension of `x` so it becomes 2D.

    Args:
        x: Any tensor with at least 2 dimensions

    Returns:
        The reshaped tensor, where all but the last dimension
        are flattened into the first dimension
    """
    return tf.reshape(x, (-1, x.shape[-1]))


def pad_right(
    x: Tensor, target_shape: TensorShape, value: Union[int, float] = 0
) -> Tensor:
    """Creates a tensor of shape `target_shape` by padding it with `value` on the right.

    Args:
        x: Any tensor
        target_shape: Shape of the padded x; must be at least as large as the
            shape of x in all dimensions

    Returns:
        A tensor like x, but padded with `value`
    """
    current_shape = tf.shape(x)
    right_padding = tf.expand_dims(
        tf.convert_to_tensor(target_shape - current_shape), -1
    )
    padding = tf.concat([tf.zeros_like(right_padding), right_padding], -1)
    return tf.pad(x, padding, "CONSTANT", constant_values=value)


def get_candidate_values(
    x: tf.Tensor,  # (batch_size, ...)
    candidate_ids: tf.Tensor,  # (batch_size, num_candidates)
) -> tf.Tensor:
    """Gathers candidate values according to IDs.

    Args:
        x: Any tensor with at least one dimension
        candidate_ids: Indicator for which candidates to gather

    Returns:
        A tensor of shape (batch_size, 1, num_candidates, tf.shape(x)[-1]), where
        for each batch example, we generate a list of num_candidates vectors, and
        each candidate is chosen from x according to the candidate id. For example:

        x = [[0 1 2],
                [3 4 5],
                [6 7 8]]
        candidate_ids = [[0, 1], [0, 0], [2, 0]]
        gives
        [
            [[0 1 2],
             [3 4 5]],
            [[0 1 2],
             [0 1 2]],
            [[6 7 8],
             [0 1 2]]
        ]
    """
    tiled_x = tf.tile(
        tf.expand_dims(batch_flatten(x), 0), (tf.shape(candidate_ids)[0], 1, 1),
    )
    candidate_values = tf.gather(tiled_x, candidate_ids, batch_dims=1)

    return candidate_values  # (batch_size, num_candidates, tf.shape(x)[-1])


def reduce_mean_equal(x: tf.Tensor, y: tf.Tensor) -> tf.Tensor:
    """Computes the mean number of matches between x and y.

    Args:
        x: Any numeric tensor
        y: Another tensor with same shape and type as x

    Returns:
        The mean of "x == y"
    """
    return tf.reduce_mean(tf.cast(tf.math.equal(x, y), tf.float32))
