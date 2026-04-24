# distutils: language=c++

# from notsokit.graph cimport _Graph
import numpy as np
cimport numpy as cnp
from libcpp.vector cimport vector
from notsokit.globals cimport edgeid, nodeid, edgeweight, nodeavoid


cdef class Graph:
	def __init__(self, int n):
		self._this = _Graph(n)
		self.external_weights = None
		self.external_avoids = None

	cdef setThis(self, _Graph& other):
		swap[_Graph](self._this, other)
		return self

	def upperNodeIdBound(self) -> int:
		return self._this.upperNodeIdBound()

	def upperEdgeIdBound(self) -> int:
		return self._this.upperEdgeIdBound()

	def transpose(self) -> Graph:
		cdef Graph g = Graph(0)
		g._this = self._this
		g._this.transpose()
		return g

	def addEdge(self, int u, int v, double w) -> int:
		return self._this.addEdge(u, v, w)

	def setWeights(self, cnp.ndarray[edgeweight, ndim=1, mode='c'] weights) -> None:
		self.external_weights = weights

		if weights.size != self._this.upperEdgeIdBound():
			raise ValueError(f"Expected weights array of size {self._this.upperEdgeIdBound()}, got {weights.size}")

		cdef edgeweight[::1] weights_view = weights
		self._this.setWeights(&weights_view[0])

	def setAvoidNodes(self, cnp.ndarray[nodeavoid, ndim=1, mode='c'] avoids) -> None:
		self.external_avoids = avoids

		if avoids.size != self._this.upperNodeIdBound():
			raise ValueError(f"Expected avoids array of size {self._this.upperNodeIdBound()}, got {avoids.size}")

		cdef nodeavoid[::1] avoids_view = avoids
		self._this.setAvoidNodes(&avoids_view[0])
	
	def isFeasible(self, cnp.ndarray[edgeweight, ndim=1, mode='c'] heu, double reltol = 1e-8, double abstol = 1e-10) -> bool:
		if heu.size != self._this.upperNodeIdBound():
			raise ValueError(f"Expected heuristic array of size {self._this.upperNodeIdBound()}, got {heu.size}")

		cdef edgeweight[::1] heu_view = heu
		return self._this.isFeasible(&heu_view[0], reltol, abstol)
