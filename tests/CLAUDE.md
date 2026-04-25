# Python Test Guidelines

These are the conventions Claude should follow when writing or modifying Python tests in this codebase. They exist to keep tests fast to read, easy to debug, and cheap to maintain.

## Stack

- **Test runner:** `pytest`
- **Style:** function-based tests (no `unittest.TestCase` subclasses unless interop demands it)
- **Layout:** tests live in `tests/`, mirroring the package structure. Files start with `test_`, functions start with `test_`.

## Core principles

### One behavior per test

Each test verifies one behavior and ideally has one assertion. When a test fails, the name and the single failing assertion should tell you exactly what broke without reading the body.

```python
# Good — one behavior, one assertion
def test_normalize_strips_trailing_whitespace():
    assert normalize("hello  ") == "hello"

def test_normalize_lowercases_input():
    assert normalize("HELLO") == "hello"
```

```python
# Avoid — multiple behaviors mashed together
def test_normalize():
    assert normalize("hello  ") == "hello"
    assert normalize("HELLO") == "hello"
    assert normalize("") == ""
```

If the second assertion fails, the first never runs and you lose information. Split them, or parametrize them (see below).

### When multiple asserts are okay

A single test may contain multiple asserts when they are checking different facets of *the same* result and reading them together is clearer than splitting. For example, asserting on multiple fields of one returned object:

```python
def test_parse_user_returns_populated_record():
    user = parse_user(RAW_PAYLOAD)
    assert user.id == 42
    assert user.email == "ada@example.com"
    assert user.is_active is True
```

The rule of thumb: if you'd give the asserts the same test name, they belong together. If you'd give them different names, split them.

### Name tests as sentences

Test names describe the behavior under test, not the function being tested. `test_<unit>_<condition>_<expected>` is a good shape.

```python
def test_withdraw_with_insufficient_funds_raises_overdraft_error(): ...
def test_withdraw_zero_amount_is_a_noop(): ...
```

You should be able to read the test names and have a spec for the unit.

### Arrange / Act / Assert

Inside a test, separate setup, the call under test, and the assertion with blank lines. It makes the "act" line obvious.

```python
def test_discount_applies_to_subtotal():
    cart = Cart(items=[Item(price=100), Item(price=50)])

    total = cart.total(discount=0.1)

    assert total == 135
```

## Fixtures

Use fixtures for any setup that more than one test needs, or any setup that's more than ~2 lines. Inline trivial setup; extract everything else.

### Where fixtures live

- **Test-file-local:** define at the top of the test module if only that file uses them.
- **Shared across a directory:** put in `conftest.py` at the appropriate level. The closest `conftest.py` to the test wins, so prefer the deepest level that covers all consumers.
- **Project-wide:** top-level `tests/conftest.py`. Keep this file small — only truly global fixtures (db connection, app factory) belong here.

### Scopes

Default to `function` scope. Only widen scope when the setup is genuinely expensive *and* the fixture is safe to share (immutable, or reset between uses). A shared mutable fixture across tests is a recipe for order-dependent failures.

```python
@pytest.fixture
def user():
    return User(id=1, email="ada@example.com")

@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(TEST_DATABASE_URL)
    yield engine
    engine.dispose()
```

### Fixture composition

Fixtures can depend on other fixtures. Build small, focused fixtures and compose them rather than writing one giant `setup_everything` fixture.

```python
@pytest.fixture
def account(user):
    return Account(owner=user, balance=Decimal("100.00"))

@pytest.fixture
def overdrawn_account(account):
    account.balance = Decimal("-5.00")
    return account
```

### Cleanup with `yield`

Use `yield` for fixtures that need teardown. Anything before `yield` is setup; anything after runs even if the test fails.

```python
@pytest.fixture
def temp_config(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text("debug = true")
    yield path
    # tmp_path cleans itself up, but if you opened a connection,
    # closed a process, etc., do it here.
```

Prefer pytest's built-in fixtures (`tmp_path`, `monkeypatch`, `caplog`, `capsys`) over hand-rolled equivalents.

### Factory fixtures

When tests need slightly different versions of the same object, return a factory function from the fixture rather than the object itself.

```python
@pytest.fixture
def make_user():
    def _make(**overrides):
        defaults = {"id": 1, "email": "ada@example.com", "is_active": True}
        return User(**{**defaults, **overrides})
    return _make

def test_inactive_user_cannot_log_in(make_user):
    user = make_user(is_active=False)

    assert user.can_log_in() is False
```

## Parametrize

