cmake_minimum_required(VERSION 3.14)
project(notsokit CXX)

if("${PROJECT_SOURCE_DIR}" STREQUAL "${PROJECT_BINARY_DIR}")
	message(SEND_ERROR "In-source builds are not allowed.")
endif("${PROJECT_SOURCE_DIR}" STREQUAL "${PROJECT_BINARY_DIR}")

# BUILD OPTIONS
option(NOTSOKIT_BUILD_CORE "Build notsokit core library" ON)
option(NOTSOKIT_BUILD_TESTS "Build notsokit C++ tests" OFF)
option(NOTSOKIT_QUIET_LOGGING "Set log level to QUIET by default (can still be changed at run time)" OFF)
option(NOTSOKIT_STATIC "Build static libraries" OFF)
option(NOTSOKIT_MONOLITH "Build single library (and tests is requested; required for shared lib)" ON)
option(NOTSOKIT_NATIVE "Optimize for native architecture (often better performance)" OFF)
option(NOTSOKIT_WARNINGS "Issue more warnings" OFF)
option(NOTSOKIT_WARNINGS_AS_ERRORS "Treat warnings as errors" OFF)
option(NOTSOKIT_CLANG_TIDY "Check code with clang-tidy" OFF)
option(NOTSOKIT_FLATINSTALL "Install into a flat directory structure (useful when building a Python package)" OFF)
option(NOTSOKIT_COVERAGE "Build with support for coverage" OFF)
option(NOTSOKIT_SANITY_CHECKS "Algorithms will perform further (expensive) checks" OFF)
set(NOTSOKIT_PYTHON "" CACHE STRING "Directory containing Python.h. Implies MONOLITH=TRUE")
set(NOTSOKIT_NUMPY "" CACHE STRING "Directory containing Numpy.h.")
set(NOTSOKIT_PYTHON_SOABI "" CACHE STRING "Platform specific file extension. Implies MONOLITH=TRUE")
set(NOTSOKIT_WITH_SANITIZERS "" CACHE STRING "Uses sanitizers during the compilation")
set(NOTSOKIT_RELEASE_LOGGING "AUTO" CACHE STRING "Do not compile log messages at levels TRACE or DEBUG (AUTO|ON|OFF)")
set(NOTSOKIT_PYTHON_RPATH "" CACHE STRING "Build specific rpath references.")
set(NOTSOKIT_EXT_TLX "" CACHE STRING "Absolute path for external tlx-library. If not set, extlibs/tlx is used")

set (NOTSOKIT_CXX_STANDARD "20" CACHE STRING "CXX Version to compile with. Currently fixed to 20")

# Allow user to set installation paths relative to CMAKE_INSTALL_PREFIX

set(NOTSOKIT_INSTALL_BIN_DIR "bin"
	CACHE PATH "Installation directory for executables")
set(NOTSOKIT_INSTALL_LIB_DIR "lib"
	CACHE PATH "Installation directory for libraries")
set(NOTSOKIT_INSTALL_INCLUDE_DIR "include"
	CACHE PATH "Installation directory for header files")
set(NOTSOKIT_INSTALL_PKGCONFIG_DIR "lib/pkgconfig"
	CACHE PATH "Installation directory for pkg-config file")

if (NOTSOKIT_PYTHON)
	if (NOT NOTSOKIT_MONOLITH)
		message(FATAL_ERROR "When building notsokit as a Python module, NOTSOKIT_MONOLITH=ON is required")
	endif()
	if(NOT NOTSOKIT_PYTHON_SOABI)
		message(WARNING "No platform-specific file extension provided. Do not distribute library.")
	endif()
endif()

if (NOT CMAKE_BUILD_TYPE)
	message("Use Release Build Type as default")
	set(CMAKE_BUILD_TYPE "Release")
endif()

################################################################################
# Compilation Flags
set(NOTSOKIT_CXX_FLAGS "")
set(NOTSOKIT_LINK_FLAGS "")

if (NOTSOKIT_QUIET_LOGGING)
	set(NOTSOKIT_CXX_FLAGS "-DNOTSOKIT_QUIET_LOGGING")
endif()

if (NOTSOKIT_RELEASE_LOGGING STREQUAL "AUTO")
	if (NOT CMAKE_BUILD_TYPE STREQUAL "Debug")
		set(NOTSOKIT_RELEASE_LOGGING "ON")
	else()
		set(NOTSOKIT_RELEASE_LOGGING "OFF")
	endif()
endif()

