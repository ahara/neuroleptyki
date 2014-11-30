import numpy as np

import consts


class Graph(object):
    """
    Graph structure for representing prescription chains
    """

    def __init__(self):
        self.layers = []
        self.SURVIVED = 'survived'
        self.DIED = 'died'
        self.NAMES = consts.ALL_MEDICINES + [self.SURVIVED, self.DIED]
        self.matrix_size = len(self.NAMES)

    def add_empty_layer(self):
        self.layers.append(np.zeros((self.matrix_size, self.matrix_size), dtype=int))

    def add_chains(self, chains, statuses):
        for i in xrange(len(statuses)):
            s = self.DIED if statuses[i] else self.SURVIVED
            chain = chains[i] + [s]
            row_num = -1
            for j in range(len(chain) - 1):
                if not j < len(self.layers):
                    self.add_empty_layer()
                col_num = self.NAMES.index(chain[j]) if row_num == -1 else row_num  # Columns represent current medicine or state
                row_num = self.NAMES.index(chain[j+1])  # Rows represent next medicine or state
                self.layers[j][row_num, col_num] += 1

