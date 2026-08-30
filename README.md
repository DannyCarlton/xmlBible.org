# xmlBible.org

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/M4M83FULE)

An exhaustively marked-up XML edition of the King James Bible, in which every English word is
attached to the original-language word it renders.

The corpus is complete: **66 books, 1,189 chapter files, 31,102 verses**, every verse carrying its
Hebrew or Greek. Each chapter is a standalone XML file under `KJVs/NN-BookName/chapter-CCC.xml`.

---

## Repository layout

```
KJVs/                 The corpus. 66 book folders, one XML file per chapter.
  01-Genesis/
    chapter-001.xml
    ...
  66-Revelation/
    chapter-022.xml

Interlinear/          Older standalone interlinear edition. Superseded; see "What changed".
Styles/Interlinear/   CSS + JS used by the Interlinear edition only.
glossary.xml          Shared definition glossary.
```

This repository holds data only. The generator, the dashboard and the job runner are PHP and live
outside it; see **Build pipeline** below.

Book folder names run `NN-BookName` with no spaces (`09-1Samuel`, `22-SongofSolomon`). Chapter files
are zero-padded to three digits.

---

## The XML format

```
translation
  testament
    book
      chapter
        paragraph | poetry          block; repeats
          verse                     repeats
            phrase                  repeats
              orig                  0+  original-language word, before the English
              word                  0+  one English word each
```

A block is either `<paragraph>` (prose) or `<poetry>`. Blocks contain whole verses and never split
one.

### `<translation>`
| attribute | value |
|---|---|
| `version` | `KJV` |
| `variant` | `Cambridge` |
| `source` | `CrossWire KJV2006 OSIS` |

### `<testament>` — `type="Old"` or `type="New"`
### `<book>` — `name`, the full book name (`Song of Solomon`, not the folder form)
### `<chapter>` — `num`

### `<paragraph>` / `<poetry>`
`type="extra"` (optional) means the block break came from an OSIS `x-extra-p` milestone — a paragraph
break with no pilcrow in the source. No `type` means a pilcrow break or the chapter start.

Poetry is classified from the Cambridge Paragraph Bible USFM: a verse is `<poetry>` if CPB sets any
of its text on a `\q` poetic-line context. No line or stanza structure is recorded yet; `<l/>`
milestones will be added inside these blocks when the line layer lands.

### `<verse>` — `num`

### `<phrase>`
Groups the English word or words that render a single original word, and carries that word's
Strong's and morphology. Five kinds, distinguished by `type`:

**No `type`** — a tagged word group.

| attribute | meaning |
|---|---|
| `strongs` | primary Strong's, `H`- or `G`-prefixed (`H7225`, `G2532`) |
| `strongs2` | secondary Strong's — e.g. the object marker `H853` riding with a content word |
| `morph` | morphology tag from the spine (`TH8799`, `V-AAI-3S`) |
| `divine="true"` | renders the divine name (the small-caps `Lord`) |

| `type` value | contents |
|---|---|
| `supplied` | KJV italics — words supplied by the translators. `<word>` children carry `supplied="true"`. |
| `untagged` | KJV words the spine carries with no Strong's number. |
| `orig-only` | An original-language word tagged to no English word. Holds `<orig>`, no `<word>`. |
| `cam-only` | A Cambridge insertion with no Oxford anchor. Holds one `<word>` with the Cambridge form. |

### `<orig>` — one Hebrew or Greek word
Element text is the pointed Hebrew or accented Greek.

| attribute | meaning |
|---|---|
| `ow` | position in original-language reading order within the verse |
| `strong` | source Strong's including its disambiguation letter (`H7225G`) |
| `translit` | transliteration |
| `pos` | morphology code — ETCBC for Hebrew, TAGNT for Greek |
| `gloss` | short English gloss |
| `match` | how the word was matched: `alt` via the alternative-Strong's column, `equiv` via the curated equivalence map. Absent means a direct root match. |

### `<word>` — one English word
`supplied="true"` (optional) marks an italic word, only inside `type="supplied"` phrases.

**Cambridge overlay.** Verses where Oxford and Cambridge agree carry none of these, so the overlay
size tracks the number of differences.

| attribute | meaning |
|---|---|
| `cam="X"` | the Cambridge form of this word — spelling, case and punctuation in one value. A value containing a space is a 1→N split; reconstruct by splitting the string as-is. |
| `cam-supplied="true\|false"` | the italics decision differs from Oxford |
| `cam-del="true"` | this Oxford word is absent in Cambridge |

