#ifndef NOTSOKIT_DISTANCE_A_STAR_ADAPTIVE_HPP_
#define NOTSOKIT_DISTANCE_A_STAR_ADAPTIVE_HPP_

#include <vector>
#include <notsokit/graph/graph.hpp>
#include <notsokit/auxiliary/vectorcomparator.hpp>
#include <tlx/container/d_ary_addressable_int_heap.hpp>

namespace notsokit {

class AStarAdaptive final {

public:
    AStarAdaptive(const Graph *G, const edgeweight *wc, edgeweight *heu, nodeid source, nodeid target);
    void run();
	const vector<edgeid>& getPath() const;
	
private:
	const Graph *G;
	const edgeweight *wc;
	edgeweight *heu;
	nodeid source;
	nodeid target;
	vector<edgeid> path;
    vector<edgeweight> distFromSource, priority;
    tlx::d_ary_addressable_int_heap<nodeid, 2, Aux::LessInVector<edgeweight>> heap;
	bool hasRun = false;
	edgeweight distance = infWeight;
};

} // namespace notsokit

#endif // NOTSOKIT_DISTANCE_A_STAR_ADAPTIVE_HPP_