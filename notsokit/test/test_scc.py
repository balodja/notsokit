import unittest
import numpy as np
import notsokit


def make_graph(n, edges):
	g = notsokit.graph.Graph(n)
	for u, v in edges:
		g.addEdge(u, v, np.array([1.0]))
	return g


class TestSCCSingleNode(unittest.TestCase):
	def test_single_node(self):
		g = make_graph(1, [])
		scc = notsokit.scc.SCC(g).run()
		self.assertEqual(scc.getNumComponents(), 1)
		self.assertEqual(scc.getComponent(0), 0)
		self.assertEqual(scc.getComponentSize(0), 1)


class TestSCCLinear(unittest.TestCase):
	"""A -> B -> C: three singleton SCCs."""

	def setUp(self):
		self.g = make_graph(3, [(0, 1), (1, 2)])
		self.scc = notsokit.scc.SCC(self.g).run()

	def test_num_components(self):
		self.assertEqual(self.scc.getNumComponents(), 3)

	def test_all_different_components(self):
		comps = {self.scc.getComponent(i) for i in range(3)}
		self.assertEqual(len(comps), 3)

	def test_component_sizes_are_one(self):
		for i in range(3):
			c = self.scc.getComponent(i)
			self.assertEqual(self.scc.getComponentSize(c), 1)


class TestSCCCycle(unittest.TestCase):
	"""A -> B -> C -> A: one SCC of size 3."""

	def setUp(self):
		self.g = make_graph(3, [(0, 1), (1, 2), (2, 0)])
		self.scc = notsokit.scc.SCC(self.g).run()

	def test_num_components(self):
		self.assertEqual(self.scc.getNumComponents(), 1)

	def test_all_same_component(self):
		c0 = self.scc.getComponent(0)
		self.assertEqual(self.scc.getComponent(1), c0)
		self.assertEqual(self.scc.getComponent(2), c0)

	def test_component_size(self):
		c = self.scc.getComponent(0)
		self.assertEqual(self.scc.getComponentSize(c), 3)


class TestSCCTwoComponents(unittest.TestCase):
	"""0<->1  2<->3, with 1->2 connecting them (but not back)."""

	def setUp(self):
		# 0 <-> 1 form one SCC, 2 <-> 3 form another
		self.g = make_graph(4, [(0, 1), (1, 0), (2, 3), (3, 2), (1, 2)])
		self.scc = notsokit.scc.SCC(self.g).run()

	def test_num_components(self):
		self.assertEqual(self.scc.getNumComponents(), 2)

	def test_nodes_01_same_component(self):
		self.assertEqual(self.scc.getComponent(0), self.scc.getComponent(1))

	def test_nodes_23_same_component(self):
		self.assertEqual(self.scc.getComponent(2), self.scc.getComponent(3))

	def test_nodes_01_differ_from_23(self):
		self.assertNotEqual(self.scc.getComponent(0), self.scc.getComponent(2))

	def test_component_sizes(self):
		c01 = self.scc.getComponent(0)
		c23 = self.scc.getComponent(2)
		self.assertEqual(self.scc.getComponentSize(c01), 2)
		self.assertEqual(self.scc.getComponentSize(c23), 2)


class TestSCCMixed(unittest.TestCase):
	"""A->B, B->C->D->B (cycle), D->E: three SCCs: {A}, {B,C,D}, {E}."""

	def setUp(self):
		# nodes: A=0, B=1, C=2, D=3, E=4
		self.g = make_graph(5, [(0, 1), (1, 2), (2, 3), (3, 1), (3, 4)])
		self.scc = notsokit.scc.SCC(self.g).run()

	def test_num_components(self):
		self.assertEqual(self.scc.getNumComponents(), 3)

	def test_bcd_same_component(self):
		self.assertEqual(self.scc.getComponent(1), self.scc.getComponent(2))
		self.assertEqual(self.scc.getComponent(1), self.scc.getComponent(3))

	def test_a_singleton(self):
		self.assertNotEqual(self.scc.getComponent(0), self.scc.getComponent(1))
		self.assertEqual(self.scc.getComponentSize(self.scc.getComponent(0)), 1)

	def test_e_singleton(self):
		self.assertNotEqual(self.scc.getComponent(4), self.scc.getComponent(1))
		self.assertEqual(self.scc.getComponentSize(self.scc.getComponent(4)), 1)

	def test_bcd_size(self):
		self.assertEqual(self.scc.getComponentSize(self.scc.getComponent(1)), 3)

	def test_all_different_components(self):
		self.assertNotEqual(self.scc.getComponent(0), self.scc.getComponent(4))


class TestSCCDisconnected(unittest.TestCase):
	"""Four isolated nodes: four singleton SCCs."""

	def test_disconnected(self):
		g = make_graph(4, [])
		scc = notsokit.scc.SCC(g).run()
		self.assertEqual(scc.getNumComponents(), 4)
		for i in range(4):
			self.assertEqual(scc.getComponentSize(scc.getComponent(i)), 1)


if __name__ == "__main__":
	unittest.main()
