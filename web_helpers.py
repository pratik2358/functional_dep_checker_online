from __future__ import annotations

import ast
import random
import string
from typing import Iterable, List, Tuple

import pandas as pd


def parse_attributes(text: str) -> set[str]:
    attrs = {tok.strip() for tok in text.replace('\n', ',').split(',') if tok.strip()}
    return attrs


def parse_attr_set(text: str) -> set[str]:
    return parse_attributes(text)


def parse_fds(text: str) -> list[tuple[set[str], set[str]]]:
    """
    Parse FDs from a simple line-based format.

    Accepted examples:
      A -> B
      A,B -> C,D
      AB -> C    (treated as attribute named 'AB', not split)
    """
    fds: list[tuple[set[str], set[str]]] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        if '->' not in line:
            raise ValueError(f"Invalid FD line: {line!r}. Expected 'LHS -> RHS'.")
        lhs_txt, rhs_txt = line.split('->', 1)
        lhs = parse_attr_set(lhs_txt)
        rhs = parse_attr_set(rhs_txt)
        if not lhs or not rhs:
            raise ValueError(f"Invalid FD line: {line!r}. LHS and RHS must both be non-empty.")
        fds.append((lhs, rhs))
    return fds


def format_fd(lhs: Iterable[str], rhs: Iterable[str]) -> str:
    return f"{{{', '.join(sorted(lhs))}}} -> {{{', '.join(sorted(rhs))}}}"


def format_fds(fds: list[tuple[set[str], set[str]]]) -> str:
    if not fds:
        return "No functional dependencies found."
    return "\n".join(format_fd(lhs, rhs) for lhs, rhs in fds)


def format_closures(closures: dict[Iterable[str], Iterable[str]]) -> str:
    lines = []
    for lhs, rhs in sorted(closures.items(), key=lambda kv: (len(tuple(kv[0])), tuple(sorted(kv[0])))):
        lines.append(f"{{{', '.join(sorted(lhs))}}}+ = {{{', '.join(sorted(rhs))}}}")
    return "\n".join(lines)


def format_candidate_keys(keys: list[tuple[str, ...]]) -> str:
    if not keys:
        return "No candidate keys found."
    return "\n".join(f"{{{', '.join(k)}}}" for k in keys)


def format_prime_attributes(attrs: Iterable[str]) -> str:
    attrs = sorted(set(attrs))
    return "{" + ", ".join(attrs) + "}" if attrs else "{}"


def grouped_fds_table(grouped_fds: list[tuple[set[str], set[str]]]) -> pd.DataFrame:
    rows = []
    for lhs, rhs in grouped_fds:
        rows.append({"LHS": ", ".join(sorted(lhs)), "RHS": ", ".join(sorted(rhs))})
    return pd.DataFrame(rows)


def literal_eval_dataframe(text: str) -> pd.DataFrame:
    obj = ast.literal_eval(text)
    if not isinstance(obj, dict):
        raise ValueError("The input must be a Python dictionary mapping column names to value lists.")
    return pd.DataFrame(obj)


def make_attribute_names(n: int) -> list[str]:
    upper = list(string.ascii_uppercase)
    lower = list(string.ascii_lowercase)
    base = upper + lower
    names = []
    k = 0
    while len(names) < n:
        for sym in base:
            if len(names) >= n:
                break
            suffix = "" if k == 0 else str(k)
            names.append(f"{sym}{suffix}")
        k += 1
    return names[:n]


def generate_random_fds(
    n_vars: int,
    num_fds: int,
    max_lhs_size: int = 3,
    max_rhs_size: int = 3,
    allow_trivial: bool = False,
    seed: int | None = None,
) -> tuple[set[str], list[tuple[set[str], set[str]]]]:
    if n_vars < 1:
        raise ValueError("n_vars must be at least 1")
    if num_fds < 1:
        raise ValueError("num_fds must be at least 1")

    rng = random.Random(seed)
    names = make_attribute_names(n_vars)
    attributes = set(names)
    fds: list[tuple[set[str], set[str]]] = []

    while len(fds) < num_fds:
        lhs_size = rng.randint(1, min(max_lhs_size, n_vars))
        lhs = set(rng.sample(names, lhs_size))

        rhs_pool = list(attributes) if allow_trivial else [a for a in names if a not in lhs]
        if not rhs_pool:
            rhs_pool = list(attributes)
        rhs_size = rng.randint(1, min(max_rhs_size, len(rhs_pool)))
        rhs = set(rng.sample(rhs_pool, rhs_size))

        fd = (lhs, rhs)
        if fd not in fds:
            fds.append(fd)

    return attributes, fds
