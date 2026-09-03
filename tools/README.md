# tools

Everything needed to rebuild the site.

```bash
bash tools/build.sh          # rebuild generated pages, then check links and content
bash tools/build.sh --all    # also recompute from raw material
```

**Keep build scripts here, never in `scratch/`.** `scratch/` is throwaway and outside git,
so anything that lives there makes the site unreproducible on any other checkout.

## The two halves

Split the build so stages that need uncommitted raw material write **aggregate**
intermediates into `derived/`, and commit those. Then every page rebuilds on a fresh
checkout, including CI, without the raw material ever being present.

| | Reads | Writes | Committed |
|---|---|---|---|
| `[raw]` stages | `../source/` | `derived/*.json` | the outputs, yes |
| page builders | `derived/`, `templates/` | `public/*.html` | yes |

## Files

- `page.py` — the shared page shell: head, masthead, nav, footer, and the previous/next
  pager. `PAGES` is the reading order and everything follows from it. A page appears in the
  nav and the pager **only once its file exists**, so a half-built site never offers a 404.
- `hl.py` — build-time syntax highlighting for Python and XML, so no page needs a CDN
  script. Correctness is checked by round-trip: strip the tags, unescape, and the result
  must equal the source byte for byte. Add a language by adding a tokeniser.
- `check_links.py` — resolves every href and anchor in `public/`, and every Colab,
  `github.com/blob` and Pages URL that points back into this repository. Those last ones
  are checked against the checkout with no network call, which is the only way to catch a
  dead Colab button: the page loads fine and the notebook 404s when a reader clicks it.
- `check_content.py` — asserts the house rules, and any claim that must appear on every
  page, against tag-stripped and entity-decoded text. Put required strings in `page.py` and
  reference them, never as literals here.
- `paths.py` — every location, plus `require_raw()`. Import from here; do not hard-code paths.
- `chart.py` — SVG chart primitives and the validated colour palette.
- `redact_pdf.py` — removes text objects from a PDF and paints the area black. A black
  box alone is not redaction; the text stays underneath.

## Rules that save time later

**Seed anything randomised** and say so in a comment. A bootstrap interval or a
cross-validated estimate changes if the split changes, and if the number is published,
an unseeded rebuild silently contradicts the page.

**Never write identifiers into `derived/`.** It is committed. Report counts, not keys.

**Verify a rebuild reproduces what is deployed** before trusting a refactor: rebuild and
diff against the live files.

## Why the build runs twice

Pages emit a link only once the target file exists. Those references are often
circular, a code page pointing at a run page and back again, and no single ordering
satisfies both on a clean tree. The first pass creates the files, the second resolves
the links. Delete everything in `public/` and rebuild to confirm it still works.

## Why there are two checkers

Both exist because ad-hoc greps were repeatedly wrong: HTML entities, an apostrophe
written literally where the check expected `&#x27;`, and a bare `#frag` resolved
against the wrong file. Checks that run in the build, against the same rendered text
a reader sees, do not have those failure modes. Break a rule on purpose once and
watch the build fail; that is the only way to know a check works.

## The same checks run in CI

`.github/workflows/check.yml` runs both checkers on every push and pull request, so a
broken link or a house-rule violation fails visibly instead of reaching the site. It is
deliberately separate from `pages.yml`: read-only permissions, and a failure there can
never wedge a Pages deployment.

CI runs the same two scripts `build.sh` does, so a developer's machine and the runner
cannot disagree about what passing means.
