#cython: boundscheck=False
#cython: wraparound=False

from cpython cimport array
import array
import numpy as np

def query_integral_image(unsigned int[:, :] integral_image, int size_x, int size_y, random_state):
    cdef int hits = c_search_for_space(integral_image, size_x, size_y)
    if not hits:
        return None
    cdef int goal = random_state.randrange(0, hits + 1)
    cdef int coordinates_array[2]
    cdef int[:] coordinates_memory_view = coordinates_array
    c_iterate_for_coordinates(integral_image, size_x, size_y, goal, coordinates_memory_view)
    return coordinates_array

cdef int c_search_for_space(unsigned int[:, :] integral_image, int size_x, int size_y):
    cdef int x = integral_image.shape[0]
    cdef int y = integral_image.shape[1]
    cdef int area, i, j
    cdef int hits = 0
    for i in xrange(x - size_x):
        for j in xrange(y - size_y):
            area = integral_image[i, j] + integral_image[i + size_x, j + size_y]
            area -= integral_image[i + size_x, j] + integral_image[i, j + size_y]
            if not area:
                hits += 1
    return hits



cdef void c_iterate_for_coordinates(unsigned int[:, :] integral_image, int size_x, int size_y, int goal, int[:] coordinates_array):
    cdef int x = integral_image.shape[0]
    cdef int y = integral_image.shape[1]
    cdef int area, i, j
    cdef int hits = 0
    for i in xrange(x - size_x):
        for j in xrange(y - size_y):
            area = integral_image[i, j] + integral_image[i + size_x, j + size_y]
            area -= integral_image[i + size_x, j] + integral_image[i, j + size_y]
            if not area:
                hits += 1
            if hits == goal:
                coordinates_array[0] = i
                coordinates_array[1] = j
                return


def test_c_search_for_space(unsigned int[:, :] integral_image, int size_x, int size_y):
    return c_search_for_space(integral_image, size_x, size_y)

def test_c_iterate_for_coordinates(unsigned int[:, :] integral_image, int size_x, int size_y, int goal, int[:] coordinates_array):
    return c_iterate_for_coordinates(integral_image, size_x, size_y, goal, coordinates_array)

