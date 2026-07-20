# Metal-Autograd (MAG)

A from-scratch autograd engine for Apple Silicon, built to learn two
things properly: how reverse-mode automatic differentiation works, and
how to program Apple GPUs with Metal/MPS.

**Status: early Phase 0** — scalar engine with graph recording.
Gradients are the next milestone. Nothing here is production-anything;
the point is understanding every line.

## What works today

- `Value`: a scalar that records the computational graph as you do math
- `+` and `*`, including mixing with plain Python numbers (`2 * x + 1`)

## Roadmap

- [x] Phase 0a: graph-recording scalar Value
- [ ] Phase 0b: gradients — `backward()` via chain rule + topo sort
- [ ] Phase 0c: train a tiny MLP on a toy dataset
- [ ] Phase 1: tensors (NumPy backend), matmul/broadcasting/reductions
- [ ] Phase 2: first Metal kernels (standalone)
- [ ] Phase 3: swap engine math onto the GPU
- [ ] Phase 4: MNIST end-to-end on Apple Silicon

## Development

```bash
python3 -m venv .venv-autograd
source .venv-autograd/bin/activate
pip install -e ".[dev]"
python -m pytest        # run tests
ruff format . && ruff check . --fix
```

Inspired by [micrograd](https://github.com/karpathy/micrograd),
rebuilt line-by-line to actually understand it, then aimed at Metal. 
