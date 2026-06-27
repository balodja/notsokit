#include <notsokit/compress.hpp>
#include <stdexcept>

namespace notsokit {


vector<nodeid> nonTrivialNodes(const Graph &G) {
	vector<bool> nonTrivial(G.upperNodeIdBound(), false);
	G.forEdges([&](edgeid e, nodeid u, nodeid v) {
		nonTrivial[u] = true;
		nonTrivial[v] = true;
		return false;
	});

	vector<nodeid> result;
	for (nodeid u = 0; u < nonTrivial.size(); ++u) {
		if (nonTrivial[u]) {
			result.push_back(u);
		}
	}
	return result;
}


Graph zeroEdges(const Graph &G) {
	edgeweight reltol, abstol;
	std::tie(reltol, abstol) = G.getTolerance();
	Graph G2(G.upperNodeIdBound(), 1, reltol, abstol);

	vector<edgeweight> wc(G.numDims(), 1.0);

	G.forEdges([&](edgeid e, nodeid u, nodeid v) {
		edgeweight w = G.getWeight(e, wc.data());
		if (w == 0.0) {
			edgeweight w2 = 1.0;
			G2.addEdge(u, v, &w2);
		}
		return false;
	});
	return G2;
}


Compressor::Compressor(const vector<nodeid> &nds, const vector<edgeid> &eds)
	: nodeUnmap(nds), edgeUnmap(eds), nodeMap(), edgeMap() {
	for (nodeid i = 0; i < (nodeid)nds.size(); ++i) {
		if (nodeMap.find(nds[i]) != nodeMap.end()) {
			throw std::invalid_argument("Duplicate node ID in Compressor constructor.");
		}
		nodeMap[nds[i]] = i;
	}
	for (edgeid i = 0; i < (edgeid)eds.size(); ++i) {
		if (edgeMap.find(eds[i]) != edgeMap.end()) {
			throw std::invalid_argument("Duplicate edge ID in Compressor constructor.");
		}
		edgeMap[eds[i]] = i;
	}
}


Compressor::Compressor(Graph &g, const vector<nodeid> &nds)
	: nodeUnmap(nds), edgeUnmap(), nodeMap(), edgeMap() {
	for (nodeid i = 0; i < (nodeid)nds.size(); ++i) {
		if (nodeMap.find(nds[i]) != nodeMap.end()) {
			throw std::invalid_argument("Duplicate node ID in Compressor constructor.");
		}
		nodeMap[nds[i]] = i;
	}

	for (nodeid i = 0; i < (nodeid)nds.size(); ++i) {
		g.forOutEdgesOf(nds[i], [&](edgeid e, nodeid u, nodeid v) {
			if (nodeMap.find(v) != nodeMap.end()) {
				edgeid e2 = (edgeid)edgeUnmap.size();
				edgeUnmap.push_back(e);
				edgeMap[e] = e2;
			}
			return false;
		});
	}
}


Compressor Compressor::operator*(const Compressor &other) const {
	vector<nodeid> newNodeUnmap;
	for (nodeid u : nodeUnmap) {
		if (u >= other.nodeUnmap.size()) {
			throw std::out_of_range("Node ID out of range in Compressor composition.");
		}
		newNodeUnmap.push_back(other.unmapNode(u));
	}

	vector<edgeid> newEdgeUnmap;
	for (edgeid e : edgeUnmap) {
		if (e >= other.edgeUnmap.size()) {
			throw std::out_of_range("Edge ID out of range in Compressor composition.");
		}
		newEdgeUnmap.push_back(other.unmapEdge(e));
	}

	return Compressor(newNodeUnmap, newEdgeUnmap);
}


Graph Compressor::mapGraph(Graph &g) const {
	edgeweight reltol, abstol;
	std::tie(reltol, abstol) = g.getTolerance();
	Graph result(nodeUnmap.size(), g.numDims(), reltol, abstol);

	for (nodeid i = 0; i < nodeUnmap.size(); ++i) {
		g.forOutEdgesOf(nodeUnmap[i], [&](edgeid e, nodeid u, nodeid v) {
			if (nodeMap.find(v) != nodeMap.end() && edgeMap.find(e) != edgeMap.end()) {
				result.addEdge(i, nodeMap.at(v), g.getWeights(e));
			}
			return false;
		});
	}
	return result;
}


}; // namespace notsokit