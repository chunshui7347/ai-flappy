import numpy as np


def make_model():
    return MLP(3, 7, 1)


class MLP:
    """simple one hidden layer mlp with relu at hidden layer and sigmoid at output layer"""
    def __init__(self, n_in, n_hidden, n_out):
        """
        :param n_in: number of input unit
        :type n_in: int
        :param n_hidden: number of nodes in hidden layer
        :type n_hidden: int
        :param n_out: number of nodes in output layer
        :type n_out: int
        """
        self.n_in = n_in
        self.n_hidden = n_hidden
        self.n_out = n_out

        self.weights = [np.random.uniform(-1, 1, (n_in, n_hidden)), np.random.uniform(-1, 1, (n_hidden, n_out))]
        self.biases = [np.zeros(n_hidden), np.zeros(n_out)]

    def get_weights(self):
        return [self.weights[0].copy(), self.biases[0].copy(), self.weights[1].copy(), self.biases[1].copy()]

    def set_weights(self, weights):
        """
        :param weights: list of numpy array as weights
        :type weights: list[numpy.ndarray]

        """
        self.weights = [weights[0].copy(), weights[2].copy()]
        self.biases = [weights[1].copy(), weights[3].copy()]

    def predict(self, Xs):
        """
        :param Xs: list of x inputs
        :type Xs: list or array-like
        :return: list of predictions
        :rtype: numpy.ndarray of shape(len(Xs), 1)
        """
        Xs = np.array(Xs)
        ans = np.zeros((len(Xs), 1))
        for i, x in enumerate(Xs):
            x = np.maximum(0, np.add(np.dot(x, self.weights[0]), self.biases[0]))  # first hidden
            x = 1 / (1 + np.exp(-np.add(np.dot(x, self.weights[1]), self.biases[1])))
            ans[i][0] = x
        return ans
