# Architecture Overview

This project is a hybrid graph library:
- Performance-critical algorithms and data structures are implemented in C++.
- Python-facing APIs are exposed through Cython extension modules.
- The package is consumed as a Python module, but can also be built/used as a C++ library.

The structure is organized by **domain modules** (for example: graph, centrality, community, IO, dynamics), and the same domain names are reused across C++, Cython, tests, and docs.

## Repository Layout (By Responsibility)

- `include/notsokit/`
  - Public C++ headers.
  - Organized into domain subdirectories.
  - Contains both algorithm interfaces and shared utility/base headers used by C++ and by Cython wrappers.

- `notsokit/cpp/`
  - C++ implementations (`.cpp`) grouped by the same domain subdirectories as headers.
  - Each domain can have a `test/` subdirectory for C++ unit tests and benchmarks.

- `notsokit/`
  - Python package root.
  - Cython modules (`.pyx`) provide Python wrappers around C++ APIs.
  - Cython declaration files (`.pxd`) hold shared C/C++ type declarations for cross-module `cimport`.
  - Pure Python modules (`.py`) provide helper utilities, adapters, plotting/profiling tooling, and package-level orchestration.

- `notsokit/test/`
  - Python test suite (unittest-discovered test modules).

- `extlibs/`
  - External C/C++ dependencies used by build and runtime of the native core (plus testing dependencies).

- `docs/`
  - Sphinx documentation and Python API docs.

- Root build/packaging files
  - `CMakeLists.txt`: native build graph (core library, Python extensions, tests, benchmarks).
  - `setup.py`: Python package build entrypoint; drives Cython generation and CMake build for native extensions.
  - `pyproject.toml` and `requirements.txt`: Python build/runtime dependencies.

## Naming and Placement Conventions

### C++ code

- Domain-first organization:
  - Header path pattern: `include/notsokit/<domain>/<ClassOrComponent>.hpp`
  - Source path pattern: `notsokit/cpp/<domain>/<ClassOrComponent>.cpp`

- Header/source naming alignment:
  - A C++ implementation unit typically mirrors a header class/component name.
  - Shared foundational types are placed in base/utility domains and reused across many domains.

- Module-level build declaration:
  - Each C++ domain has its own `notsokit/cpp/<domain>/CMakeLists.txt`.
  - That file registers source files and explicit inter-module dependencies.

### Cython/Python binding layer

- One extension module per Python-facing domain API:
  - Wrapper implementation: `notsokit/<domain>.pyx`
  - Optional declarations for reuse: `notsokit/<domain>.pxd`

- Shared Cython declarations:
  - Core C++ type aliases/base classes and helper templates are centralized in common `.pxd` modules and `cimport`ed where needed.

- Package aggregation:
  - The top-level package initializer imports domain modules and exposes selected high-level classes/functions directly.

### Tests and benchmarks

- C++ tests/benchmarks are colocated with their domain:
  - `notsokit/cpp/<domain>/test/`
  - Test source naming convention is typically `*GTest.cpp`.
  - Benchmark source naming convention is typically `*Benchmark.cpp`.

- Python tests follow module-focused naming:
  - `notsokit/test/test_<domain>.py`

## How Components Connect

## 1. C++ core layer

- Public APIs live in `include/notsokit/...` headers.
- Implementations live in matching `notsokit/cpp/...` domain sources.
- CMake composes these sources into either:
  - a monolithic native library (default), or
  - per-domain native libraries (non-monolithic mode).
- Domain-to-domain dependencies are declared explicitly in CMake, so coupling is visible at build-graph level.

## 2. Cython bridge layer

- `.pyx` wrappers call into C++ classes/functions declared via `.pxd` and `cdef extern from` blocks.
- Wrappers manage object ownership/lifetime and translate between Python objects and C++ types.
- Some wrappers release the GIL around heavy native execution.

## 3. Python API layer

- Python users import `notsokit` and domain modules.
- Top-level imports re-export frequently used classes/functions.
- Optional convenience/interop modules (plotting/adapters/notebook helpers) live as pure Python modules on top of compiled extensions.

## Build and Compilation Pipeline

## C++ build (CMake)

- Primary build system: CMake.
- Core characteristics:
  - C++20 standard.
  - OpenMP-enabled parallel execution.
  - TLX linked as a C++ dependency.
  - ttmath headers available to native code.
- Configurable build modes include:
  - monolithic vs modular core,
  - static vs shared (platform-dependent),
  - sanitizers,
  - coverage,
  - warning/clang-tidy checks,
  - optional test/benchmark targets.

## Python + Cython build

- `setup.py` is the integration entrypoint for Python packaging.
- Build flow:
  1. Cythonize all `notsokit/*.pyx` extension modules.
  2. Generate C++ translation units for those modules.
  3. Invoke CMake to build/install native artifacts into the Python build location.
  4. Compile one Python extension module per domain wrapper and link it against the core library.
- Build wiring passes Python and NumPy include paths into CMake so native modules are compiled against the active Python environment.
- Output is a Python package containing compiled extension modules plus pure-Python helpers.

## Testing, Benchmarking, and Profiling

## C++ testing

- C++ unit tests use googletest/googlemock.
- Tests are registered per domain and can be executed through CTest or through consolidated test executables.
- Benchmarks are integrated similarly, with benchmark-focused targets and benchmark test sources in domain test folders.

## Python testing

- Python tests are organized under `notsokit/test/` and executed with unittest discovery in CI.

## Profiling

- There are two profiling paths:
  - C++ benchmark/test binaries for native performance checks.
  - Python profiling package (`notsokit/profiling/`) for measuring and visualizing algorithm performance from Python workflows.

## External Libraries and Runtime Dependencies

- Native/runtime critical:
  - OpenMP runtime (parallel execution)
  - tlx (C++ utility/data-structure support)
  - ttmath (header-only numeric support used by native code)

- Native test/benchmark:
  - googletest and googlemock (C++ tests)
  - google benchmark (benchmark targets when enabled)
netbarket
- Python build/runtime:
  - cython, setuptools, wheel (build tooling)
  - numpy (build headers + runtime array interop)
  - scipy, tabulate (runtime dependencies)
  - additional optional Python packages from `requirements.txt` for visualization, notebooks, and integrations.

## Practical Rules for Adding New Functionality

1. Pick a domain name and keep it consistent across header/source/wrapper/test paths.
2. Add C++ public headers under `include/notsokit/<domain>/` and implementations under `notsokit/cpp/<domain>/`.
3. Register native sources and inter-domain dependencies in that domain's CMake file.
4. Add/extend `notsokit/<domain>.pyx` (and `.pxd` if declarations are shared).
5. Expose user-facing APIs through package imports where appropriate.
6. Add C++ tests in `notsokit/cpp/<domain>/test/` and Python tests in `notsokit/test/test_<domain>.py`.
7. Keep heavy computation in C++; keep Python/Cython focused on API shape, type conversion, and orchestration.

This pattern is the core architectural template to reuse when building a similar graph library with different algorithms or data structures.