if (NOTSOKIT_RELEASE_LOGGING STREQUAL "ON")
	set(NOTSOKIT_CXX_FLAGS "${NOTSOKIT_CXX_FLAGS} -DNOTSOKIT_RELEASE_LOGGING")
elseif(NOT NOTSOKIT_RELEASE_LOGGING STREQUAL "OFF")
	message(FATAL_ERROR "Unsupported setting ${NOTSOKIT_RELEASE_LOGGING} for NOTSOKIT_RELEASE_LOGGING")
endif()

if (("${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang") OR
	("${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU") OR
	("${CMAKE_CXX_COMPILER_ID}" STREQUAL "AppleClang"))
	if (NOTSOKIT_NATIVE)
		set(NOTSOKIT_CXX_FLAGS "${NOTSOKIT_CXX_FLAGS} -march=native")
	endif()
	if (NOTSOKIT_WARNINGS)
		set(NOTSOKIT_CXX_FLAGS "${NOTSOKIT_CXX_FLAGS} -Wall -Wextra -Wpedantic")
	endif()
	if (NOTSOKIT_WARNINGS_AS_ERRORS)
		set(NOTSOKIT_CXX_FLAGS "${NOTSOKIT_CXX_FLAGS} -Werror")
	endif()

elseif (MSVC)
	set(NOTSOKIT_CXX_FLAGS "${NOTSOKIT_CXX_FLAGS} /DNOTSOKIT_OMP2 /MP /DNOTSOKIT_WINDOWS /permissive-")

	# TTMath requires running an ASM for MSVC which we disable here at the cost of worse performance
	set(NOTSOKIT_CXX_FLAGS "${NOTSOKIT_CXX_FLAGS} /DTTMATH_NOASM=1")

	if (NOTSOKIT_NATIVE)
		message(WARNING "Compiling notsokit with native instructions is not yet supported by MSVC. Activating AVX2-support if possible.")
		include(CheckCXXCompilerFlag)
		CHECK_CXX_COMPILER_FLAG("/arch:AVX2" COMPILER_OPT_ARCH_AVX_SUPPORTED)
		if(COMPILER_OPT_ARCH_AVX_SUPPORTED)
			set(NOTSOKIT_CXX_FLAGS "${NOTSOKIT_CXX_FLAGS} /arch:AVX2")
		endif()
	endif()

else()
	message(WARNING "Support only GCC, Clang, MSVC and AppleClang. Your compiler may or may not work.")
endif()

# Checking sanitizer options; in both cases we include 'undefined'
set(NOTSOKIT_CXX_SANITIZERS "")
if ("${NOTSOKIT_WITH_SANITIZERS}" STREQUAL "address")
	set(NOTSOKIT_CXX_SANITIZERS "address,undefined")
elseif ("${NOTSOKIT_WITH_SANITIZERS}" STREQUAL "leak")
	set(NOTSOKIT_CXX_SANITIZERS "address,leak,undefined")
elseif(NOT "${NOTSOKIT_WITH_SANITIZERS}" STREQUAL "")
	message(FATAL_ERROR "Unsupported option ${NOTSOKIT_WITH_SANITIZERS}")
endif()

if (NOT "${NOTSOKIT_CXX_SANITIZERS}" STREQUAL "")
    set(NOTSOKIT_CXX_FLAGS "-fsanitize=${NOTSOKIT_CXX_SANITIZERS} ${NOTSOKIT_CXX_FLAGS}")
    set(NOTSOKIT_LINK_FLAGS "-fsanitize=${NOTSOKIT_CXX_SANITIZERS} ${NOTSOKIT_LINK_FLAGS}")
endif()

# Check if coverage support is enabled
if (NOTSOKIT_COVERAGE)
  set(NOTSOKIT_CXX_FLAGS "${NOTSOKIT_CXX_FLAGS} --coverage")
  set(NOTSOKIT_LINK_FLAGS "${NOTSOKIT_LINK_FLAGS} --coverage")
endif()

################################################################################
# ENABLE ADDITIONAL SANITY CHECKS
if (NOTSOKIT_SANITY_CHECKS)
    set(NOTSOKIT_CXX_FLAGS "${NOTSOKIT_CXX_FLAGS} -DNOTSOKIT_SANITY_CHECKS")
endif()


# finding or creating OpenMP target. This is likely to fail for CMake Version < 3.12.
find_package(OpenMP)

