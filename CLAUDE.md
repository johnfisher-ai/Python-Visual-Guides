# Python-Visual-Guides

A library of interactive Python guides, each a set of numbered Colab notebooks.
**The notebook is the product.** The explanation, the code, the output and the
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
4. **Where this shows up.** Real places, including other guides in this library.
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
| `manifest.json` | **The source of truth.** Guides, notebooks, order, blurbs. Every page, the nav, and the guide table in `README.md` are generated from it. |
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
- **Say what actually happens.** No claim in a notebook that has not been run. A sweep over
  sqlite3, Deep Dive found about thirty sentences that failed this, none of them wrong, all of
  them unsupported by the run beneath them, so the specific shapes are worth naming:

  - **A join that keeps unmatched rows needs an unmatched row in the data.** "The list has to
    include the students who have earned none at all" is an inner join in disguise until a
    student with none is in the table.
  - **A mechanism the notebook builds and credits has to run in it.** Two notebooks created a
    delete trigger, said the triggers keep the index in step, and never deleted a row; a loader
    guard, a re-raise branch, a capacity check and an unchecked file left by a crash were all
    described and never reached.
  - **A counterfactual is a claim.** "Without the index it would scan", "on a new cursor it
    would pass None", "closing the connection would not have helped": print the other case
    beside the one shown, or attribute it to the notebook that does.
  - **Where the other case cannot be printed**, because it hangs, or differs by machine, or
    differs between SQLite versions, say that plainly or hand it to the notebook that owns it.
    A local time, a float sum and a nested query plan are all unfit to print.
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

  **Describe code in the terms of code.** "The same five steps, character for character" treats
  source code as typed text, and reads oddly. Say what is true of the code: "the same five steps;
  only the class name on the first line is different", or "the same code as before".
  `check_content.py` rejects "character for character". "Character by character" is still correct
  where the subject really is text, as when two strings are compared one character at a time.

  **Name the thing, and name it once.** "Open one in Colab to run it", under the heading "The
  notebooks", made the reader look back to find out what "one" was; "**Open in Colab** runs a
  notebook" does not. A repeated bare *each* has the same fault: "Each notebook is
  self-contained, and each has a separate solutions file" says *each* twice about one subject.
  Give the subject once and join the predicates: "Each stage is one function, small enough to
  read on a single screen". `check_content.py` rejects the *each ..., and each has* shape. A
  vague *one* has no pattern a check can find, so reread for it. It is fine when its noun is in
  the same sentence, as in "Three absences, and each one causes a distinct problem".

  The Your turn opening follows the same rule in every notebook: "Five tasks. Write your answer
  in the cell under each task and run it." and then "Try a task before you look at its answer."

  **Use the subject's own vocabulary.** An HTTP exchange is a request and a response. "Three
  lines and an empty line went out" describes it as typed text, the same fault as "character for
  character". Write "the client sent a `GET` request with two headers and no body, and the server
  returned `200 OK`". The blank line that ends the headers is still the right name for that part
  of a message, and belongs where a message's layout is being explained.

- **A before and after only where a notebook makes a case.** Some Object-Oriented Python notebooks
  open with one program written without their technique and then with it, because they argue for a
  way of writing code: a class over loose functions, a decorator over repetition. A notebook that
  teaches a protocol, a library or a tool has nothing to argue against, so its Worked examples start
  with the technique itself. APIs and JSON had three such openings, among them Status Codes' four
  responses read without their status codes, and all three were removed at review. A contrast that
  is a mistake readers really make, such as `status` for `status_code`, belongs in Common errors.

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

**APIs and JSON grew from twelve notebooks to eighteen at review, before its second was
written.** The author asked for the tools people use to explore an API, for schemas, and for the
server side:

- **Exploring an API**, immediately after What an API Is: Postman, curl, browser developer tools
  and interactive documentation, and reading an OpenAPI document. A notebook rather than a section
  of What an API Is, whose idea already runs past 1,600 words, and because curl and an OpenAPI
  document can run in a cell. Postman cannot reach the practice API, whose `127.0.0.1` is Colab's
  machine, so Postman walkthroughs use a public API such as Open-Meteo.
- **Schemas and Validation**, after JSON in a Response: JSON Schema and Pydantic, and validating
  what arrives. Placed there so A Real Client can validate the responses it receives; the server
  section reuses the same models to validate requests. Before this, nothing in the plan checked a
  body's shape.
- **Your First API Server**, **Validating Requests**, **A Complete API** and **Hosting an API**,
  at the end. FastAPI, because its request and response models are schemas and it publishes
  OpenAPI documentation from them; Flask needs add-ons for both. A Complete API rebuilds the
  practice API, which What an API Is promises. Hosting uses one free host as the worked example,
  chosen when that notebook is written, because free tiers change; the deploy happens on the
  host's website, so CI runs only the cells that build and check the app.
  **The host is Render**, checked on 15 September 2026. Its docs confirm a free web service with
  no payment method, a spin-down after 15 minutes without traffic and about a minute to wake,
  750 free hours a month, an ephemeral filesystem, deploys from a Git repository, `PORT`
  (default 10000) and automatic HTTPS. Hugging Face was the other candidate, and its Docker and
  Gradio Spaces now need a paid plan to create. The notebook runs the start command locally
  with `127.0.0.1` in place of `0.0.0.0`, because this Mac's firewall is on and could prompt,
  and says why. Recheck the free tier before editing that notebook.

