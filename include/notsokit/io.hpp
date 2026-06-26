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
// edges.csv columns: from, to, weight  (effective combined weight)
inline void writeGraph(const Graph &g, const edgeweight *wc,
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
        out << "from,to,weight\n";
        out << std::setprecision(17);
        g.forEdges([&out, &g, wc](edgeid e, nodeid u, nodeid v) -> bool {
            out << u << ',' << v << ',' << g.getWeight(e, wc) << '\n';
            return false;
        });
    }
}

// Read graph from two CSV files produced by writeGraph.
// Constructs a single-dimension graph with the weights stored in edges.csv.
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

    Graph g(static_cast<nodeid>(avoids.size()), 1, 0, 0);
    g.setAvoidNodes(avoids.data());

    {
        std::ifstream in(edgesFile);
        if (!in) throw std::runtime_error("Cannot open for reading: " + edgesFile);
        std::string line;
        std::getline(in, line); // skip header
        while (std::getline(in, line)) {
            if (line.empty()) continue;
            std::istringstream ss(line);
            std::string fromStr, toStr, weightStr;
            std::getline(ss, fromStr, ',');
            std::getline(ss, toStr, ',');
            std::getline(ss, weightStr, ',');
            nodeid from = static_cast<nodeid>(std::stoul(fromStr));
            nodeid to   = static_cast<nodeid>(std::stoul(toStr));
            edgeweight w = std::stod(weightStr);
            g.addEdge(from, to, &w);
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
