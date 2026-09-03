# Python, Visually

A library of interactive Python guides. Eleven guides, each a set of numbered Colab
notebooks you open and run.

**The notebook is the product.** The explanation, the code, its output and the figures all
live in the notebook. These pages exist only to get you to the right one.

**[Browse the library](https://johnfisher-ai.github.io/Python-Visual-Guides/)**

## How to use it

Every notebook opens in Google Colab and runs with no installation. Read it on GitHub first
if you prefer, then open it and change something. The exercises are the point, and each
notebook has a separate solutions file so nothing is spoiled by sitting next to the question.

## The guides

| | Guide | Notebooks | |
|---|---|---|---|
| 1 | **Python from the Start** | 20 | Being written |
| 2 | Files, Paths and Formats | 10 | Planned |
| 3 | Object-Oriented Python | 12 | Planned |
| 4 | APIs and JSON | 12 | Planned |
| 5 | Testing and Packaging | 10 | Planned |
| 6 | NumPy, Deep Dive | 14 | Planned |
| 7 | Pandas, Deep Dive | 18 | Planned |
| 8 | Matplotlib, Deep Dive | 12 | Planned |
| 9 | SciPy, Deep Dive | 12 | Planned |
| 10 | scikit-learn, Deep Dive | 14 | Planned |
| 11 | Projects, End to End | 8 | Planned |

Guides are finished one at a time. A guide is not published until every notebook in it runs
top to bottom in a fresh runtime.

## Every notebook has the same eight parts

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

**Common errors** is the part most tutorials leave out. Each notebook breaks its own code on
purpose, runs it, and keeps the traceback, so the error you are about to hit is already
named and explained.

## What is in this repository

| Path | What it is |
|---|---|
| [`manifest.json`](manifest.json) | The source of truth: guides, notebooks, order, blurbs. Every page is generated from it. |
| [`notebooks/`](notebooks/) | The content, committed with outputs so GitHub renders them. |
| [`tools/`](tools/) | The build and its four gates. |
| `public/` | The site. Generated; never hand-edited. |

## Building

```bash
bash tools/build.sh
```

Two passes over the page builders, then four gates: the manifest is consistent, every link
resolves, the house rules hold, and every notebook has the eight-part shape. Any failure
stops the build.

Notebooks are executed separately, in CI: the ones that changed on every push, and all of
them weekly. That weekly run is what catches a library that changed its API or a download
that quietly died.

## License

**Notebooks, prose and figures: [CC BY 4.0](LICENSE). Tooling: [MIT](LICENSE-CODE).**

Use any of it, including in a course you charge for, with credit:

> John Fisher, *Python, Visually*.
> https://johnfisher-ai.github.io/Python-Visual-Guides/

## Credits

By John Fisher. Sibling to
**[Statistics, Data Science and AI: A Visual Handbook](https://github.com/johnfisher-ai/Statistics-Data-Science-AI-Visual-Book)**,
which covers the statistics these guides lean on.

© 2026 John Fisher.