The guide's prerequisites now include Object-Oriented Python: Pydantic models are classes and
FastAPI routes are decorators. Pin `requests`, `jsonschema`, `pydantic`, `fastapi` and `uvicorn`
in `requirements.txt` in the notebook that first imports each.

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

## The practice API and real services

Every notebook in **APIs and JSON** makes HTTP requests, and CI re-runs them without
`--allow-errors`. Most requests go to a practice API, `notebooks/apis-and-json/practice_api.py`,
standard library only, which the Setup cell starts inside the notebook's own process on
`127.0.0.1`. In Colab it runs on Colab's machine, so nothing touches the reader's computer. There
is only this mode: Colab, local Jupyter and CI all behave the same.

- **Setup fetches it in Colab on every run, and elsewhere only when it is missing.** Under CI and
  in a checkout, the kernel runs beside the file, so `import practice_api` finds the copy from the
  same commit as the notebook. Colab starts with only the notebook, and keeps what Setup downloads
  for the life of the runtime, which can outlast a push. When Setup fetched only a missing file, a
  reader's runtime kept a copy from before `open_meteo()` existed, and no rerun could replace it.
  So Setup fetches from `main` whenever `google.colab` is imported, and `importlib.reload` runs the
  file as it is now instead of the module imported earlier. GitHub serves raw files with
  `Cache-Control: max-age=300`: for five minutes after a push, Colab can still get the previous
  copy, and running Setup again after that picks up the new one. CI never exercises the download,
  which is why `check_links.py` resolves every self-link inside notebooks, this URL included. Keep
  the URL in one string literal, or the check sees only its first half.
- **Deterministic by construction.** The `Date` header is fixed, the `Server` header names no
  Python version, and the port is the first free one from 8765, so committed output matches what
  every reader sees.
- **Failures are made here, on purpose.** 404s, 429s, 500s, slow and flaky endpoints, keys and
  pagination belong on the practice API, never on somebody else's server.
- **`GET /status/<code>` responds with any code from 200 to 599**, carrying what a real server
  sends with it: `Retry-After` on `429` (30 seconds) and `503` (120), `WWW-Authenticate` on `401`,
  `Allow` on `405`, no body on `204` and `304`, and an HTML page on `502` and `504`, as a gateway
  would send. Status Codes commits these. Its phrases come from a fixed table, because Python 3.13
  renamed four of its own (`413`, `414`, `416` and `422`), and on 3.12, which CI runs, they
  read differently: never print `HTTPStatus(...).phrase` for those four. Like `/v0`, `/status` stays
  out of the OpenAPI document.
- **`GET /echo` responds with the query its request arrived with**: `query` as sent, still encoded,
  and `args` decoded with `parse_qs`. Query Parameters shows every encoding through it, and it stays
  out of the OpenAPI document too. A station id is decoded before it is looked up, as real servers
  decode a path parameter, so a `404` names an encoded id as it was written.
- **`GET /network` is a made-up, nested document of the whole station network**, for JSON in a
  Response: every station with a `location` object, a list of `instruments` and a `status` object.
  Its gaps are deliberate, and that notebook's lessons depend on them: Svalbard's location has no
  `elevation_m`, two instruments have `last_calibrated: null`, and Tromso's `status` is `null`.
  `GET /network/export` sends the same stations as JSON Lines, one to a line, so `response.json()`
  raises `Extra data`. Both stay out of the OpenAPI document.
- **`GET /beta/network` is the network document as a future release will send it**, for Schemas and
  Validation. Four members change in ways a schema reports: Bergen's `elevation_m` becomes the text
  `"12"`, Oslo's `active` becomes `"yes"`, a Svalbard calibration becomes `30/06/2025`, and Tromso's
  `id` is renamed `station_id`. The new top-level `version` breaks nothing. Pydantic's default mode
  quietly converts the first two, and that notebook shows it.
- **`GET /network/summary` negotiates**, for Headers and Content Types: one table of the stations as
  JSON, CSV or HTML, chosen from `Accept` by quality, where the most specific matching range sets a
  format's quality and ties go to that order. It sends `Vary: Accept` and an `ETag` hashed from the
  body, so each format has its own, and answers `If-None-Match` with `304` only for the quoted value.
  `406` lists what is available. `GET /network/summary.csv` sends the same CSV as `text/csv` with no
  charset, which requests decodes as ISO-8859-1, so `Tromsø` reads `TromsÃ¸`. `GET /echo/headers`
  responds with the request headers received; print chosen ones, since `Accept-Encoding` differs
  between installations.
- **`GET /me`, `GET /network/maintenance`, `POST /auth/token` and `GET /auth/expired-token`
  authenticate**, for Authentication. The credentials are made up: `credentials()` returns them
  named as environment variables, and that notebook's Setup puts them in `os.environ`. `/me` says
  who sent a request, and takes the API key as `Authorization: Bearer`, in `X-API-Key`, or as an
  `api_key` query parameter. `/network/maintenance` needs the `maintenance:read` scope, which the key
  lacks, so the key gets `403` with `error="insufficient_scope"`. `/auth/token` is OAuth 2.0's
  client credentials grant, with Basic authentication and a form, and errors in `error` and
  `error_description`. Tokens are JWTs signed with HMAC, and the API's clock stops at the `Date`
  header's moment, so a token is the same on every run and never expires; `/auth/expired-token`
  hands out one that has. A request with no credential, or with a scheme other than Bearer, gets
  the challenge with no error code, as RFC 6750 asks. `access_log()` returns the line the server
  logs for each request, which is where a key sent in a query shows. A credential added later keeps
  the form `practice-key-...` or `practice-secret-...`, which is how `check_notebooks.py` finds one.
