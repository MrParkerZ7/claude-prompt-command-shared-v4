# ---
# skill: spec-driven-generation
# role: workflow
# capability: value-lineage-ledger
# ships-command: null
# bundle-id: spec-driven-generation-2026-08-30
# bundle-tier: full
# body: full
# native-hint: shared/workflows/spec-lineage-reference.py
# ---
# -*- coding: utf-8 -*-
"""Value-lineage ledger — REFERENCE IMPLEMENTATION.

Copy into a project as `0-script/_lib/_lineage.py`. Generic: it knows nothing about any
particular artifact - a builder imports `Ledger`, calls `.rec()` per cell, and `.save()`.
Pairs with `spec-where-reference.py` (the query tool). See `specs/SPEC_DRIVEN_GENERATION.md`
§ Value lineage.

Value-lineage ledger — so a LATER session can trace any number back to its source.

The problem this solves: spec-driven generation records how a sheet is SHAPED, and the
manifest records which FILES fed a unit. Neither answers "where did this ฿27,976 come from,
and how was it computed?" — which is the question a new session actually has when it opens
the workbook and does not trust a figure.

Design: the builder records lineage **as it writes each cell**, in the same transaction.
A ledger maintained separately drifts from the sheet; one emitted at write time cannot.

Confidence is a closed vocabulary, and it is the field that matters most:

    documented  a source document states this figure outright        (a statement, an invoice,
                                                                      a filed return, a contract)
    derived     computed from documented figures by a stated method  (16/31 x a monthly rate)
    estimated   the user's own record, with no source document       (a pre-coverage year)
    assumed     a forward-looking input the user can edit            (an effective tax rate)

Claiming `documented` obliges you to name a path that resolves. `_spec_check.py` enforces
that: a `documented` record whose source does not exist on disk is DRIFT. This exists because a real project
shipped figures labelled "documented" that were really inherited from an earlier summary of
itself - the label was rhetoric, not a checkable claim.

Usage inside a builder:

    from _lineage import Ledger
    L = Ledger("Readings")
    L.rec("C20", 87300.0, "documented",
          src="0-records/statements/2025-07.pdf",
          method="statement line 'Total 87,300.00' - base component",
          chain=["source PDF", "extract.py", "_data/parsed.json", "build_readings.py"])
    ...
    L.save()          # merges into _data/_lineage.json, replacing this unit's block
"""
import os, io, json, datetime

CONFIDENCE = ("documented", "derived", "estimated", "assumed")
_HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(_HERE, "..", "_data", "_lineage.json")


class Ledger(object):
    def __init__(self, sheet):
        self.sheet = sheet
        self.rows = {}
        self.stamped = datetime.date.today().isoformat()

    def rec(self, cell, value, confidence, src=None, method=None, chain=None, inputs=None, note=None):
        """Record one value's lineage. `cell` is an A1 address within this sheet."""
        assert confidence in CONFIDENCE, "confidence must be one of %s, got %r" % (CONFIDENCE, confidence)
        if confidence == "documented" and not src:
            raise ValueError("a 'documented' value MUST name its source: %s!%s" % (self.sheet, cell))
        e = {"value": value, "confidence": confidence}
        if src: e["source"] = src
        if method: e["method"] = method
        if chain: e["chain"] = chain
        if inputs: e["inputs"] = inputs
        if note: e["note"] = note
        self.rows[cell] = e

    def rec_many(self, cells, **kw):
        for c, v in cells:
            self.rec(c, v, **kw)

    def save(self, coverage=None):
        led = {"_description":
               ("VALUE-LEVEL lineage: where every recorded figure came from and how it was "
                "computed. Written BY the builders at cell-write time, so it cannot drift from "
                "the sheet. Query it with `0-script/_lib/_where.py \"<Sheet>!<Cell>\"`. "
                "confidence: documented (a source document states it) | derived (computed from "
                "documented figures by the stated method) | estimated (own record, no document) | "
                "assumed (an editable forward input). A 'documented' record MUST name a path that "
                "resolves - _spec_check.py enforces it."),
               "sheets": {}}
        if os.path.isfile(LEDGER):
            try:
                led = json.load(io.open(LEDGER, encoding="utf-8"))
                led.setdefault("sheets", {})
            except Exception:
                pass
        led["sheets"][self.sheet] = {"stamped": self.stamped, "cells": self.rows}
        if coverage: led["sheets"][self.sheet]["coverage"] = coverage
        os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
        json.dump(led, io.open(LEDGER, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        n = len(self.rows)
        from collections import Counter
        c = Counter(v["confidence"] for v in self.rows.values())
        return "lineage: %d values recorded for %s (%s)" % (
            n, self.sheet, ", ".join("%s %d" % (k, c[k]) for k in CONFIDENCE if c[k]))
