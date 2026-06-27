# distutils: language=c++

import numpy as np
cimport numpy as cnp
from libcpp.vector cimport vector
from libcpp.pair cimport pair
from notsokit.globals cimport edgeid, nodeid, edgeweight, nodeavoid


cdef class Graph:
	def __init__(self, int n, int k = 1, double reltol = 1e-8, double abstol = 1e-10):
		self._this = _Graph(n, k, reltol, abstol)
		self.external_weights = None
		self.external_avoids = None

	cdef setThis(self, _Graph& other):
		swap[_Graph](self._this, other)
		return self

	def upperNodeIdBound(self) -> int:
		return self._this.upperNodeIdBound()

	def upperEdgeIdBound(self) -> int:
		return self._this.upperEdgeIdBound()

	def numDims(self) -> int:
		return self._this.numDims()

	def transpose(self) -> Graph:
		cdef Graph g = Graph(0, self._this.numDims())
		g._this = self._this
		g._this.transpose()
		return g

	def addEdge(self, int u, int v, cnp.ndarray[edgeweight, ndim=1, mode='c'] weights) -> int:
		if weights.shape[0] != self._this.numDims():
			raise ValueError(f"Expected weights array of size {self._this.numDims()}, got {weights.shape[0]}")
		cdef edgeweight[::1] weights_view = weights
		return self._this.addEdge(u, v, &weights_view[0])

	def getEdges(self, int u, int v) -> list:
		return list(self._this.getEdges(u, v))

	def getWeight(self, int e, cnp.ndarray[edgeweight, ndim=1, mode='c'] wc) -> float:
		if wc.shape[0] != self._this.numDims():
			raise ValueError(f"Expected wc array of size {self._this.numDims()}, got {wc.shape[0]}")
		cdef edgeweight[::1] wc_view = wc
		return self._this.getWeight(e, &wc_view[0])

	def setWeights(self, cnp.ndarray[edgeweight, ndim=2, mode='c'] weights) -> None:
		self.external_weights = weights

		if weights.shape[0] != self._this.upperEdgeIdBound() or weights.shape[1] != self._this.numDims():
			raise ValueError(f"Expected weights array of shape ({self._this.upperEdgeIdBound()}, {self._this.numDims()}), got ({weights.shape[0]}, {weights.shape[1]})")

		cdef edgeweight[:,::1] weights_view = weights
		self._this.setWeights(&weights_view[0, 0])

	def setAvoidNodes(self, cnp.ndarray[nodeavoid, ndim=1, mode='c'] avoids) -> None:
		self.external_avoids = avoids

		if avoids.size != self._this.upperNodeIdBound():
			raise ValueError(f"Expected avoids array of size {self._this.upperNodeIdBound()}, got {avoids.size}")

		cdef nodeavoid[::1] avoids_view = avoids
		self._this.setAvoidNodes(&avoids_view[0])

	def isFeasible(self, cnp.ndarray[edgeweight, ndim=1, mode='c'] wc, cnp.ndarray[edgeweight, ndim=1, mode='c'] heu) -> bool:
		if wc.shape[0] != self._this.numDims():
			raise ValueError(f"Expected wc array of size {self._this.numDims()}, got {wc.shape[0]}")
		if heu.size != self._this.upperNodeIdBound():
			raise ValueError(f"Expected heuristic array of size {self._this.upperNodeIdBound()}, got {heu.size}")

		cdef edgeweight[::1] wc_view = wc
		cdef edgeweight[::1] heu_view = heu
		return self._this.isFeasible(&wc_view[0], &heu_view[0])

	def setTolerance(self, double reltol, double abstol) -> None:
		self._this.setTolerance(reltol, abstol)

	def getTolerance(self) -> tuple:
		cdef pair[edgeweight, edgeweight] tol = self._this.getTolerance()
		return (tol.first, tol.second)