- **`GET /network/readings` and `GET /network/events` paginate**, for Pagination. The readings are
  made up: 72 hours at Bergen, Oslo and Tromso up to the `Date` header's moment, 216 in all, since
  Svalbard is inactive. They take `page` and `per_page` (30, and more than 100 gets 100), send a
  `total`, and a `Link` header whose addresses keep the request's own query. The events are a log of
  54, newest first, paged by an opaque `next_cursor` that is `null` on the last page, with a `limit`
  of 10 that refuses more than 50. With `station`, an events page holds that station's events from
  among the `limit` it looked through, so a page can be short or empty before the last, as Slack
  warns. Events also answer `page` and `per_page`, and in that mode gain one event before every page
  after the first, so page numbers repeat event 45 on every run and cursors do not. On both, a
  parameter given twice gets `400`, which is what a next link followed with `params=` still set
  runs into.
- **`GET /network/latest` and `GET /beta/network/latest` are rate limited, and `GET /rate-limit`
  reports the limit**, for Rate Limits: 5 requests in a 2-second window of real time, which opens at
  the first request after the last window closed and is shared by every caller. Every response
  carries `X-RateLimit-Limit`, `X-RateLimit-Remaining` and `X-RateLimit-Reset`, the seconds to the
  window's end rounded up, and a request past the limit gets `429` with `Retry-After` in the same
  seconds. The beta endpoint spends the same allowance and sends `Retry-After` as an HTTP date on the
  stopped clock, so the date minus the response's `Date` is the wait. `/rate-limit` does not count.
  Committed output depends on each example starting a fresh window, so every example that spends the
  limit calls `wait_for_reset()` first. A wait taken from a response always reaches the window's end,
  because the server rounds up and the client starts waiting after the server counted; spacing
  requests on the client's own clock needs a margin, which `Throttle` adds.
- **`GET /network/report`, `/network/unstable`, `/hang-up` and `/trickle` fail on purpose**, for
  Errors and Retries. `/network/report` answers after 2 seconds, so `timeout=1` raises `ReadTimeout`.
  `/hang-up` closes every connection without a response, which requests raises as `ConnectionError`
  with "Remote end closed connection without response". `/trickle` sends the report in 6 pieces half
  a second apart, so a read timeout of 1 never fires on a 3-second response. `/network/unstable`
  counts attempts by `X-Request-Id`: the first is closed without a response, the second gets `503`
  with `Retry-After: 1`, the third is answered, and a request with no id gets `400`. Examples send a
  fresh `uuid4` id, so a rerun meets the same failures. `Server.handle_error` ignores a client that
  went away, so a timed-out request's late reply never prints a traceback into a notebook. Never run
  a host name that fails in DNS: `stations.invalid` took 30 seconds to fail on macOS. A refused
  connection's message carries the operating system's error number, so print only its class. Seeds
  for jittered waits are chosen so that a deadline's stop-or-continue decision is at least half a
  second from its boundary.
- **`/network/plans` is the one collection a client can change**, for Sending Data. `GET` lists the
  plans, and `GET /network/plans/<id>` sends one with an `ETag`. `POST` creates a plan (`201`, with
  `Location` and `ETag`), `PUT` replaces one, `PATCH` changes the fields its body names and removes a
  field sent as `null`, and `DELETE` answers `204`. A body must be JSON with
  `Content-Type: application/json`, or `415` comes back; a dictionary passed to `requests.post` by
  position is sent as a form, and draws it. A plan with problems gets `422` and a list of them, with
  the reason phrase sent from `PHRASES`, since Python 3.13 renamed 422's. `POST` with an
  `Idempotency-Key` saves the created plan under the key: a repeat with the same body gets the same
  `201` with `Idempotent-Replayed: true` and creates nothing, the same key with another body gets
  `422`, and a body that failed validation is not saved. `POST ?delay=N`, up to 5, sleeps after
  creating the plan and before answering, so that a client's timeout loses the response to a
  request that worked. `If-Match` on `PUT`, `PATCH` and `DELETE` answers `412` when the plan has
  changed. The collection is empty whenever the module loads, so a notebook run from the top prints
  the same ids every time. Running a `POST` cell again makes another plan, which the notebook says,
  since showing that is the point of the notebook.
- **`start()` is idempotent** within a process, so rerunning Setup is safe. After a reload, it
  stops the server an earlier copy started and starts the new code on that port, so a rerun keeps
  `BASE` and nothing answers with old code. A second process moves to the next free port.
- **`serve(app)` runs an app a notebook writes**, from Your First API Server on. It runs uvicorn in a
  daemon thread on the first free port from 8000, serves one app at a time (serving another stops
  the first and takes its port), and survives Setup's reload as `start()` does. uvicorn's log level
  is critical, because a log line from the server's thread lands in whichever cell is running, with
  a traceback and a local path in it. uvicorn is imported inside `serve()`, so the module still needs
  only the standard library. uvicorn takes a reason phrase from the running Python's `HTTPStatus`,
  so a `422` from an app reads differently in CI (3.12) and here (3.14): never print it, which
  rules out a `raise_for_status()` message for an app's `422`. FastAPI's `TestClient` warns, with
  this machine's starlette, that its httpx is deprecated, and the warning carries a path, so a
  notebook tests an app by serving it and sending it requests. A cell that adds routes creates its
  app too, because a route added again when a cell reruns never replaces the first.
