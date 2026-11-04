"""Armor set modules. Each module exposes SET_ID, UV_REGION and build(anchors) -> {bone: [boxes]}. See README.md."""
import importlib

SET_IDS = ("sand", "usmc", "cerberus", "votoms", "outlander", "polar", "salvage", "shiden", "khamsin",
           "riverine", "specter", "valkyrie", "police", "rescue", "industrial", "amphibious", "utility", "mobility")


def load_all():
    return [importlib.import_module(f"{__name__}.{s}") for s in SET_IDS]
