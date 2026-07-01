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

    vector<edgeweight> distFromSource(n, infWeight);
	distFromSource[source] = 0.;

    vector<edgeweight> priority(n, infWeight);
	priority[source] = 0.;

    tlx::d_ary_addressable_int_heap<nodeid, 2, Aux::LessInVector<edgeweight>> heap(priority);
	heap.reserve(n);
	heap.push(source);

	nodeid none = std::numeric_limits<nodeid>::max();
	nodeid top = none;
	do {
		top = heap.extract_top();
		++visitedVerticesCount;

		if (priority[top] >= priority[target]) {
			break;
		}

		G->forOutEdgesOf(top, [&](edgeid e, nodeid uu, nodeid v) {
			edgeweight w = G->getWeight(e, wc);

			if (visited.find(v) == visited.end()) {
				visited.insert(v);
			}

			const edgeweight newDist = distFromSource[top] + w;
			const edgeweight oldDist = distFromSource[v];

			if (oldDist == newDist) {
				preds_pool.push_back({top, e, preds[v]});
				preds[v] = preds_pool.size() - 1;

				if (preds_pool.size() == nonePred) {
					throw std::runtime_error("AStarAdaptive::run: Predecessor pool overflow.");
				}
			} else if (newDist < oldDist) {
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

	if (distance == infWeight) {
		return {};
	}

	return predPoolGetPaths(preds, preds_pool, source, target);
}
} // namespace notsokit