- **Grow it; do not change what exists.** Later notebooks add endpoints. Changing an existing
  response changes the committed output of every notebook that printed it.
- **The stations are read-only, permanently.** `GET` works on `/`, `/stations`,
  `/stations/{id}` and `/openapi.json`; every other method there responds `405` with
  `Allow: GET`, which What an API Is commits. Writable resources for **Sending Data** go at new
  paths.
- **The OpenAPI document describes the stations endpoints and nothing else.** Exploring an API
  commits its paths and prints them, so an endpoint added for teaching stays out of it, as
  `GET /v0/<path>` does: an old address that answers `301 Moved Permanently` with
  `Location: /<path>`, for Your First Request's `history`. Retired addresses are rarely documented,
  which the notebook says.
- **What `requests` sends depends on the installation.** Its default `Accept-Encoding` gains `br`
  or `zstd` when brotli or zstandard is installed (this machine has zstandard; Colab and CI do not),
  and `User-Agent` carries the version. Print chosen request headers, and only the product name
  from `User-Agent`.

**Real services** appear where the real internet is the point, and print only stable fields.
Open-Meteo's archive is keyless and free for non-commercial use, under 10,000 calls a day. Always
pass `models=era5`: the default model silently returned different values in testing, while ERA5
returned the same values on every fetch. Use dates long in the past. The data is CC BY 4.0 and ERA5
is Copernicus data, so every notebook that prints it carries: "Weather data by Open-Meteo.com, under
CC BY 4.0, from the ERA5 reanalysis. Generated using Copernicus Climate Change Service information
2026." The guide's `credits` says the same.

**`Connection refused` differs by operating system**: `[Errno 61]` on macOS, where outputs are
recorded, and `[Errno 111]` on Linux, which Colab and CI run. A notebook that commits it says so.

**Swagger's Petstore** (`https://petstore3.swagger.io`) is the public API for Postman's OpenAPI
import and for interactive documentation, because Open-Meteo publishes no OpenAPI document. Its
data changes as visitors add pets, so no committed output reads it.

**Open-Meteo fails intermittently from GitHub's runners, at the connection.** Two pushes on
14 September 2026 failed on it, once in the TLS handshake and once waiting for a response, while
the same requests took under half a second from elsewhere and the scheduled run an hour earlier
had passed. A longer timeout would not help; a fresh attempt does. `tools/run_notebooks.sh`, which
the notebooks workflow runs, retries a notebook whose failure names a network error, and warns
when it had to. It is also the way to run a notebook locally exactly as CI will:
`bash tools/run_notebooks.sh notebooks/<guide>/NN-slug.ipynb`.

**Open-Meteo has a recorded fallback.** On 14 September 2026 its archive, a single server,
answered with `500`s after half a minute for about an hour, for everyone. A reader in Colab met
it as a cell that hung and a next cell that failed. So `practice_api.open_meteo()`, called in the
Setup of every notebook that uses Open-Meteo, sends every recorded request to the archive, four at
a time, and returns its address if every response comes back as JSON within 10 seconds, or, with a
printed notice, the address of `/open-meteo/v1/archive`, a recording the practice API serves. Every
Open-Meteo request goes to `OPEN_METEO`, so curl lines use `{OPEN_METEO}` and double curl's own
braces. Four at a time, because Open-Meteo limits concurrent requests: once the recording held ten,
sending all ten at once drew `429`, "Too many concurrent requests", for one or two of them, and
Setup fell back to the recording although Open-Meteo was answering.

- The recording holds only the requests this guide makes, all for 2025-01-15 to 2025-01-17 from
  ERA5: every station's daily means, in Celsius, and Tromso's and Bergen's in Fahrenheit too; and
  every station's daily maximum, minimum and precipitation together, for Query Parameters. It is
  keyed by latitude, longitude, unit and daily variables, which it reads from a comma-separated
  value or a repeated name, as Open-Meteo does. It copies the behaviors notebooks show: an
  unrecognized parameter is ignored, and a daily value naming a variable outside `DAILY_VARIABLES`
  gets Open-Meteo's `400`, whose reason quotes the whole value, list and all. A notebook that makes
  a new Open-Meteo request adds it to the recording first, recorded from the live service.
- Commit outputs from a live run. `check_notebooks.py` fails on output showing the recording was
  used. `OPEN_METEO_RECORDING=1` forces the recording, which is how to test a notebook's fallback.

**Never print a real API's raw body.** Open-Meteo returned the same error body with its keys in a
different order on two requests. Parse it and print fields by name.

**Never show a credential, even a practice one.** A notebook is committed with its outputs, and
APIs and JSON teaches readers never to print a key. Print facts about a credential instead: its
length and last four characters, whether some text holds it, or text with it replaced by the name
of its variable. `check_notebooks.py` fails on the practice API's key or secret, or on any JSON Web
Token, in a notebook's source or output.

### Shell commands in a notebook

Exploring an API is the first notebook with `!` lines. IPython runs them in a pseudo-terminal, so
their output arrives with a carriage return before every line feed, and tools that detect a
terminal add escape codes: curl bolds header names, and Python 3.14's `json.tool` colors its output
where Colab's 3.12 does not. `tools/clean_outputs.py`, run by the build, strips both from stream
output, and `check_notebooks.py` fails on any it missed. Tracebacks keep their color.

