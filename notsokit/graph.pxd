cdef extern from "<algorithm>" namespace "std":
	void swap[T](T &a,  T &b)
	_Graph move( _Graph t ) nogil

cdef extern from "notsokit/graph/graph.hpp" namespace "notsokit":
	cdef cppclass _Graph "notsokit::Graph":
		_Graph() except +
		double callme() const

cdef class Graph:
	cdef _Graph _this
	cdef setThis(self, _Graph& other)
