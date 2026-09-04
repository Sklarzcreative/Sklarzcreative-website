# The routing gate

The most important safeguard in the system. It runs before generation and
`--force` does not open it.

| Route | Meaning | May call an image model? |
|---|---|---|
| `GENERATE` | Base art with no annotation layer | Yes |
| `HYBRID` | Generated base art + deterministic vector overlay | Yes |
| `VECTOR_BUILD` | Exact structure *is* the content — chemistry, karyotype, genomics | No |
| `DATA_DRIVEN` | Must originate in verified source data | No |
| `HUMAN_BUILD` | Neither generation nor automated builders are appropriate | No |
| `HOLD` | An author, scientific or regulatory decision is unresolved | No |

## Rules

Declared in `config/routing_rules.yaml`, applied in order, and **escalation
only**: a rule can make a figure stricter, never looser.

```
GENERATE < HYBRID < VECTOR_BUILD < DATA_DRIVEN < HUMAN_BUILD < HOLD
```

1. **Explicit directive** in the tracker's *Current Status* → `confidence: explicit`.
2. **Scientific-note escalation** — e.g. "exact structures must be added from
   authoritative chemical drawing sources" forces `VECTOR_BUILD`.
3. **Visual-type escalation** for figures with no explicit directive.
4. **Hybrid upgrade** — a figure with manual labels cannot be pure `GENERATE`,
   because its labels belong in a deterministic overlay.
5. **Fallback** → `HYBRID` with `needs_route_confirmation: true`.

A **derived** route can never generate until a human passes `--confirm-route`.

## Overriding a route

The canonical tracker is read-only to automation, so a deliberate reroute is
recorded in `canonical/route_overrides.yaml` in the private workspace:

```yaml
overrides:
  CH07-IMG-02:
    route: VECTOR_BUILD
    reason: "Evidence hierarchy; the ranking is the science"
    authorized_by: "Cassandra Sklarz"
```

Overrides obey the same escalation rule as everything else: **stricter only.**
An override that would loosen a route is refused, so this file can never be used
to talk a figure into the generative lane, and it can never release a `HOLD`.

A route named explicitly by a human counts as its confirmation, so an override
also clears `needs_route_confirmation`.

## Why so few figures are purely generative

Every figure in the current tracker that the project marked `GENERATE` also
carries a manual-label list. Under this model all of them are `HYBRID`: the art
is generated, the science-bearing text is not. That is the whole point of the
vector overlay stage.
