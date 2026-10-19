# Architecture

Three stages, each a pure step over files, so every stage can be tested without the network.

```
GitHub REST API --collect--> snapshot.json --compute--> metrics.json --render--> site/index.html
```

- **collect** (`ouroboros.collect`): the only module that talks to the network. Reads pull requests, their commits
  and check runs, and default-branch workflow runs for one repository. Writes a snapshot: plain JSON, sorted keys,
  stable across runs for the same data. Auth: `GITHUB_TOKEN` environment variable.
- **model** (`ouroboros.model`): typed dataclasses for the snapshot and its JSON (de)serialisation.
- **metrics** (`ouroboros.metrics`): pure functions from a snapshot to the metrics defined in `docs/metrics.md`.
  No I/O, no clock: "now" is passed in.
- **render** (`ouroboros.render`): metrics to one static HTML page with inline SVG charts. No JavaScript framework,
  no external requests; works offline and in light and dark mode.
- **cli** (`ouroboros.cli`): `ouroboros collect <owner/repo> -o snapshot.json`, `ouroboros report snapshot.json -o site/`.

Dependencies are kept small: `httpx` for HTTP, the standard library for everything else.
Tests use recorded JSON fixtures in `tests/fixtures/`; no test touches the network.
