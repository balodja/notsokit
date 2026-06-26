
#ifndef NOTSOKIT_DISTANCE_DIJKSTRA_HPP_
#define NOTSOKIT_DISTANCE_DIJKSTRA_HPP_

#include <tlx/container/d_ary_addressable_int_heap.hpp>

#include <notsokit/auxiliary/vectorcomparator.hpp>

#include <notsokit/graph.hpp>
#include <notsokit/distance/predecessor.hpp>

namespace notsokit {

class Dijkstra final {

public:
    Dijkstra(const Graph *G, const edgeweight *wc, nodeid source);
    void run();
	vector<vector<edgeid>> getPaths(nodeid target) const;
	vector<edgeweight> getDistances() const { return distances; }
	
private:
	const Graph *G;
	const edgeweight *wc;
	nodeid source;
    vector<edgeweight> distances;
	vector<predid> preds;
	vector<Predecessor> preds_pool;
	bool hasRun = false;
};

}
#endif // NOTSOKIT_DISTANCE_DIJKSTRA_HPP_