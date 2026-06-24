#include <notsokit/distance/distance.hpp>
#include <vector>
#include <functional>
#include <algorithm>

namespace notsokit {

using std::vector;

vector<vector<edgeid>> predPoolGetPaths(const vector<predid>& preds, const vector<Predecessor>& preds_pool, nodeid source, nodeid target) {
	vector<vector<edgeid>> paths = {};

	vector<bool> visited(preds.size(), false);
	vector<edgeid> current;
	std::function<void(nodeid)> collect = [&](nodeid v) {
		if (v == source) {
			paths.push_back(current);
			std::reverse(paths.back().begin(), paths.back().end());
			return;
		}
		predid pid = preds[v];
		while (pid != nonePred) {
			const Predecessor& pred = preds_pool[pid];
			if (!visited[pred.node]) {
				current.push_back(pred.edge);
				visited[pred.node] = true;
				collect(pred.node);
				current.pop_back();
				visited[pred.node] = false;
			}
			pid = pred.previous;
		}
	};

	collect(target);
	return paths;
}

} // namespace notsokit