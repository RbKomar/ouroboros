---
paths: ["tests/**"]
---
- Test behaviour through the public function of the module, not private helpers.
- Fixtures are minimal JSON shaped like the real GitHub REST API response; name them after what they show
  (`pr_reverted.json`), not after the test.
- Time in tests is explicit UTC (`datetime(2026, 10, 5, tzinfo=UTC)`); never depend on the current date.
- A test that covers a spec id asserts the exact value the spec definition implies for the fixture, with a short
  comment showing the arithmetic.
