# Tests

Three layers of testing in this repo, from fastest to slowest:

| Layer | Location | Speed | AI calls | What it tests |
|-------|----------|-------|----------|---------------|
| Unit | [`unit/`](unit/) | Seconds | No | Orchestrator Python modules in isolation |
| Regression / replay | [`regression/`](regression/) | ~1 min | No | Full pipeline end-to-end using pre-recorded AI responses |
| Regression / live | [`regression/`](regression/) | 10–30 min | Yes | Full pipeline end-to-end with real AI |

---

## Unit tests

Fast, no dependencies, no pipeline execution. Run them often — before and
after any change to the orchestrator Python modules.

```bash
python3 -m unittest discover -s tests/unit -v
```

See [`unit/README.md`](unit/README.md) for what each test covers.

---

## Regression tests

End-to-end tests that run the full orchestrator against a real job spec and
verify the generated output. Two modes — see
[`regression/README.md`](regression/README.md) for full details including
when to use each.

**Replay (no AI cost):**
```bash
bash tests/regression/<name>/test-replay.sh
```

**Full live run:**
```bash
bash tests/regression/<name>/reset.sh
# ... then run the orchestrator (see each test's README)
cd tests/regression/<name>/gold && go test -tags regression ./...
```

See [`regression/how-to-write-a-regression-test.md`](regression/how-to-write-a-regression-test.md)
when adding a new regression test.
