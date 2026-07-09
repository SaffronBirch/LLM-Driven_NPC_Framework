/* Shared atoms: badges, score bars, icons, sparklines, gauges */

const { useState, useEffect, useRef, useMemo } = React;

const pctFmt = (n) => `${Math.round(n * 100)}`;
const pctFmt1 = (n) => `${(n * 100).toFixed(1)}`;

const scoreClass = (s) => s >= 0.8 ? "pass" : s >= 0.6 ? "warn" : "fail";

function ScoreBar({ value, kind }) {
  const k = kind || scoreClass(value);
  return (
    <div className={`score-bar ${k}`}>
      <span style={{ width: `${Math.max(2, value * 100)}%` }} />
    </div>
  );
}

function ScoreCell({ value, showBar = true }) {
  const k = scoreClass(value);
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8, minWidth: 110 }}>
      <span className="mono tnum" style={{ width: 30, textAlign: "right", color: `var(--${k})`, fontWeight: 500 }}>
        {pctFmt(value)}
      </span>
      {showBar && <div style={{ flex: 1 }}><ScoreBar value={value} /></div>}
    </div>
  );
}

function Delta({ from, to, format = "pct" }) {
  const d = to - from;
  const sign = d > 0.005 ? "up" : d < -0.005 ? "down" : "flat";
  const arrow = sign === "up" ? "↑" : sign === "down" ? "↓" : "–";
  const val = format === "pct" ? `${d >= 0 ? "+" : ""}${(d * 100).toFixed(1)}` : d.toFixed(2);
  return <span className={`delta ${sign}`}>{arrow} {val}{format === "pct" ? "" : ""}</span>;
}

function Badge({ kind = "neutral", children }) {
  return <span className={`badge ${kind}`}>{children}</span>;
}

function GSwatch({ cat }) {
  return <span className={`g-swatch ${cat}`} />;
}

function Spark({ data, w = 60, h = 20 }) {
  const max = Math.max(...data, 0.01);
  const min = Math.min(...data, 0);
  const range = max - min || 1;
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} style={{ display: "block" }}>
      <polyline
        fill="none"
        stroke="currentColor"
        strokeWidth="1.2"
        points={data.map((v, i) => {
          const x = (i / (data.length - 1)) * w;
          const y = h - ((v - min) / range) * (h - 2) - 1;
          return `${x},${y}`;
        }).join(" ")}
      />
      <circle
        cx={w}
        cy={h - ((data[data.length - 1] - min) / range) * (h - 2) - 1}
        r="1.8"
        fill="currentColor"
      />
    </svg>
  );
}

function Gauge({ value, label = "GC", size = 110, stroke = 8 }) {
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const off = c * (1 - value);
  const col = value >= 0.8 ? "var(--pass)" : value >= 0.6 ? "var(--warn)" : "var(--fail)";
  return (
    <div className="gauge" style={{ width: size, height: size }}>
      <svg width={size} height={size}>
        <circle cx={size / 2} cy={size / 2} r={r} stroke="var(--rule)" strokeWidth={stroke} fill="none" />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          stroke={col}
          strokeWidth={stroke}
          fill="none"
          strokeDasharray={c}
          strokeDashoffset={off}
          strokeLinecap="round"
          style={{ transition: "stroke-dashoffset 0.6s ease" }}
        />
      </svg>
      <div className="gauge-val">
        <div className="big">{pctFmt1(value)}</div>
        <div className="small">{label}</div>
      </div>
    </div>
  );
}

/* Minimal SVG icons — 14×14 stroke */
const I = {
  upload: <svg className="nav-icon" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.3"><path d="M7 10V3M7 3L4 6M7 3L10 6M2 11v1h10v-1" /></svg>,
  globe: <svg className="nav-icon" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.3"><circle cx="7" cy="7" r="5"/><path d="M2 7h10M7 2c1.8 2 1.8 8 0 10M7 2c-1.8 2-1.8 8 0 10"/></svg>,
  user: <svg className="nav-icon" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.3"><circle cx="7" cy="5" r="2.3"/><path d="M2.5 12c0-2.5 2-4 4.5-4s4.5 1.5 4.5 4"/></svg>,
  chat: <svg className="nav-icon" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.3"><path d="M2 3h10v7H6l-3 2V3z"/></svg>,
  beaker: <svg className="nav-icon" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.3"><path d="M5 2v3L2.5 11c-.3.7.2 1.5 1 1.5h7c.8 0 1.3-.8 1-1.5L9 5V2M4 2h6M4 8h6"/></svg>,
  chart: <svg className="nav-icon" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.3"><path d="M2 12V2M2 12h10M4 10V6M7 10V4M10 10V7"/></svg>,
  shield: <svg className="nav-icon" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.3"><path d="M7 1.5l4.5 1.5v4c0 3-2 5-4.5 6-2.5-1-4.5-3-4.5-6v-4L7 1.5z"/></svg>,
  settings: <svg className="nav-icon" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.3"><circle cx="7" cy="7" r="1.8"/><path d="M7 1v2M7 11v2M1 7h2M11 7h2M2.8 2.8l1.4 1.4M9.8 9.8l1.4 1.4M2.8 11.2l1.4-1.4M9.8 4.2l1.4-1.4"/></svg>,
  play: <svg width="10" height="10" viewBox="0 0 10 10" fill="currentColor"><path d="M2 1l7 4-7 4z"/></svg>,
  check: <svg width="10" height="10" viewBox="0 0 10 10" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M2 5l2 2 4-4"/></svg>,
  x: <svg width="10" height="10" viewBox="0 0 10 10" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M2 2l6 6M8 2l-6 6"/></svg>,
  plus: <svg width="10" height="10" viewBox="0 0 10 10" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M5 2v6M2 5h6"/></svg>,
  copy: <svg width="10" height="10" viewBox="0 0 10 10" fill="none" stroke="currentColor" strokeWidth="1.2"><rect x="3" y="3" width="5" height="5" rx="0.5"/><path d="M2 6V2h4"/></svg>,
  download: <svg width="10" height="10" viewBox="0 0 10 10" fill="none" stroke="currentColor" strokeWidth="1.3"><path d="M5 1v6M5 7L3 5M5 7l2-2M2 9h6"/></svg>,
  refresh: <svg width="10" height="10" viewBox="0 0 10 10" fill="none" stroke="currentColor" strokeWidth="1.3"><path d="M8 3A3 3 0 1 0 8 7M8 1v2H6"/></svg>,
};

function CategoryTag({ cat }) {
  const label = {
    personality: "Personality", meta: "Meta", bias: "Bias", narrative: "Narrative", compliance: "Compliance",
  }[cat] || cat;
  return (
    <span className="tag"><GSwatch cat={cat} /> {label}</span>
  );
}

Object.assign(window, {
  ScoreBar, ScoreCell, Delta, Badge, GSwatch, Spark, Gauge, I, CategoryTag,
  pctFmt, pctFmt1, scoreClass,
});