# FindOpenMP.cmake does not reliably find a user installed openmp library for clang/llvm on
# both Linux- and macOS-systems (even for CMake Version >= 3.12). The following section
# manually sets the required fields for clang-like compiler.
if(NOT OpenMP_FOUND)
	if("${CMAKE_CXX_COMPILER_ID}" STREQUAL "AppleClang")
		# This will find default libomp-installations for homebrew/MacPorts
		find_library(LIBOMP_PATH NAMES omp PATHS "/usr/local/opt/libomp/lib" "/opt/local/lib/libomp" "/opt/homebrew/opt/libomp/lib")
		find_path(LIBOMP_INCLUDE NAMES omp.h PATHS "/usr/local/opt/libomp/include" "/opt/local/include/libomp" "/opt/homebrew/opt/libomp/include")
		if(LIBOMP_PATH AND LIBOMP_INCLUDE)
			set(OpenMP_CXX_FLAGS "-Xpreprocessor -fopenmp -I${LIBOMP_INCLUDE}" CACHE STRING "Manually set" FORCE)
		endif()
	elseif("${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang")
		find_library(LIBOMP_PATH NAMES omp PATHS "/usr/lib" "/usr/lib64" "/opt/local/lib/libomp" "/opt/homebrew/opt/libomp/lib")
		find_path(LIBOMP_INCLUDE NAMES omp.h PATHS "/usr/include" "/usr/local/opt/libomp/include" "/opt/local/include/libomp" "/opt/homebrew/opt/libomp/include")
		set(OpenMP_CXX_FLAGS "-fopenmp -I${LIBOMP_INCLUDE}" CACHE STRING "Manually set" FORCE)
	endif()

	# If libomp was not found yet, try to find it in conda environment
	if(NOT LIBOMP_PATH OR NOT LIBOMP_INCLUDE)
			find_library(LIBOMP_PATH NAMES omp HINTS "$ENV{CONDA_PREFIX}/lib"
				PATHS "/usr/lib" "/usr/lib64")
			find_path(LIBOMP_INCLUDE NAMES omp.h HINTS "$ENV{CONDA_PREFIX}/include"
				PATHS "/usr/include")
	endif()

	# Set OpenMP-folders in case they are found with the aid of additional hints
	if(LIBOMP_PATH AND LIBOMP_INCLUDE)
		set(OpenMP_CXX_LIB_NAMES "omp" CACHE STRING "Manually set" FORCE)
		set(OpenMP_omp_LIBRARY "${LIBOMP_PATH}" CACHE STRING "Manually set" FORCE)
	else()
		message(FATAL_ERROR "libomp was not found, but necessary to run notsokit with ${CMAKE_CXX_COMPILER_ID}")
	endif()

	# After setting basic OpenMP-folders, run find_package again to set everything. Also acts as a final sanity check.
	find_package(OpenMP REQUIRED)
endif()

if(NOT TARGET OpenMP::OpenMP_CXX)
	message("Creating custom OpenMP target for CMake Version < 3.12. Current CMake Version ${CMAKE_VERSION}")
	find_package(Threads REQUIRED)
	add_library(OpenMP::OpenMP_CXX IMPORTED INTERFACE)
	set_property(TARGET OpenMP::OpenMP_CXX
				 PROPERTY INTERFACE_COMPILE_OPTIONS ${OpenMP_CXX_FLAGS})
	set_property(TARGET OpenMP::OpenMP_CXX
				 PROPERTY INTERFACE_LINK_LIBRARIES ${OpenMP_CXX_FLAGS} Threads::Threads)
endif()

