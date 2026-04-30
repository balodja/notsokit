#include <algorithm>
#include <notsokit/distance/dijkstra.hpp>
#include <notsokit/globals.hpp>

namespace notsokit {

Dijkstra::Dijkstra(const Graph &G, nodeid source)
    : G(&G),
	source(source),
	distances(G.upperNodeIdBound()),
	preNodes(G.upperNodeIdBound()),
	preEdges(G.upperNodeIdBound()),
	heap(Aux::LessInVector<double>(distances))
{}

void Dijkstra::run() {
	if (hasRun)
		return;

    std::fill(distances.begin(), distances.end(), infWeight);

    distances[source] = 0.;
    heap.clear();
    heap.push(source);

    do {
        nodeid u = heap.extract_top();
        ++visitedVerticesCount;

        if (distances[u] == infWeight)
            break;

        G->forOutEdgesOf(u, [&](edgeid e, nodeid uu, nodeid v, edgeweight w) {
            edgeweight newDist = distances[u] + w;

			if (newDist == infWeight)
                return false;

            if (distances[v] == infWeight) {
                distances[v] = newDist;
                heap.push(v);
				preNodes[v] = u;
				preEdges[v] = e;
            } else if (distances[v] > newDist) {
                distances[v] = newDist;
                heap.update(v);
				preNodes[v] = u;
				preEdges[v] = e;
            }

			return false;
        });
    } while (!heap.empty());

    hasRun = true;
}

vector<edgeid> Dijkstra::getPath(nodeid target) const {
	vector<edgeid> path;
	if (!hasRun || distances[target] == infWeight)
		return path;

	for (nodeid u = target; u != source; u = preNodes[u]) {
		path.push_back(preEdges[u]);
	}
	std::reverse(path.begin(), path.end());
	return path;
}

} // namespace notsokit
