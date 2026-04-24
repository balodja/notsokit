#include <notsokit/graph/graph.hpp>
#include <iostream>
#include <iomanip>

namespace notsokit {

edgeid Graph::addEdge(nodeid from, nodeid to, edgeweight weight) {
	if (from >= n || to >= n) {
		throw std::out_of_range("Node id out of range");
	}

	edgeid id = edgeWeights.size();
	outEdges[from].emplace_back(to, id);
	inEdges[to].emplace_back(from, id);
	edgeWeights.push_back(weight);
	return id;
}

void Graph::setWeights(const edgeweight *weights) {
	for (edgeid e = 0; e < edgeWeights.size(); ++e) {
		edgeWeights[e] = weights[e];
	}
}

void Graph::setAvoidNodes(const nodeavoid *avoids) {
	for (nodeid u = 0; u < n; ++u) {
		avoidNodes[u] = avoids[u];
	}
}

void Graph::transpose() {
	std::swap(inEdges, outEdges);
}

bool is_close(double a, double b, double reltol, double abstol) {
    return std::fabs(a - b) <= std::max(reltol * std::max(std::fabs(a), std::fabs(b)), abstol);
}

bool Graph::isFeasible(const edgeweight *heu, double reltol, double abstol) const {
    bool br = forEdges([&](edgeid e, nodeid u, nodeid v, edgeweight w) {
        if ((w + heu[v] < heu[u]) && !is_close(w + heu[v], heu[u], reltol, abstol)) {
			std::cerr << std::setprecision(20);
			std::cerr << "Infeasible edge: " << u << " -> " << v << " (" << e << ") with weight " << w << std::endl;
            return true;
        }
        return false;
    });

    return !br;
}


} // namespace notsokit
