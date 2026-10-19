---
paths: ["src/ouroboros/metrics/**"]
---
- One public function per metric id, named after it in the docstring (`"""M-THR-02 Lead time for changes."""`).
- Return "no data" as `None`, never 0, when a period has no data.
- Every metric is computed per provenance (`agent`, `human`, `unknown`, `all`) as the spec ground rules require.
