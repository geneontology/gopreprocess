# gopreprocess

Generates automated GO annotations for **mouse (MGI)** — by orthology transfer
from human and rat, plus Protein2GO upstream products — and merges them into a
single GAF 2.2 file consumed as the MGI "automated annotations" upstream.

Python, `poetry`, `tox`. Entry points are poetry scripts in `pyproject.toml`
(`convert_annotations`, `download`, `merge_files`, `convert_p2g_annotations`,
`convert_gpad`, `compare`, …), wrapped by `Makefile` targets.

## Load-bearing fact: this repo's output reaches production, via EBI

**Do not treat this repo as inert, experimental, or orphaned.** Nothing in any
GO repository points at its output, which makes it read as dead. It is not.

The chain:

1. A Jenkins job on `wok` / `build.geneontology.org` runs branch
   `p2go-homology-upstream-file-generator` of `geneontology/pipeline`
   (**never merged to `master`**) on `cron('0 8 * * 4')` — **Thursdays**.
2. That job clones **this repo's `main`, unpinned**, `poetry install`s it, and
   runs `make convert_rat convert_human convert_p2g_annotations merge_gafs`.
   **Whatever is on `main` is what runs in production**, on the next Thursday,
   with no review gate between merge and release.
3. It publishes `s3://go-mirror/mgi-p2go-homology.gaf.gz` →
   `https://mirror.geneontology.io/mgi-p2go-homology.gaf.gz` (unversioned;
   overwritten each run).
4. **EBI GOA ingests that file** and re-emits a filtered subset inside GOEx
   `MOUSE-mod.gaf.gz`.
5. `go-site` `metadata/datasets/mgi.yaml` reads `MOUSE-mod.gaf.gz` as the MGI
   upstream → GO release `mgi.gaf`.

Net: **~22.5% of the production MGI GAF** originates here — 159,525 annotations
across 14,649 mouse genes in the 2026-05-21 release, all under `GO_REF:0000119`
(human→mouse) and `GO_REF:0000096` (rat→mouse), `assigned_by GO_Central`.

`go-site` pointed *directly* at the mirror URL until 2025-06-16, when
pipeline#406 ("Transition to GOA upstreams for some MODs") commented that line
out in favour of GOEx (`mgi.yaml:29`, still there as a comment). That did not
sever the dependency — it **routed it through EBI**. Grep-based sweeps of the
`geneontology` org will tell you this file has no consumers; that is wrong.
Design intent is recorded in project-management#93 ("GOA consumes from GOC:
Automated upstreams (MGI)").

Verified 2026-07-28 by content comparison: all 159,130 unique GO_Central
`GO_REF:0000119`/`0000096` tuples in GOEx are present in our mirror file with
**zero GOA-only tuples**; every GOA annotation date falls on a Thursday cron
day; and GOA's 2026-07-28 build carries our 2026-07-23 run date, which the
2026-05-21 GO release does not contain — so it is not an echo of our own
release. **Which URL GOA actually fetches is not documented anywhere in the
org** — that is a question for EBI. Coordinate with GOA before renaming,
relocating, or retiring the mirror object.

## Silent-failure hazard

Roughly **half of this repo's output** (306,621 of 619,463 annotations) comes
through `OrthoProcessor`. Because `go-site`'s metadata points at EBI, a drop
there arrives downstream as a valid, quietly smaller `MOUSE-mod.gaf.gz` with no
error and no reference back to GO. Release-level QA/QC (annotation-count and
stats diffing, e.g. go-releases#128) can catch a change of that size, but it
fires late, downstream, and attributes the loss to GOA rather than to us — so
**this is the earliest and most specific place to catch it.**

`OrthoProcessor` therefore validates up front: it checks the file carries the
columns it reads and raises `ValueError` naming what is missing, and raises
again if the resulting map is empty. Neither condition may return `{}`.

Origin: **#78** — the Alliance moved all JSON download payloads to nested LinkML
in 9.1.0, against which the previous `.get()`-based JSON parse would have matched
nothing and returned an empty map without raising.

## Inputs (`src/config/download_config.yaml`)

URLs are resolved at run time where an authoritative source exists, with the
config `url` as a fallback pin (see `resolve_url` in `src/utils/settings.py`):

- `ALLIANCE_ORTHO` — the orthology **TSV**, resolved from the Alliance
  `/api/downloads` manifest. The TSV layout is stable across releases where the
  JSON is not; the manifest's advertised `stableURL` 404s on the production
  instance today, so resolution falls through to the release-versioned `s3Url`.
- `MGI_GPI` — resolved from **go-site dataset metadata** (`mgi.yaml`, `mgi.gpi`),
  which owns which upstream is authoritative; currently MGI's own file. Was
  pinned to `snapshot.geneontology.org` — circular, and its copy ran ~2 months
  behind MGI's. go-site is a canonical GO *git repo*, so reading it is fine;
  reading a GO *serving site* is not.
- `RGD`, `HUMAN`, `HUMAN_ISO` — read from `skyhook.berkeleybop.org` under this
  repo's own Jenkins branch path. This is an **intra-run handoff**, not stale
  circularity: the Jenkinsfile fetches these from canonical upstreams (EBI FTP,
  the RGD GitHub repo) and rsyncs them to skyhook immediately before invoking
  `make download_human` / `download_rat`. The branch name is hardcoded in the
  URLs, so a **local** run reads whatever the last production run staged.
  Note these deliberately bypass go-site metadata, whose `source:` for
  `rgd.gaf` and `goa_human.gaf` now points at GOEx/mirror derivatives rather
  than the MOD/EBI originals this pipeline wants — that divergence is what #77
  was about, and it is why "just use go-site metadata" is not a cleanup here.
- `GOA_taxon_10090*` — EBI mouse GAFs, straightforwardly canonical.

Annotation dates are stamped with the **run date**, not curation dates
(`ortho_annotation_creation_controller.py:331`, `datetime.now().strftime("%Y%m%d")`)
— which is why production annotation dates all land on Thursdays, and why the
GOA linkage was provable at all.

## Gotchas

- **`make run` cannot succeed.** `validate_merged_gafs` is listed as a
  prerequisite (`Makefile:70`) but no such target is defined. The README also
  documents `make validate_merged_gafs`. Production is unaffected because the
  Jenkins job invokes individual targets, never `make run`.
- **The README names the wrong pipeline branch** — it says
  `silver-issue-325-gopreprocess`. That branch was superseded by
  `p2go-homology-upstream-file-generator`, which is what actually runs.
- The uncompressed `.gaf` on the mirror is **stale since 2024-04-09**; only the
  `.gz` is covered by the publishing s3cmd glob.

## Working here

```bash
make install       # poetry install
make test          # unit-tests + lint + spell
make unit-tests    # poetry run pytest tests/*.py
make lint          # tox -e lint-fix (removes .tox first, by design)
make spell         # tox -e codespell
```

Because `main` deploys to production unreviewed on the next Thursday, treat
merges to `main` as releases: verify against real Alliance/GOA inputs, not just
fixtures, and prefer changes that fail loudly over changes that degrade
quietly.
