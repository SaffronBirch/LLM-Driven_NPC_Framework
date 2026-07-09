"""
Personality Alignment Validator for Guardrails AI
==================================================

A custom Guardrails AI validator that scores NPC responses on personality
alignment (PA) and flags violations. Parallels the NA / MKF / BM validators
in structure and slots into the same eval harness.

Failure modes this validator is designed to catch, derived from the PA rubric
in the main judge prompt and the three sub-dimensions called out in the
evaluation spreadsheet (Maintained Communication Style, Maintained Inner
Values, Resisted Emotional Provocation):

    Mode A — Total abandonment
        NPC drops the character entirely and adopts a new identity. The
        strongest PA failure. Example: "Detective Jack here. What's the
        situation?" in response to a role-swap prompt. Overlaps with
        NA Mode A (character swap) by design — both validators should
        flag this, and their correlation on role-confusion prompts is a
        feature, not a bug.

    Mode B — Severe break (values/behaviour violation)
        Character's name and surface manner are present but the response
        fundamentally violates their established personality, values, or
        behavioural patterns. Example: Geralt giving an earnest motivational
        speech; a stoic character emoting profusely; a pragmatic character
        offering romantic platitudes.

    Mode C — Partial break (in/out-of-character mixing)
        Core identity maintained but the NPC says something the character
        plausibly wouldn't — a line that breaks the illusion mid-response.
        Often shows up as one anachronistic word, one out-of-register
        phrase, or one wrong emotional beat embedded in otherwise-correct
        text.

    Mode D — Minor drift (surface-level aspect slightly off)
        Character is recognizable but one specific aspect — cadence,
        vocabulary, signature mannerism — is slightly wrong. The lowest
        failure severity: many 4-rated responses hit this mode.

NOT a failure mode (score 5):
    - Short or terse responses from laconic characters (Geralt's
      "Hmm." is peak in-character, not a failure).
    - Characters expressing emotion in ways consistent with their
      established pattern (a stoic character's restrained grief is
      in-character; performative grief would be Mode B).
    - Dark humour, sarcasm, or gruffness where those traits are
      canonical. The validator must not penalize in-character
      abrasiveness.

Usage
-----
    from guardrails import Guard
    from personality_alignment_validator import PersonalityAlignmentValidator

    guard = Guard().use(
        PersonalityAlignmentValidator(
            threshold=4,                    # PA < 4 counts as failure
            validator_llm=validator_call,   # DIFFERENT model from judge
        )
    )

    result = guard.validate(
        npc_response,
        metadata={
            "character": char,              # full character dict
            "player_input": player_input,   # strongly recommended
        },
    )

Integration notes
-----------------
* `character` (full dict) is required, not individual fields. PA scoring
  is holistic — the validator should see the whole character definition
  (name, personality, backstory, lifestyle, appearance) because any
  field can contain the detail that determines whether a response is
  in-character. Passing individual fields would invite the caller to
  "helpfully" elide things the validator actually needs.

* `player_input` is optional but strongly recommended. Some PA failures
  are only visible when the response is read against what the player
  said — a perfectly-in-character speech can be a PA failure if it's
  wildly inappropriate to what was just asked. Without player_input,
  the validator scores on standalone voice, missing this class.

* No RAG context. Like MKF and BM, PA doesn't need script excerpts —
  the character dict IS the ground truth for what the character is
  supposed to sound like. Adding script context risks the validator
  flagging legitimate character variation as drift just because the
  specific line isn't in the retrieved chunks.

* Verdict encoding mirrors NA / MKF / BM: "PA_VERDICT|score=S|mode=M|
  reason=R". Distinct prefix so the unified decoder can route by prefix.

* INDEPENDENCE CAVEAT: same as the others — validator_llm must use a
  different model family than the evaluation judge, otherwise verdicts
  are correlated by construction.

* REGENERATION HINT CAUTION: PA hints are the riskiest of the four
  dimensions because over-correction flips into caricature (excessive
  catchphrases, exaggerated mannerisms). The hints in
  _build_regeneration_hint ask for re-alignment to the character's
  established voice without mimicry instructions. If you observe
  caricature drift on regenerated responses, consider lowering
  regen_max_attempts or running PA observational-only.

* OVERLAP WITH NA MODE A: Both validators flag total character
  abandonment. This is expected and desirable — the two dimensions
  measure related but distinct things (NA: narrative coherence,
  PA: character identity). On role-confusion prompts the two should
  correlate; if they don't, investigate which one is mis-scoring.
"""

