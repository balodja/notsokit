#include <functional>
#include <notsokit/scc.hpp>

namespace notsokit {


void SCC::run() {
	nodeid n = G->upperNodeIdBound();
	vector<bool> visited(n, false);
	vector<nodeid> order;
	order.reserve(n);

	// First pass: DFS on original graph, record finish order
	std::function<void(nodeid)> dfs1 = [&](nodeid u) {
		visited[u] = true;
		G->forOutEdgesOf(u, [&](edgeid, nodeid, nodeid v) {
			if (!visited[v]) dfs1(v);
			return false;
		});
		order.push_back(u);
	};
	for (nodeid start = 0; start < n; ++start) {
		if (!visited[start]) dfs1(start);
	}

	// Second pass: DFS on transposed graph in reverse finish order
	std::fill(visited.begin(), visited.end(), false);
	compid comp = 0;
	std::function<void(nodeid)> dfs2 = [&](nodeid u) {
		visited[u] = true;
		assignments[u] = comp;
		sizes[comp]++;
		G->forInEdgesOf(u, [&](edgeid, nodeid from, nodeid) {
			if (!visited[from]) dfs2(from);
			return false;
		});
	};
	for (int i = (int)order.size() - 1; i >= 0; --i) {
		nodeid start = order[i];
		if (!visited[start]) {
			comp = (compid)sizes.size();
			sizes.push_back(0);
			dfs2(start);
		}
	}
}


}