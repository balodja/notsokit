import unittest
import numpy as np
import notsokit


class TestIsFeasible(unittest.TestCase):
    """Test suite for Graph.isFeasible."""

    def _make_graph(self):
        """Triangle graph: 0->1 (w=1), 1->2 (w=2), 0->2 (w=4)."""
        g = notsokit.graph.Graph(3)
        g.addEdge(0, 1, np.array([1.0]))
        g.addEdge(1, 2, np.array([2.0]))
        g.addEdge(0, 2, np.array([4.0]))
        g.setAvoidNodes(np.array([0, 0, 0], dtype=np.uint8))
        return g

    def test_feasible_zero_heuristic(self):
        """Zero heuristic is always feasible."""
        g = self._make_graph()
        heu = np.zeros(3, dtype=np.float64)
        self.assertTrue(g.isFeasible(np.array([1.0]), heu))

    def test_feasible_exact_distances(self):
        """Exact shortest-path distances from source 0 are feasible."""
        g = self._make_graph()
        # Shortest distances from 0: d[0]=0, d[1]=1, d[2]=3
        heu = np.array([0.0, 1.0, 3.0], dtype=np.float64)
        self.assertTrue(g.isFeasible(np.array([1.0]), heu))

    def test_feasible_underestimate(self):
        """Heuristic that strictly underestimates all distances is feasible."""
        g = self._make_graph()
        heu = np.array([0.0, 0.5, 2.0], dtype=np.float64)
        self.assertTrue(g.isFeasible(np.array([1.0]), heu))

    def test_infeasible_overestimate(self):
        """Heuristic that overestimates along an edge is infeasible."""
        g = self._make_graph()
        # heu[1]=10 violates: w(0->1) + heu[1]=11 > heu[0]=0
        heu = np.array([0.0, 10.0, 3.0], dtype=np.float64)
        self.assertFalse(g.isFeasible(np.array([1.0]), heu))

    def test_infeasible_single_violated_edge(self):
        """Infeasibility from a single violated edge is detected."""
        g = self._make_graph()
        # w(1->2)=2, heu[2]=1 but heu[1]=4: 2+1=3 < 4, violates consistency
        heu = np.array([0.0, 4.0, 1.0], dtype=np.float64)
        self.assertFalse(g.isFeasible(np.array([1.0]), heu))

    def test_feasible_with_weight_coefficients(self):
        """Multi-dimensional graph: feasibility respects wc scaling."""
        g = notsokit.graph.Graph(3, 2)
        g.addEdge(0, 1, np.array([1.0, 0.0]))
        g.addEdge(1, 2, np.array([0.0, 2.0]))
        g.addEdge(0, 2, np.array([1.0, 2.0]))
        g.setAvoidNodes(np.array([0, 0, 0], dtype=np.uint8))
        # wc=[1,0]: effective weights are 1, 0, 1 -> distances from 0: 0, 1, 1
        heu = np.array([0.0, 1.0, 1.0], dtype=np.float64)
        self.assertTrue(g.isFeasible(np.array([1.0, 0.0]), heu))

    def test_infeasible_with_weight_coefficients(self):
        """Multi-dimensional graph: infeasibility detected under wc scaling."""
        g = notsokit.graph.Graph(3, 2)
        g.addEdge(0, 1, np.array([1.0, 0.0]))
        g.addEdge(1, 2, np.array([0.0, 2.0]))
        g.addEdge(0, 2, np.array([1.0, 2.0]))
        g.setAvoidNodes(np.array([0, 0, 0], dtype=np.uint8))
        # wc=[0,1]: effective weights are 0, 2, 2
        # heu[1]=5 violates: w(0->1)=0, heu[2]=2, but 0+5=5 > 0 is fine;
        # but w(1->2)+heu[2] = 2+2=4 < heu[1]=5, so infeasible
        heu = np.array([0.0, 5.0, 2.0], dtype=np.float64)
        self.assertFalse(g.isFeasible(np.array([0.0, 1.0]), heu))

    def test_abstol_makes_near_violation_feasible(self):
        """A heuristic slightly off by less than abstol is considered feasible."""
        # Edge 0->1 w=1.0; heu[0]=3.0, heu[1]=1.99 → w+heu[1]=2.99, diff=0.01
        # With abstol=0 this is infeasible; with abstol=0.02 it is feasible.
        g = notsokit.graph.Graph(2, 1, reltol=0.0, abstol=0.02)
        g.addEdge(0, 1, np.array([1.0]))
        g.setAvoidNodes(np.array([0, 0], dtype=np.uint8))
        heu = np.array([3.0, 1.99], dtype=np.float64)
        self.assertTrue(g.isFeasible(np.array([1.0]), heu))

    def test_abstol_zero_catches_near_violation(self):
        """Same heuristic is infeasible when abstol=0."""
        g = notsokit.graph.Graph(2, 1, reltol=0.0, abstol=0.0)
        g.addEdge(0, 1, np.array([1.0]))
        g.setAvoidNodes(np.array([0, 0], dtype=np.uint8))
        heu = np.array([3.0, 1.99], dtype=np.float64)
        self.assertFalse(g.isFeasible(np.array([1.0]), heu))

    def test_reltol_makes_near_violation_feasible(self):
        """A heuristic slightly off by less than reltol*max(|a|,|b|) is feasible."""
        # Edge 0->1 w=1.0; heu[0]=100.0, heu[1]=98.9 → w+heu[1]=99.9, diff=0.1
        # reltol=0.01: 0.01 * max(99.9, 100.0) = 1.0 >= 0.1 → feasible
        g = notsokit.graph.Graph(2, 1, reltol=0.01, abstol=0.0)
        g.addEdge(0, 1, np.array([1.0]))
        g.setAvoidNodes(np.array([0, 0], dtype=np.uint8))
        heu = np.array([100.0, 98.9], dtype=np.float64)
        self.assertTrue(g.isFeasible(np.array([1.0]), heu))

    def test_reltol_zero_catches_near_violation(self):
        """Same heuristic is infeasible when reltol=0 and abstol=0."""
        g = notsokit.graph.Graph(2, 1, reltol=0.0, abstol=0.0)
        g.addEdge(0, 1, np.array([1.0]))
        g.setAvoidNodes(np.array([0, 0], dtype=np.uint8))
        heu = np.array([100.0, 98.9], dtype=np.float64)
        self.assertFalse(g.isFeasible(np.array([1.0]), heu))

    def test_set_tolerance_relaxes_to_feasible(self):
        """setTolerance can loosen tolerances so a near-violation becomes feasible."""
        g = notsokit.graph.Graph(2, 1, reltol=0.0, abstol=0.0)
        g.addEdge(0, 1, np.array([1.0]))
        g.setAvoidNodes(np.array([0, 0], dtype=np.uint8))
        heu = np.array([3.0, 1.99], dtype=np.float64)
        self.assertFalse(g.isFeasible(np.array([1.0]), heu))
        g.setTolerance(0.0, 0.02)
        self.assertTrue(g.isFeasible(np.array([1.0]), heu))


