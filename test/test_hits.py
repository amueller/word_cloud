import pytest
import numpy as np
from wordcloud.query_integral_image import test_c_search_for_space as c_search_for_space


shape_x = 100
shape_y = 100


@pytest.fixture
def integral_image():
    return np.zeros((shape_x, shape_y), dtype=np.uint32)


# Add any additional tests here using the format:
# ('test_name', {'word_x':val, 'word_y': val, 'expected_hits': val})
# they will be collected by the fixture function
_test_hit_parameters = [('small word', {'word_x': 10, 'word_y': 10, 'expected_hits': 8100}),
                        ('maximum sized word', {'word_x': shape_x - 1, 'word_y': shape_y - 1, 'expected_hits': 1}),
                        ('oversized word', {'word_x': shape_x + 1, 'word_y': shape_y + 1, 'expected_hits': 0})]


@pytest.fixture(params=[p[1] for p in _test_hit_parameters], ids=[p[0] for p in _test_hit_parameters])
def test_hit_parameters(request):
    return request.param


def test_hits_equals_expected(integral_image, test_hit_parameters):
    value = c_search_for_space(integral_image, test_hit_parameters['word_x'], test_hit_parameters['word_y'])
    assert value == test_hit_parameters['expected_hits']
