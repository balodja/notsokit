
from libcpp.vector cimport vector
from notsokit.graph cimport _Graph, Graph
from notsokit.globals cimport edgeid, nodeid, edgeweight
from libc.stdint cimport uint64_t


cdef extern from "notsokit/globals.hpp" namespace "notsokit":
	uint64_t visitedVerticesCount


cdef extern from "notsokit/distance/dijkstra.hpp" namespace "notsokit":
	cdef cppclass _Dijkstra "notsokit::Dijkstra":
		_Dijkstra(const _Graph *g, const edgeweight *wc, nodeid source) except +
		void run() except +
		vector[edgeid] getPath(nodeid target) except +
		vector[edgeweight] getDistances() except +


cdef class Dijkstra:
	cdef _Dijkstra *_this
	cdef object graph
	cdef object wc


cdef extern from "notsokit/distance/astar.hpp" namespace "notsokit":
	cdef cppclass _AStarAdaptive "notsokit::AStarAdaptive":
		_AStarAdaptive(const _Graph *g, const edgeweight *wc, edgeweight *heu, nodeid source, nodeid target) except +
		void run() except +
		vector[edgeid] getPath() except +


cdef class AStarAdaptive:
	cdef _AStarAdaptive *_this
	cdef object wc
	cdef object heu
	cdef object graph
