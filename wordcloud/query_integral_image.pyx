# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
import array
import numpy as np


def query_integral_image(unsigned int[:,:] integral_image, int size_x, int
                         size_y, random_state):
    cdef int x = integral_image.shape[0]
    cdef int y = integral_image.shape[1]
    cdef int area, i, j
    cdef int hits = 0

    # count how many possible locations
    for i in xrange(x - size_x):
        for j in xrange(y - size_y):
            area = integral_image[i, j] + integral_image[i + size_x, j + size_y]
            area -= integral_image[i + size_x, j] + integral_image[i, j + size_y]
            if not area:
                hits += 1
    if not hits:
        # no room left
        return None
    # pick a location at random
    cdef int goal = random_state.randint(0, hits)
    hits = 0
    for i in xrange(x - size_x):
        for j in xrange(y - size_y):
            area = integral_image[i, j] + integral_image[i + size_x, j + size_y]
            area -= integral_image[i + size_x, j] + integral_image[i, j + size_y]
            if not area:
                hits += 1
                if hits == goal:
                    return i, j
