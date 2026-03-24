
#ifndef NOTSOKIT_DISTANCE_DIJKSTRA_HPP_
#define NOTSOKIT_DISTANCE_DIJKSTRA_HPP_

#include <tlx/container/d_ary_addressable_int_heap.hpp>

#include <notsokit/auxiliary/vectorcomparator.hpp>

#include <notsokit/graph/graph.hpp>

namespace notsokit {

class Dijkstra final {

public:
    Dijkstra(const Graph &G, nodeid source);
    void run();
	vector<edgeid> getPath(nodeid target) const;
	vector<edgeweight> getDistances() const { return distances; }
	
private:
	const Graph *G;
	nodeid source;
    vector<edgeweight> distances;
    vector<nodeid> preNodes;
	vector<edgeid> preEdges;
    tlx::d_ary_addressable_int_heap<nodeid, 2, Aux::LessInVector<edgeweight>> heap;
	bool hasRun = false;
};

}
#endif // NOTSOKIT_DISTANCE_DIJKSTRA_HPP_