### Reconstructing either reading

**Oxford** — every `<word>` except those in `type="cam-only"` phrases, using its own text. Keep
`cam-del` words.

**Cambridge** — walk `<word>` elements in document order; skip `cam-del`; use `cam` where present,
otherwise the word text; include `cam-only` words.

The build runs this round-trip against the CPB token stream on every chapter. A mismatch fails the
build.

### Example

```xml
<poetry>
  <verse num="1">
    <phrase strongs="H7891" morph="TH8799">
      <orig ow="2" strong="H7891" translit="ya.shir-" pos="HVqi3ms" gloss="he sang">יָשִֽׁיר\־</orig>
      <word>Then</word>
      <word>sang</word>
    </phrase>
    <phrase strongs="H3068" divine="true">
      <orig ow="9" strong="H3068G" translit="la./Yah.weh" pos="HR/Npt" gloss="to/ Yahweh">לַֽ/יהוָ֔ה</orig>
      <word>unto</word>
      <word>the</word>
      <word>Lord,</word>
    </phrase>
    <phrase type="supplied"><word supplied="true">is</word></phrase>
    <phrase type="orig-only">
      <orig ow="3" strong="H0413" translit="'el-" pos="HR" gloss="&lt;to&gt;">אֶל\־</orig>
    </phrase>
  </verse>
</poetry>
```

---

## Sources

| Layer | Source |
|---|---|
| English text, Strong's, morphology, italics, divine name, paragraph breaks | CrossWire *KJV (1769) with Strongs Numbers and Morphology* OSIS |
| Hebrew `<orig>` | STEPBible TAHOT — Translators Amalgamated Hebrew OT (CC BY 4.0) |
| Greek `<orig>` | STEPBible TAGNT — Translators Amalgamated Greek NT (CC BY 4.0) |
| Poetry classification, Cambridge overlay | Cambridge Paragraph Bible USFM (engkjvcpb, Scrivener 1873, public domain) |

**Greek witness filter.** The New Testament includes Textus Receptus readings only — TAGNT rows
carrying the Scrivener K witness. Non-K rows are discarded. This is not configurable.

---

## Build pipeline

The build tooling is not in this repository. `kjvx-osis-build.php` generates the corpus from the
CrossWire OSIS spine plus the TAHOT/TAGNT and CPB sources; a dashboard and a whitelisted job runner
drive it. Those files are PHP and are kept alongside the repository rather than inside it, so what
is published here is the text and nothing else.

Each book goes through a four-step protocol:

1. **Probe** — read-only measurement of the book's own figures. Never inherited from another book.
2. **Build** — write to a smoke tree and verify against the probe's numbers.
3. **Publish** — copy the verified tree into the corpus.
4. **Audit** — corpus-wide verification.

Every English word round-trips byte-exact against the OSIS spine text, and the Cambridge
reconstruction round-trips against the CPB token stream. Both are hard failures.

---

## What changed in this commit

The repository carried five overlapping generations of the text. Four are gone:

| Removed | Was |
|---|---|
| `KJV/` | Plain verse text, UTF-16, `xml version="1.1"`, no Strong's. Fully contained in the corpus. |
| `Output/` | Phase-1 generator output, Genesis 1–12 only, retired schema. |
| `Interlinear-slim/` | Attribute-compressed copy of `Interlinear/`, generated on demand. |
| `01-Genesis/` (root) | A single orphaned prototype chapter. |

The old `KJVs/` — KJV text with unprefixed numeric Strong's on phrase-level groupings — has been
**replaced** by the OSIS-spine corpus previously built at `Output-osis/`. The folder name is kept;
the contents and schema are new. Consumers of the old `KJVs/` format need to migrate:

- Strong's numbers are now prefixed (`H7225`, not `7225`).
- Phrase text is no longer a plain string; English is in `<word>` children.
- The root element is `<translation>`, not `<book>`.
- `chapter.xsd` described the old format and no longer applies.
- Book folder names lost their spaces (`09-1 Samuel` → `09-1Samuel`).

`Interlinear/` remains for now. Its data will be folded into the corpus, after which it and
`Styles/` will be removed.

The PHP build tooling has also been taken out. The dashboard, the job runner and the interlinear
slimmer were tracked here because the repository doubles as the local web root; they are build
machinery, not published text, and they are now kept outside it.

---

## Licence

Code is GPL-3.0. Source texts carry their own licences: STEPBible TAHOT and TAGNT are CC BY 4.0; the
CrossWire OSIS spine and the Cambridge Paragraph Bible are public domain.
