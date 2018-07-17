import pytest


@pytest.fixture()
def tmp_text_file(tmpdir_factory):
    fn = tmpdir_factory.mktemp("data").join("empty.txt")
    fn.write(b'')
    return fn