- `{BASE}` in a `!` line is IPython's expansion of a Python expression. If any `{...}` in the line
  fails to evaluate, IPython expands nothing, so curl's own `%{http_code}` must be written
  `%{{http_code}}` in a line that also uses a Python variable. A line with no Python variable can
  keep curl's single braces. Exploring an API commits the mistake as a Common error.
- Pass curl `-s` whenever its output is piped or saved, or it prints a progress meter.
- A failed shell command raises nothing: the cell finishes and the error is only printed. Never tag
  such a cell `raises-exception`; there is no exception to expect.

## Testing and Packaging

Every notebook in **Testing and Packaging** works on one small project, the weather stations'
readings: a module, `readings.py`, a script, `summary.py`, and their tests, written into
`scratch/stations` with `%%writefile` and removed by the notebook's last cell.

- **Setup sets `NO_COLOR`.** ipykernel puts `FORCE_COLOR=1` and `CLICOLOR_FORCE=1` into the kernel's
  environment (6.30.1, which CI installs, and 7.2.0 on this Mac; Colab's 6.17.1 does not), and every
  program a cell starts inherits them. Python 3.13 and later then color a traceback, pytest colors its
  report, and the codes land in whatever a cell captures. `os.environ["NO_COLOR"] = "1"` keeps
  captured text the same in Colab, in CI and here. pip is the exception: it colors its error
  messages under `FORCE_COLOR` whatever `NO_COLOR` says, since it hands its own `--no-color` setting
  to rich, so the `pip` function passes `--no-color` from Requirements and Pinning on. The build
  strips terminal codes, so a colored line would be committed as an empty one.
- **Setup also sets `PYTHONDONTWRITEBYTECODE`**, from Your First Test on. A compiled copy in
  `__pycache__`, whether Python's or pytest's rewritten test file, counts as current while its source
  keeps its size and its modification time in whole seconds. A cell that rewrites a file to the same
  size within a second of the last run gets the old code: a test corrected from `return ... == 213`
  to `assert ... == 212` still warned until this was set.
- **Colab, CI and this Mac run three different Pythons.** Colab's published environment
  (`googlecolab/backend-info`, checked 15 September 2026) has Python 3.13.15, CI runs 3.12, and this
  Mac 3.14. Print nothing whose text depends on the version, such as the `^^^` markers under a line
  of a traceback, or the files a new virtual environment holds.
- **A notebook that rewrites a module reloads it.** `importlib.reload` runs the file as it is now. Why
  Test commits the mistake of testing the copy imported before the file changed as a Common error.
- **Notebooks run pytest through `run_pytest`**, which runs `python -m pytest --no-header` in the
  project's folder with `subprocess.run` and prints the report. It sets `COLUMNS=80`,
  `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`, since Colab installs anyio, langsmith and typeguard, which
  register pytest plugins, and `PYTHONNODEBUGRANGES=1`, which removes the `^^^` under a failing line.
  It takes out the folder's path, the path to pytest's own files and the time a run took. Your First
  Test explains every setting, and later notebooks define the function in Setup. `pytest_report`
  returns the text, for a cell that prints only some lines, such as a collection error's `E` line,
  whose traceback carries Python's own file paths.
- **pytest is pinned to 8.4.2, Colab's version**, and docs.pytest.org's stable pages now describe
  pytest 9. Check a message against the 8.4 pages at `docs.pytest.org/en/8.4.x/`: 8.4 prints
  `DID NOT RAISE <class 'ValueError'>`, where 9.1 prints the name alone.
- **Show at most one differing item when an `assert` compares dictionaries.** pytest 8.4.2 lists
  "Differing items" by walking a set of the keys, so two or more differences under string keys print
  in an order that changes from one run to the next. Test Structure's whole-value example breaks one
  station for that reason.
- **Virtual Environments, Requirements and Pinning and Project Layout install packages from PyPI.**
  Every environment is made with `--without-pip`, since Colab's Python has no `ensurepip`, and
  packages go in with the notebook's own pip, as `python -m pip --python ENV`. Install pinned
  versions, and print only what does not depend on the day or on pip's cache: exit codes, package
  names, the `Would install` line of a fully pinned `--dry-run`, and the last line of an error. Never
  print a version that floats, or a path inside an environment, which names its Python's version.
- **Continuous Integration runs a workflow's job on this computer.** `run_job` reads the workflow
  from the last commit with `git show`, clones that commit with `git clone --depth 1` from a
  `file://` address, makes a `--without-pip` environment in the clone and installs `pip==25.3` into
  it, so that the workflow's own `python -m pip` commands run unchanged, and runs every `run` step
  with `bash -e -c` and the environment's `bin` first on `PATH`. Setup sets `GIT_CONFIG_GLOBAL` to
  `os.devnull` and `GIT_CONFIG_NOSYSTEM`, so that a signing or branch setting on this Mac cannot
  change a commit, and gives commits a practice author through `GIT_AUTHOR_*` and
  `GIT_COMMITTER_*`. Print exit codes and pytest's `E`, `FAILED` and `ERROR` lines, never a hash or
  a date. PyYAML is pinned to 6.0.3, Colab's version, and reads a workflow's `on` key as `True`.

## SQLAlchemy, Deep Dive

Every notebook in **SQLAlchemy, Deep Dive** works on a college, which the author chose over the
weather stations because it has the relationships an ORM exists for. Why SQLAlchemy builds its first
two tables in Setup with the standard library's `sqlite3`: 25 students, among them Aoife O'Brien,
whose apostrophe is what the notebook's f-string breaks on, and 10 courses. From Connections and
Transactions on, Setup builds five tables with `sqlite3` (the string lives in the builders'
`sqa_common.py`): 4 `terms`, Fall 2024 to Spring 2026, which is under way; 40 `sections`, one of every
course in every term, where course `c` in term `t` is section `(t - 1) * 10 + c`, so Spring 2026's
are 31 to 40; and 228 `enrollments`, three courses a term for every student from the term they
started, `completed` with a grade in the first three terms and `enrolled` with none in Spring 2026.
An enrollment's status and grade make it the association table with extra columns that Many to Many
is about. Every student has enrollments and every section has students, so a notebook whose outer
join needs an unmatched row adds one. The data comes from lists and a formula in Setup, never from
`random`.

- **Pinned at SQLAlchemy 2.0.54**, the release the research outline was fact-checked against, in
  `requirements.txt` for CI. Colab ships its own 2.0 release, so every Setup prints
  `sqlalchemy.__version__`, and its prose says how to match 2.0.54 exactly with `%pip install` and a
  restart. The research outline's advice to open every notebook with a `pip install` cell does not
  survive the house rule that Setup is the first code cell.
- **Never print `echo=True` output through SQLAlchemy's own handler.** Every line starts with a
  timestamp, and the line after each statement says how long it took to compile, so no rerun matches.
  Show SQL with `compile`, as the notebooks' `show_sql` helper does, or through `PrintStatements`,
  which Engines and URLs teaches: a handler on the `sqlalchemy.engine.Engine` logger, with
  `propagate` off, that prints every statement and, from the record whose message is `[%s] %r`, only
  the values. SQLAlchemy adds its timestamped handler only to a logger that has none, so a notebook
  installs `PrintStatements` before any engine sets `echo`, and later notebooks define it in Setup.
- **Every notebook from Engines and URLs on makes its engines with `college_engine(path=None,
  echo=False)`**, defined in its Setup: a file with the default `QueuePool`, or with no path a database
  in memory on `StaticPool` with `check_same_thread=False`, and a `connect` event that switches on
  `PRAGMA foreign_keys` for every connection.
- **From Connections and Transactions on, the helper passes `connect_args={"autocommit": False}`.**
  Under `sqlite3`'s default legacy control, a `SAVEPOINT` that comes before any write starts a
  transaction of its own and commits when released, so an outer rollback leaves its rows saved, which
  that notebook shows as its last Common error. `autocommit=False` keeps a transaction open from the
  moment of connecting, where `PRAGMA foreign_keys` does nothing, so the `connect` event sets
  `autocommit` to `True` for the `PRAGMA` and back to `False`, as SQLAlchemy's SQLite documentation
  shows. Without that toggle the pragma reads 0 on every connection, with no error.
- **Let a reading connection's block end before another connection commits.** With `autocommit=False`
  a connection that has read holds SQLite's shared lock until its transaction ends, and a commit
  elsewhere waits for it, then fails with `database is locked`.
- **Never dispose an in-memory engine that two threads used through its default
  `SingletonThreadPool`.** `dispose()` closes every thread's connection from the thread that calls it,
  `sqlite3` refuses for the others, and the pool logs each refusal to stderr with a memory address and
  two thread numbers. Engines and URLs leaves such an engine for Python to collect, which is silent,
  since Python ignores `ResourceWarning` unless told otherwise.
- **Colab ships `psycopg2` and SQLAlchemy 2.0.52** (`googlecolab/backend-info`, checked 18 September
  2026), so `create_engine("postgresql://...")` succeeds there and fails here. A missing driver is
  shown with `psycopg`, version 3, which none of Colab, CI or this Mac has installed, and a default
  driver is read with `make_url(...).get_driver_name()`, which imports nothing.
- **Never print a mapped object without a `__repr__`.** The default is its memory address, which
  differs on every run, so a mapped class gets a `__repr__` the first time it is printed.
- **Sort what comes from a set or from SQLite's catalog before printing it.** `Table.constraints` is a
  set, whose order changes between runs, and `inspect(engine).get_foreign_keys()` lists a table's
  foreign keys in the order SQLite's `PRAGMA foreign_key_list` gives, the reverse of the order they
  were declared. Tables and Metadata sorts both, and prints `sorted(metadata.tables)` after
  `MetaData.reflect`.
- **Tables and Metadata names every constraint with `NAMING`**, the convention SQLAlchemy's
  documentation recommends for Alembic, with `%(column_0_N_name)s` for unique constraints so that the
  pair of course and term is `uq_sections_course_id_term_id`. Migrations with Alembic needs those
  names for batch mode on SQLite.
- **Compile for another database with no driver.** `postgresql.dialect()` and `mssql.dialect()`
  write SQL without importing a driver or reaching a server. `literal_binds` writes values into the
  SQL for a reader, never for running.

## sqlite3, Deep Dive

Every notebook in **sqlite3, Deep Dive** but Joins and Everyday Requests works on the weather
stations' hourly readings
for 2025 at Bergen, Oslo, Svalbard and Tromso, with Svalbard's readings empty for 2 March. Why
sqlite3's Setup writes them to `scratch/readings.csv` and loads that into a table. Later notebooks
build `scratch/stations.db` directly, handing a generator of the same values to `executemany`, and
every notebook's last cell removes the scratch folder. Tables and Queries splits the data into two
tables, `stations (id, name, latitude)` and `readings (id, station_id, hour, celsius)`, and adds
Kirkenes (latitude 69.73) as a station with no readings, which the left joins rely on. A later
notebook that joins stations to readings builds those two tables the way Tables and Queries does.

Everyday Requests, the guide's last notebook, has two databases of its own, since its subject is the
requests a developer answers against a schema somebody else designed: `school.db`, with 26 students,
10 courses, 3 terms, 41 sections, their enrollments and a `grades` lookup of grade points, and
`ledger.db`, with 9 customers, 48 invoices and their lines, and the payments applied to them. Both
come from formulas, both use `STRICT` tables, money is in `INTEGER` cents, and every report runs as
of `TODAY = "2026-04-15"` rather than asking the clock. Two of the students have completed nothing,
one registered for the current term and one not registered at all, and one section has no
enrollments: without them the notebook's `LEFT JOIN`s would all have behaved like inner joins, and
the prose around them would have been describing rows that were not there.

Joins works on the author's own example instead, at the author's request: `Employees` (Alice in
department 1, Bob in 2, Charlie in none) and `Departments` (1 HR, 2 IT, 3 Marketing, which has no
employees), with `EmpID`, `ManagerID` and `Salary` added for self joins and sums, in a database in
memory. Its prose names the people and never gives them a pronoun.

Full-Text Search and A Searchable Archive search text the readings could not give them, so both
generate it from the same formula: a technician's note for every station and day, its weather
sentence written from that day's lowest and highest reading, and an event from a fixed list chosen by
`(day_of_year * 37 + station_index * 101) % 23`. The research outline suggested the standard library's
own `.py` files, which differ between Pythons, so no search would print the same everywhere. Many notes
repeat a sentence and score the same, so every ranked query orders by `rank, rowid`.

- **The readings come from a formula, never from `random`.** Every number a notebook prints is then
  the same in Colab, in CI and here, and a later notebook can quote a value an earlier one printed.
- **Print nothing that depends on the SQLite version.** This Mac's Python 3.14.2 bundles SQLite
  3.50.4, and the SQLite that Colab's and CI's Pythons use has not been checked. Never print
  `sqlite3.sqlite_version`, a database file's size beyond what the page size fixes (an empty file,
  or the two pages of a database holding one small table), or a mean from `AVG` without rounding it.
