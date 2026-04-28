#include <notsokit/distance/astar.hpp>
#include <unordered_set>
#include <algorithm>
#include <stdexcept>

namespace notsokit {

AStarAdaptive::AStarAdaptive(const Graph *G, edgeweight *heu, nodeid source, nodeid target)
	: G(G), heu(heu), source(source), target(target), path(), distFromSource(), priority(), heap{priority}
{
}

void AStarAdaptive::run() {
	hasRun = true;

	if (G->getAvoidNode(source) || G->getAvoidNode(target)) {
		return;
	}

	if (source == target) {
		distance = 0.;
		return;
	}

	const nodeid n = G->upperNodeIdBound();
	std::unordered_set<nodeid> visited;

	vector<nodeid> preNodes(n, noneNode);
	vector<edgeid> preEdges(n, noneEdge);

	visited.reserve(n);

	std::fill(distFromSource.begin(), distFromSource.end(), infWeight);
	distFromSource.resize(n, infWeight);
	distFromSource[source] = 0.;

	std::fill(priority.begin(), priority.end(), infWeight);
	priority.resize(n, infWeight);
	priority[source] = 0.;

	heap.clear();
	heap.reserve(n);
	heap.push(source);

	nodeid none = std::numeric_limits<nodeid>::max();
	nodeid top = none;
	do {
		top = heap.extract_top();
		if (top == target) {
			distance = distFromSource[target];
			for (const auto& u : visited) {
				heu[u] = std::max(heu[u], distance - distFromSource[u]);
			}
			break;
		}

		G->forOutEdgesOf(top, [&](edgeid e, nodeid uu, nodeid v, edgeweight w) {
			if (visited.find(v) == visited.end()) {
				visited.insert(v);
			}
			const edgeweight newDist = distFromSource[top] + w;
			if (newDist < distFromSource[v]) {
				distFromSource[v] = newDist;
				priority[v] = newDist + heu[v];
				heap.update(v);
				preEdges[v] = e;
				preNodes[v] = top;
			}
			return false;
		});
	} while (!heap.empty());

	if (distance == infWeight) {
		return;
	}

	nodeid v = target;
	while (v != source) {
		path.push_back(preEdges[v]);
		v = preNodes[v];
	}
	std::reverse(path.begin(), path.end());
}

const vector<edgeid>& AStarAdaptive::getPath() const {
	if (!hasRun) {
		throw std::runtime_error("AStarAdaptive::getPath: run() must be called before getPath().");
	}

	return path;
}

} // namespace notsokit
