# Build and Learning log 
## 2026-08-04 (Learning
### Build & tooling
- **PyO3 & maturin**: PyO3 is the in-code bridge (the `#[pymodule]`/`#[pyfunction]` macros + Python↔Rust type conversion); maturin is the build/packaging tool that drives Cargo to compile the Rust and wraps it as an installable wheel. Mantra: PyO3 makes the code *callable*, maturin makes the package *installable*.
- **Packaging fundamentals**: a package = prebuilt reusable code; `pip` = the fetcher/installer; PyPI = the warehouse it fetches from; a venv = an isolated per-project environment so versions can't collide; a build tool = assembles source (especially compiled code) into an installable package. Cargo = Rust's pip + venv + build tool in one command.
- **Cargo.toml**: `[features]` (default `cpu`, plus a gated `metal`); `[lib] crate-type = ["cdylib","rlib"]` (cdylib = the loadable Python module, rlib = lets `cargo test`/other crates link it); pyo3's `extension-module` feature so it doesn't link libpython directly.
- **pyproject.toml**: maturin as the build backend; `module-name` must match `[lib] name`; `python-source` points at the hand-written Python; `dynamic = ["version"]` pulls the version from Cargo so the two can't drift.
- **The `#[pymodule] mod _warthog` style**: the `mod` name *is* the Python module name and must match the compiled `.so`; PyO3 generates the `PyInit__warthog` symbol that Python imports by. This was the root of the whole rename saga.
- **`__init__.py`**: thin re-export from the compiled `._warthog`; version via `importlib.metadata.version(...)`; the module docstring is just a string literal at the top of the file.
- **Rust modules aren't auto-discovered**: unlike Python, a `.rs` file is invisible to the compiler until declared with `mod`. `backend/` was inert because `lib.rs` never said `mod backend;`.
- *(git aside)* contribution-graph attribution needs a verified commit email on the default branch of a non-fork; the "missing" square was just browser cache.

### How warthog works (mental model)
- Layered: **Python API** (what you touch) → **autograd engine** (records each op, replays it backward for gradients) → **Rust backends** (CPU, Metal etc.) → **BLAS** (gemm etc.).
- **BLAS** = the core linear-algebra routines, above all **gemm** (matrix multiply). Neural nets are mostly matmul, so BLAS speed ≈ whole-library speed. aardvark is the from-scratch BLAS.

### The Python↔Rust boundary (why the architecture is shaped this way)
- **CPython** = Python implemented in C. It compiles source to bytecode, then an interpreter loop runs it instruction by instruction; every value is a `PyObject` (a C struct carrying a type pointer).
- **Why pure-Python math is slow**: one addition = bytecode dispatch + type inspection + operation-slot lookup + call through a function pointer + a fresh heap allocation, vs a *single* CPU instruction in compiled Rust. (Saw this in the `a + b` stack-machine trace.)
- **PyO3 mechanism**: its macros generate glue code at compile time (baked into the `.so`); at runtime that glue converts Python values ↔ Rust types *per call* via CPython's C API (Not an IR!). It's a shared *interface*, not a shared middle language.
- **API vs ABI**: an API is a source-level contract (names/types you compile against); an ABI is the binary-level contract (how args sit in registers/stack, struct layout/what you link against). The C ABI is the universal handshake that lets different languages call each other; compiled extensions break across Python versions when that binary layout shifts.
- **The boundary "tax"**: conversion cost is per-*call*, not per-*element*, so the design rule is: each call does a whole tensor's worth of work and the tax amortizes to ~zero.
- **How the fast libraries dodge it**: PyTorch: pybind11 (C++'s PyO3) + a runtime dispatcher, coarse ops, async GPU kernel launches, `torch.compile`. JAX: trace a function to a graph, XLA JIT-compiles it into one fused artifact so Python leaves the hot loop. warthog's path: eager now (fine), fusion/laziness later, async-hides-Python once Metal lands.

### Rust itself
- **Why Rust over C/C++/ObjC**: memory safety with no garbage collector; the borrow checker rejects use-after-free, out-of-bounds, and data races at compile time. Plus Cargo (one unified tool vs C's fragmented build ecosystem) and C-level runtime speed. Objective-C(++) only appears at the Metal edge.
- **Why compiles feel slow**: borrow checking, monomorphization (a specialized copy per concrete generic type), and LLVM optimization. But incremental compilation caches unchanged parts, `cargo check` skips codegen for a fast feedback loop, and debug builds compile fast (only `--release` is slow). Building rustc itself (bootstrapping) is the worst case and unrepresentative. `maturin develop` runs in seconds.
- **Reproducible builds**: rustc isn't bit-for-bit reproducible by default (parallel codegen-units, hashmap iteration order, embedded absolute paths/timestamps/build-ids); achievable with a pinned toolchain + scrubbing; matters for chain-of-trust.

### Adjacent (Ethereum, briefly)
- The ABI idea generalizes: the EVM is an abstract machine every node runs, and a contract ABI (4-byte keccak256 selector + 32-byte-padded args) is a byte-encoding convention layered on top, not something the EVM enforces. Same "agree on the bytes at a boundary" intuition as the Python↔Rust crossing.
