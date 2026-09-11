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
## The idea
## Setup
## Worked examples
## Your turn
## Common errors
## Recap
## What is next
```

| Part | Cells | What goes in it |
|---|---|---|
| What you will be able to do | markdown | One or two sentences in the reader's terms. First, because it is read before anything runs. |
| The idea | **markdown only** | Orientation, then a read-only first look as a fenced block. No runnable cell. See below. |
| Setup | **exactly one** code cell | Imports and any data. Runs clean on a fresh runtime. Keep it even when there is nothing to import, so the shape holds. |
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

### The idea is prose; Setup is the first thing anyone runs

**The idea contains no code cells.** It ends with a read-only first look, written as a fenced
```python block with the output in a second fence underneath:

    ### A first look

    Before any of the detail, here is the whole idea in a few lines. There is nothing to run
    yet: read it, and read the output underneath it. ...

    ```python
    ...
    ```

    ```
    ...
    ```

Two things went wrong before this rule existed. Files and Paths had an idea cell that created
the directory every later cell wrote into, so Setup looked like the setup step while the real
one sat above it under a different heading. And more generally a runnable cell above Setup
makes the running order ambiguous: a reader cannot tell which cells are required and which are
illustration.

Setup is now the **first executable cell in the notebook**, without exception, and it owns
everything the later sections depend on.

`check_notebooks.py` fails the build if The idea holds a code cell, if any code cell appears
above Setup, or if a Worked examples cell reads a name only Setup or The idea created.

### The idea: orient before you demonstrate

**The idea comes before Setup.** Setup is a code cell, and a reader who meets code before
any explanation has been handed syntax with no context. Explanation first, then the
housekeeping, then the worked examples. A code cell inside The idea has to stand on its own,
so if it needs an import, it does that import itself.

`Three lines beats thirty` applies to the **example**, never to the explanation. A reader
arriving at a notebook does not yet know what the thing is or why it exists, and a definition
followed straight away by code teaches only syntax.

Before the first code cell, work through these under `###` subheadings:

1. **The problem.** What the reader would be stuck doing without this. Concrete: five thousand
   survey responses, not "a large collection". Two or three paragraphs.
2. **A formal definition**, set in a blockquote so it stands apart from the prose around it.
   Name the term in bold. State it precisely enough to be worth rereading later.
3. **Why it works that way.** The mental model, the consequence, the thing that surprises
   people. This is usually the longest part and it is where the teaching happens.
4. **Where you will meet this.** Real places, including other guides in this library.
5. **What this notebook covers.** A short list. The reader should know what is ahead before
   they run anything.

Then the smallest example that runs.

