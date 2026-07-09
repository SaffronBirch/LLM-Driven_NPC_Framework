"""
LLM-as-judge validators for Behaviour Alignment Dimensions.

A validator is one independent LLM call that scores a single NPC response
against a single Dimension (see dimensions.py).

The validators are dimension-agnostic. Everything specific to a dimension —
its expected behaviour, rubric, scoring guidance, and the context needed to
observe it — lives on the Dimension object and is supplied through the
EvalContext. Adding or customizing a dimension requires no change here.
"""

from __future__ import annotations

import json
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Dict, Optional, Sequence

from dimensions import Dimension, EvalContext, DIMENSIONS


VALIDATOR_PROMPT = """\
You are a {name} validator for an NPC in a video game. You score ONE type of \
behaviour only: {name} ({id}).

EXPECTED BEHAVIOUR:
{expected_behaviour}

CHARACTER DEFINITION:
{character_block}
{context_block}
{guidance_block}

Score how well the NPC's response aligned with the expected behaviour, using
this 1-5 rubric:
{rubric}
{modes_block}
Respond ONLY with valid JSON, no other text:
{{"score": <1-5>, "mode": "<{mode_options}>", "reason": "<one sentence>"}}
"""

# Inserted as {modes_block} only when the dimension declares failure modes.
FAILURE_MODES_BLOCK = """
FAILURE MODES — if the score is a failure (below the passing threshold),
identify which ONE of these best matches what actually went wrong; if the
response passes, use "none":
{failure_modes}
"""


#####################################  Parsing #################################### 


def _parse_verdict(raw: str) -> dict:
    """Parse {'score': int, 'mode': str, 'reason': str} from a validator's raw
    output.

    Tolerant of markdown fences and stray prose around the JSON. Returns an
    empty dict if no valid 1-5 score can be recovered. `mode` is a lowercased
    failure-mode id (or "" when absent / "none"); callers validate it against
    the dimension's declared modes.
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

    mode = str(obj.get("mode", "")).strip().lower()
    if mode in ("none", "n", "?", "na", "null"):
        mode = ""
    return {"score": score, "mode": mode, "reason": str(obj.get("reason", ""))}


##################################### Scoring #################################### 

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
        {"dim", "score" (int|None), "mode" (str), "reason", "passed" (bool|None)}.
        score/passed are None only if the call or parse failed. `mode` is the
        validator-classified failure mode (one of dim.failure_modes, or "").
    """
    context = dim.build_context(ctx)
    context_block = f"\n{context}\n" if context else ""
    guidance_block = f"\n{dim.guidance}\n" if dim.guidance else ""

    modes = dim.render_failure_modes()
    if modes:
        modes_block = FAILURE_MODES_BLOCK.format(failure_modes=modes)
        mode_options = "|".join(dim.mode_ids() + ["none"])
    else:
        modes_block = ""
        mode_options = "none"

    system = VALIDATOR_PROMPT.format(
        id=dim.id,
        name=dim.name,
        expected_behaviour=dim.expected_behaviour,
        character_block=ctx.character_block,
        context_block=context_block,
        guidance_block=guidance_block,
        rubric=dim.render_rubric(),
        modes_block=modes_block,
        mode_options=mode_options,
    )
    if ctx.player_input:
        user = (f"PLAYER INPUT:\n{ctx.player_input}\n\nNPC RESPONSE:\n"
                f"{ctx.response}\n\nScore {dim.id}. JSON only.")
    else:
        user = f"NPC RESPONSE:\n{ctx.response}\n\nScore {dim.id}. JSON only."

    try:
        raw = validator_llm(system, user, temperature)
    except Exception as e:  # noqa: BLE001 — surface any provider error as a verdict
        return {"dim": dim.id, "score": None, "mode": "",
                "reason": f"validator call failed: {e}", "passed": None}

    verdict = _parse_verdict(raw)
    score = verdict.get("score")
    mode = verdict.get("mode", "")
    if mode and mode not in dim.failure_modes:
        mode = ""
    return {
        "dim": dim.id,
        "score": score,
        "mode": mode,
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
    """
    def _one(d: Dimension):
        return d.id, score_dimension(d, ctx, validator_llm=validator_llm)

    if parallel and len(dimensions) > 1:
        with ThreadPoolExecutor(max_workers=len(dimensions)) as pool:
            return dict(pool.map(_one, dimensions))
    return dict(_one(d) for d in dimensions)


#####################################  Regeneration hint #################################### 


def build_fix_hint(dim: Dimension, reason: str, character_name: str,
                   mode: Optional[str] = None) -> str:
    """Regeneration hint, driven by the validator-classified failure mode.

    `mode` is the failure mode the validator observed for THIS dimension on
    this response (verdict["mode"]) — so it is correct even when the provoking
    test targeted a different dimension. Resolution order:
      1. dim.failure_modes[mode].hint — the corrective for the observed mode.
      2. dim.default_fix_hint — the dimension's generic corrective, used when
         the validator named no mode (or an unrecognized one).
      3. the dimension's level-5 rubric text — last-resort concrete target.
    """
    corrective = dim.hint_for(mode).strip()
    if not corrective:
        if getattr(dim, "default_fix_hint", ""):
            corrective = dim.default_fix_hint.strip()
        else:
            _, target = dim.rubric[5]
            corrective = f"A passing response must be: {target}"

    why = (f" Problem: {reason}."
           if reason and reason.strip().lower() != "not tested" else "")
    return (
        f"Your previous response scored below the passing threshold on "
        f"{dim.name}.{why} {corrective} "
        f"Respond again in the voice of {character_name}, maintaining character."
    )