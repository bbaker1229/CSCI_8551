#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt

# define the ratio of white to black squares
# number_of_white_squares / total_number_of_squares
R = 0.70

# define width and height of play area in tile size
WIDTH = 8
HEIGHT = 8

N = WIDTH * HEIGHT
K = round(R * N)
arr = np.array([1] * K + [0] * (N-K))
seed_num = np.random.randint(1, 10000)
np.random.seed(seed_num)
np.random.shuffle(arr)
arr = arr.reshape((WIDTH, HEIGHT))

filename = "floor_plan_R_" + str(round(R*100)) + "_seed_" + str(seed_num) + ".jpeg"

plt.imshow(arr, cmap='gray')
plt.axis('off')
plt.savefig(filename, bbox_inches='tight')