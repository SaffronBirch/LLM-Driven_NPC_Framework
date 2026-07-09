/* Hero: Results page with before/after guardrail comparison */

function ResultsPage({ selectedCaseId, setSelectedCaseId, comparisonLayout }) {
  const { summary, guardrails, history, cases, character } = MOCK;
  const guardrailsNo = guardrails.filter((g) => g.key !== "compliance");
  const cumulative = guardrails.find((g) => g.key === "compliance");
  const selectedCase = cases.find((c) => c.id === selectedCaseId) || cases[0];

  return (
    <>
      <div className="page-head">
        <div
          style={{
            display: "flex",
            alignItems: "flex-start",
            justifyContent: "space-between",
            gap: 20,
          }}
        >
          <div>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 8,
                marginBottom: 4,
              }}
            >
              <span
                className="mono"
                style={{ fontSize: 11, color: "var(--ink-3)" }}
              >
                RUN #1
              </span>
              <Badge kind="pass">COMPLETED</Badge>
              <span
                className="mono"
                style={{ fontSize: 11, color: "var(--ink-3)" }}
              >
                · {MOCK.project.lastRun}
              </span>
            </div>
            <h1>Guardrail Evaluation — {character.name}</h1>
            <div className="sub">
              Baseline (no guardrails) vs. guarded (PA + MK + BM + NA) across{" "}
              {summary.casesRun} test cases.
            </div>
            <div className="meta-row">
              <span>
                runtime <b>{summary.runtime}</b>
              </span>
              <span>
                tokens <b>{summary.tokensUsed.toLocaleString()}</b>
              </span>
              <span>
                cost <b>${summary.costUsd.toFixed(2)}</b>
              </span>
              <span>
                Validator <b>gemini-2.5-flash</b>
              </span>
              <span>
                seed <b>123</b>
              </span>
            </div>
          </div>
          <div style={{ display: "flex", gap: 6 }}>
            <button className="btn">{I.download} Export CSV</button>
            <button className="btn">{I.copy} Share</button>
            <button className="btn primary">{I.refresh} Rerun</button>
          </div>
        </div>
      </div>

      <div className="page-body">
        {/* Top metrics row */}
        <div className="grid-5" style={{ marginBottom: 20 }}>
          <div
            className="card-metric"
            style={{
              gridColumn: "span 1",
              display: "flex",
              alignItems: "center",
              gap: 12,
            }}
          >
            <Gauge
              value={summary.guarded.compliance}
              label="GC guarded"
              size={90}
              stroke={7}
            />
            <div>
              <div
                style={{
                  fontSize: 10.5,
                  textTransform: "uppercase",
                  letterSpacing: "0.08em",
                  color: "var(--ink-3)",
                  fontWeight: 600,
                  marginBottom: 2,
                }}
              >
                vs. baseline
              </div>
              <div
                className="mono"
                style={{ fontSize: 14, color: "var(--ink-3)" }}
              >
                {pctFmt1(summary.baseline.compliance)}
              </div>
              <Delta
                from={summary.baseline.compliance}
                to={summary.guarded.compliance}
              />
            </div>
          </div>
          {guardrailsNo.map((g) => (
            <div className="card-metric" key={g.key}>
              <div
                className="label"
                style={{ display: "flex", alignItems: "center", gap: 6 }}
              >
                <GSwatch cat={g.key} /> {g.short} · {g.name.split(" ")[0]}
              </div>
              <div
                className="val"
                style={{
                  color: `var(--${scoreClass(summary.guarded[g.key])})`,
                }}
              >
                {pctFmt1(summary.guarded[g.key])}
              </div>
              <div className="foot">
                <Delta
                  from={summary.baseline[g.key]}
                  to={summary.guarded[g.key]}
                />
                <span style={{ color: "var(--ink-3)" }}>
                  <Spark data={history[g.key]} />
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* Guardrail-level comparison bar chart */}
        <div className="panel" style={{ marginBottom: 20 }}>
          <div className="panel-head">
            <span>Guardrail-Level Comparison</span>
            <div className="actions">
              <span className="muted mono" style={{ fontSize: 10.5 }}>
                baseline ▂▂
              </span>
              <span
                className="mono"
                style={{ fontSize: 10.5, color: "var(--pass)" }}
              >
                guarded █
              </span>
            </div>
          </div>
          <div
            className="panel-body"
            style={{ display: "flex", flexDirection: "column", gap: 14 }}
          >
            {guardrails.map((g) => {
              const b = summary.baseline[g.key];
              const a = summary.guarded[g.key];
              const isCum = g.key === "compliance";
              return (
                <div key={g.key}>
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      marginBottom: 5,
                    }}
                  >
                    <div
                      style={{ display: "flex", alignItems: "center", gap: 8 }}
                    >
                      <GSwatch cat={g.key} />
                      <span
                        style={{
                          fontWeight: isCum ? 600 : 500,
                          fontSize: 12.5,
                        }}
                      >
                        {g.name}
                      </span>
                      <span className="mono muted" style={{ fontSize: 10.5 }}>
                        {g.short}
                      </span>
                      {isCum && <Badge kind="neutral">cumulative</Badge>}
                    </div>
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: 18,
                        fontFamily: "var(--font-mono)",
                        fontSize: 11.5,
                      }}
                    >
                      <span className="muted">{pctFmt1(b)} →</span>
                      <span
                        style={{
                          color: `var(--${scoreClass(a)})`,
                          fontWeight: 500,
                        }}
                      >
                        {pctFmt1(a)}
                      </span>
                      <span style={{ width: 70, textAlign: "right" }}>
                        <Delta from={b} to={a} />
                      </span>
                    </div>
                  </div>
                  <div
                    style={{
                      position: "relative",
                      height: 16,
                      background: "var(--bg-sunk)",
                      borderRadius: 2,
                      overflow: "hidden",
                    }}
                  >
                    {/* baseline — hatched */}
                    <div
                      style={{
                        position: "absolute",
                        left: 0,
                        top: 0,
                        bottom: 0,
                        width: `${b * 100}%`,
                        background: `repeating-linear-gradient(45deg, var(--rule-strong) 0 3px, transparent 3px 6px)`,
                      }}
                    />
                    {/* guarded — solid */}
                    <div
                      style={{
                        position: "absolute",
                        left: 0,
                        top: 0,
                        bottom: 0,
                        width: `${a * 100}%`,
                        background: `var(--${g.key === "compliance" ? "ink" : "g-" + g.key})`,
                        opacity: isCum ? 0.85 : 0.55,
                        borderRight: `2px solid var(--${g.key === "compliance" ? "ink" : "g-" + g.key})`,
                      }}
                    />
                    {/* 0.8 threshold marker */}
                    <div
                      style={{
                        position: "absolute",
                        left: "80%",
                        top: -2,
                        bottom: -2,
                        width: 1,
                        background: "var(--ink-3)",
                        opacity: 0.4,
                      }}
                    />
                  </div>
                </div>
              );
            })}
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                fontFamily: "var(--font-mono)",
                fontSize: 10,
                color: "var(--ink-4)",
                marginTop: 2,
              }}
            >
              <span>0.0</span>
              <span>0.2</span>
              <span>0.4</span>
              <span>0.6</span>
              <span>0.8 ←threshold</span>
              <span>1.0</span>
            </div>
          </div>
        </div>

        {/* Cases table + detail */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns:
              comparisonLayout === "stacked"
                ? "1fr"
                : "minmax(0, 1.15fr) minmax(0, 1fr)",
            gap: 20,
          }}
        >
          <CasesTable
            cases={cases}
            selectedId={selectedCase.id}
            onSelect={setSelectedCaseId}
          />
          <CaseDetail caseItem={selectedCase} layout={comparisonLayout} />
        </div>
      </div>
    </>
  );
}

