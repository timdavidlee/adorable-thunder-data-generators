# Random State

All randomness in `make/` flows through one seeded stream so that runs are reproducible.

## Rule

**Never call `np.random.<method>(...)` directly in `src/adorable_thunder/make/`.**

Always go through the shared seeded `RandomState`:

```python
from adorable_thunder.make.field_generators._random_state import get_random_state

values = get_random_state().choice(pool, p=weights, size=n_samples)
amounts = get_random_state().lognormal(mean=mu, sigma=sigma, size=n_samples)
days = get_random_state().randint(0, span, size=n)
```

This applies to field generators, record generators, flow assembly, and `common/` helpers — anything in the `make/` tree.

## Why

`np.random.<method>(...)` reads from a process-global state seeded with OS entropy, so two runs of the same generator config produce different data. That makes regression testing, scrutinize-vs-baseline comparisons, and bug repros impossible. The shared `RandomState` in `_random_state.py` is seeded with a fixed `RANDOM_SEED` at import time, so call-order alone determines the output.

## Tests

Tests that depend on specific values should call `reset_random_state()` in setup:

```python
from adorable_thunder.make.field_generators._random_state import reset_random_state

def test_something():
    reset_random_state()
    ...
```

## Out of scope

`identifiers.py` uses `uuid.uuid4()` for UUIDs, which bypasses this stream by design (OS entropy). That is a known gap tracked separately — do not paper over it by importing `random` and seeding it ad hoc.

## Type annotations are fine

Annotating a parameter as `np.random.RandomState` (e.g. `def f(rng: np.random.RandomState)`) is allowed — the rule is about *calling* `np.random.<method>`, not about referencing the class.
