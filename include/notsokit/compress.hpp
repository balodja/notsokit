#ifndef NOTSOKIT_GRAPH_COMPRESS_HPP
#define NOTSOKIT_GRAPH_COMPRESS_HPP

#include <vector>
#include <unordered_map>
#include <notsokit/graph/graph.hpp>

namespace notsokit {

using std::vector, std::tuple, std::unordered_map;

vector<nodeid> nonTrivialNodes(const Graph &G);

Graph zeroEdges(const Graph &G);


class Compressor {
public:
	Compressor() = default;
	Compressor(const vector<nodeid> &nds, const vector<edgeid> &eds);
	Compressor(Graph &g, const vector<nodeid> &nds);
	Compressor(const Compressor &other) = default;
	Compressor(Compressor &&other) noexcept = default;
	Compressor &operator=(const Compressor &other) = default;
	Compressor &operator=(Compressor &&other) noexcept = default;
	~Compressor() = default;

	nodeid mapNode(nodeid u) const { return nodeMap.at(u); }
	edgeid mapEdge(edgeid e) const { return edgeMap.at(e); }
	nodeid unmapNode(nodeid u) const { return nodeUnmap.at(u); }
	edgeid unmapEdge(edgeid e) const { return edgeUnmap.at(e); }
	Graph mapGraph(Graph &g) const;

	Compressor operator*(const Compressor &other) const;
private:
	vector<nodeid> nodeUnmap;
	vector<edgeid> edgeUnmap;
	unordered_map<nodeid, nodeid> nodeMap;
	unordered_map<edgeid, edgeid> edgeMap;
};



}; // namespace notsokit

#endif // NOTSOKIT_GRAPH_COMPRESS_HPP
