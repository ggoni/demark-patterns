## Context

The current plotting workflow in this repository persists static PNG artifacts. The requested change requires Plotly output that is HTML browser compliant so interactive charts can be opened and used directly in standard browsers. The design must preserve compatibility with current CLI workflows and analysis persistence behavior while introducing a reliable HTML artifact path.

## Goals / Non-Goals

**Goals:**
- Add browser-compliant HTML Plotly artifact generation for plot outputs.
- Preserve optional PNG output for compatibility with existing static workflows.
- Expose output mode control in CLI paths without breaking existing defaults unexpectedly.
- Keep output files deterministic and storable in the current analysis artifact model.

**Non-Goals:**
- Redesign indicator calculations or recommendation logic.
- Add new market-analysis features beyond plot output behavior.
- Introduce server-side hosting for generated HTML artifacts.

## Decisions

- Use Plotly HTML export as the canonical interactive artifact format.
  - Rationale: HTML is directly consumable by browsers and supports native Plotly interactivity.
  - Alternative considered: JSON-only export was rejected because it requires extra rendering steps for users.

- Support selectable output modes: html, png, and both.
  - Rationale: users need browser interactivity while retaining compatibility with existing PNG-based workflows.
  - Alternative considered: replacing PNG entirely was rejected to avoid breaking consumers that depend on static images.

- Keep artifact naming aligned with existing analysis conventions and write outputs into the same analysis folder.
  - Rationale: preserves discoverability and minimizes downstream integration changes.
  - Alternative considered: separate output tree for HTML was rejected due to migration overhead.

- Generate self-contained, browser-compliant HTML that does not require local Python runtime once written.
  - Rationale: artifact portability is required for sharing and offline browser viewing.
  - Alternative considered: CDN-dependent assets were rejected because they reduce portability and can fail in restricted networks.

## Risks / Trade-offs

- [Larger artifact size for HTML] -> Mitigation: keep PNG optional and allow users to choose output mode.
- [Differences in rendering between browsers] -> Mitigation: validate generated files in major modern browsers and keep export path standards-compliant.
- [Dependency growth from Plotly integration] -> Mitigation: remove Matplotlib when migration is complete and pin Plotly versions in project dependencies.
- [Backward compatibility drift in CLI behavior] -> Mitigation: preserve current defaults where possible and add explicit flags for mode selection.

## Migration Plan

1. Introduce Plotly HTML rendering path behind configurable output mode.
2. Add/adjust CLI flags for output mode selection with clear defaults.
3. Persist HTML artifacts into current analysis output location with deterministic filenames.
4. Keep PNG generation supported during transition.
5. Add tests for HTML artifact creation and output mode behavior.
6. Validate runtime behavior through CLI execution and browser-openable artifacts.
7. Remove Matplotlib dependency once all plotting paths are migrated.

## Open Questions

- Should default plot mode become both html and png, or remain png until a major version boundary?
- Is browser validation required for a defined browser matrix or only standards-compliance checks?
- Should HTML export include embedded Plotly JS or use external references when file size is a concern?