if (CMAKE_SIZEOF_VOID_P LESS 8)
	if (MSVC)
		message(FATAL_ERROR "notsokit supports only 64bit builds.
		                     Make sure to select a x64 target rather than x86, e.g. when invoking cmake with -G")
	else()
		message(FATAL_ERROR "notsokit supports only 64bit builds")
	endif()
endif()

# specify linking flags for MacOS
if (APPLE)
	set(NOTSOKIT_LINK_FLAGS "-undefined dynamic_lookup ${NOTSOKIT_LINK_FLAGS}")
endif()

if(NOT NOTSOKIT_BUILD_CORE)
	if(WIN32)
		message(FATAL_ERROR "Make sure to enable NOTSOKIT_BUILD_CORE. notsokit on Windows does not support Python-builds with external core-libs.")
	endif()
	find_library(EXTERNAL_NOTSOKIT_CORE NAMES notsokit DOC "External notsokit core library")
endif()

if(NOTSOKIT_FLATINSTALL)
	set(NOTSOKIT_LIB_DEST ".")
else()
	set(NOTSOKIT_LIB_DEST "lib/")
endif()

################################################################################
# Use TLX as a CMake submodule
if(NOT NOTSOKIT_EXT_TLX)
	if(EXISTS "${PROJECT_SOURCE_DIR}/extlibs/tlx/CMakeLists.txt")
		add_subdirectory(extlibs/tlx)
	else()
		message(FATAL_ERROR
				"Missing TLX library in extlibs/tlx "
				"Please run `git submodule update --init` to fetch the submodule.")
	endif()
else()
	add_library(tlx STATIC IMPORTED)
	set_target_properties(tlx PROPERTIES
			IMPORTED_LOCATION "${NOTSOKIT_EXT_TLX}/lib/${CMAKE_SHARED_LIBRARY_PREFIX}tlx${CMAKE_STATIC_LIBRARY_SUFFIX}"
			INTERFACE_INCLUDE_DIRECTORIES "${NOTSOKIT_EXT_TLX}/include/")
endif()

################################################################################
# NOTSOKIT MODULES
if(NOTSOKIT_BUILD_CORE AND NOTSOKIT_MONOLITH)

	if(NOTSOKIT_STATIC)
		add_library(notsokit notsokit/cpp/notsokit.cpp)
	else()
		if(WIN32)
			message(FATAL_ERROR
					"Windows does only support static builds. Call cmake with '-DNOTSOKIT_STATIC=ON'.")
		endif()
		add_library(notsokit SHARED notsokit/cpp/notsokit.cpp)
	endif()

	if(WIN32)
		# For Windows all global shared variables have to be exported additionally as dll
		add_library(notsokit_state SHARED notsokit/cpp/GlobalState.cpp)

		set_target_properties(notsokit_state PROPERTIES
				CXX_STANDARD ${NOTSOKIT_CXX_STANDARD}
				COMPILE_FLAGS "${NOTSOKIT_CXX_FLAGS} /DNOTSOKIT_BUILDING_STATELIB"
				LINK_FLAGS "${NOTSOKIT_LINK_FLAGS}")

		install(TARGETS notsokit_state
				LIBRARY DESTINATION "${NOTSOKIT_LIB_DEST}/notsokit"
				ARCHIVE DESTINATION "${NOTSOKIT_LIB_DEST}/notsokit"
				RUNTIME DESTINATION "${NOTSOKIT_LIB_DEST}/notsokit")

		target_link_libraries(notsokit PUBLIC notsokit_state)
		target_link_libraries(notsokit_state PUBLIC tlx)
		target_include_directories(notsokit_state BEFORE PUBLIC "${PROJECT_SOURCE_DIR}/include")
	endif()

	target_link_libraries(notsokit PRIVATE OpenMP::OpenMP_CXX PUBLIC tlx)

	set_target_properties(notsokit PROPERTIES
			CXX_STANDARD ${NOTSOKIT_CXX_STANDARD}
			COMPILE_FLAGS "${NOTSOKIT_CXX_FLAGS}"
			LINK_FLAGS "${NOTSOKIT_LINK_FLAGS}")
	
	install(TARGETS notsokit
			LIBRARY DESTINATION ${NOTSOKIT_LIB_DEST}
			ARCHIVE DESTINATION ${NOTSOKIT_LIB_DEST}
			RUNTIME DESTINATION ${NOTSOKIT_LIB_DEST})

	target_include_directories(notsokit BEFORE PUBLIC "${PROJECT_SOURCE_DIR}/include")
	target_include_directories(notsokit PUBLIC "${PROJECT_SOURCE_DIR}/extlibs/ttmath/")

endif()

################################################################################
# ENABLE CLANG-TIDY
if (NOTSOKIT_CLANG_TIDY)
	if ("${CMAKE_CXX_COMPILER_ID}" STREQUAL "Clang")
		set_target_properties(notsokit PROPERTIES CXX_CLANG_TIDY clang-tidy)
	else()
		message(FATAL_ERROR "clang-tidy is only supported when compiling with clang")
	endif()
endif()

if(NOTSOKIT_PYTHON)

	if(WIN32)
		# Linking against Python3_libs is only neccessary on Windows. On other OSes 
		# this can lead to segmentation faults when importing notsokit in Python.
		if(${CMAKE_VERSION} VERSION_LESS "3.12.0") 
			FIND_PACKAGE(FindPythonLibs ${NOTSOKIT_PYTHON_VERSION} EXACT REQUIRED)
		else()
			FIND_PACKAGE(Python3 ${NOTSOKIT_PYTHON_VERSION} EXACT COMPONENTS Interpreter Development REQUIRED)
		endif()
	endif()
	
	foreach (EXT graph distance)

		if(NOT EXISTS "${PROJECT_SOURCE_DIR}/notsokit/${EXT}.cpp")
			message(FATAL_ERROR "notsokit/${EXT}.cpp is missing. Invoke Cython manually.")
		endif()

		set(TARGET_LIB ${EXT})

		add_library(${TARGET_LIB} MODULE notsokit/${EXT}.cpp)
		target_include_directories(${TARGET_LIB} BEFORE PUBLIC "${PROJECT_SOURCE_DIR}/include")
		target_include_directories(${TARGET_LIB} PRIVATE "${PROJECT_SOURCE_DIR}/extlibs/ttmath/")
		target_include_directories(${TARGET_LIB} PRIVATE "${NOTSOKIT_PYTHON}")
		target_include_directories(${TARGET_LIB} PUBLIC "${NOTSOKIT_NUMPY}")

		if(NOT NOTSOKIT_BUILD_CORE)
			if(NOT EXTERNAL_NOTSOKIT_CORE)
				message(FATAL_ERROR "Core build is disabled but no external core library was found.")
			endif()
			target_link_libraries(${TARGET_LIB} PRIVATE ${EXTERNAL_NOTSOKIT_CORE})
		else()
			target_link_libraries(${TARGET_LIB} PRIVATE notsokit)
		endif()

		set_target_properties(${TARGET_LIB} PROPERTIES
					CXX_STANDARD ${NOTSOKIT_CXX_STANDARD}
					COMPILE_FLAGS "${NOTSOKIT_CXX_FLAGS}"
					LINK_FLAGS "${NOTSOKIT_LINK_FLAGS}"
					PREFIX ""
					OUTPUT_NAME "${TARGET_LIB}.${NOTSOKIT_PYTHON_SOABI}")

		if (NOTSOKIT_BUILD_TESTS)
			target_compile_definitions(${TARGET_LIB} PRIVATE CYTHON_TRACE=1 CYTHON_TRACE_NOGIL=1)
		endif()

		if(WIN32)
			set_target_properties(${TARGET_LIB} PROPERTIES SUFFIX .pyd)
			target_link_libraries(${TARGET_LIB} PRIVATE ${Python3_LIBRARIES})
		endif()

		# If rpath-content is set explicitly, omit the dynamic binary path
		if(NOTSOKIT_PYTHON_RPATH)
			set_target_properties(${TARGET_LIB} PROPERTIES
				INSTALL_RPATH "${NOTSOKIT_PYTHON_RPATH}")
		else()
			# DSOs on Apple OSes use different conventions for RPATH.
			if(APPLE)
				set_target_properties(${TARGET_LIB} PROPERTIES
					INSTALL_RPATH "@loader_path/..")
			else()
				set_target_properties(${TARGET_LIB} PROPERTIES
					INSTALL_RPATH "$ORIGIN/..")
			endif()
		endif()

		target_link_libraries(${TARGET_LIB} PRIVATE OpenMP::OpenMP_CXX PUBLIC tlx)

		install(TARGETS ${TARGET_LIB}
			LIBRARY DESTINATION "${NOTSOKIT_LIB_DEST}/notsokit")
	endforeach()
endif()

# Register a new notsokit module named ${modname}
# Files additionally passed are interpreted as PUBLIC source files to this module
function(notsokit_add_module modname)
	if(NOT NOTSOKIT_BUILD_CORE)
		return()
	endif()

	if(NOTSOKIT_MONOLITH)
		# in case we are building a monolith, no submodule are registered
		# and we simple add the source file to the networkkit target
		set(MODULE_TARGET "notsokit")
	else()
		set(MODULE_TARGET "notsokit_${modname}")

		add_library(${MODULE_TARGET}
					${PROJECT_SOURCE_DIR}/notsokit/cpp/notsokit.cpp)

		set_target_properties(${MODULE_TARGET} PROPERTIES
			CXX_STANDARD ${NOTSOKIT_CXX_STANDARD}
			COMPILE_FLAGS "${NOTSOKIT_CXX_FLAGS}"
			LINK_FLAGS "${NOTSOKIT_LINK_FLAGS}")

		target_link_libraries(${MODULE_TARGET} PRIVATE OpenMP::OpenMP_CXX PUBLIC tlx)
		target_include_directories(${MODULE_TARGET} BEFORE PUBLIC "${PROJECT_SOURCE_DIR}/include")
		target_include_directories(${MODULE_TARGET} PUBLIC "${PROJECT_SOURCE_DIR}/extlibs/ttmath/")

		# All tests added to this module will will also become a dependency
		# of notsokit_tests_MODNAME. This target hence allows to build all
		# tests associated with this module
		if (NOTSOKIT_BUILD_TESTS)
			add_custom_target(notsokit_tests_${modname})
		endif()
	endif()


	# Add source files (it's important to mark them private; otherwise
	# all targets linking to the lib, will recompile the objects from scratch)
	foreach(file ${ARGN})
		target_sources(${MODULE_TARGET}
			PRIVATE ${CMAKE_CURRENT_LIST_DIR}/${file})
	endforeach()
endfunction()

# Analogous to target_link_libraries with KEYWORDS.
# Use the module's name (without notsokit_ prefix) for target.
# In case of monolithic builds, the call is ignored.
# To link against another module use notsokit_module_link_modules
# Example: notsokit_module_link_libraries(graph PRIVATE foobar_lib)
function(notsokit_module_link_libraries modname)
	set(options )
	set(oneValueArgs )
	set(multiValueArgs PRIVATE PUBLIC)
	cmake_parse_arguments(NMLL
		"${options}" "${oneValueArgs}" "${multiValueArgs}" ${ARGN})

	if(NOT NOTSOKIT_BUILD_CORE)
		return()
	endif()

	if(NOT NOTSOKIT_MONOLITH)
		target_link_libraries(notsokit_${modname}
			PRIVATE ${NMLL_PRIVATE}
			PUBLIC ${NMLL_PUBLIC})
	endif()
endfunction()

# Specifiy inter-module dependencies. The function expects a list of at least
# two module names (without the notsokit_ prefix). The first one add all following
# ones as dependencies. In case of monolith build, the function does nothing.
# Example: notsokit_module_link_modules(io graph) # io depends on graph
function(notsokit_module_link_modules modname)
	if(NOT NOTSOKIT_BUILD_CORE)
		return()
	endif()

	if(NOT NOTSOKIT_MONOLITH)
		foreach(dep IN LISTS ARGN)
			target_link_libraries(notsokit_${modname} PUBLIC notsokit_${dep})
		endforeach()
	endif()
endfunction()

################################################################################
# TESTING and BENCHMARKING
if (NOTSOKIT_BUILD_TESTS)
	enable_testing()

	if(EXISTS "${PROJECT_SOURCE_DIR}/extlibs/googletest/CMakeLists.txt")
		if (MSVC)
			# While by default MSVC projects link against the shared runtime library
			# (and hence also notsokit), GTest defaults to the static runtime lib.
			# Both must not be mix, so we request GTest here to also use the shared CRT.
			set( gtest_force_shared_crt ON CACHE BOOL "Always use msvcrt.dll" FORCE)
		endif()
		option(BUILD_GTEST "Builds the googletest subproject" ON)
		option(BUILD_GMOCK "Builds the googlemock subproject" ON)
		add_subdirectory(extlibs/googletest)
	else()
		message(FATAL_ERROR
			"Missing GoogleTest and GoogleMock in extlibs/googletest. "
			"Please run `git submodule update --init` to fetch the submodule.")
	endif()

	if (NOTSOKIT_MONOLITH)
		add_executable(notsokit_tests notsokit/cpp/Unittests-X.cpp)

		target_link_libraries(notsokit_tests
			PRIVATE
				gtest
				gmock
				notsokit
				tlx
				OpenMP::OpenMP_CXX
		)

		if(WIN32)
			target_link_libraries(notsokit_tests
				PRIVATE
					notsokit_state
			)
		endif()

		if(WIN32)
			set(NOTSOKIT_CXX_FLAGS "${NOTSOKIT_CXX_FLAGS} /wd4996")
		else()
			set(NOTSOKIT_CXX_FLAGS "${NOTSOKIT_CXX_FLAGS} -Wno-deprecated-declarations")
		endif()
		set_target_properties(notsokit_tests PROPERTIES
			CXX_STANDARD ${NOTSOKIT_CXX_STANDARD}
			COMPILE_FLAGS "${NOTSOKIT_CXX_FLAGS}"
			LINK_FLAGS "${NOTSOKIT_LINK_FLAGS}")

		add_test(
			NAME notsokit_tests
			COMMAND notsokit_tests -t --srcloc
			WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
		)

		add_test(
			NAME notsokit_tests_no_assertions
			COMMAND notsokit_tests -r --srcloc
			WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
		)

	else()
		add_library(notsokit_gtest_main STATIC notsokit/cpp/Unittests-X.cpp)

		set_target_properties(notsokit_gtest_main PROPERTIES
				CXX_STANDARD ${NOTSOKIT_CXX_STANDARD}
				COMPILE_FLAGS "${NOTSOKIT_CXX_FLAGS}"
				LINK_FLAGS "${NOTSOKIT_LINK_FLAGS}")

		target_link_libraries(notsokit_gtest_main
				PUBLIC
					gtest
					gmock
				PRIVATE
					tlx
					notsokit_auxiliary
					OpenMP::OpenMP_CXX
		)
	endif()
endif()

# internal use only
# IS_TEST   indicates whether add_test should be invoked for executable
#		   an whether it should be assigned to the module's test target
# MOD	   Name of module the test/benchmark assigned to. It will
#		   join its namespace, assigned to its test target and linked
# TESTNAME  Name of the CPP File (excluding its .cpp extension). Will
#		   also be used to derive the test's name
function(notsokit_add_extra IS_TEST MOD NAME)
	if (NOTSOKIT_BUILD_TESTS)
		set(TEST_SOURCE ${CMAKE_CURRENT_LIST_DIR}/${NAME}.cpp)

		if (NOTSOKIT_MONOLITH)
			target_sources(notsokit_tests PRIVATE ${TEST_SOURCE})

		else()
			if (NOT TARGET notsokit_${MOD})
				MESSAGE(FATAL_ERROR "Unknown notsokit module '${MOD}'")
			endif()

			set(TARGET_NAME "notsokit_${MOD}_${NAME}")

			add_executable(${TARGET_NAME} ${TEST_SOURCE})

			target_link_libraries(${TARGET_NAME}
				PRIVATE
					gtest notsokit_gtest_main
				PRIVATE
					notsokit_${MOD}
					tlx
					OpenMP::OpenMP_CXX
					)
			set_target_properties(${TARGET_NAME} PROPERTIES
				CXX_STANDARD ${NOTSOKIT_CXX_STANDARD}
				COMPILE_FLAGS "${NOTSOKIT_CXX_FLAGS}"
				LINK_FLAGS "${NOTSOKIT_LINK_FLAGS}")

			foreach(dep IN LISTS ARGN)
				target_link_libraries(${TARGET_NAME} PRIVATE notsokit_${dep})
			endforeach()

			if (${IS_TEST})
				add_dependencies(notsokit_tests_${MOD} ${TARGET_NAME})

				add_test(
					NAME "${MOD}/${NAME}"
					COMMAND ${TARGET_NAME} -t --srcloc
					WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
					)

				add_test(
					NAME "${MOD}/${NAME}_no_assertions"
					COMMAND ${TARGET_NAME} -r --srcloc
					WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
				)
			endif()
		endif()
	endif()
endfunction()

# Wrapper for notsokit_add_extra with (IS_TEST=ON)
# Example: notsokit_add_test(io SpecialIOGTest graph) compiles
#  io/test/SpecialIOGTest.cpp, registers is as an test of notsokit_tests_io
#  and links it against io and graph.
function(notsokit_add_test MOD NAME)
	notsokit_add_extra(ON ${MOD} ${NAME} ${ARGN})
endfunction(notsokit_add_test)

# Wrapper for notsokit_add_extra with (IS_TEST=OFF)
function(notsokit_add_benchmark MOD NAME)
	notsokit_add_extra(OFF ${MOD} ${NAME} ${ARGN})
endfunction(notsokit_add_benchmark)


################################################################################
# Benchmarks

# In case of monolithic builds we add the target notsokit_benchmarks, and later add
# source files via notsokit_add_gbenchmark. In case of non-monolithic builds, each
# notsokit_add_test creates it own target.
if (NOTSOKIT_BUILD_BENCHMARKS AND NOTSOKIT_MONOLITH)
	add_executable(notsokit_benchmarks notsokit/cpp/notsokit.cpp)

	target_link_libraries(notsokit_benchmarks
			PRIVATE
			benchmark_main benchmark
			notsokit
			)

	set_target_properties(notsokit_tests PROPERTIES
			CXX_STANDARD ${NOTSOKIT_CXX_STANDARD}
			COMPILE_FLAGS "${NOTSOKIT_CXX_FLAGS}"
			LINK_FLAGS "${NOTSOKIT_LINK_FLAGS}")
endif()

function(notsokit_add_gbenchmark MOD NAME)
	if (NOTSOKIT_BUILD_BENCHMARKS)
		set(BENCH_SOURCE ${CMAKE_CURRENT_LIST_DIR}/${NAME}.cpp)

		if (NOTSOKIT_MONOLITH)
			target_sources(notsokit_benchmarks PRIVATE ${BENCH_SOURCE})

		else()
			if (NOT TARGET notsokit_${MOD})
				MESSAGE(FATAL_ERROR "Unknown notsokit module '${MOD}'")
			endif()

			set(TARGET_NAME "notsokit_${MOD}_${NAME}")

			add_executable(${TARGET_NAME} ${BENCH_SOURCE})
			message("${TARGET_NAME}: ${BENCH_SOURCE}")

			target_link_libraries(${TARGET_NAME}
				PRIVATE
					benchmark_main benchmark
					notsokit_${MOD})

			set_target_properties(${TARGET_NAME} PROPERTIES
					CXX_STANDARD ${NOTSOKIT_CXX_STANDARD}
					COMPILE_FLAGS "${NOTSOKIT_CXX_FLAGS}"
					LINK_FLAGS "${NOTSOKIT_LINK_FLAGS}")

			foreach(dep IN LISTS ARGN)
				target_link_libraries(${TARGET_NAME} PRIVATE notsokit_${dep})
			endforeach()
		endif()
	endif()
endfunction(notsokit_add_gbenchmark)

################################################################################
# Documentation

find_program(SPHINX_EXECUTABLE
	NAMES
		sphinx-build sphinx-build.exe
	PATHS
		/usr/bin
		/usr/local/bin
		/opt/local/bin
	DOC "Sphinx documentation generator")

if (NOT SPHINX_EXECUTABLE)
	message(STATUS "sphinx-build not found. Disable documentation targets")

else()
	message(STATUS "Found sphinx-build: ${SPHINX_EXECUTABLE}")

	add_custom_target(prepare_docs
			COMMAND mkdir -p ${CMAKE_SOURCE_DIR}/docs/input
			COMMAND cp -r ${CMAKE_SOURCE_DIR}/input/* ${CMAKE_SOURCE_DIR}/docs/input
			COMMAND mkdir -p ${CMAKE_SOURCE_DIR}/docs/notebooks
			COMMAND cp -r ${CMAKE_SOURCE_DIR}/notebooks/* ${CMAKE_SOURCE_DIR}/docs/notebooks)

	add_custom_target(general_docs
			COMMAND rm -rf htmldocs
			COMMAND ${SPHINX_EXECUTABLE} ${CMAKE_SOURCE_DIR}/docs htmldocs
			DEPENDS prepare_docs)

	add_custom_target(docs DEPENDS general_docs)

	add_custom_command(TARGET docs
		POST_BUILD
		COMMAND rm -rf ${CMAKE_SOURCE_DIR}/docs/input
		COMMAND rm -rf ${CMAKE_SOURCE_DIR}/docs/notebooks)
endif()

################################################################################
# Subdirectories
add_subdirectory(notsokit/cpp)

# Install notsokit header files
set(NOTSOKIT_LIBRARIES notsokit)
install(DIRECTORY include/notsokit
	DESTINATION ${NOTSOKIT_INSTALL_INCLUDE_DIR}
	FILES_MATCHING PATTERN "*.hpp")

# Install ttmath header files
install(DIRECTORY extlibs/ttmath/ttmath
	DESTINATION ${NOTSOKIT_INSTALL_INCLUDE_DIR}
	FILES_MATCHING PATTERN "*.h")

################################################################################
# Prepare pkg-config file

set(NOTSOKIT_LIBNAME notsokit)

execute_process(COMMAND ${NOTSOKIT_PYTHON_EXECUTABLE} -c "from version import version; print(version, end='')"
	WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
	OUTPUT_VARIABLE NOTSOKIT_VERSION)
configure_file(notsokit.pc
	"${PROJECT_BINARY_DIR}/${NOTSOKIT_LIBNAME}.pc" @ONLY)

if(NOTSOKIT_INSTALL_PKGCONFIG_DIR)
	INSTALL(FILES ${PROJECT_BINARY_DIR}/${NOTSOKIT_LIBNAME}.pc
		DESTINATION ${NOTSOKIT_INSTALL_PKGCONFIG_DIR})
endif()