Aim for 450 to 600 words before that first code cell. This is a chapter opening, not a preamble:
a reader who stops after it should still have learned something. `check_notebooks.py` enforces
a floor of 350, and a floor is not a target: clearing it says only that prose is present, not
that it explains anything.

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
- **No sentence that has to be decoded.** A negation or a pronoun is fine when what it refers
  to is the thing immediately before it. It stops being fine when the reader has to hold two
  earlier clauses in mind and negate both.

  | Do not write | Write |
  |---|---|
  | covered code you wrote and code that ships with Python. Almost everything else you will use is neither | covered two kinds of code: the code you write, and the code that ships with Python. Most of what you will use falls into a third kind |
  | `else` runs whenever the `if` did not | `else` runs whenever the `if` condition was false |
  | Put an even number in the list and it will not | Put an even number in the list and the `break` fires, so the `else` is skipped |
  | `except FileNotFoundError` when it is not | `except FileNotFoundError` when a missing file means something has gone wrong |

  These are fine and should stay, because the thing being negated is the previous sentence:
  "Ints grow as needed. Floats do not." "A tuple qualifies. A list does not." Do not flatten
  those into longer sentences; the fault is distance, not brevity.
  Two specific faults worth naming, because both appeared in Environments and pip:

  - **Literary inversion.** "The commands are few" reads as writing rather than explaining.
    "Here are the commands that cover ordinary use" says the same thing plainly.
  - **A verb that cannot carry the meaning.** "`python` and `pip` mean the copies inside
    `.venv`" leaves the reader guessing at the mechanism. Say what happens: typing `pip` runs
    the copy inside `.venv` instead of the one on your system.

  Note that "means" is correct when explaining what a message signifies, as in "`Result too
  large` means the number no longer fits". That use should stay.

  A third fault in the same family, found across several notebooks: **informal or British
  prepositions**. "Only the name straight after `venv`", "tells you straight away", "the right
  way round". Write "immediately after", "immediately", "in the correct order". The house rule
  is American English, and it covers idiom as well as spelling.

  Note that "kind of" meaning *a type of* is correct and common here: "a kind of
  `ArithmeticError`", "what kind of value". Only the hedging sense is a problem.

  **A heading must say what the section teaches**, not how well it does it. "Print well",
  "Aliasing, properly this time" and "Guard clauses, properly this time" all describe a quality
  rather than a subject, and leave the reader no wiser about what is inside. Write "Make print
  say what it printed", "Aliasing: two names on one list", "Guard clauses with an early return".

  The same goes for a claim in the prose: "most people do it badly" is a judgment about the
  reader. "The usual way is `print(x)`, and with three of those in a loop the output is three
  unlabeled values" is the fact that motivates the section.

  **Say what the code does, not how it feels about it.** "The module declines" leaves a reader
  guessing whether it skipped the value, returned `None`, or stopped. Name the behavior:
  "`json.dumps` raises `TypeError`". The same applies to "complains", "objects" and "balks".

  "Refuses to guess" and "gave up" are fine when the actual exception is shown in the cell
  beside them, because then the vague word is commentary on a fact the reader can already see,
  not a substitute for it.

  The same test applies to a capability statement. "Get at more than one sheet" does not say
  what the reader will do; "reach any sheet in a workbook by name rather than only the first"
  does. Phrasal verbs are fine when precise, and "carries on with wrong data", "the two pictures
  come apart" and "reach into a string" all name something specific.

- **No flourish.** This is a technical guide, and ornament reads as padding. Say what happens.

  | Do not write | Write |
  |---|---|
  | with no ceremony at all | without declaring anything |
  | this is where the model earns its keep | this is where the model matters |
  | costs people an afternoon | is easy to miss |
  | there is no prize for the one-liner | brevity is not the goal |
  | a wrong answer with total confidence | a wrong answer and no warning |
  | nobody will be able to read it a month later | it becomes unreadable |
  | feels wrong for about a week | takes practice |

  The test: if a phrase makes a claim about the reader's future, their feelings, or how famous
  something is, it is doing decoration rather than teaching. "Merely" and "simply" are fine
  when they mean exactly that.


---

## Reference material

`A Whirlwind Tour of Python` by Jake VanderPlas is CC0, No Rights Reserved. Read it at
<https://jakevdp.github.io/WhirlwindTourOfPython/>, where chapter N is
`NN-<slug>.html`. A local copy of all 19 chapters once sat in `~/Desktop/Tour of Python/` and
is no longer there, so do not rely on a local path; fetch the chapter or ask for it.

It is a tour for people who already program. It moves faster than this guide should, it assumes
a terminal, and it skips beginner failure modes entirely, which is exactly the part these
notebooks exist to cover. Take the **shape of an explanation** from it. Never take the prose.

### Which chapter feeds which notebook

The table indexes by number because it maps against the source book's chapters. Everywhere
else, and in the notebooks themselves, references are written by title.

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

- **Operators**, in **Numbers** and **Booleans and Comparison**. The full table, including `//`, `%` and `**`. The `is` versus
  `==` distinction belongs here and follows directly from the pointer model **Values and Variables** sets up: `is`
  asks whether two names label the same value, `==` asks whether two values are equal. Also
  `in` and `not in`, which read better than a manual search loop.