- **Guard what needs a newer SQLite than 3.37.** `RIGHT JOIN` and `FULL JOIN` need 3.39.0, so Joins
  runs them only when `sqlite3.sqlite_version_info >= (3, 39, 0)`, and otherwise runs the `LEFT JOIN`
  or `UNION ALL` query that returns the same rows, which prints the same everywhere. `unixepoch()`
  needs 3.38.0 and `string_agg` 3.44.0, so SQL Syntax writes `CAST(strftime('%s', ...) AS INTEGER)`
  and Joins `group_concat`. `NULLS LAST` and an aggregate's `FILTER` need 3.30.0, from 2019, and go
  unguarded.
- **`connect(path)` creates a missing file.** A notebook that means to open a database that already
  exists opens it as `file:PATH?mode=rw` with `uri=True`, which Why sqlite3 teaches as a Common error.
- **Close a connection in the cell that opens it**, unless the next cell carries on with it. An open
  connection holds the file, and Python 3.13 and later emit `ResourceWarning` for a connection
  collected without being closed. CI runs Python 3.12, which emits nothing, so a cell that shows
  the warning prints what it caught and never indexes into it.
- **Close a cursor you stop reading before a later cell writes.** A cursor stopped partway through
  its results keeps a read lock on the database until it is closed, read to the end or deleted, even
  after its connection's `close()`, and a write from another connection then fails with
  `database is locked`. Connections and Cursors failed its first run this way, and now teaches it.