function CasesTable({ cases, selectedId, onSelect }) {
  const [filter, setFilter] = useState("all");
  const filtered =
    filter === "all"
      ? cases
      : filter === "regressions"
        ? cases.filter((c) => c.baseline.scores.compliance < 0.6)
        : cases.filter((c) => c.category === filter);

  return (
    <div className="panel">
      <div className="panel-head">
        <span>
          Test Cases · {filtered.length}/{cases.length}
        </span>
        <div className="actions">
          <div className="segmented">
            <button
              className={filter === "all" ? "active" : ""}
              onClick={() => setFilter("all")}
            >
              All
            </button>
            <button
              className={filter === "regressions" ? "active" : ""}
              onClick={() => setFilter("regressions")}
            >
              Fails
            </button>
            <button
              className={filter === "personality" ? "active" : ""}
              onClick={() => setFilter("personality")}
            >
              PA
            </button>
            <button
              className={filter === "meta" ? "active" : ""}
              onClick={() => setFilter("meta")}
            >
              MK
            </button>
            <button
              className={filter === "bias" ? "active" : ""}
              onClick={() => setFilter("bias")}
            >
              BM
            </button>
            <button
              className={filter === "narrative" ? "active" : ""}
              onClick={() => setFilter("narrative")}
            >
              NA
            </button>
          </div>
        </div>
      </div>
      <div style={{ maxHeight: 520, overflow: "auto" }}>
        <table className="data">
          <thead>
            <tr>
              <th style={{ width: 62 }}>ID</th>
              <th style={{ width: 80 }}>Cat</th>
              <th>Prompt</th>
              <th style={{ width: 90 }}>Baseline</th>
              <th style={{ width: 90 }}>Guarded</th>
              <th style={{ width: 50 }}>Δ</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((c) => {
              const b = c.baseline.scores.compliance;
              const a = c.guarded.scores.compliance;
              return (
                <tr
                  key={c.id}
                  className={`clickable ${selectedId === c.id ? "selected" : ""}`}
                  onClick={() => onSelect(c.id)}
                >
                  <td
                    className="mono"
                    style={{ color: "var(--ink-3)", fontSize: 11 }}
                  >
                    {c.id}
                  </td>
                  <td>
                    <CategoryTag cat={c.category} />
                  </td>
                  <td
                    style={{
                      maxWidth: 260,
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                    }}
                  >
                    {c.prompt}
                  </td>
                  <td>
                    <span
                      className="mono tnum"
                      style={{ color: `var(--${scoreClass(b)})` }}
                    >
                      {pctFmt1(b)}
                    </span>
                  </td>
                  <td>
                    <span
                      className="mono tnum"
                      style={{ color: `var(--${scoreClass(a)})` }}
                    >
                      {pctFmt1(a)}
                    </span>
                  </td>
                  <td>
                    <Delta from={b} to={a} />
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function CaseDetail({ caseItem, layout }) {
  const stacked = layout === "stacked";
  const { guardrails } = MOCK;
  const grNoCum = guardrails.filter((g) => g.key !== "compliance");

  return (
    <div className="panel">
      <div className="panel-head">
        <span>
          Case Detail ·{" "}
          <span className="mono" style={{ textTransform: "none" }}>
            {caseItem.id}
          </span>
        </span>
        <div className="actions">
          <CategoryTag cat={caseItem.category} />
          <button className="btn sm ghost">{I.copy} JSON</button>
        </div>
      </div>
      <div className="panel-body">
        <div style={{ marginBottom: 12 }}>
          <div
            className="label"
            style={{
              fontSize: 10.5,
              textTransform: "uppercase",
              letterSpacing: "0.08em",
              color: "var(--ink-3)",
              fontWeight: 600,
              marginBottom: 5,
            }}
          >
            Prompt
          </div>
          <div className="chat-bubble user">
            <div className="role">USER</div>
            {caseItem.prompt}
          </div>
          <div
            style={{
              marginTop: 6,
              fontSize: 11,
              color: "var(--ink-3)",
              fontStyle: "italic",
            }}
          >
            Intent: {caseItem.intent}
          </div>
        </div>

        <div
          className={stacked ? "col" : "split"}
          style={stacked ? { gap: 10 } : {}}
        >
          <ResponseColumn
            label="BASELINE"
            subLabel="no guardrails"
            kind="before"
            response={caseItem.baseline.response}
            scores={caseItem.baseline.scores}
            issues={caseItem.baseline.issues}
            guardrails={grNoCum}
            stacked={stacked}
          />
          <ResponseColumn
            label="GUARDED"
            subLabel="PA + MK + BM + NA"
            kind="after"
            response={caseItem.guarded.response}
            scores={caseItem.guarded.scores}
            issues={caseItem.guarded.issues}
            guardrails={grNoCum}
            stacked={stacked}
          />
        </div>

        <hr className="rule" />
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div
            style={{
              display: "flex",
              gap: 16,
              fontFamily: "var(--font-mono)",
              fontSize: 11,
              color: "var(--ink-3)",
            }}
          >
            <span>
              Compliance Δ{" "}
              <Delta
                from={caseItem.baseline.scores.compliance}
                to={caseItem.guarded.scores.compliance}
              />
            </span>
            <span>
              Validator: <span className="strong">gemini-2.5-flash</span>
            </span>
            <span>
              Temp: <span className="strong">0.7 / 0.3</span>
            </span>
          </div>
          <div style={{ display: "flex", gap: 6 }}>
            <button className="btn sm">Prev case</button>
            <button className="btn sm primary">Next case →</button>
          </div>
        </div>
      </div>
    </div>
  );
}

function ResponseColumn({
  label,
  subLabel,
  kind,
  response,
  scores,
  issues,
  guardrails,
  stacked,
}) {
  return (
    <div
      style={{
        padding: stacked ? 0 : 14,
        border: stacked ? "1px solid var(--rule)" : "none",
        borderRadius: stacked ? 5 : 0,
      }}
    >
      <div
        className={`split-head ${kind}`}
        style={stacked ? {} : { margin: -14, marginBottom: 10 }}
      >
        <span>{label}</span>
        <span
          style={{
            fontFamily: "var(--font-mono)",
            fontSize: 10,
            textTransform: "none",
            letterSpacing: 0,
            color: "var(--ink-3)",
          }}
        >
          {subLabel}
        </span>
      </div>
      <div style={{ padding: stacked ? 12 : 0 }}>
        <div
          className={`chat-bubble npc`}
          style={{ whiteSpace: "pre-wrap", minHeight: 80 }}
        >
          <div
            className="role"
            style={{ display: "flex", justifyContent: "space-between" }}
          >
            <span>NPC · {MOCK.character.name}</span>
            <span
              className={`mono`}
              style={{ color: `var(--${scoreClass(scores.compliance)})` }}
            >
              GC {pctFmt1(scores.compliance)}
            </span>
          </div>
          <HighlightedResponse text={response} issues={issues} />
        </div>

        {issues.length > 0 ? (
          <div
            style={{ display: "flex", flexWrap: "wrap", gap: 4, marginTop: 8 }}
          >
            {issues.map((iss) => (
              <Badge key={iss} kind="fail">
                {I.x} {iss}
              </Badge>
            ))}
          </div>
        ) : (
          <div style={{ marginTop: 8 }}>
            <Badge kind="pass">{I.check} no issues flagged</Badge>
          </div>
        )}

        <div
          style={{
            marginTop: 12,
            display: "flex",
            flexDirection: "column",
            gap: 6,
          }}
        >
          {guardrails.map((g) => (
            <div
              key={g.key}
              style={{ display: "flex", alignItems: "center", gap: 8 }}
            >
              <GSwatch cat={g.key} />
              <span
                style={{
                  fontSize: 11,
                  flex: "0 0 90px",
                  color: "var(--ink-2)",
                }}
              >
                {g.short} · {g.name.split(" ")[0]}
              </span>
              <div style={{ flex: 1 }}>
                <ScoreBar value={scores[g.key]} />
              </div>
              <span
                className="mono tnum"
                style={{
                  width: 36,
                  textAlign: "right",
                  fontSize: 11,
                  color: `var(--${scoreClass(scores[g.key])})`,
                }}
              >
                {pctFmt1(scores[g.key])}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function HighlightedResponse({ text, issues }) {
  // naive highlight: mark common failure phrases
  const patterns = [
    { re: /as an AI( language model)?/gi, cls: "hl-fail" },
    {
      re: /totally|really gets|heartfelt|wondrous|pretty sneaky/gi,
      cls: "hl-fail",
    },
    { re: /ChatGPT|OpenAI|Python|IndexError/gi, cls: "hl-fail" },
    { re: /in real life/gi, cls: "hl-fail" },
    { re: /Hmm\.|Law of Surprise|Kaer Morhen|Nilfgaard/g, cls: "hl-pass" },
  ];
  let segments = [{ t: text, cls: null }];
  patterns.forEach(({ re, cls }) => {
    const next = [];
    segments.forEach((seg) => {
      if (seg.cls) {
        next.push(seg);
        return;
      }
      let last = 0;
      let m;
      re.lastIndex = 0;
      while ((m = re.exec(seg.t)) !== null) {
        if (m.index > last)
          next.push({ t: seg.t.slice(last, m.index), cls: null });
        next.push({ t: m[0], cls });
        last = m.index + m[0].length;
      }
      if (last < seg.t.length) next.push({ t: seg.t.slice(last), cls: null });
    });
    segments = next;
  });
  return (
    <span>
      {segments.map((s, i) =>
        s.cls ? (
          <span key={i} className={s.cls}>
            {s.t}
          </span>
        ) : (
          <React.Fragment key={i}>{s.t}</React.Fragment>
        ),
      )}
    </span>
  );
}

Object.assign(window, {
  ResultsPage,
  CasesTable,
  CaseDetail,
  ResponseColumn,
  HighlightedResponse,
});