class TestGetPathWeights(unittest.TestCase):
    """Test suite for Graph.getPathWeights."""

    def _make_graph(self):
        """Triangle graph: 0->1 (e0, w=1), 1->2 (e1, w=2), 0->2 (e2, w=4)."""
        g = notsokit.graph.Graph(3)
        g.addEdge(0, 1, np.array([1.0]))
        g.addEdge(1, 2, np.array([2.0]))
        g.addEdge(0, 2, np.array([4.0]))
        return g

    def test_single_edge(self):
        """Path of one edge returns that edge's weight."""
        g = self._make_graph()
        result = g.getPathWeights([0])
        np.testing.assert_array_almost_equal(result, [1.0])

    def test_two_edge_path(self):
        """Path 0->1->2 sums weights of edges 0 and 1."""
        g = self._make_graph()
        result = g.getPathWeights([0, 1])
        np.testing.assert_array_almost_equal(result, [3.0])

    def test_single_edge_alternative(self):
        """Direct edge 0->2 (e2) has weight 4."""
        g = self._make_graph()
        result = g.getPathWeights([2])
        np.testing.assert_array_almost_equal(result, [4.0])

    def test_empty_path(self):
        """Empty path returns zero weights."""
        g = self._make_graph()
        result = g.getPathWeights([])
        np.testing.assert_array_almost_equal(result, [0.0])

    def test_multidim_path(self):
        """Multi-dimensional weights are summed per dimension."""
        g = notsokit.graph.Graph(3, 2)
        g.addEdge(0, 1, np.array([1.0, 10.0]))
        g.addEdge(1, 2, np.array([2.0, 20.0]))
        result = g.getPathWeights([0, 1])
        np.testing.assert_array_almost_equal(result, [3.0, 30.0])


