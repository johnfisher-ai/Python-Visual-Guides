# Python-Visual-Guides

A library of interactive Python guides. Eleven guides, each a set of numbered Colab
notebooks. **The notebook is the product.** The explanation, the code, the output and the
figures all live in the notebook; the site is a thin index that gets a reader to the right
one and gets out of the way.

**Author: John Fisher.** Repo: `johnfisher-ai/Python-Visual-Guides`.
Sibling to `Statistics-Data-Science-AI-Visual-Book`.

---

## Hard rules

- **Never push.** The author pushes with `bash scripts/push_to_github.sh "message"` and
  reviews before publishing. Commit freely; pushing is the author's.
- **Never `git commit --amend`, rebase, or rewrite history.** Always a new follow-up commit.
- **No `Co-Authored-By` trailer** on commits.
- **On resume:** `git log --oneline -5` and confirm what is already pushed.
- **This repo is PUBLIC.** Pushing is publication and cannot be undone.

---

## The page / notebook boundary

This is the decision everything else follows from. Get it wrong and the project becomes two
documents saying the same thing differently.

| The page carries | The page never carries |
|---|---|
| What the guide is, and who it is for | Explanations |
| A numbered index of its notebooks, one line each | Code listings |
| An Open in Colab button, and a Read on GitHub link | Output, figures, exercises |
| Prerequisites, and what comes next | Anything a reader would want to run or copy |

**The test: if a sentence would be better with a cell under it, it belongs in the notebook.**

Twelve pages in total. One library front page, one per guide. That is the whole site.

---

## The eight parts of a notebook

Every notebook has these eight sections, in this order, under these **exact** level-two
headings. `tools/check_notebooks.py` enforces it, so a drift fails the build.

```
## What you will be able to do
## Setup
## The idea
## Worked examples
## Your turn
## Common errors
## Recap
## What is next
```

| Part | Cells | What goes in it |
|---|---|---|
| What you will be able to do | markdown | One or two sentences in the reader's terms. First, because it is read before anything runs. |
| Setup | **exactly one** code cell | Imports and any data. Runs clean on a fresh runtime. Keep it even when there is nothing to import, so the shape holds. |
| The idea | markdown, then a short cell | The explanation, then the smallest example that runs. Three lines beats thirty. |
| Worked examples | many cells | Where the guide earns its length. One idea per cell, every output committed. Diagrams and plots live here. |
| Your turn | task cells | Three to six tasks, increasing. Each states the goal and leaves `# your code here`. **Never pre-filled.** |
| Common errors | broken cells, run | Break it on purpose, run it, leave the traceback in as committed output. Then what it means and the fix. |
| Recap | markdown | Four or five lines, each a thing the reader can now do. It answers part 1. |
| What is next | markdown | One line naming the next notebook and why it follows. |

**Solutions live in a separate notebook**, `NN-slug-solutions.ipynb`. Never in the same file:
an answer one scroll below the question is not an exercise.

**Link to it from `Your turn`**, with a Colab URL, after the encouragement to try first and
before the tasks. A promise of solutions with no link leaves the reader hunting for a file
they have no way to find. `check_notebooks.py` fails when the link is missing.

**No size ceiling.** Comprehensive, visual and interactive beats small. The only limit is
GitHub's: past a few megabytes it stops rendering a notebook in the browser and a reader sees
"too big to display" instead of your work. If a notebook crosses that, **split it rather than
thin it.**

---

## Navigation

A reader who opens a notebook in Colab has no site around it: no contents, no next, no way
back. `tools/inject_nav.py` puts two generated cells into every notebook and the build runs
it, so this is never hand-written and never drifts.

| Cell | Tag | Carries |
|---|---|---|
| First | `nav-top` | Breadcrumb to the library and the guide, then the title |
| Last | `nav-bottom` | Previous notebook, the guide's notebook list, next notebook |

Previous and next appear only when that neighbour actually exists, so a half-written guide
never offers a link to a notebook that is not there. `check_notebooks.py` fails on a notebook
with no navigation.

**Do not hand-write a title cell.** `nav-top` owns the `# Heading`. A second one is a
duplicate that the injector will not remove for you.

## Layout

| Path | What it is |
|---|---|
| `manifest.json` | **The source of truth.** Guides, notebooks, order, blurbs. Every page and nav is generated from it. |
| `notebooks/<guide>/NN-slug.ipynb` | The content. Committed **with outputs**. |
| `notebooks/<guide>/NN-slug-solutions.ipynb` | Its companion. |
| `data/` | Shared across guides. Never duplicated per guide. |
| `public/` | The site. **The only folder Pages serves.** GENERATED, never hand-edited. |
| `tools/` | Build machinery. See `tools/README.md`. |

---

## Build and validate

```
bash tools/build.sh
```

Two passes over the page builders, then four gates: the manifest, links, house rules, and
the notebook shape. Any failure stops the build.

```
python3 tools/manifest.py          validate the manifest alone
python3 tools/check_notebooks.py   the eight-part shape
```

**Re-execute a notebook after editing it.** A notebook whose committed output disagrees with
its committed code teaches the reader something false, and nothing but you will catch it.

---

## House style

- **American English.** color, behavior, analyze, license.
- **No prose em-dashes.** Commas or parentheses.
- **Write for someone learning.** Name the thing they will see, not the thing the language
  calls it internally. "The error you will get" beats "the exception raised by the
  interpreter".
- **Say what actually happens.** No claim in a notebook that has not been run.

---

## Traps

- **`build.sh` shipped with commented placeholders.** The `pages()` function did nothing, so
  a build appeared to succeed while the HTML stayed stale. If a change is not showing up,
  check that the builder is actually called.
- **A notebook on disk that the manifest does not name is invisible.** `manifest.py` fails on
  that rather than silently ignoring it.
- **It is very easy to solve your own exercise** while testing that it works, save, and ship
  the answer inside the question. `check_notebooks.py` fails on any code in a `Your turn` cell.
- **A slice from a heading cell starts AT it, not after it.** The `## Heading` shares a cell
  with the text under it, so `cells[idx + 1:]` silently skips the first paragraph. This made a
  checker rule fail on a notebook that was correct.
- **The nav is not the guide list.** Eleven guides across the top would wrap to three lines.
  Nav is the library plus the repository; the pager walks the guides.
