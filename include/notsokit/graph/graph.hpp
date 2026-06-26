#ifndef NOTSOKIT_GRAPH_GRAPH_HPP
#define NOTSOKIT_GRAPH_GRAPH_HPP

#include <utility>
#include <vector>
#include <tuple>
#include <notsokit/globals.hpp>

namespace notsokit {

using std::vector, std::tuple;

class Graph final {
	nodeid n;
	edgeid k;
	vector<vector<tuple<nodeid, edgeid>>> outEdges;
    vector<vector<tuple<nodeid, edgeid>>> inEdges;
	vector<edgeweight> edgeWeights;
	vector<nodeavoid> avoidNodes;
	edgeweight reltol;
	edgeweight abstol;
public:
	Graph() : Graph(0, 1, 0, 0) {};
	Graph(nodeid numNodes, edgeid numDims, edgeweight reltol, edgeweight abstol)
    	: n(numNodes), k(numDims), outEdges(numNodes, vector<tuple<nodeid, edgeid>>()), inEdges(numNodes, vector<tuple<nodeid, edgeid>>()), edgeWeights(), avoidNodes(numNodes, false), reltol(reltol), abstol(abstol)
	{
		edgeWeights.reserve(numNodes * numDims);
	};

    Graph(const Graph &other)
		: n(other.n), k(other.k), inEdges(other.inEdges), outEdges(other.outEdges), edgeWeights(other.edgeWeights), avoidNodes(other.avoidNodes), reltol(other.reltol), abstol(other.abstol)
		{};

    Graph(Graph &&other) noexcept
        : n(other.n),
          k(other.k),
          inEdges(std::move(other.inEdges)),
          outEdges(std::move(other.outEdges)),
		  edgeWeights(std::move(other.edgeWeights)),
          avoidNodes(std::move(other.avoidNodes)),
		  reltol(other.reltol),
		  abstol(other.abstol)
		{};

    ~Graph() = default;

    Graph &operator=(Graph &&other) noexcept {
        std::swap(n, other.n);
        std::swap(k, other.k);
        std::swap(inEdges, other.inEdges);
        std::swap(outEdges, other.outEdges);
		std::swap(edgeWeights, other.edgeWeights);
		std::swap(avoidNodes, other.avoidNodes);
		std::swap(reltol, other.reltol);
		std::swap(abstol, other.abstol);

        return *this;
    };

    Graph &operator=(const Graph &other) {
        n = other.n;
        k = other.k;
        inEdges = other.inEdges;
        outEdges = other.outEdges;
		edgeWeights = other.edgeWeights;
		avoidNodes = other.avoidNodes;
		reltol = other.reltol;
		abstol = other.abstol;
        return *this;
    };

	edgeid addEdge(nodeid from, nodeid to, const edgeweight *weights);
	void setWeights(const edgeweight *weights);
	edgeweight getWeight(edgeid e, const edgeweight *wc) const {
		edgeweight w = 0;
		for (edgeid d = 0; d < k; ++d)
			w += wc[d] * edgeWeights[e * k + d];
		return w;
	};

	void setAvoidNodes(const nodeavoid *avoids);
	nodeavoid getAvoidNode(nodeid u) const { return avoidNodes[u]; }
	const nodeavoid* getAvoidNodes() const { return avoidNodes.data(); }
	void transpose();

	nodeid upperNodeIdBound() const { return n; }
	edgeid upperEdgeIdBound() const { return edgeWeights.size() / k; }
	edgeid numDims() const { return k; }
	bool isFeasible(const edgeweight *wc, const edgeweight *heu) const;
	void setTolerance(edgeweight reltol, edgeweight abstol) { this->reltol = reltol; this->abstol = abstol; }
	std::pair<edgeweight, edgeweight> getTolerance() const { return {reltol, abstol}; }

	template <typename L> inline bool forEdges(L handle) const;
	template <typename L> inline bool forOutEdgesOf(nodeid u, L handle) const;
};

template <typename L> inline bool Graph::forOutEdgesOf(nodeid u, L handle) const {
	if (this->avoidNodes[u]) return false;

    for (nodeid i = 0; i < outEdges[u].size(); ++i) {
        tuple<nodeid, edgeid> tpl = outEdges[u][i];

		nodeid v = std::get<0>(tpl);
		if (this->avoidNodes[v]) continue;

		edgeid e = std::get<1>(tpl);

		if (handle(e, u, v)) return true;
    }
    return false;
}

template <typename L> inline bool Graph::forEdges(L handle) const {
    for (nodeid u = 0; u < n; ++u) {
        if (forOutEdgesOf(u, handle)) return true;
    }
	return false;
}


// dijkstra and astar -- return edgeids as path, not nodeids

} // namespace notsokit

#endif // NOTSOKIT_GRAPH_GRAPH_HPP
