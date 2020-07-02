import pytest

from grapresso.backend.memory import InMemoryBackend, Trait
from grapresso.backend.networkx import NetworkXBackend

ALL_BACKENDS = ('InMemory-OptimizeMemory', 'InMemory-OptimizePerformance', 'NetworkXBackend',)
ENABLED_BACKENDS = ALL_BACKENDS


@pytest.fixture(params=ENABLED_BACKENDS)
def create_backend(request, tmp_path):
    def _create_backend():
        return {
            ALL_BACKENDS[0]: InMemoryBackend(Trait.OPTIMIZE_MEMORY),
            ALL_BACKENDS[1]: InMemoryBackend(Trait.OPTIMIZE_PERFORMANCE),
            ALL_BACKENDS[2]: NetworkXBackend(),
            # 'PickleFile': PickleFileBackend(str(tmp_path))
        }[request.param]

    return _create_backend


@pytest.fixture
def create_graph(importer, create_backend):
    def _graph(name, directed=False):
        return importer.read_graph(create_backend(), name, directed)

    return _graph

