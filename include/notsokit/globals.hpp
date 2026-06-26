#ifndef NOTSOKIT_GLOBALS_HPP_
#define NOTSOKIT_GLOBALS_HPP_

#include <algorithm>
#include <limits>
#include <cstdint>
#include <cmath>

namespace notsokit {

using nodeid = uint32_t;
using edgeid = uint32_t;
using edgeweight = double;
using nodeavoid = uint8_t;
using compid = uint32_t; // Strongly connected component ID

constexpr edgeweight infWeight = std::numeric_limits<edgeweight>::infinity();
constexpr nodeid noneNode = std::numeric_limits<nodeid>::max();
constexpr edgeid noneEdge = std::numeric_limits<edgeid>::max();
constexpr compid noneComp = std::numeric_limits<compid>::max();

// Number of vertices settled (extracted from the priority queue) by path search algorithms.
inline uint64_t visitedVerticesCount = 0;

inline bool is_close(double a, double b, double reltol, double abstol) {
	// The min(fabs(a), fabs(b)) is crucial to avoid false positives when one of them is infinite.
    return std::fabs(a - b) <= std::max(reltol * std::min(std::fabs(a), std::fabs(b)), abstol);
}

} // namespace notsokit

#endif // NOTSOKIT_GLOBALS_HPP_
