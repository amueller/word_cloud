import numpy as np
import pytest
from numpy.testing import assert_array_equal

from wordcloud import WordCloud


@pytest.fixture(params=['RGB', 'RGBA'])
def cloud(request):
    return WordCloud(width=120, height=60, mode=request.param,
                     background_color=None, random_state=0).generate('hello world')


@pytest.mark.parametrize('convert', [np.array, np.asarray])
@pytest.mark.parametrize('dtype', [np.uint8, np.float32, np.float64])
def test_numpy_dtype(cloud, convert, dtype):
    expected = np.asarray(cloud.to_image(), dtype=dtype)
    result = convert(cloud, dtype=dtype)
    assert result.dtype == dtype
    assert_array_equal(result, expected)


@pytest.mark.parametrize('keyword', [False, True])
def test_array_protocol_dtype(cloud, keyword):
    if keyword:
        result = cloud.__array__(dtype=np.float32)
    else:
        result = cloud.__array__(np.dtype('float32'))
    assert result.dtype == np.float32
    assert_array_equal(result, np.asarray(cloud.to_image(), dtype=np.float32))


def test_array_protocol_copy(cloud):
    expected = cloud.to_array()
    result = cloud.__array__(copy=True)
    assert result.flags.writeable
    assert not np.shares_memory(result, expected)
    assert_array_equal(result, expected)
    result[:] = 0
    assert_array_equal(cloud.to_array(), expected)


def test_array_protocol_no_copy(cloud):
    expected = cloud.to_array()
    assert_array_equal(cloud.__array__(copy=False), expected)
    assert_array_equal(cloud.__array__(dtype=np.uint8, copy=False), expected)
    with pytest.raises(ValueError, match='copy'):
        cloud.__array__(dtype=np.float32, copy=False)


def test_numpy_no_copy(cloud):
    assert_array_equal(np.array(cloud, copy=False), cloud.to_array())
    if np.lib.NumpyVersion(np.__version__) >= '2.0.0':
        with pytest.raises(ValueError, match='copy'):
            np.array(cloud, dtype=np.float32, copy=False)
    else:
        # NumPy 1 does not pass copy to __array__ and permits materialization.
        assert_array_equal(np.array(cloud, dtype=np.float32, copy=False),
                           cloud.to_array().astype(np.float32))


@pytest.mark.parametrize('copy', [None, False, True])
def test_to_array_copy_compatibility(cloud, copy):
    # Keep the established positional to_array(copy) API on both NumPy versions.
    result = cloud.to_array(copy)
    assert result.dtype == np.uint8
    assert_array_equal(result, np.asarray(cloud.to_image()))


def test_array_dtype_before_generation():
    with pytest.raises(ValueError, match='call generate'):
        np.array(WordCloud(), dtype=np.float32)