- **Strings**. Chapter 14 splits in half. The first half, case methods, `strip`,
  `find` and `replace`, `split` and `partition`, then format strings, is close to a ready-made
  outline for it and matches its blurb exactly. The second half is regular expressions, which
  **Strings** should not absorb, which is why **Regular Expressions** exists.
- **Line continuation**, in **Numbers**. A statement ends at the end of the line, and a long expression
  continues inside parentheses rather than with a backslash. Numbers is where expressions first
  get long enough for this to matter.
- **Mutable versus immutable**, in **Lists**. **Values and Variables** previews aliasing with a
  list, and **Lists** has to land it properly, because that preview creates the obligation.
- **Functions**. Default argument values, then `*args` and `**kwargs`, then `lambda`.
  The mutable-default-argument trap is not in the source and should be in Common errors.
- **Errors**, in **Errors and Exceptions**. `try` / `except` / `else` / `finally`, `raise`, reading the message off the
  exception object, and defining your own. This is the one chapter whose structure maps almost
  one to one onto a notebook.
- **Iterators**, in **Loops**. `range` is not a list, `enumerate` beats a manual counter, `zip` walks
  two things at once. `itertools` is specialized and has no home in this guide; leave it out.
- **Comprehensions**. Basic, then multiple iteration, then a condition on the iterator,
  then a condition on the value. That is a good running order and worth keeping.
- **Modules**, in **Modules and Imports**. The four import forms and why `from x import *` is the one to avoid.
  Third-party installs belong in **Environments and pip**, not **Modules and Imports**.

### Gaps this exposed

**Regular Expressions** was inserted after **Strings** and is settled. `re` is standard
library, so it belongs with the language rather than in a library guide. That insertion is why
this guide has 21 notebooks, and why every numeric cross-reference written before it was
silently wrong. It is the reason references are written by title now.

**Regular Expressions** also carries a downstream obligation: the **Pandas** guide teaches the
`.str` accessor, where `.str.contains` and `.str.extract` take patterns. **Regular Expressions**
is the only place a reader learns to read one, so it has to be enough on its own.

**Resolved.** Generator expressions are a closing section of the **Comprehensions**
notebook: the parenthesis form, single use, and the memory difference measured against a
list. `yield` and generator functions are a step beyond this guide and remain out.

**Two more gaps, found while planning Object-Oriented Python, and both the same shape as
regex: the reader is taught to use a thing and never to write one.**

`with` is taught twice, in **Files and Paths** and again in **Reading and Writing Text**, and
`for` over an iterable is taught in **Loops**. Nothing anywhere taught `__enter__`, `__exit__`,
`__iter__` or `__next__`. **Context Managers and Iterators** was inserted after **Dunder
Methods** to carry them. It is deliberately not called Protocols, because **Interfaces** covers
`typing.Protocol` and two notebooks called the same thing would be worse than the gap.

Decorators were worse: no notebook mentioned one, and none contained an `@` line, yet
**Properties**, **Class and Static Methods**, **Dataclasses** and **Interfaces** all require
one, as do **Fixtures** and **Parametrize** in the **Testing and Packaging** guide. The
**Dataclasses** blurb used the word "decorator" as though it had been defined. **Decorators**
was inserted immediately before **Properties**, its first consumer.

Guide 1 was the arguable home, since **Functions** teaches that a function is a value and
teaches `*args`, and **Scope** teaches closures, which is the whole of a decorator. It was
placed in Object-Oriented Python anyway: the reader needs it there, not three guides earlier,
and every decorator they meet first is one of this guide's. That leaves an off-theme notebook in
an OOP guide, which is the price of teaching it where it is needed.

