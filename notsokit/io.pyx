# distutils: language=c++

from libcpp.vector cimport vector
from notsokit.graph cimport Graph, _Graph
from notsokit.globals cimport edgeweight
from notsokit.io cimport writeGraph as _writeGraph, readGraph as _readGraph
from notsokit.io cimport writeHeuristics as _writeHeuristics, readHeuristics as _readHeuristics
import numpy as np
cimport numpy as np
from notsokit.globals import edgeweight_t


def write_graph(Graph g, np.ndarray[edgeweight, ndim=1, mode='c'] wc, str nodes_file, str edges_file) -> None:
    if wc.shape[0] != g.numDims():
        raise ValueError(f"Expected wc array of size {g.numDims()}, got {wc.shape[0]}")
    cdef edgeweight[::1] wc_view = wc
    _writeGraph(g._this, &wc_view[0], nodes_file.encode(), edges_file.encode())


def read_graph(str nodes_file, str edges_file) -> Graph:
    cdef Graph g = Graph.__new__(Graph)
    g._this = _readGraph(nodes_file.encode(), edges_file.encode())
    g.external_weights = None
    g.external_avoids = None
    return g


def write_heuristics(np.ndarray[edgeweight, ndim=1, mode='c'] heu, str heu_file) -> None:
    cdef vector[edgeweight] vec
    cdef edgeweight[::1] view
    if heu.size > 0:
        view = heu
        vec.assign(&view[0], &view[0] + heu.size)
    _writeHeuristics(vec, heu_file.encode())


def read_heuristics(str heu_file) -> np.ndarray:
    cdef vector[edgeweight] vec = _readHeuristics(heu_file.encode())
    arr = np.empty(vec.size(), dtype=edgeweight_t)
    cdef edgeweight[::1] view = arr
    for i in range(vec.size()):
        view[i] = vec[i]
    return arr
