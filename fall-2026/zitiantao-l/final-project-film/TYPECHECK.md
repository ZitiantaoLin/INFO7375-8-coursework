# TYPECHECK.md — GATE T

Reel: `eyespan-final-project-pitch`  |  Checked: 2026-10-24T21:23  |  Overall: PASS  |  Beats checked: 13  |  FAILs: 0

Spec: `skills/make/kerning/reference/type-spec.md` §8.  Floor: 1.9% frame-height.  Contrast: 4.5:1 WCAG.  Kern threshold: 3.5× expected advance.  Wordy budget: 2 elements.

| beat | lane | polarity | worst finding | status | fix |
|------|------|----------|---------------|--------|-----|
| B00 | ? | light | min-size §8.1: min text-run height 31px >= floor 20px | PASS | — |
| B01 | ? | light | min-size §8.1: min text-run height 32px >= floor 20px | PASS | — |
| B02 | ? | light | min-size §8.1: min text-run height 22px >= floor 20px (individual-char fallback at 1×) | PASS | — |
| B03 | ? | light | min-size §8.1: min text-run height 21px >= floor 20px (individual-char fallback at 1×) | PASS | — |
| B04 | ? | light | min-size §8.1: min text-run height 22px >= floor 20px (individual-char fallback at 1×) | PASS | — |
| B05 | ? | light | min-size §8.1: min text-run height 31px >= floor 20px | PASS | — |
| B06 | ? | light | min-size §8.1: min text-run height 21px >= floor 20px (individual-char fallback at 1×) | PASS | — |
| B07 | ? | light | min-size §8.1: min text-run height 32px >= floor 20px | PASS | — |
| B08 | ? | light | min-size §8.1: min text-run height 32px >= floor 20px | PASS | — |
| B09 | ? | light | min-size §8.1: min text-run height 25px >= floor 20px | PASS | — |
| B10 | ? | light | min-size §8.1: min text-run height 31px >= floor 20px | PASS | — |
| B11 | ? | light | min-size §8.1: min text-run height 31px >= floor 20px | PASS | — |
| B12 | ? | light | min-size §8.1: min text-run height 20px >= floor 20px (individual-char fallback at 1×) | PASS | — |

---

## Failures requiring action before cut

*None — GATE T PASS.*
---

## Check summary

| Check | Beats checked | FAILs |
|-------|---------------|-------|
| no-wordy-card §8.5 | 0 | 0 |
| min-size §8.1 | 13 | 0 |
| overflow §8.2 | 13 | 0 |
| contrast §8.3 | 13 | 0 |
| contrast-local §8.3b | 13 | 0 |
| bbox-overlap §8.6b | 13 | 0 |
| card-clip §8.13 | 13 | 0 |
| kerning §8.4 | 0 | 0 |
| redundancy §8.10 (advisory) | 0 | 0 (advisory — no exit effect) |

---

*GATE T: any FAIL blocks `./art run` and `./art final`. Fix the flagged beats and re-run `scripts/type_check.py` until green.*
