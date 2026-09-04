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

**Links off google.com get a Google interstitial in Colab.** A reader clicking the breadcrumb
sees a "Redirect Notice" page first. Nothing in the notebook suppresses it: an HTML anchor with
`target="_blank"` was tried and Colab strips the attribute, so the reader still loses their tab.
The site links are plain markdown, and the interstitial is accepted as a Colab constraint.

Previous, next and back-to-notebook all point at `colab.research.google.com`, stay on Google's
domain, and are unaffected. They are the links a reader uses most, which is the part that
matters.

**Solutions notebooks get navigation too**, and are read on their own. Their footer goes
**back to their own notebook** rather than on to the next one: somebody reading answers is
mid-exercise, not moving through the guide. They are exempt from the eight-part shape, which
is for teaching notebooks.

**Do not hand-write a title cell**, in either file. `nav-top` owns the `# Heading`, and a
second one is a duplicate the injector will not remove for you. It also carries no guide
number and no "notebook N of M": the breadcrumb names the guide, the heading names the
notebook, and a count goes stale the moment the order changes.

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

## Reference material

`A Whirlwind Tour of Python` by Jake VanderPlas is CC0, No Rights Reserved. The complete book,
all 19 chapters, is saved at `~/Desktop/Tour of Python/` and is also online at
<https://jakevdp.github.io/WhirlwindTourOfPython/>. Nothing more needs to be attached to a
session; open the file for the chapter you need.

It is a tour for people who already program. It moves faster than this guide should, it assumes
a terminal, and it skips beginner failure modes entirely, which is exactly the part these
notebooks exist to cover. Take the **shape of an explanation** from it. Never take the prose.

### Which chapter feeds which notebook

All notebook numbers are guide 1, `Python from the Start`, unless noted.

| Whirlwind chapter | Lands in |
|---|---|
| 01 How to run Python code | nb 1 Running Python **(done)** |
| 02 A quick tour of syntax | nb 1, nb 2 |
| 03 Variables and objects | nb 2 Values and Variables **(done)** |
| 04 Operators | nb 3 Numbers, nb 6 Booleans and Comparison |
| 05 Built-in types, simple values | nb 3 Numbers, nb 4 Strings |
| 06 Built-in data structures | nb 7 Lists, nb 8 Tuples and Unpacking, nb 9 Dictionaries, nb 10 Sets |
| 07 Control flow | nb 11 Conditionals, nb 12 Loops |
| 08 Defining and using functions | nb 14 Functions, nb 15 Scope |
| 09 Errors and exceptions | nb 16 Errors and Exceptions |
| 10 Iterators | nb 12 Loops, nb 13 Comprehensions |
| 11 List comprehensions | nb 13 Comprehensions |
| 12 Generators | nb 13 Comprehensions, and see the gap below |
| 13 Modules and packages | nb 18 Modules and Imports, nb 19 Environments and pip |
| 14 Strings and regular expressions | nb 4 Strings, nb 5 Regular Expressions |
| 15 Preview of data science tools | guides 6 to 10 |

### Worth reaching for, by topic

- **Operators**, nb 3 and nb 6. The full table, including `//`, `%` and `**`. The `is` versus
  `==` distinction belongs here and follows directly from the pointer model nb 2 sets up: `is`
  asks whether two names label the same value, `==` asks whether two values are equal. Also
  `in` and `not in`, which read better than a manual search loop.
- **Strings**, nb 4. Chapter 14 splits in half. The first half, case methods, `strip`,
  `find` and `replace`, `split` and `partition`, then format strings, is close to a ready-made
  outline for nb 4 and matches its blurb exactly. The second half is regular expressions, which
  nb 4 should not absorb, which is why nb 5 exists.
- **Line continuation**, nb 3. A statement ends at the end of the line, and a long expression
  continues inside parentheses rather than with a backslash. Numbers is where expressions first
  get long enough for this to matter.
- **Mutable versus immutable**, nb 7. Notebook 2 previews aliasing with a list. Notebook 7 has
  to land it properly, because that preview creates the obligation.
- **Functions**, nb 14. Default argument values, then `*args` and `**kwargs`, then `lambda`.
  The mutable-default-argument trap is not in the source and should be in Common errors.
- **Errors**, nb 16. `try` / `except` / `else` / `finally`, `raise`, reading the message off the
  exception object, and defining your own. This is the one chapter whose structure maps almost
  one to one onto a notebook.
- **Iterators**, nb 12. `range` is not a list, `enumerate` beats a manual counter, `zip` walks
  two things at once. `itertools` is specialized and has no home in guide 1; leave it out.
- **Comprehensions**, nb 13. Basic, then multiple iteration, then a condition on the iterator,
  then a condition on the value. That is a good running order and worth keeping.
- **Modules**, nb 18. The four import forms and why `from x import *` is the one to avoid.
  Third-party installs belong in nb 19, not nb 18.

### Gaps this exposed

**Regular expressions are now guide 1 notebook 6**, inserted after Strings and settled. `re`
is standard library, so it belongs with the language rather than in a library guide. This is
why guide 1 has 21 notebooks and everything from Booleans onward carries a number one higher
than the original plan.

Notebook 5 also carries a downstream obligation: guide 7 notebook 17 teaches the pandas `.str`
accessor, where `.str.contains` and `.str.extract` take patterns. Notebook 6 is the only place
a reader learns to read one, so it has to be enough on its own.

**Guide 1 has no generators notebook,** and generator expressions are a genuinely useful idea:
same syntax as a list comprehension with parentheses instead of brackets, a recipe rather than
a collection, single use rather than repeatable. The natural home is nb 13 Comprehensions, as
a final section, since the syntax is one character away from what that notebook already
teaches. `yield` and generator functions are a step beyond guide 1 and can wait.

Unlike the regex gap above, this one needs no decision in advance. It fits inside
the existing plan, so revisit it when nb 13 is written.

### Attribution

When a guide draws on the tour, set that guide's `credits` field in `manifest.json`. The guide
page renders it as a `Sources` section. CC0 requires no attribution, but the author asks for it
and it costs nothing.

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
