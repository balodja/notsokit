#ifndef NOTSOKIT_GRAPH_GRAPH_HPP
#define NOTSOKIT_GRAPH_GRAPH_HPP

#include <vector>
#include <tuple>
#include <notsokit/globals.hpp>

namespace notsokit {

using std::vector, std::tuple;

class Graph final {
	nodeid n;
	vector<vector<tuple<nodeid, edgeid>>> outEdges;
    vector<vector<tuple<nodeid, edgeid>>> inEdges;
	vector<edgeweight> edgeWeights;
	vector<nodeavoid> avoidNodes;
public:
	Graph()
		: Graph(0) {}

	Graph(nodeid numNodes)
    	: n(numNodes), outEdges(numNodes, vector<tuple<nodeid, edgeid>>()), inEdges(numNodes, vector<tuple<nodeid, edgeid>>()), edgeWeights(), avoidNodes(numNodes, false)
	{
		edgeWeights.reserve(numNodes);
	};

    Graph(const Graph &other)
		: n(other.n), inEdges(other.inEdges), outEdges(other.outEdges), edgeWeights(other.edgeWeights), avoidNodes(other.avoidNodes)
		{};

    Graph(Graph &&other) noexcept
        : n(other.n),
          inEdges(std::move(other.inEdges)),
          outEdges(std::move(other.outEdges)),
		  edgeWeights(std::move(other.edgeWeights)),
          avoidNodes(std::move(other.avoidNodes))
		{};

    ~Graph() = default;

    Graph &operator=(Graph &&other) noexcept {
        std::swap(n, other.n);
        std::swap(inEdges, other.inEdges);
        std::swap(outEdges, other.outEdges);
		std::swap(edgeWeights, other.edgeWeights);
		std::swap(avoidNodes, other.avoidNodes);

        return *this;
    };

    Graph &operator=(const Graph &other) {
        n = other.n;
        inEdges = other.inEdges;
        outEdges = other.outEdges;
		edgeWeights = other.edgeWeights;
		avoidNodes = other.avoidNodes;
        return *this;
    };

	edgeid addEdge(nodeid from, nodeid to, edgeweight weight);
	void setWeights(const edgeweight *weights);
	void setAvoidNodes(const nodeavoid *avoids);
	nodeavoid getAvoidNode(nodeid u) const { return avoidNodes[u]; }
	void transpose();

	nodeid upperNodeIdBound() const { return n; }
	bool isFeasible(const edgeweight *heu, double reltol, double abstol) const;

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

		if (handle(e, u, v, edgeWeights[e])) return true;
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
