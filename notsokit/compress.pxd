from notsokit.graph cimport _Graph, Graph
from notsokit.globals cimport edgeid, nodeid
from libcpp.vector cimport vector

cdef extern from "<algorithm>" namespace "std":
	_Compressor move(_Compressor t) nogil

cdef extern from "notsokit/compress.hpp" namespace "notsokit":
	cdef _Graph _zeroEdges "notsokit::zeroEdges"(const _Graph &G) except +

	cdef cppclass _Compressor "notsokit::Compressor":
		_Compressor() except +
		_Compressor(const vector[nodeid] &nds, const vector[edgeid] &eds) except +
		_Compressor(_Graph &g, const vector[nodeid] &nds) except +
		_Compressor(const _Compressor &other) except +
		nodeid mapNode(nodeid u) except +
		edgeid mapEdge(edgeid e) except +
		nodeid unmapNode(nodeid u) except +
		edgeid unmapEdge(edgeid e) except +
		_Graph mapGraph(_Graph &g) except +
		_Compressor operator*(const _Compressor &other) except +

cdef class Compressor:
	cdef _Compressor *_this
