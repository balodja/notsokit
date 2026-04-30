#ifndef NOTSOKIT_GLOBALS_HPP_
#define NOTSOKIT_GLOBALS_HPP_

#include <limits>
#include <cstdint>

namespace notsokit {

using nodeid = uint32_t;
using edgeid = uint32_t;
using edgeweight = double;
using nodeavoid = uint8_t;

constexpr edgeweight infWeight = std::numeric_limits<edgeweight>::infinity();
constexpr nodeid noneNode = std::numeric_limits<nodeid>::max();
constexpr edgeid noneEdge = std::numeric_limits<edgeid>::max();

// Number of vertices settled (extracted from the priority queue) by path search algorithms.
inline uint64_t visitedVerticesCount = 0;

} // namespace notsokit

#endif // NOTSOKIT_GLOBALS_HPP_