class TestGetEdges(unittest.TestCase):
    """Test suite for Graph.getEdges."""

    def _make_graph(self):
        """Graph: 0->1 (e0), 0->1 (e1, parallel), 0->2 (e2), 1->2 (e3)."""
        g = notsokit.graph.Graph(3)
        g.addEdge(0, 1, np.array([1.0]))
        g.addEdge(0, 1, np.array([2.0]))
        g.addEdge(0, 2, np.array([4.0]))
        g.addEdge(1, 2, np.array([3.0]))
        return g

    def test_single_edge(self):
        g = self._make_graph()
        self.assertEqual(g.getEdges(0, 2), [2])

    def test_parallel_edges(self):
        g = self._make_graph()
        self.assertEqual(g.getEdges(0, 1), [0, 1])

    def test_no_edge(self):
        g = self._make_graph()
        self.assertEqual(g.getEdges(1, 0), [])

    def test_self_loop_absent(self):
        g = self._make_graph()
        self.assertEqual(g.getEdges(0, 0), [])


class TestSetWeights(unittest.TestCase):
    """Test suite for Graph.setWeights."""

    def test_setWeights_replaces_all_weights(self):
        g = notsokit.graph.Graph(2)
        g.addEdge(0, 1, np.array([1.0]))
        g.addEdge(0, 1, np.array([2.0]))
        new_weights = np.array([[10.0], [20.0]], dtype=np.float64)
        g.setWeights(new_weights)
        wc = np.array([1.0])
        self.assertAlmostEqual(g.getWeight(0, wc), 10.0)
        self.assertAlmostEqual(g.getWeight(1, wc), 20.0)

    def test_setWeights_wrong_shape_raises(self):
        g = notsokit.graph.Graph(2)
        g.addEdge(0, 1, np.array([1.0]))
        with self.assertRaises(ValueError):
            g.setWeights(np.array([[1.0, 2.0]], dtype=np.float64))


class TestGetWeights(unittest.TestCase):
    """Test suite for Graph.getWeights."""

    def test_single_dim(self):
        """Returns the single weight for a 1-D edge."""
        g = notsokit.graph.Graph(2)
        g.addEdge(0, 1, np.array([7.0]))
        np.testing.assert_array_almost_equal(g.getWeights(0), [7.0])

    def test_multidim(self):
        """Returns all dimensions for a multi-dimensional edge."""
        g = notsokit.graph.Graph(2, 3)
        g.addEdge(0, 1, np.array([1.0, 2.0, 3.0]))
        np.testing.assert_array_almost_equal(g.getWeights(0), [1.0, 2.0, 3.0])

    def test_multiple_edges(self):
        """Each edge has independent weights."""
        g = notsokit.graph.Graph(3, 2)
        g.addEdge(0, 1, np.array([1.0, 2.0]))
        g.addEdge(1, 2, np.array([3.0, 4.0]))
        np.testing.assert_array_almost_equal(g.getWeights(0), [1.0, 2.0])
        np.testing.assert_array_almost_equal(g.getWeights(1), [3.0, 4.0])

    def test_after_setWeights(self):
        """getWeights reflects updated weights after setWeights."""
        g = notsokit.graph.Graph(2)
        g.addEdge(0, 1, np.array([1.0]))
        g.setWeights(np.array([[99.0]], dtype=np.float64))
        np.testing.assert_array_almost_equal(g.getWeights(0), [99.0])


class TestGetWeight(unittest.TestCase):
    """Test suite for Graph.getWeight."""

    def _make_graph(self):
        """Graph: 0->1 (w=[1,2]), 1->2 (w=[3,4])."""
        g = notsokit.graph.Graph(3, 2)
        g.addEdge(0, 1, np.array([1.0, 2.0]))
        g.addEdge(1, 2, np.array([3.0, 4.0]))
        return g

    def test_single_dim_weight(self):
        g = notsokit.graph.Graph(2)
        g.addEdge(0, 1, np.array([5.0]))
        self.assertAlmostEqual(g.getWeight(0, np.array([1.0])), 5.0)

    def test_multidim_dot_product(self):
        g = self._make_graph()
        # edge 0: wc=[1,1] -> 1*1 + 1*2 = 3
        self.assertAlmostEqual(g.getWeight(0, np.array([1.0, 1.0])), 3.0)

    def test_multidim_scaled(self):
        g = self._make_graph()
        # edge 1: wc=[2,0] -> 2*3 + 0*4 = 6
        self.assertAlmostEqual(g.getWeight(1, np.array([2.0, 0.0])), 6.0)

    def test_wrong_wc_size_raises(self):
        g = self._make_graph()
        with self.assertRaises(ValueError):
            g.getWeight(0, np.array([1.0]))


if __name__ == '__main__':
    unittest.main()
