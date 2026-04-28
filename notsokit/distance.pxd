
from libcpp.vector cimport vector
from notsokit.graph cimport _Graph, Graph
from notsokit.globals cimport edgeid, nodeid, edgeweight


cdef extern from "notsokit/distance/dijkstra.hpp" namespace "notsokit":
	cdef cppclass _Dijkstra "notsokit::Dijkstra":
		_Dijkstra(_Graph & g, nodeid n) except +
		void run() except +
		vector[edgeid] getPath(nodeid target) except +
		vector[edgeweight] getDistances() except +


cdef class Dijkstra:
	cdef _Dijkstra *_this
	cdef object graph


cdef extern from "notsokit/distance/astar.hpp" namespace "notsokit":
	cdef cppclass _AStarAdaptive "notsokit::AStarAdaptive":
		_AStarAdaptive(const _Graph *g, edgeweight *heu, nodeid source, nodeid target) except +
		void run() except +
		vector[edgeid] getPath() except +


cdef class AStarAdaptive:
	cdef _AStarAdaptive *_this
	cdef object heu
	cdef object graph
