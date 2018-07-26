import pytest


@pytest.fixture()
def tmp_text_file(tmpdir_factory):
    fn = tmpdir_factory.mktemp("data").join("empty.txt")
    fn.write(b'')
    return fn


@pytest.fixture
def no_cover_compat(request):
    """A pytest fixture to disable coverage.

    .. note::

         After the next version of ``pytest-cov`` is released, it will be possible to directly
         use the ``no_cover`` fixture or marker.
    """

    # Check with hasplugin to avoid getplugin exception in older pytest.
    if request.config.pluginmanager.hasplugin('_cov'):
        plugin = request.config.pluginmanager.getplugin('_cov')
        if plugin.cov_controller:
            plugin.cov_controller.cov.stop()
            plugin.cov_controller.unset_env()
            yield plugin.cov_controller
            plugin.cov_controller.set_env()
            plugin.cov_controller.cov.start()
