import unittest
import numpy as np
import notsokit


class TestDijkstra(unittest.TestCase):
    """Test suite for Dijkstra shortest path algorithm."""

    def setUp(self):
        """Set up test graph with 3 nodes and various edge configurations."""
        self.g = notsokit.graph.Graph(3)
        self.g.addEdge(0, 1, np.array([1.0]))
        self.g.addEdge(1, 2, np.array([2.0]))
        self.g.addEdge(0, 2, np.array([3.5]))

    def test_set_weights(self):
        """Test that setting custom edge weights works correctly."""
        g = notsokit.graph.Graph(3)
        g.addEdge(0, 1, np.array([1.0]))
        g.addEdge(1, 2, np.array([2.0]))
        g.setWeights(np.array([[1.0], [2.0]], dtype=np.float64))
        d = notsokit.distance.Dijkstra(g, np.array([1.0]), 0)
        d.run()
        self.assertEqual(d.getDistances().tolist(), [0.0, 1.0, 3.0])

    def _getPath(self, dijkstra):
        """Helper to get paths from all nodes in Dijkstra result."""
        return [dijkstra.getPath(i) for i in range(3)]

    def test_avoid_nodes_blocks_path(self):
        """Test that avoiding a node prevents paths through it."""
        self.g.setWeights(np.array([[1.0], [2.0], [3.5]], dtype=np.float64))
        self.g.setAvoidNodes(np.array([0, 1, 0], dtype=np.uint8))
        d = notsokit.distance.Dijkstra(self.g, np.array([1.0]), 0)
        d.run()
        self.assertEqual(self._getPath(d), [[], [], [2]])

    def test_no_avoidance(self):
        """Test standard shortest paths with no node avoidance."""
        self.g.setWeights(np.array([[1.0], [2.0], [3.5]], dtype=np.float64))
        self.g.setAvoidNodes(np.array([0, 0, 0], dtype=np.uint8))
        d = notsokit.distance.Dijkstra(self.g, np.array([1.0]), 0)
        d.run()
        self.assertEqual(self._getPath(d), [[], [0], [0, 1]])

    def test_custom_weights(self):
        """Test shortest paths with custom edge weights."""
        self.g.setWeights(np.array([[1.0], [2.0], [2.5]], dtype=np.float64))
        self.g.setAvoidNodes(np.array([0, 0, 0], dtype=np.uint8))
        d = notsokit.distance.Dijkstra(self.g, np.array([1.0]), 0)
        d.run()
        self.assertEqual(self._getPath(d), [[], [0], [2]])

    def test_infinite_weight_blocks_edge(self):
        """Test that infinite edge weights block paths."""
        self.g.setWeights(np.array([[float('inf')], [2.0], [2.5]], dtype=np.float64))
        self.g.setAvoidNodes(np.array([0, 0, 0], dtype=np.uint8))
        d = notsokit.distance.Dijkstra(self.g, np.array([1.0]), 0)
        d.run()
        self.assertEqual(self._getPath(d), [[], [], [2]])

    def test_heuristic_feasibility(self):
        """Test feasibility check for heuristic values."""
        self.g.setWeights(np.array([[1.0], [2.0], [3.5]], dtype=np.float64))
        self.g.setAvoidNodes(np.array([0, 0, 0], dtype=np.uint8))
        heuristic = np.array([1, 10, 1], dtype=np.float64)
        self.assertFalse(self.g.isFeasible(np.array([1.0]), heuristic))

    def test_astar_matches_dijkstra(self):
        """Test that A* with zero heuristic matches Dijkstra."""
        # Create a larger 10-node graph
        g = notsokit.graph.Graph(10)
        g.addEdge(0, 1, np.array([1.0]))
        g.addEdge(1, 2, np.array([2.0]))
        g.addEdge(0, 2, np.array([3.5]))
        g.addEdge(2, 3, np.array([1.5]))
        g.addEdge(1, 4, np.array([4.0]))
        g.addEdge(4, 3, np.array([2.0]))
        g.addEdge(3, 5, np.array([1.0]))
        g.addEdge(5, 6, np.array([2.5]))
        g.addEdge(2, 6, np.array([5.0]))
        g.addEdge(4, 7, np.array([3.0]))
        g.addEdge(7, 6, np.array([1.5]))

        # Zero heuristic means A* behaves like Dijkstra
        heu = np.zeros(10, dtype=np.float64)
        a = notsokit.distance.AStarAdaptive(g, np.array([1.0]), heu, 0, 6)
        a.run()

        d = notsokit.distance.Dijkstra(g, np.array([1.0]), 0)
        d.run()

        # A* path to 6 should match Dijkstra's path to 6
        self.assertEqual(a.getPath(), d.getPath(6))

    def test_distance_feasibility(self):
        """Test feasibility of computed shortest path distances."""
        # Create a larger 10-node graph
        g = notsokit.graph.Graph(10)
        g.addEdge(0, 1, np.array([1.0]))
        g.addEdge(1, 2, np.array([2.0]))
        g.addEdge(0, 2, np.array([3.5]))
        g.addEdge(2, 3, np.array([1.5]))
        g.addEdge(1, 4, np.array([4.0]))
        g.addEdge(4, 3, np.array([2.0]))
        g.addEdge(3, 5, np.array([1.0]))
        g.addEdge(5, 6, np.array([2.5]))
        g.addEdge(2, 6, np.array([5.0]))
        g.addEdge(4, 7, np.array([3.0]))
        g.addEdge(7, 6, np.array([1.5]))

        d = notsokit.distance.Dijkstra(g, np.array([1.0]), 0)
        d.run()

        dists = d.getDistances()
        # Shortest path distances should be feasible
        self.assertTrue(g.isFeasible(np.array([1.0]), dists))


if __name__ == '__main__':
    unittest.main()
