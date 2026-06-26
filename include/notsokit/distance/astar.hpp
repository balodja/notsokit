#ifndef NOTSOKIT_DISTANCE_A_STAR_ADAPTIVE_HPP_
#define NOTSOKIT_DISTANCE_A_STAR_ADAPTIVE_HPP_

#include <vector>
#include <notsokit/graph.hpp>
#include <notsokit/auxiliary/vectorcomparator.hpp>
#include <tlx/container/d_ary_addressable_int_heap.hpp>
#include <notsokit/distance/predecessor.hpp>

namespace notsokit {

class AStarAdaptive final {

public:
    AStarAdaptive(const Graph *G, const edgeweight *wc, edgeweight *heu, nodeid source, nodeid target);
    void run();
	vector<vector<edgeid>> getPaths() const;
private:
	const Graph *G;
	const edgeweight *wc;
	edgeweight *heu;
	nodeid source;
	nodeid target;
	bool hasRun = false;
	edgeweight distance = infWeight;
	vector<predid> preds;
	vector<Predecessor> preds_pool;
};

} // namespace notsokit

#endif // NOTSOKIT_DISTANCE_A_STAR_ADAPTIVE_HPP_