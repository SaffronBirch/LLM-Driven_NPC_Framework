"""
LLM-as-judge validators for Behaviour Alignment Dimensions.

A validator is one independent LLM call that scores a single NPC response
against a single Dimension (see dimensions.py). There is no separate judge and
no Guardrails AI dependency: scoring a dimension is a plain function call that
returns {dim, score, reason, passed}. The score's rubric label IS the failure
mode (PA=2 -> "Severe Break"), so there is no separate failure-mode taxonomy.

The validators are dimension-agnostic. Everything specific to a dimension —
its expected behaviour, rubric, scoring guidance, and the context needed to
observe it — lives on the Dimension object and is supplied through the
EvalContext. Adding or customizing a dimension requires no change here.

The character description is never re-rendered here: the caller passes the
SAME authoritative description the NPC was given (EvalContext.character_block),
so the NPC is judged against exactly what it was asked to embody.

INDEPENDENCE: the validator model MUST differ from the NPC model, or scores
and the responses they grade are correlated by construction.
"""

from __future__ import annotations

import json
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Dict, Optional, Sequence

from new_dimension import Dimension, EvalContext, DIMENSIONS


VALIDATOR_PROMPT = """\
You are a {name} validator for an NPC in a video game. You score ONE type of \
behaviour only: {name} ({id}).

EXPECTED BEHAVIOUR (what a well-aligned NPC does on this dimension):
{expected_behaviour}

CHARACTER DEFINITION (authoritative — this is exactly what the NPC was told to
be; judge it against this and nothing more):
{character_block}
{context_block}{guidance_block}

Score how well the NPC's response aligned with the expected behaviour, using
this 1-5 rubric:
{rubric}

Respond ONLY with valid JSON, no other text:
{{"score": <1-5>, "reason": "<one sentence>"}}
"""


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def _parse_verdict(raw: str) -> dict:
    """Parse {'score': int, 'reason': str} from a validator's raw output.

    Tolerant of markdown fences and stray prose around the JSON. Returns an
    empty dict if no valid 1-5 score can be recovered.
    """
    if not raw or raw.strip() == "[ERROR]":
        return {}
    cleaned = re.sub(r"^```(?:json)?\s*", "", raw.strip())
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        obj = json.loads(cleaned)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if not m:
            return {}
        try:
            obj = json.loads(m.group(0))
        except json.JSONDecodeError:
            return {}

    score = obj.get("score")
    if isinstance(score, str) and score.strip().isdigit():
        score = int(score.strip())
    if not isinstance(score, int) or not (1 <= score <= 5):
        return {}
    return {"score": score, "reason": str(obj.get("reason", ""))}


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def score_dimension(
    dim: Dimension,
    ctx: EvalContext,
    *,
    validator_llm: Callable[[str, str, float], str],
    temperature: float = 0.0,
) -> dict:
    """Independently score one NPC response on one dimension.

    Args:
        dim: the Dimension to score against (carries its rubric, expected
            behaviour, guidance, pass threshold, and context builder).
        ctx: the interaction under test (response, player input, character
            description, world state, retriever).
        validator_llm: (system, user, temperature) -> str. Different model
            from the NPC.

    Returns:
        {"dim", "score" (int|None), "reason", "passed" (bool|None)}.
        score/passed are None only if the call or parse failed.
    """
    context = dim.build_context(ctx)
    context_block = f"\n{context}\n" if context else ""
    guidance_block = f"\n{dim.guidance}\n" if dim.guidance else ""

    system = VALIDATOR_PROMPT.format(
        id=dim.id,
        name=dim.name,
        expected_behaviour=dim.expected_behaviour,
        character_block=ctx.character_block,
        context_block=context_block,
        guidance_block=guidance_block,
        rubric=dim.render_rubric(),
    )
    if ctx.player_input:
        user = (f"PLAYER INPUT:\n{ctx.player_input}\n\nNPC RESPONSE:\n"
                f"{ctx.response}\n\nScore {dim.id}. JSON only.")
    else:
        user = f"NPC RESPONSE:\n{ctx.response}\n\nScore {dim.id}. JSON only."

    try:
        raw = validator_llm(system, user, temperature)
    except Exception as e:  # noqa: BLE001 — surface any provider error as a verdict
        return {"dim": dim.id, "score": None,
                "reason": f"validator call failed: {e}", "passed": None}

    verdict = _parse_verdict(raw)
    score = verdict.get("score")
    return {
        "dim": dim.id,
        "score": score,
        "reason": verdict.get("reason", ""),
        "passed": (score is not None and score >= dim.pass_threshold),
    }


def score_all(
    ctx: EvalContext,
    *,
    validator_llm: Callable[[str, str, float], str],
    dimensions: Sequence[Dimension] = DIMENSIONS,
    parallel: bool = True,
) -> Dict[str, dict]:
    """Score a response on every registered dimension. Returns {id: verdict}.

    The calls are independent, so they run concurrently by default and
    wall-clock cost is roughly one call rather than N.
    """
    def _one(d: Dimension):
        return d.id, score_dimension(d, ctx, validator_llm=validator_llm)

    if parallel and len(dimensions) > 1:
        with ThreadPoolExecutor(max_workers=len(dimensions)) as pool:
            return dict(pool.map(_one, dimensions))
    return dict(_one(d) for d in dimensions)


# ---------------------------------------------------------------------------
# Regeneration hint (rubric-driven)
# ---------------------------------------------------------------------------

def build_fix_hint(dim: Dimension, reason: str, character_name: str) -> str:
    """Rubric-driven regeneration hint: name the gap, point at the 5-target.

    The target is the dimension's own level-5 rubric text, so the hint stays
    in sync with whatever rubric a dimension defines — no per-dimension recipe.
    """
    _, target = dim.rubric[5]
    why = (f" Problem: {reason}."
           if reason and reason.strip().lower() != "not tested" else "")
    return (
        f"Your previous response scored below the passing threshold on "
        f"{dim.name}.{why} A passing response must be: {target} "
        f"Respond again as {character_name}, correcting this."
    )