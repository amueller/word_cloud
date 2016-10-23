import argparse
import os
from collections import namedtuple
from tempfile import NamedTemporaryFile

import wordcloud as wc
from wordcloud import wordcloud_cli as cli
from mock import patch
from nose.tools import assert_equal, assert_greater, assert_true, assert_in, assert_not_in

import matplotlib
matplotlib.use('Agg')

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


def test_main_passes_arguments_through():
    temp_imagefile = NamedTemporaryFile()

    args = argparse.Namespace(text='some long text', imagefile=open(temp_imagefile.name, 'w'))
    for option in all_arguments():
        setattr(args, option.init_name, option.pass_value)

    with patch('wordcloud.wordcloud_cli.wc.WordCloud', autospec=True) as mock_word_cloud:
        cli.main(args)

    posargs, kwargs = mock_word_cloud.call_args
    for option in all_arguments():
        assert_in(option.init_name, kwargs)


def check_argument(name, result_name, value):
    text = NamedTemporaryFile()

    args = cli.parse_args(['--text', text.name, '--' + name, str(value)])
    assert_in(result_name, vars(args))


def check_argument_type(name, value):
    text = NamedTemporaryFile()

    try:
        with patch('sys.stderr') as mock_stderr:
            args = cli.parse_args(['--text', text.name, '--' + name, str(value)])
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
        cli.parse_args(['--color', 'red', '--colormask', color_mask_file.name, '--text', text_file.name])
        raise AssertionError('parse_args(...) didn\'t raise')
    except ValueError as e:
        assert_true('specify either' in str(e), msg='expecting the correct error message, instead got: ' + str(e))


def test_parse_args_defaults_to_random_color():
    text = NamedTemporaryFile()

    args = cli.parse_args(['--text', text.name])
    assert_equal(args.color_func, wc.random_color_func)


def test_cli_writes_image():
    # ensure writting works with all python versions
    temp_imagefile = NamedTemporaryFile()
    temp_textfile = NamedTemporaryFile()
    temp_textfile.write(b'some text')
    temp_textfile.flush()

    args = cli.parse_args(['--text', temp_textfile.name, '--imagefile', temp_imagefile.name])
    cli.main(args)

    assert_greater(os.path.getsize(temp_imagefile.name), 0, msg='expecting image to be written')
