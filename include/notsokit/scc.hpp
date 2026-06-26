#ifndef NOTSOKIT_SCC_HPP_
#define NOTSOKIT_SCC_HPP_

#include <notsokit/graph.hpp>

namespace notsokit {


class SCC {
public:
	SCC(Graph *G) : G(G), assignments(G->upperNodeIdBound()), sizes() {};
	~SCC() = default;

	compid getComponent(nodeid u) const { return assignments[u]; }
	compid getNumComponents() const { return (compid)sizes.size(); }
	compid getComponentSize(compid c) const { return sizes[c]; }
	void run();
private:
	Graph *G;
	vector<compid> assignments;
	vector<compid> sizes;
};

}
#endif // NOTSOKIT_SCC_HPP_