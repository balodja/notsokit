#ifndef NOTSOKIT_DISTANCE_PREDECESSOR_HPP_
#define NOTSOKIT_DISTANCE_PREDECESSOR_HPP_

#include <notsokit/globals.hpp>
#include <limits>
#include <vector>


namespace notsokit {

using predid = uint32_t;
using std::vector;

constexpr predid nonePred = std::numeric_limits<predid>::max();

struct Predecessor {
	nodeid node;
	edgeid edge;
	predid previous;
};

vector<vector<edgeid>> predPoolGetPaths(
	const vector<predid>& preds,
	const vector<Predecessor>& preds_pool,
	nodeid source,
	nodeid target
);


} // namespace notsokit

#endif // NOTSOKIT_DISTANCE_PREDECESSOR_HPP_