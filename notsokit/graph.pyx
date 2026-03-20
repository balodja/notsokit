# distutils: language = c++

# from notsokit.graph cimport _Graph

cdef class Graph:
	def __cinit__(self):
		self._this = move(_Graph())

	cdef setThis(self, _Graph& other):
		swap[_Graph](self._this, other)
		return self

	def callme(self):
		return self._this.callme()
