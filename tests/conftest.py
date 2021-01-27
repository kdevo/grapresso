import pytest

from grapresso.backends.memory import InMemoryBackend
from grapresso.backends.networkx import NetworkXBackend

ALL_BACKENDS = ('InMemory-OptimizeMemory', 'NetworkXBackend',)
ENABLED_BACKENDS = ALL_BACKENDS


@pytest.fixture(params=ENABLED_BACKENDS)
def create_backend(request, tmp_path):
    def _create_backend():
        return {
            ALL_BACKENDS[0]: InMemoryBackend(),
            ALL_BACKENDS[1]: NetworkXBackend(),
        }[request.param]

    return _create_backend


@pytest.fixture
def create_graph(importer, create_backend):
    def _graph(name, directed=False):
        return importer.read_graph(create_backend(), name, directed)

    return _graph

