/* App shell: topbar + sidebar */

function Topbar({ crumbs, onPageSwitch }) {
  return (
    <div className="topbar">
      <div className="brand">
        <div className="brand-mark" />
        <span>LLM-Driven NPC Evaluator</span>
        <span
          className="mono"
          style={{ color: "var(--ink-4)", fontSize: 10.5, marginLeft: 4 }}
        >
          v0.4.2
        </span>
      </div>
      <div style={{ width: 1, height: 20, background: "var(--rule)" }} />
      <div className="crumbs">
        {crumbs.map((c, i) => (
          <React.Fragment key={i}>
            {i > 0 && <span className="sep">/</span>}
            <span className={i === crumbs.length - 1 ? "cur" : ""}>{c}</span>
          </React.Fragment>
        ))}
      </div>
      <div className="right">
        <span>
          <span className="status-dot" /> evaluator online
        </span>
        <span>run #1</span>
      </div>
    </div>
  );
}

function Sidebar({ page, setPage }) {
  const items = [
    { group: "Project" },
    { id: "dashboard", label: "Overview", icon: I.chart },
    {
      id: "upload",
      label: "Script / World Source",
      icon: I.upload,
      num: "1 file",
    },
    { id: "world", label: "World & Regions", icon: I.globe, num: "6" },
    { id: "characters", label: "Characters", icon: I.user, num: "4" },
    { group: "Evaluation" },
    { id: "chat", label: "NPC Chat", icon: I.chat },
    { id: "configure", label: "Configure Cases", icon: I.beaker, num: "37" },
    {
      id: "results",
      label: "Run Results",
      icon: I.shield,
      highlight: true,
    },
    { group: "Settings" },
    { id: "guardrails", label: "Guardrail Rubrics", icon: I.settings },
  ];

  return (
    <div className="sidebar">
      {items.map((it, i) => {
        if (it.group)
          return (
            <div className="group" key={i}>
              {it.group}
            </div>
          );
        return (
          <div
            key={it.id}
            className={`nav-item ${page === it.id ? "active" : ""}`}
            onClick={() => setPage(it.id)}
          >
            {it.icon}
            <span>{it.label}</span>
            {it.num && <span className="num">{it.num}</span>}
          </div>
        );
      })}
      <div
        style={{
          padding: "18px 14px 0",
          marginTop: 14,
          borderTop: "1px solid var(--rule)",
        }}
      >
        <div
          style={{
            fontSize: 10.5,
            textTransform: "uppercase",
            letterSpacing: "0.08em",
            color: "var(--ink-3)",
            fontWeight: 600,
            marginBottom: 6,
          }}
        >
          Active Character
        </div>
        <div style={{ fontSize: 12.5, fontWeight: 500 }}>
          {MOCK.character.name}
        </div>
        <div className="mono" style={{ fontSize: 10.5, color: "var(--ink-3)" }}>
          {MOCK.character.id}
        </div>
        <div
          style={{ marginTop: 8, display: "flex", gap: 4, flexWrap: "wrap" }}
        >
          {MOCK.character.knowledge.slice(0, 5).map((k) => (
            <span key={k} className="tag">
              {k}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}

Object.assign(window, { Topbar, Sidebar });
