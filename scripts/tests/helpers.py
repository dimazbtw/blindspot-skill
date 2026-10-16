"""Shared fixtures for the test suite: the bakery example, loaded fresh and deep-copied per call."""
import copy
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SCRIPTS = os.path.join(ROOT, "scripts")
EXAMPLE = os.path.join(ROOT, "examples", "bakery")
SESSIONS = os.path.join(EXAMPLE, "sessions")
sys.path.insert(0, SCRIPTS)


def _load(name):
    with open(os.path.join(EXAMPLE, name), "r", encoding="utf-8") as handle:
        return json.load(handle)


def ledger():
    return copy.deepcopy(_load("coverage-ledger.json"))


def findings():
    return copy.deepcopy(_load("findings.json"))


def adjustments():
    return copy.deepcopy(_load("adjustments.json"))


def scorecard():
    return copy.deepcopy(_load("scorecard.json"))


def finding(record, fid):
    return next(f for f in record["findings"] if f["id"] == fid)


def unit(led, uid):
    return next(u for u in led["units"] if u["id"] == uid)
