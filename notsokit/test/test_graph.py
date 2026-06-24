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

    def test_set_tolerance_tightens_to_infeasible(self):
        """setTolerance can tighten tolerances so a previously-passing check fails."""
        g = notsokit.graph.Graph(2, 1, reltol=0.0, abstol=0.02)
        g.addEdge(0, 1, np.array([1.0]))
        g.setAvoidNodes(np.array([0, 0], dtype=np.uint8))
        heu = np.array([3.0, 1.99], dtype=np.float64)
        self.assertTrue(g.isFeasible(np.array([1.0]), heu))
        g.setTolerance(0.0, 0.0)
        self.assertFalse(g.isFeasible(np.array([1.0]), heu))

    def test_get_tolerance_returns_constructor_values(self):
        """getTolerance returns the reltol and abstol set at construction."""
        g = notsokit.graph.Graph(2, 1, reltol=1e-5, abstol=2e-9)
        self.assertEqual(g.getTolerance(), (1e-5, 2e-9))

    def test_get_tolerance_reflects_set_tolerance(self):
        """getTolerance returns updated values after setTolerance."""
        g = notsokit.graph.Graph(2, 1, reltol=1e-8, abstol=1e-10)
        g.setTolerance(0.5, 0.25)
        self.assertEqual(g.getTolerance(), (0.5, 0.25))


if __name__ == '__main__':
    unittest.main()
