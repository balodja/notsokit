from libcpp.string cimport string
from libcpp.vector cimport vector
from notsokit.graph cimport _Graph
from notsokit.globals cimport edgeweight


cdef extern from "notsokit/io.hpp" namespace "notsokit":
	void writeGraph(const _Graph &g, const edgeweight *wc, const string &nodesFile, const string &edgesFile) except +
	_Graph readGraph(const string &nodesFile, const string &edgesFile) except +
	void writeHeuristics(const vector[edgeweight] &heu, const string &heuFile) except +
	vector[edgeweight] readHeuristics(const string &heuFile) except +
