---
paths:
  - "**/*.py"
---

# Python Class vs. Function Style Guide

**Default to functions.** A module full of pure functions is almost always simpler than a class.

**Use a function when:**
- The operation is stateless
- There's no meaningful lifecycle (init → use → teardown)
- You'd write `MyClass().do_thing(data)` — that's just a function with extra syntax

**Use a class when:**
- You're managing state that persists across calls (`self.connection`, `self.cache`)
- You have a clear lifecycle (`__enter__`/`__exit__`, `open`/`close`)
- Multiple methods share non-trivial state and grouping them reduces parameter passing significantly
- You're modeling a domain entity with identity (`User`, `Order`) — not just a bag of related functions

**Anti-patterns to avoid:**
```python
# Bad: class with one method that holds no state
class CurrencyFormatter:
    def format(self, amount): ...

# Good: just a function
def format_currency(amount): ...

# Bad: class as a namespace for unrelated utilities
class Utils:
    def parse_date(...): ...
    def round_amount(...): ...

# Good: module-level functions in a well-named module
```

**Dataclasses** (`@dataclass`) are for typed records with optional methods — prefer them over plain classes with `__init__` boilerplate, and over dicts when fields are stable and named.

**The test:** If the class has no `__init__` state, or its `__init__` only stores arguments it never mutates, it should probably be a function (or a dataclass if it's just data).
