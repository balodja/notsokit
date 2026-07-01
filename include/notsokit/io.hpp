#ifndef NOTSOKIT_IO_HPP
#define NOTSOKIT_IO_HPP

#include <fstream>
#include <iomanip>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
#include <notsokit/globals.hpp>
#include <notsokit/graph.hpp>

namespace notsokit {

// Write graph to two CSV files.
// nodes.csv columns: node_id, avoid
// edges.csv columns: from, to, weight_0, weight_1, ..., weight_{k-1}
inline void writeGraph(const Graph &g,
                       const std::string &nodesFile,
                       const std::string &edgesFile)
{
    {
        std::ofstream out(nodesFile);
        if (!out) throw std::runtime_error("Cannot open for writing: " + nodesFile);
        out << "node_id,avoid\n";
        for (nodeid u = 0; u < g.upperNodeIdBound(); ++u)
            out << u << ',' << static_cast<int>(g.getAvoidNode(u)) << '\n';
    }
    {
        std::ofstream out(edgesFile);
        if (!out) throw std::runtime_error("Cannot open for writing: " + edgesFile);
        out << "from,to";
        for (edgeid d = 0; d < g.numDims(); ++d)
            out << ",weight_" << d;
        out << '\n';
        out << std::setprecision(17);
        g.forEdges([&out, &g](edgeid e, nodeid u, nodeid v) -> bool {
            out << u << ',' << v;
            const edgeweight *w = g.getWeights(e);
            for (edgeid d = 0; d < g.numDims(); ++d)
                out << ',' << w[d];
            out << '\n';
            return false;
        });
    }
}

// Read graph from two CSV files produced by writeGraph.
// Determines the number of weight dimensions from the edges.csv header.
inline Graph readGraph(const std::string &nodesFile,
                       const std::string &edgesFile)
{
    std::vector<nodeavoid> avoids;
    {
        std::ifstream in(nodesFile);
        if (!in) throw std::runtime_error("Cannot open for reading: " + nodesFile);
        std::string line;
        std::getline(in, line); // skip header
        while (std::getline(in, line)) {
            if (line.empty()) continue;
            std::istringstream ss(line);
            std::string nodeIdStr, avoidStr;
            std::getline(ss, nodeIdStr, ',');
            std::getline(ss, avoidStr, ',');
            avoids.push_back(static_cast<nodeavoid>(std::stoi(avoidStr)));
        }
    }

    // Determine number of weight dimensions from the edges header.
    edgeid numDims = 0;
    {
        std::ifstream in(edgesFile);
        if (!in) throw std::runtime_error("Cannot open for reading: " + edgesFile);
        std::string header;
        std::getline(in, header);
        std::istringstream ss(header);
        std::string col;
        edgeid ncols = 0;
        while (std::getline(ss, col, ',')) ++ncols;
        if (ncols < 3) throw std::runtime_error("edges CSV must have at least 3 columns (from,to,weight_0)");
        numDims = ncols - 2;
    }

    Graph g(static_cast<nodeid>(avoids.size()), numDims, 0, 0);
    g.setAvoidNodes(avoids.data());

    {
        std::ifstream in(edgesFile);
        if (!in) throw std::runtime_error("Cannot open for reading: " + edgesFile);
        std::string line;
        std::getline(in, line); // skip header
        std::vector<edgeweight> weights(numDims);
        while (std::getline(in, line)) {
            if (line.empty()) continue;
            std::istringstream ss(line);
            std::string fromStr, toStr;
            std::getline(ss, fromStr, ',');
            std::getline(ss, toStr, ',');
            nodeid from = static_cast<nodeid>(std::stoul(fromStr));
            nodeid to   = static_cast<nodeid>(std::stoul(toStr));
            for (edgeid d = 0; d < numDims; ++d) {
                std::string wStr;
                std::getline(ss, wStr, ',');
                weights[d] = std::stod(wStr);
            }
            g.addEdge(from, to, weights.data());
        }
    }

    return g;
}

// Write heuristics (one edgeweight per node) to a CSV file.
// Column: node_id, heuristic
inline void writeHeuristics(const std::vector<edgeweight> &heu,
                            const std::string &heuFile)
{
    std::ofstream out(heuFile);
    if (!out) throw std::runtime_error("Cannot open for writing: " + heuFile);
    out << "node_id,heuristic\n";
    out << std::setprecision(17);
    for (std::size_t i = 0; i < heu.size(); ++i)
        out << i << ',' << heu[i] << '\n';
}

// Read heuristics from a CSV file produced by writeHeuristics.
inline std::vector<edgeweight> readHeuristics(const std::string &heuFile)
{
    std::ifstream in(heuFile);
    if (!in) throw std::runtime_error("Cannot open for reading: " + heuFile);
    std::vector<edgeweight> heu;
    std::string line;
    std::getline(in, line); // skip header
    while (std::getline(in, line)) {
        if (line.empty()) continue;
        std::istringstream ss(line);
        std::string nodeIdStr, valStr;
        std::getline(ss, nodeIdStr, ',');
        std::getline(ss, valStr, ',');
        heu.push_back(std::stod(valStr));
    }
    return heu;
}

} // namespace notsokit

#endif // NOTSOKIT_IO_HPP
