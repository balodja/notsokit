from notsokit.graph cimport _Graph, Graph
from notsokit.globals cimport nodeid, compid

cdef extern from "notsokit/scc.hpp" namespace "notsokit":
	cdef cppclass _SCC "notsokit::SCC":
		_SCC(_Graph *G) except +
		compid getComponent(nodeid u) except +
		compid getNumComponents() except +
		compid getComponentSize(compid c) except +
		void run() except +

cdef class SCC:
	cdef _SCC *_this
	cdef Graph _graph
