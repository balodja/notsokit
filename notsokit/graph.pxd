from notsokit.globals cimport edgeid, nodeid, edgeweight, nodeavoid
from libcpp.vector cimport vector
from libcpp cimport bool as bool_t


cdef extern from "<algorithm>" namespace "std":
	void swap[T](T &a,  T &b)
	_Graph move( _Graph t ) nogil
	vector[edgeweight] move( vector[edgeweight] t ) nogil
	vector[nodeavoid] move( vector[nodeavoid] t ) nogil


cdef extern from "notsokit/graph/graph.hpp" namespace "notsokit":
	cdef cppclass _Graph "notsokit::Graph":
		_Graph(nodeid n) except +
		_Graph() except +
		nodeid upperNodeIdBound() except +
		void transpose() except +
		edgeid addEdge(nodeid u, nodeid v, edgeweight w) except +
		void setWeights(const edgeweight *w) except +
		void setAvoidNodes(const nodeavoid *avoids) except +
		bool_t isFeasible(const edgeweight *heu, double reltol, double abstol) except +


cdef class Graph:
	cdef _Graph _this
	cdef setThis(self, _Graph& other)
	cdef object external_weights
	cdef object external_avoids