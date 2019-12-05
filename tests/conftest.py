import pytest

from grapresso.backend.file import PickleFileBackend
from grapresso.backend.memory import InMemoryBackend, Trait

ALL_BACKENDS = ('InMemory-OptimizeMemory', 'InMemory-OptimizePerformance', 'PickleFile')
ENABLED_BACKENDS = ALL_BACKENDS


@pytest.fixture(params=ENABLED_BACKENDS)
def create_backend(request, tmp_path):
    def _create_backend():
        return {'InMemory-OptimizeMemory': InMemoryBackend(Trait.OPTIMIZE_MEMORY),
                'InMemory-OptimizePerformance': InMemoryBackend(Trait.OPTIMIZE_PERFORMANCE),
                'PickleFile': PickleFileBackend(str(tmp_path))}[request.param]

    return _create_backend



@pytest.fixture
def create_graph(importer, create_backend):
    def _graph(name, directed=False):
        return importer.read_graph(create_backend(), name, directed)

    return _graph

# @pytest.fixture(autouse=True, scope="class")
# def reset_backends_to_use():
#     global test_backends
#     print("Backends to use for testing are: ", test_backends)
#     yield
#     test_backends = ALL_BACKENDS
#     print("Reset backends to default: ", test_backends)
