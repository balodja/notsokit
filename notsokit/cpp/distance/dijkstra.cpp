#include <algorithm>
#include <notsokit/distance/dijkstra.hpp>
#include <notsokit/globals.hpp>

namespace notsokit {

Dijkstra::Dijkstra(const Graph *G, const edgeweight *wc, nodeid source)
    : G(G),
	wc(wc),
	source(source),
	distances(G->upperNodeIdBound(), infWeight),
	preds(G->upperNodeIdBound(), nonePred),
	preds_pool()
{}

void Dijkstra::run() {
	if (hasRun)
		return;
	
	nodeid n = G->upperNodeIdBound();
	edgeweight reltol, abstol;
	std::tie(reltol, abstol) = G->getTolerance();

    distances[source] = 0.;

    tlx::d_ary_addressable_int_heap<nodeid, 2, Aux::LessInVector<edgeweight>> heap(distances);
	heap.reserve(n);
    heap.push(source);

    do {
        nodeid u = heap.extract_top();
        ++visitedVerticesCount;

        if (distances[u] == infWeight)
            break;

        G->forOutEdgesOf(u, wc, [&](edgeid e, nodeid uu, nodeid v, edgeweight w) {
            edgeweight newDist = distances[u] + w;

			if (newDist == infWeight)
                return false;

            if (is_close(newDist, distances[v], reltol, abstol)) {
				preds_pool.push_back({u, e, preds[v]});
				preds[v] = preds_pool.size() - 1;

				if (preds_pool.size() == nonePred) {
					throw std::runtime_error("Dijkstra::run: Predecessor pool overflow.");
				}
            } else if (distances[v] > newDist) {
                distances[v] = newDist;
                heap.update(v);

				preds_pool.push_back({u, e, nonePred});
				preds[v] = preds_pool.size() - 1;
            }

			return false;
        });
    } while (!heap.empty());

    hasRun = true;
}

vector<vector<edgeid>> Dijkstra::getPaths(nodeid target) const {
	if (!hasRun || distances[target] == infWeight)
		return {};

	return predPoolGetPaths(preds, preds_pool, source, target);
}

} // namespace notsokit
