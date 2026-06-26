import unittest
import numpy as np
import notsokit


def make_graph():
    """Diamond graph: 0->1 (w=1), 0->2 (w=2), 1->3 (w=3), 2->3 (w=4)."""
    g = notsokit.graph.Graph(4)
    g.addEdge(0, 1, np.array([1.0]))
    g.addEdge(0, 2, np.array([2.0]))
    g.addEdge(1, 3, np.array([3.0]))
    g.addEdge(2, 3, np.array([4.0]))
    return g


class TestCompressorFromLists(unittest.TestCase):
    """Compressor(nds, eds) — explicit node and edge lists."""

    def test_mapNode_unmapNode_roundtrip(self):
        c = notsokit.compress.Compressor([10, 20, 30], [0, 1])
        for i in range(3):
            self.assertEqual(c.mapNode(c.unmapNode(i)), i)

    def test_unmapNode_gives_original_id(self):
        c = notsokit.compress.Compressor([10, 20, 30], [])
        self.assertEqual(c.unmapNode(0), 10)
        self.assertEqual(c.unmapNode(1), 20)
        self.assertEqual(c.unmapNode(2), 30)

    def test_mapNode_gives_compressed_index(self):
        c = notsokit.compress.Compressor([10, 20, 30], [])
        self.assertEqual(c.mapNode(10), 0)
        self.assertEqual(c.mapNode(20), 1)
        self.assertEqual(c.mapNode(30), 2)

    def test_mapEdge_unmapEdge_roundtrip(self):
        c = notsokit.compress.Compressor([0, 1], [5, 7])
        for i in range(2):
            self.assertEqual(c.mapEdge(c.unmapEdge(i)), i)

    def test_unmapEdge_gives_original_id(self):
        c = notsokit.compress.Compressor([0, 1], [5, 7])
        self.assertEqual(c.unmapEdge(0), 5)
        self.assertEqual(c.unmapEdge(1), 7)

    def test_mapNode_missing_raises(self):
        c = notsokit.compress.Compressor([10, 20], [])
        with self.assertRaises((KeyError, Exception)):
            c.mapNode(99)

    def test_unmapNode_oob_raises(self):
        c = notsokit.compress.Compressor([10, 20], [])
        with self.assertRaises((IndexError, Exception)):
            c.unmapNode(5)

    def test_mapEdge_missing_raises(self):
        c = notsokit.compress.Compressor([0], [42])
        with self.assertRaises((KeyError, Exception)):
            c.mapEdge(99)

    def test_unmapEdge_oob_raises(self):
        c = notsokit.compress.Compressor([0], [42])
        with self.assertRaises((IndexError, Exception)):
            c.unmapEdge(5)


class TestCompressorFromGraph(unittest.TestCase):
    """Compressor(graph, nds) — edges derived from graph."""

    def test_nodes_mapped_correctly(self):
        g = make_graph()
        c = notsokit.compress.Compressor(g, [0, 1, 3])
        self.assertEqual(c.mapNode(0), 0)
        self.assertEqual(c.mapNode(1), 1)
        self.assertEqual(c.mapNode(3), 2)

    def test_included_edge_is_mapped(self):
        """Edge 0->1 (edge 0) should be present when both endpoints are in nds."""
        g = make_graph()
        c = notsokit.compress.Compressor(g, [0, 1, 3])
        # edge 0 (0->1) and edge 2 (1->3) are fully within the subgraph
        self.assertEqual(c.unmapEdge(c.mapEdge(0)), 0)
        self.assertEqual(c.unmapEdge(c.mapEdge(2)), 2)

    def test_excluded_edge_not_mapped(self):
        """Edge 1 (0->2): node 2 not in nds, so edge must be absent."""
        g = make_graph()
        c = notsokit.compress.Compressor(g, [0, 1, 3])
        with self.assertRaises((KeyError, Exception)):
            c.mapEdge(1)

    def test_unmapped_node_not_accessible(self):
        g = make_graph()
        c = notsokit.compress.Compressor(g, [0, 1])
        with self.assertRaises((KeyError, Exception)):
            c.mapNode(3)


