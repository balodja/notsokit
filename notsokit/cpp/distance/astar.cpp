#include <notsokit/distance/astar.hpp>
#include <notsokit/globals.hpp>
#include <unordered_set>
#include <algorithm>
#include <functional>
#include <stdexcept>

namespace notsokit {

AStarAdaptive::AStarAdaptive(const Graph *G, const edgeweight *wc, edgeweight *heu, nodeid source, nodeid target)
	:
	G(G),
	wc(wc),
	heu(heu),
	source(source),
	target(target),
	preds(G->upperNodeIdBound(), nonePred),
	preds_pool()
{}


void AStarAdaptive::run() {
	hasRun = true;

	edgeweight reltol, abstol;
	std::tie(reltol, abstol) = G->getTolerance();

	if (G->getAvoidNode(source) || G->getAvoidNode(target)) {
		return;
	}

	if (source == target) {
		distance = 0.;
		return;
	}

	const nodeid n = G->upperNodeIdBound();
	std::unordered_set<nodeid> visited;
	visited.reserve(n);

	std::fill(preds.begin(), preds.end(), nonePred);
	preds.resize(n, nonePred);

    vector<edgeweight> distFromSource;
	std::fill(distFromSource.begin(), distFromSource.end(), infWeight);
	distFromSource.resize(n, infWeight);
	distFromSource[source] = 0.;

    vector<edgeweight> priority;
	std::fill(priority.begin(), priority.end(), infWeight);
	priority.resize(n, infWeight);
	priority[source] = 0.;

    tlx::d_ary_addressable_int_heap<nodeid, 2, Aux::LessInVector<edgeweight>> heap(priority);
	heap.clear();
	heap.reserve(n);
	heap.push(source);

	nodeid none = std::numeric_limits<nodeid>::max();
	nodeid top = none;
	do {
		top = heap.extract_top();
		++visitedVerticesCount;

		if (priority[top] > priority[target] && !is_close(priority[top], priority[target], reltol, abstol)) {
			break;
		}

		G->forOutEdgesOf(top, wc, [&](edgeid e, nodeid uu, nodeid v, edgeweight w) {
			if (visited.find(v) == visited.end()) {
				visited.insert(v);
			}

			const edgeweight newDist = distFromSource[top] + w;
			const edgeweight oldDist = distFromSource[v];

			if (is_close(newDist, oldDist, reltol, abstol)) {
				// add to the pool of predecessors for v
				preds_pool.push_back({top, e, preds[v]});
				preds[v] = preds_pool.size() - 1;

				if (preds_pool.size() == nonePred) {
					throw std::runtime_error("AStarAdaptive::run: Predecessor pool overflow.");
				}
			}

			if (newDist < oldDist) {
				distFromSource[v] = newDist;
				priority[v] = newDist + heu[v];
				heap.update(v);

				preds_pool.push_back({top, e, nonePred});
				preds[v] = preds_pool.size() - 1;
			}
			return false;
		});
	} while (!heap.empty());

	distance = distFromSource[target];
	if (distance == infWeight) {
		return;
	}

	for (const auto& u : visited) {
		heu[u] = std::max(heu[u], distance - distFromSource[u]);
	}
}


vector<vector<edgeid>> AStarAdaptive::getPaths() const {
	if (!hasRun) {
		throw std::runtime_error("AStarAdaptive::getPaths: run() must be called before getPaths().");
	}

	vector<vector<edgeid>> paths;
	paths.clear();
	if (distance == infWeight) {
		return paths;
	}

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
			current.push_back(pred.edge);
			collect(pred.node);
			current.pop_back();
			pid = pred.previous;
		}
	};

	collect(target);
	return paths;
}

} // namespace notsokit
