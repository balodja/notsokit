# distutils: language=c++

import numpy as np
from libcpp.vector cimport vector
from notsokit.globals cimport edgeid, nodeid


def zeroEdges(Graph G) -> Graph:
	cdef Graph result = Graph.__new__(Graph)
	cdef _Graph tmp = _zeroEdges(G._this)
	result.setThis(tmp)
	return result


cdef class Compressor:
	"""Bidirectional mapping between a subgraph's compressed indices and original IDs.

	Two constructors:
	  Compressor(nds, eds)         — explicit node and edge ID lists
	  Compressor(graph, nds)       — derive edges automatically from graph
	"""

	def __cinit__(self, nds_or_graph=None, eds_or_nds=None):
		cdef vector[nodeid] nds_vec
		cdef vector[edgeid] eds_vec
		if nds_or_graph is None:
			self._this = NULL
			return
		if isinstance(nds_or_graph, Graph):
			for n in eds_or_nds:
				nds_vec.push_back(n)
			self._this = new _Compressor((<Graph>nds_or_graph)._this, nds_vec)
		else:
			for n in nds_or_graph:
				nds_vec.push_back(n)
			for e in eds_or_nds:
				eds_vec.push_back(e)
			self._this = new _Compressor(nds_vec, eds_vec)

	def __dealloc__(self):
		if self._this is not NULL:
			del self._this

	def mapNode(self, nodeid u) -> int:
		return self._this.mapNode(u)

	def mapEdge(self, edgeid e) -> int:
		return self._this.mapEdge(e)

	def unmapNode(self, nodeid u) -> int:
		return self._this.unmapNode(u)

	def unmapEdge(self, edgeid e) -> int:
		return self._this.unmapEdge(e)

	def mapGraph(self, Graph g) -> Graph:
		cdef Graph result = Graph.__new__(Graph)
		cdef _Graph tmp = self._this.mapGraph(g._this)
		result.setThis(tmp)
		return result

	def __mul__(self, Compressor other) -> Compressor:
		cdef Compressor result = Compressor.__new__(Compressor)
		result._this = new _Compressor(self._this[0] * other._this[0])
		return result