class TestMapGraph(unittest.TestCase):
    """Compressor.mapGraph produces the correct subgraph."""

    def test_node_count(self):
        g = make_graph()
        c = notsokit.compress.Compressor(g, [0, 1, 3])
        sub = c.mapGraph(g)
        self.assertEqual(sub.upperNodeIdBound(), 3)

    def test_edge_count(self):
        """Subgraph over {0,1,3} should have edges 0->1 and 1->3 only."""
        g = make_graph()
        c = notsokit.compress.Compressor(g, [0, 1, 3])
        sub = c.mapGraph(g)
        self.assertEqual(sub.upperEdgeIdBound(), 2)

    def test_full_subgraph_matches_original(self):
        """Compressing with all nodes yields a graph with the same edge count."""
        g = make_graph()
        c = notsokit.compress.Compressor(g, [0, 1, 2, 3])
        sub = c.mapGraph(g)
        self.assertEqual(sub.upperEdgeIdBound(), g.upperEdgeIdBound())

    def test_single_node_subgraph_has_no_edges(self):
        g = make_graph()
        c = notsokit.compress.Compressor(g, [0])
        sub = c.mapGraph(g)
        self.assertEqual(sub.upperEdgeIdBound(), 0)


class TestCompressorComposition(unittest.TestCase):
    """operator* composes two compressors."""

    def test_compose_identity(self):
        """Composing with an identity-renaming c2 leaves nodeUnmap unchanged."""
        # c1: compressed {0,1} → original {5, 3}
        c1 = notsokit.compress.Compressor([5, 3], [7, 2])
        # c2 acts as identity lookup covering indices 0..7
        c2 = notsokit.compress.Compressor(list(range(8)), list(range(8)))
        composed = c1 * c2
        self.assertEqual(composed.unmapNode(0), 5)  # c2.unmapNode(5) = 5
        self.assertEqual(composed.unmapNode(1), 3)  # c2.unmapNode(3) = 3
        self.assertEqual(composed.unmapEdge(0), 7)  # c2.unmapEdge(7) = 7
        self.assertEqual(composed.unmapEdge(1), 2)  # c2.unmapEdge(2) = 2

    def test_compose_two_compressors(self):
        """c1 maps {0->5, 1->3}; c2 maps index 0->5, 1->3 of c1 back out.
        Actually: c2.unmapNode(u) where u in c1.nodeUnmap.
        c1.nodeUnmap=[5,3], c2 must have nodeUnmap[5] and nodeUnmap[3].
        Build c2 with nodeUnmap big enough: [0,1,2,3,4,99].
        Then (c1*c2).unmapNode(0) = c2.unmapNode(5) = 99."""
        # c1: compressed indices 0,1 correspond to original nodes 1,2
        c1 = notsokit.compress.Compressor([1, 2], [0, 1])
        # c2: node unmap must cover indices 1 and 2
        # nodeUnmap[1]=10, nodeUnmap[2]=20
        c2 = notsokit.compress.Compressor([0, 10, 20], [5, 6])
        composed = c1 * c2
        self.assertEqual(composed.unmapNode(0), 10)  # c2.unmapNode(1)
        self.assertEqual(composed.unmapNode(1), 20)  # c2.unmapNode(2)
        self.assertEqual(composed.unmapEdge(0), 5)   # c2.unmapEdge(0)
        self.assertEqual(composed.unmapEdge(1), 6)   # c2.unmapEdge(1)

    def test_compose_oob_raises(self):
        """Composing when other's nodeUnmap is too small raises."""
        c1 = notsokit.compress.Compressor([5, 3], [])
        c2 = notsokit.compress.Compressor([0, 1], [])  # size 2; indices 5,3 OOB
        with self.assertRaises((IndexError, Exception)):
            _ = c1 * c2

    def test_compose_graph_subgraph(self):
        """Compose a subgraph compressor with a full-graph compressor."""
        g = make_graph()
        # c1: keep nodes {0,1,3} — c1.nodeUnmap = [0,1,3]
        c1 = notsokit.compress.Compressor(g, [0, 1, 3])
        # c2: full graph, acts as identity lookup for indices 0..3
        c2 = notsokit.compress.Compressor(g, [0, 1, 2, 3])
        composed = c1 * c2
        sub = composed.mapGraph(g)
        self.assertEqual(sub.upperNodeIdBound(), 3)
        self.assertEqual(sub.upperEdgeIdBound(), 2)


