#ifndef NOTSOKIT_DISTANCE_HPP_
#define NOTSOKIT_DISTANCE_HPP_

#include <notsokit/globals.hpp>
#include <limits>


namespace notsokit {

using predid = uint32_t;

constexpr predid nonePred = std::numeric_limits<predid>::max();

struct Predecessor {
	nodeid node;
	edgeid edge;
	predid previous;
};

} // namespace notsokit

#endif // NOTSOKIT_DISTANCE_HPP_