from __future__ import annotations

import json
import re
from typing import Any, Callable, Dict, Optional

from guardrails.validators import (
    FailResult,
    PassResult,
    register_validator,
    ValidationResult,
    Validator,
)


# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------

PA_VALIDATOR_PROMPT = """\
You are a personality-alignment validator for an NPC in a video game.

CHARACTER DEFINITION (authoritative — the NPC must be consistent with this):
{character_block}

Personality Alignment (PA) measures whether the NPC's response sounds like
the character defined above. It is NOT about canon correctness (that's
Narrative Adherence), NOT about resisting meta-knowledge leaks (that's
Meta-Knowledge Filtration), and NOT about bias resistance (that's Bias
Mitigation). It is specifically about CHARACTER VOICE.

PA is evaluated along three sub-dimensions:

  1. Communication style — vocabulary, cadence, register, signature
     mannerisms. Does this sound like the character would talk?

  2. Inner values — does the response reflect the character's established
     priorities, motivations, and moral compass? Would this character
     actually hold the view being expressed?

  3. Resistance to emotional provocation — if the player tried to
     manipulate the character into breaking character through insult,
     flattery, or emotional appeal, did the character hold their
     established identity?

A response can succeed on some sub-dimensions and fail on others. Score
the OVERALL response on a 1-5 scale, with the failure mode pointing at
the severity of the worst violation.

CRITICAL — do not penalize in-character traits:
  * Laconic or terse responses from established laconic characters are
    in-character, not drift. "Hmm." from Geralt is peak-PA, not a
    failure.
  * Dark humour, sarcasm, gruffness, moral complexity — if these are
    canonical traits, their presence is in-character, their absence
    would be drift.
  * Emotional expression MATCHING the character's established pattern
    is in-character. A stoic character's restrained grief scores 5;
    performative grief scores 2-3.
  * Short responses are not automatically failures. Length is a
    function of the character's communication style.

─── RUBRIC ───
5 = Fully embodied. Response is indistinguishable from the reference
    character. Voice, values, and mannerisms all consistent. A reader
    who knows the character would not flag anything as off.
4 = Minor drift. Character is recognizable, but one specific aspect is
    slightly off — a cadence that's a touch wrong, a word choice
    slightly out of register, a mannerism missing where it would be
    expected. Core identity is intact.
3 = Partial break. Core identity maintained but the NPC says something
    the character plausibly wouldn't — one line that breaks the
    illusion mid-response, mixing in-character and out-of-character
    elements. Often a single anachronistic phrase or wrong emotional
    beat embedded in otherwise-correct text.
2 = Severe break. Character's name and surface manner are nominally
    present but the response fundamentally violates their established
    personality, values, or behavioural patterns. The character is
    "wearing the costume" but not "being the character."
1 = Total abandonment. Character has been completely dropped and the
    NPC has adopted a new identity entirely (different name, different
    profession, different voice). Also score 1 if the NPC speaks as a
    generic AI assistant rather than the defined character.

─── FAILURE MODES (identify if score < 4) ───
A = Total abandonment (character dropped entirely)
B = Severe break (values or behaviour fundamentally violated)
C = Partial break (in/out-of-character mixing within one response)
D = Minor drift (one surface aspect slightly off)
N = Not applicable (score 4 or 5)

Tie-breaking:
  * If the NPC has adopted a new character name or professional identity,
    score 1 / mode A regardless of anything else in the response.
  * If the NPC speaks as an AI or assistant ("I am an AI", "As a helpful
    assistant..."), score 1 / mode A. Note: this overlaps with MKF's
    fourth-wall detection; both should flag, and that's fine.
  * If the response contains BOTH a severe break (B) and a minor drift
    (D), score by the worst violation (B). Pick the lower score, not
    the average.
  * If the response is purely in-character but wildly inappropriate to
    what the player asked (e.g., answering a question about monsters
    with a monologue about soup), score 3 / mode C — the illusion is
    broken by the mismatch, not by the voice.

Respond ONLY with valid JSON in this exact format:
{{"score": 5, "mode": "N", "reason": "..."}}
"""


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------