Use `@pytest.mark.parametrize` whenever you'd otherwise write near-identical tests that differ only in inputs and expected outputs. Each parameter set runs as its own test — you get the "one assertion per failure" benefit *and* avoid duplication.

### Basic shape

```python
@pytest.mark.parametrize(
    "raw, expected",
    [
        ("hello  ", "hello"),
        ("HELLO", "hello"),
        ("  Hello World  ", "hello world"),
        ("", ""),
    ],
)
def test_normalize(raw, expected):
    assert normalize(raw) == expected
```

### Use `ids` for readability

When inputs aren't self-explanatory, give each case an id so failures and `pytest -v` output are readable.

```python
@pytest.mark.parametrize(
    "amount, balance, expected",
    [
        (50, 100, 50),
        (100, 100, 0),
        (0, 100, 100),
    ],
    ids=["partial_withdrawal", "exact_balance", "zero_withdrawal"],
)
def test_withdraw_updates_balance(amount, balance, expected):
    account = Account(balance=balance)

    account.withdraw(amount)

    assert account.balance == expected
```

### Parametrizing exceptions

Group success cases and error cases into separate tests rather than mixing them. A test should answer one question.

```python
@pytest.mark.parametrize("amount", [-1, -100, -0.01], ids=["neg_int", "large_neg", "neg_float"])
def test_withdraw_negative_amount_raises(amount):
    account = Account(balance=100)

    with pytest.raises(ValueError, match="must be positive"):
        account.withdraw(amount)
```

### Stacked parametrize

Stacking decorators creates the cartesian product. Useful, but watch the multiplication — two `@parametrize`s with 5 values each is 25 tests.

```python
@pytest.mark.parametrize("currency", ["USD", "EUR", "GBP"])
@pytest.mark.parametrize("amount", [0, 1, 1_000_000])
def test_format_money(currency, amount):
    assert format_money(amount, currency).startswith(SYMBOLS[currency])
```

### Parametrize with fixtures via `indirect`

When a parameter should be passed *through* a fixture (e.g., to construct an object), use `indirect`.

```python
@pytest.fixture
def user(request):
    return User(role=request.param)

@pytest.mark.parametrize("user", ["admin", "viewer"], indirect=True)
def test_user_role_is_set(user):
    assert user.role in {"admin", "viewer"}
```

## Assertions

- Use plain `assert`. Pytest rewrites them to give rich failure messages — you don't need `assertEqual` or custom messages most of the time.
- For exceptions, use `pytest.raises` with `match=` to pin the error message:
  ```python
  with pytest.raises(ValueError, match="must be positive"):
      withdraw(-1)
  ```
- For floats, use `pytest.approx`:
  ```python
  assert result == pytest.approx(0.1 + 0.2)
  ```
- For "this thing was logged", use `caplog`. For "this thing was printed", use `capsys`. Don't capture stdout by hand.

## Mocking

- Prefer real objects over mocks where the real thing is cheap (dataclasses, pure functions, in-memory stores).
- Mock at boundaries: network, filesystem (when `tmp_path` won't do), time, randomness.
- Use `monkeypatch` for env vars and attribute patching; use `unittest.mock` (`patch`, `MagicMock`) for replacing callables and methods.
- Patch where the name is *looked up*, not where it's defined: `patch("myapp.services.requests.get")`, not `patch("requests.get")`.

## What not to test

- Don't test the standard library or third-party code. Test *your* use of it.
- Don't write tests that just mirror the implementation — if the test and the code are the same shape, a refactor will require rewriting both, and the test catches nothing.
- Don't test private helpers directly when their behavior is fully covered through the public API. If a private helper has behavior worth testing on its own, it's probably not really private.

## Test independence

Every test must pass in isolation and in any order. If a test relies on another test having run first, it's broken. Run with `pytest -p no:randomly --tb=short` periodically to flush out hidden ordering bugs (or use `pytest-randomly` to randomize automatically).

## Speed

- Unit tests should run in milliseconds. If a test takes >100ms, ask whether it should be marked `@pytest.mark.slow` and excluded from the default run.
- Don't sleep. If you're tempted to `time.sleep`, you're probably testing real time when you should be controlling it (`freezegun`, `monkeypatch` on `time.time`, etc.).

## Coverage

Coverage is a floor, not a ceiling. 100% line coverage with weak assertions is worse than 70% coverage with sharp ones. Aim for branch coverage on logic-heavy modules and don't chase coverage on trivial code (dataclasses, `__repr__`, etc.).