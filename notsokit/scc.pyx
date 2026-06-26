# distutils: language=c++

from notsokit.globals cimport nodeid, compid


cdef class SCC:
	"""Kosaraju's strongly connected components algorithm.

	Parameters
	----------
	G : Graph
		The graph to compute SCCs on. Must remain alive for the lifetime of this object.
	"""

	def __cinit__(self, Graph G):
		self._graph = G
		self._this = new _SCC(&G._this)

	def __dealloc__(self):
		if self._this is not NULL:
			del self._this

	def run(self) -> "SCC":
		self._this.run()
		return self

	def getComponent(self, nodeid u) -> int:
		return self._this.getComponent(u)

	def getNumComponents(self) -> int:
		return self._this.getNumComponents()

	def getComponentSize(self, compid c) -> int:
		return self._this.getComponentSize(c)