- **Look through a connection that holds no transaction.** A connection opened with
  `autocommit=False` begins a transaction as it connects, and its first read takes a shared lock that
  it keeps until it commits, so a write from any other connection then waits and fails with
  `database is locked`. autocommit and isolation_level checks what a load did through a `checker`
  connection opened with `autocommit=True`, and a later notebook that keeps an `autocommit=False`
  connection open beside other writers does the same.
- **Replace a memory address or a thread number before printing a message.** The
  `ResourceWarning` names the connection's address, a printed `sqlite3.Row` shows only its own
  address, and the thread error names two thread ids, all different on every run. Print the warning
  and the error through `re.sub`, as Connections and Cursors does, and a row as `dict(row)`. An error
  raised in another thread never reaches the cell, so the thread catches it for the cell to print.
- **A cell whose behavior changed between Pythons prints what happened.** A tuple for named
  placeholders raises `ProgrammingError` on Python 3.14 and only emits a `DeprecationWarning` on 3.12
  and 3.13, so Parameters runs it inside `warnings.catch_warnings(record=True)` and a `try`, and
  prints whichever came. Its Common errors heading is the 3.14 message, and the prose names both.
- **`executemany` with `RETURNING` does not do what Python's documentation says.** The documentation
  says the rows are discarded, and Python 3.14.2 inserts the first row and raises
  `sqlite3.InterfaceError: bad parameter or other API misuse` at the second. executemany catches
  `sqlite3.Error` around it and prints whichever happens, under a Common errors heading with the 3.14
  message.
- **Print a timing as a comparison, never as seconds.** The second run has to print what the first
  committed, so executemany prints `every_row > 50 * one_commit`, a margin chosen well below the
  several hundred times measured here, and says in prose that the seconds vary.