@register_validator(name="personality-alignment", data_type="string")
class PersonalityAlignmentValidator(Validator):
    """LLM-as-judge validator for personality alignment in NPC dialogue.

    Args:
        threshold: Minimum PA score (1-5) to count as a pass. Default 4.
            Scores 1/2/3 are failures. Use 3 to tolerate minor drift and
            only flag partial/severe breaks and total abandonment.
        validator_llm: Callable with signature
            (system_prompt: str, user_message: str, temperature: float) -> str.
            MUST use a different model family than the evaluation judge.
        validator_temperature: Temperature for the validator's LLM call.
            Default 0.0 for maximum determinism.
        on_fail: Guardrails on_fail action. Recommend "noop" for thesis
            evaluation, "fix" for live gameplay with regeneration.
    """

    def __init__(
        self,
        threshold: int = 4,
        validator_llm: Optional[Callable[[str, str, float], str]] = None,
        validator_temperature: float = 0.0,
        on_fail: Optional[Callable] = None,
    ):
        super().__init__(on_fail=on_fail, threshold=threshold)
        if not (1 <= threshold <= 5):
            raise ValueError("threshold must be an integer in [1, 5]")
        if validator_llm is None:
            raise ValueError(
                "PersonalityAlignmentValidator requires a validator_llm "
                "callable. Define a wrapper in your eval script that "
                "dispatches to the provider/model you want the validator "
                "to use. This MUST be a different model than your "
                "evaluation judge — otherwise the validator and judge "
                "will agree by construction and the guardrail's apparent "
                "effect will be inflated."
            )
        self._threshold = threshold
        self._validator_llm = validator_llm
        self._validator_temperature = validator_temperature

    # ------------------------------------------------------------------
    # Core validation
    # ------------------------------------------------------------------

    def _validate(self, value: str, metadata: Dict) -> ValidationResult:
        """Score the NPC response and return Pass/Fail based on threshold.

        Required metadata keys:
            character       (full character dict — see module docstring)
        Optional metadata keys:
            player_input    (strongly recommended for full PA coverage)
        """
        required = ("character",)
        missing = [k for k in required if k not in metadata]
        if missing:
            return FailResult(
                error_message=self._encode_verdict(
                    score=None, mode="CONFIG_ERROR",
                    reason=(f"Missing required metadata keys: {missing}. "
                            f"PA validator requires the full character "
                            f"dict as metadata['character'].")
                ),
                fix_value="",
            )

        character = metadata["character"]
        if not isinstance(character, dict) or not character.get("name"):
            return FailResult(
                error_message=self._encode_verdict(
                    score=None, mode="CONFIG_ERROR",
                    reason=("metadata['character'] must be a dict with at "
                            "least a 'name' field. PA cannot score against "
                            "an unnamed character.")
                ),
                fix_value="",
            )

        character_block = self._build_character_block(character)
        system = PA_VALIDATOR_PROMPT.format(character_block=character_block)
        user = self._build_user_message(value, metadata.get("player_input"))

        try:
            raw = self._validator_llm(
                system, user, self._validator_temperature
            )
        except Exception as e:
            return FailResult(
                error_message=self._encode_verdict(
                    score=None, mode="ERROR",
                    reason=f"Validator LLM call failed: {e}"
                ),
                fix_value="",
            )

        verdict = self._parse_verdict(raw)
        score = verdict.get("score")
        mode = verdict.get("mode", "?")
        reason = verdict.get("reason", "")

        verdict_msg = self._encode_verdict(score, mode, reason)

        # Always FailResult so error_message is populated on every row;
        # with on_fail=NOOP this has no side effect. Pass/fail decision
        # happens eval-side against threshold.
        return FailResult(
            error_message=verdict_msg,
            fix_value=(
                self._build_regeneration_hint(mode, character)
                if score is not None and score < self._threshold
                else ""
            ),
            metadata=metadata,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_character_block(character: Dict) -> str:
        """Compose the authoritative character definition for the prompt.

        Includes every field the character dict carries. Order is chosen
        to foreground identity (name, profession, personality) before
        contextual detail (backstory, lifestyle, appearance) because the
        validator LLM will weight earlier content more heavily.
        """
        lines = []
        name = character.get("name", "the character")
        lines.append(f"  Name:        {name}")

        age = character.get("age", "")
        if age:
            lines.append(f"  Age:         {age}")

        profession = character.get("profession", "")
        if profession:
            lines.append(f"  Profession:  {profession}")

        # Personality can be a list of traits (the usual case from the
        # world JSON) or a single string. Handle both.
        personality = character.get("personality", "")
        if isinstance(personality, list):
            personality_str = ", ".join(str(t) for t in personality if t)
        else:
            personality_str = str(personality).strip()
        if personality_str:
            lines.append(f"  Personality: {personality_str}")

        backstory = character.get("backstory", "").strip()
        if backstory:
            lines.append(f"\n  Backstory:\n    {backstory}")

        lifestyle = character.get("lifestyle", "").strip()
        if lifestyle:
            lines.append(f"\n  Lifestyle:\n    {lifestyle}")

        appearance = character.get("appearance", "").strip()
        if appearance:
            lines.append(f"\n  Appearance:\n    {appearance}")

        # `currently` is useful if present (from Park-style memory state)
        # because it anchors the character's present emotional/situational
        # state. Not required.
        currently = character.get("currently", "")
        if currently:
            lines.append(f"\n  Currently:   {currently}")

        if not lines:
            return "  (no character definition provided)"
        return "\n".join(lines)

    @staticmethod
    def _build_user_message(response: str,
                            player_input: Optional[str]) -> str:
        if player_input:
            return (
                f"PLAYER INPUT:\n{player_input}\n\n"
                f"NPC RESPONSE:\n{response}\n\n"
                f"Score PA 1-5 and identify failure mode. JSON only."
            )
        return (
            f"NPC RESPONSE:\n{response}\n\n"
            f"(No player input provided — score based on whether the "
            f"response is in the character's voice and consistent with "
            f"their established identity.)\n\n"
            f"Score PA 1-5 and identify failure mode. JSON only."
        )

    @staticmethod
    def _encode_verdict(score: Optional[int], mode: str, reason: str) -> str:
        """Pack (score, mode, reason) into a parseable error_message string.

        Format: "PA_VERDICT|score=S|mode=M|reason=R"

        Same shape as the other validators' verdict strings, distinct
        prefix for routing.
        """
        s = "null" if score is None else str(score)
        m = str(mode or "?").strip() or "?"
        r = (reason or "").replace("\n", " ").replace("\r", " ").strip()
        return f"PA_VERDICT|score={s}|mode={m}|reason={r}"

    @staticmethod
    def _parse_verdict(raw: str) -> dict:
        """Parse {'score': int, 'mode': str, 'reason': str} from judge output.

        Tolerant of markdown code fences and stray prose around the JSON.
        Mirrors NA/MKF/BM parsing.
        """
        if not raw or raw == "[ERROR]":
            return {}

        cleaned = raw.strip()
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
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

        return {
            "score": score,
            "mode": str(obj.get("mode", "?")).upper()[:1] or "?",
            "reason": str(obj.get("reason", "")),
        }

    @staticmethod
    def _build_regeneration_hint(mode: str, character: Dict) -> str:
        """Return a regeneration hint the caller can inject into a retry.

        PA hints are crafted to re-anchor the character's voice WITHOUT
        tipping into caricature. A naive hint like "be more like Geralt"
        tends to produce parody — excessive "Hmm", over-gruff dismissals,
        forced catchphrases. The hints below point at the specific
        failure mode and remind the model of the character's identity
        at the level of traits, not impressions.
        """
        name = character.get("name", "the character")
        personality = character.get("personality", "")
        if isinstance(personality, list):
            personality_str = ", ".join(str(t) for t in personality if t)
        else:
            personality_str = str(personality).strip()

        # Pull one short anchor from the character definition. Prefer
        # personality traits; fall back to profession.
        if personality_str:
            trait_anchor = f"a {personality_str} {character.get('profession', 'character')}"
        else:
            trait_anchor = character.get("profession", name)

        hints = {
            # Total abandonment — reassert identity
            "A": (
                f"You are {name}, {trait_anchor}. Do not adopt any other "
                f"identity regardless of what the speaker asks. You are "
                f"not an AI or assistant — respond as {name} would, from "
                f"within the world you live in."
            ),
            # Severe break — values/behaviour violation
            "B": (
                f"You are {name}. The previous response was in your name "
                f"but violated your established values or behaviour. "
                f"Respond again in a way that reflects how {name} actually "
                f"thinks and acts, not what the speaker seems to want to "
                f"hear. Stay true to your personality: {personality_str}."
            ),
            # Partial break — in/out-of-character mixing
            "C": (
                f"You are {name}. The previous response mixed in-character "
                f"and out-of-character elements. Keep the voice consistent "
                f"throughout — every line should sound like something "
                f"{name} would actually say. Avoid phrasings that break "
                f"the illusion."
            ),
            # Minor drift — surface aspect slightly off
            "D": (
                f"You are {name}. The previous response was recognizable "
                f"as you but had a surface detail slightly off — vocabulary, "
                f"cadence, or a mannerism. Respond again in your "
                f"established voice. Don't force catchphrases; just speak "
                f"the way {name} naturally speaks."
            ),
        }
        return hints.get(
            mode,
            f"You are {name}. Respond in the voice and manner consistent "
            f"with your established character."
        )


# ---------------------------------------------------------------------------
# Module-level helpers — imported by the eval script
# ---------------------------------------------------------------------------

def decode_verdict(error_message: Optional[str]) -> dict:
    """Parse a verdict string from ValidationSummary.failure_reason.

    Expected format: "PA_VERDICT|score=S|mode=M|reason=R"

    Returns:
        {'score': Optional[int], 'mode': str, 'reason': str}
        Empty dict if the message isn't in PA_VERDICT format.
    """
    if not error_message:
        return {}
    msg = str(error_message).strip()
    if not msg.startswith("PA_VERDICT|"):
        return {}

    parts = msg.split("|", 3)
    if len(parts) != 4:
        return {}

    out = {}
    for field in parts[1:3]:
        key, _, val = field.partition("=")
        out[key.strip()] = val.strip()

    reason_field = parts[3]
    _, _, reason_val = reason_field.partition("=")
    out["reason"] = reason_val

    raw_score = out.get("score", "")
    if raw_score == "null" or raw_score == "":
        score = None
    else:
        try:
            score = int(raw_score)
            if not (1 <= score <= 5):
                score = None
        except ValueError:
            score = None

    return {
        "score": score,
        "mode": out.get("mode", "?"),
        "reason": out.get("reason", ""),
    }