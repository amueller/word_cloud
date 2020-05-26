import argparse
import os
import subprocess
import sys
from collections import namedtuple

import wordcloud as wc
from wordcloud import wordcloud_cli as cli

from mock import patch
import pytest

import matplotlib
matplotlib.use('Agg')


class PassFile(object):
    pass


ArgOption = namedtuple('ArgOption', ['cli_name', 'init_name', 'pass_value', 'fail_value'])
ARGUMENT_SPEC_TYPED = [
    ArgOption(cli_name='width', init_name='width', pass_value=13, fail_value=1.),
    ArgOption(cli_name='height', init_name='height', pass_value=15, fail_value=1.),
    ArgOption(cli_name='margin', init_name='margin', pass_value=17, fail_value=1.),
    ArgOption(cli_name='relative_scaling', init_name='relative_scaling', pass_value=1, fail_value='c'),
]
ARGUMENT_SPEC_UNARY = [
    ArgOption(cli_name='no_collocations', init_name='collocations', pass_value=True, fail_value=1),
    ArgOption(cli_name='include_numbers', init_name='include_numbers', pass_value=True, fail_value=2),
    ArgOption(cli_name='no_normalize_plurals', init_name='normalize_plurals', pass_value=True, fail_value=3),
    ArgOption(cli_name='repeat', init_name='repeat', pass_value=True, fail_value=4),
]
ARGUMENT_SPEC_REMAINING = [
    ArgOption(cli_name='stopwords', init_name='stopwords', pass_value=PassFile(), fail_value=None),
    ArgOption(cli_name='regexp', init_name='regexp', pass_value=r'\w{2,}', fail_value=r'12('),
    ArgOption(cli_name='mask', init_name='mask', pass_value=PassFile(), fail_value=None),
    ArgOption(cli_name='fontfile', init_name='font_path', pass_value=PassFile(), fail_value=None),
    ArgOption(cli_name='color', init_name='color_func', pass_value='red', fail_value=None),
    ArgOption(cli_name='background', init_name='background_color', pass_value='grey', fail_value=None),
    ArgOption(cli_name='contour_color', init_name='contour_color', pass_value='grey', fail_value=None),
    ArgOption(cli_name='contour_width', init_name='contour_width', pass_value=0.5, fail_value='blue'),
    ArgOption(cli_name='min_word_length', init_name='min_word_length', pass_value=5, fail_value='blue'),
    ArgOption(cli_name='prefer_horizontal', init_name='prefer_horizontal', pass_value=.1, fail_value='blue'),
    ArgOption(cli_name='scale', init_name='scale', pass_value=1., fail_value='blue'),
    ArgOption(cli_name='colormap', init_name='colormap', pass_value='Greens', fail_value=1),
    ArgOption(cli_name='mode', init_name='mode', pass_value='RGBA', fail_value=2),
    ArgOption(cli_name='max_words', init_name='max_words', pass_value=10, fail_value='blue'),
    ArgOption(cli_name='min_font_size', init_name='min_font_size', pass_value=10, fail_value='blue'),
    ArgOption(cli_name='max_font_size', init_name='max_font_size', pass_value=10, fail_value='blue'),
    ArgOption(cli_name='font_step', init_name='font_step', pass_value=10, fail_value='blue'),
    ArgOption(cli_name='random_state', init_name='random_state', pass_value=100, fail_value='blue'),
]
ARGUMENT_CLI_NAMES_UNARY = [arg_opt.cli_name for arg_opt in ARGUMENT_SPEC_UNARY]


def all_arguments():
    arguments = []
    arguments.extend(ARGUMENT_SPEC_TYPED)
    arguments.extend(ARGUMENT_SPEC_UNARY)
    arguments.extend(ARGUMENT_SPEC_REMAINING)
    return arguments


def test_main_passes_arguments_through(tmpdir):

    image_filepath = str(tmpdir.join('word_cloud.png'))

    args = argparse.Namespace()
    for option in all_arguments():
        setattr(args, option.init_name, option.pass_value)

    text = 'some long text'
    image_file = open(image_filepath, 'w')
    with patch('wordcloud.wordcloud_cli.wc.WordCloud', autospec=True) as mock_word_cloud:
        cli.main(vars(args), text, image_file)

    posargs, kwargs = mock_word_cloud.call_args
    for option in all_arguments():
        assert option.init_name in kwargs


def check_argument(text_filepath, name, result_name, value):
    args, text, image_file = cli.parse_args(['--text', text_filepath, '--' + name, str(value)])
    assert result_name in args


def check_argument_unary(text_filepath, name, result_name):
    args, text, image_file = cli.parse_args(['--text', text_filepath, '--' + name])
    assert result_name in args