- **Print a plan's detail column, and keep plans simple.** SQLite's documentation says the wording
  of `EXPLAIN QUERY PLAN` can change between releases, so Indexes and Query Plans prints only the fourth
  column of each row, never the step numbers, and avoids plans that grew new lines in recent releases,
  such as an `IN` subquery, which 3.38.0 and later plan with a Bloom filter.
- **Read a plan after `DROP INDEX` through a new connection.** sqlite3 caches prepared statements by
  their text, and on SQLite 3.50.4 a cached `EXPLAIN QUERY PLAN` still names a dropped index, while a
  plan asked after `CREATE INDEX` or `ANALYZE` is fresh. Indexes and Query Plans teaches this as a
  Common error, and orders its examples so that no other plan follows a drop.
- **Run `ANALYZE`, not `PRAGMA optimize`, before a plan a notebook prints.** `PRAGMA optimize`
  analyzes only tables with an index that lacks statistics, and reads part of each index, and on the
  report in Indexes and Query Plans those partial counts led to a skip-scan through every station.
- **Stage a lock with an Event, never a sleep.** Concurrency and WAL has a thread take a lock, set a
  `threading.Event`, and only then lets the main thread act, so the order never depends on how fast a
  thread starts. `attempt` prints whether a statement ran at once or after waiting, never the seconds,
  and every thread opens and closes a connection of its own.
- **Never back a connection up while it holds a write transaction.** `backup` hears that the source
  is busy until the transaction ends, and sqlite3 retries forever, so the cell hangs and a run only
  ends at the executor's timeout. Backup and Copying warns about it in prose and never runs it.
- **Wrap `iterdump` in a transaction.** It runs one query for every table, so in WAL mode a commit
  that lands mid-dump appears in the tables dumped after it and not in those dumped before. Backup
  and Copying teaches this as a "No error" Common error, and dumps inside `BEGIN` and `COMMIT`.
- **Serialize only a database that is not in WAL mode.** Its header records WAL, and the bytes
  deserialize without complaint, then the first query fails with `unable to open database file`.
  `VACUUM INTO` writes a copy in the rollback journal mode, and `backup` keeps the source's mode.
- **Search for words that some documents lack.** A word in every document gets FTS5's smallest
  weight, so its `rank` prints as `-0.0` and the order rests on length alone. A Searchable Archive's
  monthly files all mention a battery, so its searches use `logger failed` and `above freezing`.
- **Print a snippet on one line.** A snippet of a document with line breaks can span them, so A
  Searchable Archive's `search` wraps it in `trim(replace(..., char(10), ' '))`.
- **`INSERT OR REPLACE` runs no delete trigger** unless `PRAGMA recursive_triggers` is on, so an
  external content FTS5 index keeps the replaced row's words under its old rowid, and a count by
  `MATCH` finds both. A Searchable Archive teaches it as a Common error, fixed with `'rebuild'`.
- **Never print a `SUM` over `REAL` values.** SQLite 3.43 and later add floating point numbers with
  Kahan-Babuska-Neumaier summation, and earlier versions add them plainly, so the last digits of a
  total can differ between Colab and here. Everyday Requests keeps money in `INTEGER` cents and shows
  the cost of a `REAL` with `CAST(dollars * 100 AS INTEGER)`, which is the same on every machine.
- **Give a computed column a name no table in the query has.** A bare name in `HAVING` resolves to a
  column of a joined table before it resolves to the `SELECT`'s alias, so `HAVING credits < 15`
  silently tested `courses.credits` and let every group through. Everyday Requests calls it
  `credits_earned` and teaches the shadowing as a Common error.
- **Set SQLite's double-quote fallback, never assume it.** A build of SQLite can be compiled so that
  a double-quoted word naming no column is an error instead of text, so a cell that shows the
  fallback first calls `conn.setconfig(sqlite3.SQLITE_DBCONFIG_DQS_DML, True)`, which needs Python
  3.12. With the fallback off, SQLite 3.46 and later add `- should this be a string literal in
  single-quotes?` to `no such column`, and 3.45 does not, so print only the part before the colon.
- **The guide's research lives outside git**, in `source/outlines/relational-and-document-databases.md`
  beside `site/`: the error each notebook is meant to show, the versions its claims were checked
  against, and the corrections the fact-check made.

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
- **The nav is not the guide list.** The guides across the top would wrap to several lines and
  tell a reader nothing. Nav is the library plus the repository; the pager walks the guides.
- **Never let a cell recurse without bound, even inside `try`.** The Jupyter kernel handles runaway
  recursion inconsistently. In **Dunder Methods**, a `__repr__` that formats itself raised a
  catchable `RecursionError`, but its message reports how many kilobytes of stack were used, which
  differs between machines, so that notebook catches it and prints a fixed line. In
  **Properties**, a setter that assigns to its own property did not raise at all under nbconvert:
  the C stack overflowed first and the kernel died (`DeadKernelError`), which no `except` can
  survive, and which would fail CI and wipe a reader's Colab session. Plain Python raised a clean
  `RecursionError` for the same code, so testing it outside a notebook proves nothing. To teach
  runaway recursion, make the cell count its own calls and stop itself, as Properties does.
- **A guide can have no outline yet.** `"notebooks": []` is valid: its page says the outline is
  not written yet instead of printing an empty table, and the index and the README leave the
  count blank. Write the outline into the manifest before that guide's first notebook.
- **A band is a block of consecutive guides.** The index prints a band heading whenever the band
  changes as it walks the guides by number, so the guides of one band are numbered together, and
  moving a guide into another band renumbers everything after it.