**`yield` found its home in Context Managers and Iterators.** The Comprehensions note above
kept `yield` out of Python from the Start, and nothing else in the plan picked it up: no
notebook contained the word, and the only "generator" in the manifest is NumPy's random one.
Writing `__iter__` is where it belongs, because a method containing `yield` is the idiomatic
way to write one. That notebook teaches the explicit `__next__` and `StopIteration` protocol
first, so the reader knows what `for` actually does, and then `yield` as the short form.
Generator functions used outside a class remain out of scope.

### Attribution

When a guide draws on the tour, set that guide's `credits` field in `manifest.json`. The guide
page renders it as a `Sources` section. CC0 requires no attribution, but the author asks for it
and it costs nothing.

### Every import gets a reason

A Setup cell that reads `import locale` tells a reader nothing. Name each import and say what
the notebook uses it for, as a short list above the cell:

    ## Setup

    Three imports and a folder to work in.

    - `Path` builds paths and reads and writes files with an explicit encoding
    - `locale` reports which encoding Python would use if you did not name one
    - `shutil` removes the scratch folder at the end

One line each. Say the job, not the package description: "removes the scratch folder at the end"
beats "high-level file operations". If an import is used once, say where, so a reader knows it
is not needed for the parts before that.

An import that appears later, in the section that needs it, is fine and often better. Say so in
Setup when it happens, as Modules and Imports does for `importlib`.

### Illustrative absolute paths

A notebook that needs to show an absolute path must not print a real one, because the committed
output would carry the author's home directory and would differ from what every reader sees.

Build it with `PurePosixPath`, which never touches the disk, and choose a location **outside**
`/home` and `/Users`. `check_notebooks.py` rejects committed output containing either prefix,
and it cannot tell an invented `/home/ada/...` from a genuine leak. `/srv/analysis/data.csv`
reads as illustrative and keeps the check strict.

## Cross-references

**Refer to a notebook by its title, never by its number.** Write **Lists**, not "notebook 7".

Two reasons, and the second is the one that decides it:

- A reader remembers "the Lists notebook". Nobody remembers which number it was.
- Numbers move. Inserting Regular Expressions at position 5 shifted every notebook after it,
  and prose does not shift with the manifest. Every numeric reference written before that
  insertion was silently wrong until it was found and fixed by hand.

Write it as a **noun phrase**, not a bare title: "the **Lists** notebook showed", never
"**Lists** showed". A bolded title standing alone as the subject of a sentence reads as though
the word is missing, because it is.

The same goes for guides: the **Pandas** guide, not "guide 7".

**Never hardcode how many guides or notebooks there are.** "Ten guides follow", "the ten
remaining guides", "three bands" all go stale the moment one is added, and the front page is
the only list that stays current. Write "the guides that follow" and point at the library page.

**Position counts as a number even when it is spelled out.** "Ten notebooks in", "the last
notebook", "six notebooks ago" and "the first notebook" all break the moment one is inserted or
moved, exactly as a digit would. Name the notebook, or drop the positional framing entirely:
"every program you have written so far" says what "ten notebooks in" was reaching for and
survives any reordering.

`check_notebooks.py` rejects any `notebook N` reference outright. It also flags a bolded phrase
that matches a real title apart from case or spacing. It cannot catch a reference to a notebook
that never existed, because bold is used for emphasis too and everything bolded would be a
suspect, so a plausible wrong title still needs a human to notice.

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
- **Never let a cell recurse without bound, even inside `try`.** The Jupyter kernel handles runaway
  recursion inconsistently. In **Dunder Methods**, a `__repr__` that formats itself raised a
  catchable `RecursionError`, but its message reports how many kilobytes of stack were used, which
  differs between machines, so that notebook catches it and prints a fixed line. In
  **Properties**, a setter that assigns to its own property did not raise at all under nbconvert:
  the C stack overflowed first and the kernel died (`DeadKernelError`), which no `except` can
  survive, and which would fail CI and wipe a reader's Colab session. Plain Python raised a clean
  `RecursionError` for the same code, so testing it outside a notebook proves nothing. To teach
  runaway recursion, make the cell count its own calls and stop itself, as Properties does.
