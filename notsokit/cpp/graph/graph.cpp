#include <notsokit/globals.hpp>
#include <notsokit/graph/graph.hpp>
#include <iostream>
#include <iomanip>

namespace notsokit {

edgeid Graph::addEdge(nodeid from, nodeid to, const edgeweight *weights) {
	if (from >= n || to >= n) {
		throw std::out_of_range("Node id out of range");
	}

	edgeid id = edgeWeights.size() / k;
	outEdges[from].emplace_back(to, id);
	inEdges[to].emplace_back(from, id);
	for (edgeid d = 0; d < k; ++d)
		edgeWeights.push_back(weights[d]);
	return id;
}

void Graph::setWeights(const edgeweight *weights) {
	std::copy(weights, weights + edgeWeights.size(), edgeWeights.begin());
}

void Graph::setAvoidNodes(const nodeavoid *avoids) {
	std::copy(avoids, avoids + n, avoidNodes.begin());
}

void Graph::transpose() {
	std::swap(inEdges, outEdges);
}

bool Graph::isFeasible(const edgeweight *wc, const edgeweight *heu) const {
    bool br = forEdges(wc, [&](edgeid e, nodeid u, nodeid v, edgeweight w) {
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
