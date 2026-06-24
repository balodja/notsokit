import os
import tempfile
import unittest
import numpy as np
import notsokit
from notsokit.io import read_graph, write_graph, read_heuristics, write_heuristics


class TestIO(unittest.TestCase):
    """Test suite for graph CSV read/write."""

    def _make_graph(self):
        g = notsokit.graph.Graph(4)
        g.addEdge(0, 1, np.array([1.0]))
        g.addEdge(1, 2, np.array([2.5]))
        g.addEdge(0, 3, np.array([4.0]))
        g.addEdge(3, 2, np.array([1.5]))
        g.setAvoidNodes(np.array([0, 0, 0, 0], dtype=np.uint8))
        return g

    def test_roundtrip_node_count(self):
        """Roundtrip preserves node count."""
        g = self._make_graph()
        with tempfile.TemporaryDirectory() as d:
            write_graph(g, os.path.join(d, 'nodes.csv'), os.path.join(d, 'edges.csv'))
            g2 = read_graph(os.path.join(d, 'nodes.csv'), os.path.join(d, 'edges.csv'))
        self.assertEqual(g2.upperNodeIdBound(), g.upperNodeIdBound())

    def test_roundtrip_edge_count(self):
        """Roundtrip preserves edge count."""
        g = self._make_graph()
        with tempfile.TemporaryDirectory() as d:
            write_graph(g, os.path.join(d, 'nodes.csv'), os.path.join(d, 'edges.csv'))
            g2 = read_graph(os.path.join(d, 'nodes.csv'), os.path.join(d, 'edges.csv'))
        self.assertEqual(g2.upperEdgeIdBound(), g.upperEdgeIdBound())

    def test_roundtrip_distances(self):
        """Shortest paths computed on a roundtripped graph match the original."""
        g = self._make_graph()
        with tempfile.TemporaryDirectory() as d:
            write_graph(g, os.path.join(d, 'nodes.csv'), os.path.join(d, 'edges.csv'))
            g2 = read_graph(os.path.join(d, 'nodes.csv'), os.path.join(d, 'edges.csv'))

        d1 = notsokit.distance.Dijkstra(g, 0)
        d1.run()
        d2 = notsokit.distance.Dijkstra(g2, 0)
        d2.run()
        self.assertEqual(d1.getDistances().tolist(), d2.getDistances().tolist())

    def test_roundtrip_avoid_nodes(self):
        """Avoid flags are preserved through roundtrip."""
        g = notsokit.graph.Graph(3)
        g.addEdge(0, 1, np.array([1.0]))
        g.addEdge(1, 2, np.array([1.0]))
        g.addEdge(0, 2, np.array([3.0]))
        g.setAvoidNodes(np.array([0, 1, 0], dtype=np.uint8))

        with tempfile.TemporaryDirectory() as d:
            write_graph(g, os.path.join(d, 'nodes.csv'), os.path.join(d, 'edges.csv'))
            g2 = read_graph(os.path.join(d, 'nodes.csv'), os.path.join(d, 'edges.csv'))

        # With node 1 avoided, only the direct 0->2 edge was written.
        # In the reconstructed graph it gets edge id 0.
        d2 = notsokit.distance.Dijkstra(g2, 0)
        d2.run()
        self.assertEqual(d2.getPath(2), [0])

    def test_nodes_csv_format(self):
        """nodes.csv has expected header and one row per node."""
        g = notsokit.graph.Graph(3)
        g.addEdge(0, 1, np.array([1.0]))
        g.setAvoidNodes(np.array([0, 0, 0], dtype=np.uint8))
        with tempfile.TemporaryDirectory() as d:
            nodes_path = os.path.join(d, 'nodes.csv')
            write_graph(g, nodes_path, os.path.join(d, 'edges.csv'))
            with open(nodes_path) as f:
                lines = f.read().splitlines()
        self.assertEqual(lines[0], 'node_id,avoid')
        self.assertEqual(len(lines), 4)  # header + 3 nodes

    def test_edges_csv_format(self):
        """edges.csv has expected header and one row per edge."""
        g = notsokit.graph.Graph(3)
        g.addEdge(0, 1, np.array([1.0]))
        g.addEdge(1, 2, np.array([2.0]))
        g.setAvoidNodes(np.array([0, 0, 0], dtype=np.uint8))
        with tempfile.TemporaryDirectory() as d:
            edges_path = os.path.join(d, 'edges.csv')
            write_graph(g, os.path.join(d, 'nodes.csv'), edges_path)
            with open(edges_path) as f:
                lines = f.read().splitlines()
        self.assertEqual(lines[0], 'from,to,weight')
        self.assertEqual(len(lines), 3)  # header + 2 edges


class TestHeuristicsIO(unittest.TestCase):
    """Test suite for heuristics CSV read/write."""

    def _make_heuristics(self):
        return np.array([0.0, 1.5, 3.0, 2.25], dtype=np.float64)

    def test_roundtrip_values(self):
        """Roundtrip preserves all heuristic values."""
        heu = self._make_heuristics()
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, 'heu.csv')
            write_heuristics(heu, path)
            heu2 = read_heuristics(path)
        np.testing.assert_array_equal(heu, heu2)

    def test_roundtrip_length(self):
        """Roundtrip preserves array length."""
        heu = self._make_heuristics()
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, 'heu.csv')
            write_heuristics(heu, path)
            heu2 = read_heuristics(path)
        self.assertEqual(len(heu2), len(heu))

    def test_csv_format(self):
        """heu.csv has expected header and one row per node."""
        heu = self._make_heuristics()
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, 'heu.csv')
            write_heuristics(heu, path)
            with open(path) as f:
                lines = f.read().splitlines()
        self.assertEqual(lines[0], 'node_id,heuristic')
        self.assertEqual(len(lines), len(heu) + 1)  # header + one row per node

    def test_csv_node_ids(self):
        """node_id column contains sequential integers starting from 0."""
        heu = self._make_heuristics()
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, 'heu.csv')
            write_heuristics(heu, path)
            with open(path) as f:
                lines = f.read().splitlines()
        for i, line in enumerate(lines[1:]):
            node_id = int(line.split(',')[0])
            self.assertEqual(node_id, i)

    def test_precision(self):
        """Full double precision is preserved through roundtrip."""
        heu = np.array([1.0 / 3.0, np.pi], dtype=np.float64)
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, 'heu.csv')
            write_heuristics(heu, path)
            heu2 = read_heuristics(path)
        np.testing.assert_array_equal(heu, heu2)

    def test_empty(self):
        """Empty heuristics array roundtrips correctly."""
        heu = np.array([], dtype=np.float64)
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, 'heu.csv')
            write_heuristics(heu, path)
            heu2 = read_heuristics(path)
        self.assertEqual(len(heu2), 0)


if __name__ == '__main__':
    unittest.main()
