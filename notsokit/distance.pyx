# distutils: language=c++

from libcpp.vector cimport vector
from notsokit.graph cimport Graph
import numpy as np
cimport numpy as np
from notsokit.globals import edgeweight_t
from notsokit.globals cimport edgeweight


cdef class Dijkstra:
	def __cinit__(self, Graph g, int source):
		self.graph = g
		self._this = new _Dijkstra(g._this, source)

	def __dealloc__(self):
		del self._this

	def run(self):
		self._this.run()

	def getPath(self, int target):
		return self._this.getPath(target)

	def getDistances(self):
		cdef vector[edgeweight] distances = self._this.getDistances()

		arr = np.empty(distances.size(), dtype=edgeweight_t)
		cdef edgeweight[:] view = arr

		for i in range(distances.size()):
			view[i] = distances[i]

		return arr


cdef class AStarAdaptive:
	def __cinit__(self, Graph g, np.ndarray[edgeweight, ndim=1, mode='c'] heu, int source, int target):
		self.graph = g
		self.heu = heu

		cdef edgeweight[::1] heu_view = heu

		if heu.size != self.graph.upperNodeIdBound():
			raise ValueError(f"Expected heuristic array of size {self.graph.upperNodeIdBound()}, got {heu.size}")

		self._this = new _AStarAdaptive(&g._this, &heu_view[0], source, target)

	def __dealloc__(self):
		del self._this

	def run(self):
		self._this.run()

	def getPath(self):
		return self._this.getPath()
