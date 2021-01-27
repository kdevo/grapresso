import pickle

import pytest

from grapresso import DiGraph


class TestTransformations:
    def test_pickling(self, tmp_path, create_backend):
        graph = DiGraph(create_backend())
        graph.add_node('a', test_node_attr=1)
        graph.add_edge('a', 'b', test={'nested': {True}})
        with open(tmp_path.joinpath('test_graph.pkl'), 'wb') as f:
            pickle.dump(graph, f)
        with tmp_path.joinpath('test_graph.pkl').open('rb') as f:
            unpickled_nodes = pickle.load(f)
        assert list(graph.edges()) == list(graph.edges())
        assert unpickled_nodes['a'].data['test_node_attr'] == 1.
        assert True in unpickled_nodes['a'].edge('b').data['test']['nested']