def check_argument_type(text_filepath, name, value):
    with pytest.raises((SystemExit, ValueError),):
        args, text, image_file = cli.parse_args(['--text', text_filepath, '--' + name, str(value)])


@pytest.mark.parametrize("option", all_arguments())
def test_parse_args_are_passed_along(option, tmpdir, tmp_text_file):
    if option.cli_name in ARGUMENT_CLI_NAMES_UNARY:
        check_argument_unary(str(tmp_text_file), option.cli_name, option.init_name)
    elif option.cli_name != 'mask':
        pass_value = option.pass_value
        if isinstance(option.pass_value, PassFile):
            input_file = tmpdir.join("%s_file" % option.cli_name)
            input_file.write(b"")
            pass_value = str(input_file)
        check_argument(str(tmp_text_file), option.cli_name, option.init_name, pass_value)


@pytest.mark.parametrize("option", ARGUMENT_SPEC_TYPED)
def test_parse_arg_types(option, tmp_text_file):
    check_argument_type(str(tmp_text_file), option.cli_name, option.fail_value)


def test_check_duplicate_color_error(tmpdir, tmp_text_file):
    color_mask_file = tmpdir.join("input_color_mask.png")
    color_mask_file.write(b"")

    with pytest.raises(ValueError, match=r'.*specify either.*'):
        cli.parse_args(['--color', 'red', '--colormask', str(color_mask_file), '--text', str(tmp_text_file)])


def test_parse_args_defaults_to_random_color(tmp_text_file):
    args, text, image_file = cli.parse_args(['--text', str(tmp_text_file)])
    assert args['color_func'] == wc.random_color_func


def test_unicode_text_file():
    unicode_file = os.path.join(os.path.dirname(__file__), "unicode_text.txt")
    args, text, image_file = cli.parse_args(['--text', unicode_file])
    assert len(text) == 16


def test_unicode_with_stopwords():
    unicode_file = os.path.join(os.path.dirname(__file__), "unicode_text.txt")
    stopwords_file = os.path.join(os.path.dirname(__file__), "unicode_stopwords.txt")
    args, text, image_file = cli.parse_args(['--text', unicode_file, '--stopwords', stopwords_file])

    # expect the unicode character from stopwords file was correctly read in
    assert u'\u304D' in args['stopwords']


def test_cli_writes_to_imagefile(tmpdir, tmp_text_file):
    # ensure writing works with all python versions
    tmp_image_file = tmpdir.join("word_cloud.png")

    tmp_text_file.write(b'some text')

    args, text, image_file = cli.parse_args(['--text', str(tmp_text_file), '--imagefile', str(tmp_image_file)])
    cli.main(args, text, image_file)

    # expecting image to be written to imagefile
    assert tmp_image_file.size() > 0


# capsysbinary should be used here, but it's not supported in python 2.
def test_cli_writes_to_stdout(tmpdir, tmp_text_file):
    # ensure writing works with all python versions
    tmp_image_file = tmpdir.join("word_cloud.png")

    tmp_text_file.write(b'some text')

    originalBuffer = sys.stdout.buffer
    sys.stdout.buffer = tmp_image_file.open('wb+')

    args, text, image_file = cli.parse_args(['--text', str(tmp_text_file)])
    cli.main(args, text, image_file)

    sys.stdout.buffer = originalBuffer

    # expecting image to be written to stdout
    assert tmp_image_file.size() > 0


def test_cli_regexp(tmp_text_file):
    cli.parse_args(['--regexp', r"\w[\w']+", '--text', str(tmp_text_file)])


def test_cli_regexp_invalid(tmp_text_file, capsys):
    with pytest.raises(SystemExit):
        cli.parse_args(['--regexp', r"invalid[", '--text', str(tmp_text_file)])

    _, err = capsys.readouterr()
    assert "Invalid regular expression" in err


@pytest.mark.parametrize("command,expected_output, expected_exit_code", [
    ("wordcloud_cli --help", "usage: wordcloud_cli", 0),
    ("python -m wordcloud --help", "usage: __main__", 0),
    ("python %s/../wordcloud/wordcloud_cli.py --help" % os.path.dirname(__file__), "To execute the CLI", 1),
])
def test_cli_as_executable(command, expected_output, expected_exit_code, tmpdir, capfd, no_cover_compat):

    ret_code = 0
    try:
        subprocess.check_call(
            command,
            shell=True,
            cwd=str(tmpdir)
        )
    except subprocess.CalledProcessError as excinfo:
        ret_code = excinfo.returncode

    out, err = capfd.readouterr()
    assert expected_output in out if ret_code == 0 else err

    assert ret_code == expected_exit_code