class TestZeroEdges(unittest.TestCase):
    """Test suite for graph.zeroEdges."""

    def test_empty_graph_returns_empty(self):
        """A graph with no edges produces an empty result."""
        g = notsokit.graph.Graph(5)
        result = notsokit.compress.zeroEdges(g)
        self.assertEqual(result.upperEdgeIdBound(), 0)

    def test_no_zero_weight_edges(self):
        """A graph with only positive-weight edges produces an empty result."""
        g = notsokit.graph.Graph(3)
        g.addEdge(0, 1, np.array([1.0]))
        g.addEdge(1, 2, np.array([2.0]))
        result = notsokit.compress.zeroEdges(g)
        self.assertEqual(result.upperEdgeIdBound(), 0)

    def test_all_zero_weight_edges(self):
        """All zero-weight edges are kept."""
        g = notsokit.graph.Graph(3)
        g.addEdge(0, 1, np.array([0.0]))
        g.addEdge(1, 2, np.array([0.0]))
        result = notsokit.compress.zeroEdges(g)
        self.assertEqual(result.upperEdgeIdBound(), 2)

    def test_mixed_edges_only_zero_kept(self):
        """Only the zero-weight edges are present in the result."""
        g = notsokit.graph.Graph(4)
        g.addEdge(0, 1, np.array([0.0]))
        g.addEdge(1, 2, np.array([5.0]))
        g.addEdge(2, 3, np.array([0.0]))
        g.addEdge(3, 0, np.array([3.0]))
        result = notsokit.compress.zeroEdges(g)
        self.assertEqual(result.upperEdgeIdBound(), 2)

    def test_result_has_unit_weight(self):
        """Edges in the result graph have weight 1.0 regardless of original."""
        g = notsokit.graph.Graph(2)
        g.addEdge(0, 1, np.array([0.0]))
        result = notsokit.compress.zeroEdges(g)
        self.assertEqual(result.numDims(), 1)
        self.assertTrue(result.isFeasible(np.array([1.0]), np.array([0.0, 0.0])))

    def test_result_node_bound_matches_input(self):
        """The result graph has the same node id bound as the input."""
        g = notsokit.graph.Graph(10)
        g.addEdge(0, 9, np.array([0.0]))
        result = notsokit.compress.zeroEdges(g)
        self.assertEqual(result.upperNodeIdBound(), g.upperNodeIdBound())

    def test_multidim_zero_by_uniform_wc(self):
        """Multi-dim edge with all-zero weights is included."""
        g = notsokit.graph.Graph(2, 3)
        g.addEdge(0, 1, np.array([0.0, 0.0, 0.0]))
        result = notsokit.compress.zeroEdges(g)
        self.assertEqual(result.upperEdgeIdBound(), 1)

    def test_multidim_nonzero_excluded(self):
        """Multi-dim edge whose dot-product with uniform wc is nonzero is excluded."""
        g = notsokit.graph.Graph(2, 3)
        g.addEdge(0, 1, np.array([0.0, 1.0, 0.0]))
        result = notsokit.compress.zeroEdges(g)
        self.assertEqual(result.upperEdgeIdBound(), 0)

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


if __name__ == "__main__":
    unittest.main()
