import argparse
import inspect
import wordcloud_cli
import wordcloud as wc
import sys
from collections import namedtuple
from mock import patch, MagicMock
from nose.tools import assert_equal, assert_true, assert_in

from tempfile import NamedTemporaryFile

temp = NamedTemporaryFile()
ArgOption = namedtuple('ArgOption', ['cli_name', 'init_name', 'pass_value', 'fail_value'])
ARGUMENT_SPEC_TYPED = [
    ArgOption(cli_name='width', init_name='width', pass_value=13, fail_value=1.),
    ArgOption(cli_name='height', init_name='height', pass_value=15, fail_value=1.),
    ArgOption(cli_name='margin', init_name='margin', pass_value=17, fail_value=1.),
    ArgOption(cli_name='relative_scaling', init_name='relative_scaling', pass_value=1, fail_value='c')
]
ARGUMENT_SPEC_REMAINING = [
    ArgOption(cli_name='stopwords', init_name='stopwords', pass_value=temp.name, fail_value=None),
    ArgOption(cli_name='mask', init_name='mask', pass_value=temp.name, fail_value=None),
    ArgOption(cli_name='fontfile', init_name='font_path', pass_value=temp.name, fail_value=None),
    ArgOption(cli_name='color', init_name='color_func', pass_value='red', fail_value=None),
    ArgOption(cli_name='background', init_name='background_color', pass_value='grey', fail_value=None)
]

def all_arguments():
    arguments = []
    arguments.extend(ARGUMENT_SPEC_TYPED)
    arguments.extend(ARGUMENT_SPEC_REMAINING)
    return arguments


def test_argument_spec_matches_to_constructor_args():
    args = argparse.Namespace()
    for option in all_arguments():
        setattr(args, option.init_name, option.pass_value)

    supported_args = inspect.getargspec(wc.WordCloud.__init__).args
    supported_args.remove('self')
    for arg_name in vars(args).keys():
        assert_in(arg_name, supported_args)


def test_main_passes_arguments_through():
    args = argparse.Namespace()
    for option in all_arguments():
        setattr(args, option.init_name, option.pass_value)
    args.imagefile = NamedTemporaryFile()
    args.text = 'some long text'

    with patch('wordcloud_cli.wc.WordCloud', autospec=True) as mock_word_cloud:
        instance = mock_word_cloud.return_value
        instance.to_image.return_value = MagicMock()
        wordcloud_cli.main(args)

    posargs, kwargs = mock_word_cloud.call_args
    for option in all_arguments():
        assert_in(option.init_name, kwargs)


def check_argument(name, result_name, value):
    text = NamedTemporaryFile()

    args = wordcloud_cli.parse_args(['--text', text.name, '--' + name, str(value)])
    assert_in(result_name, vars(args))


def check_argument_type(name, value):
    text = NamedTemporaryFile()

    try:
        with patch('wordcloud_cli.sys.stderr') as mock_stdout:
            args = wordcloud_cli.parse_args(['--text', text.name, '--' + name, str(value)])
        raise AssertionError('argument "{}" was accepted even though the type did not match'.format(name))
    except SystemExit:
        pass
    except ValueError:
        pass


def test_parse_args_are_passed_along():
    for option in all_arguments():
        if option.cli_name != 'mask':
            yield check_argument, option.cli_name, option.init_name, option.pass_value


def test_parse_arg_types():
    for option in ARGUMENT_SPEC_TYPED:
        yield check_argument_type, option.cli_name, option.fail_value


def test_check_duplicate_color_error():
    color_mask_file = NamedTemporaryFile()
    text_file = NamedTemporaryFile()

    try:
        wordcloud_cli.parse_args(['--color', 'red', '--colormask', color_mask_file.name, '--text', text_file.name])
        raise AssertionError('parse_args(...) didn\'t raise')
    except ValueError as e:
        assert_true('specify either' in str(e), msg='expecting the correct error message, instead got: ' + str(e))


def test_parse_args_defaults_to_random_color():
    text = NamedTemporaryFile()

    args = wordcloud_cli.parse_args(['--text', text.name])
    assert_equal(args.color_func, wc.random_color_func)
