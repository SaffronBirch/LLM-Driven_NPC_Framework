/* Tweaks panel + main app */

const DEFAULTS = /*EDITMODE-BEGIN*/ {
  theme: "light",
  density: "default",
  comparisonLayout: "side-by-side",
  accent: "ink",
}; /*EDITMODE-END*/

function Tweaks({ state, setState, open, setOpen }) {
  if (!open) return null;
  const set = (k, v) => {
    const next = { ...state, [k]: v };
    setState(next);
    window.parent.postMessage(
      { type: "__edit_mode_set_keys", edits: { [k]: v } },
      "*",
    );
  };
  return (
    <div className="tweaks">
      <div className="tweaks-head">
        <span>Tweaks</span>
        <button
          className="btn sm ghost"
          onClick={() => setOpen(false)}
          style={{ padding: "0 4px" }}
        >
          ✕
        </button>
      </div>
      <div className="tweaks-body">
        <div className="tweak-row">
          <div className="lbl">
            <span>Theme</span>
            <span className="v">{state.theme}</span>
          </div>
          <div className="segmented" style={{ width: "100%" }}>
            <button
              className={state.theme === "light" ? "active" : ""}
              style={{ flex: 1 }}
              onClick={() => set("theme", "light")}
            >
              Light
            </button>
            <button
              className={state.theme === "dark" ? "active" : ""}
              style={{ flex: 1 }}
              onClick={() => set("theme", "dark")}
            >
              Dark
            </button>
          </div>
        </div>
        <div className="tweak-row">
          <div className="lbl">
            <span>Density</span>
            <span className="v">{state.density}</span>
          </div>
          <div className="segmented" style={{ width: "100%" }}>
            <button
              className={state.density === "compact" ? "active" : ""}
              style={{ flex: 1 }}
              onClick={() => set("density", "compact")}
            >
              Compact
            </button>
            <button
              className={state.density === "default" ? "active" : ""}
              style={{ flex: 1 }}
              onClick={() => set("density", "default")}
            >
              Default
            </button>
            <button
              className={state.density === "roomy" ? "active" : ""}
              style={{ flex: 1 }}
              onClick={() => set("density", "roomy")}
            >
              Roomy
            </button>
          </div>
        </div>
        <div className="tweak-row">
          <div className="lbl">
            <span>Before/After layout</span>
            <span className="v">{state.comparisonLayout}</span>
          </div>
          <div className="segmented" style={{ width: "100%" }}>
            <button
              className={
                state.comparisonLayout === "side-by-side" ? "active" : ""
              }
              style={{ flex: 1 }}
              onClick={() => set("comparisonLayout", "side-by-side")}
            >
              Side
            </button>
            <button
              className={state.comparisonLayout === "stacked" ? "active" : ""}
              style={{ flex: 1 }}
              onClick={() => set("comparisonLayout", "stacked")}
            >
              Stack
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

/* Main App */
function App() {
  const [page, setPage] = useState(
    () => localStorage.getItem("page") || "results",
  );
  const [selectedCaseId, setSelectedCaseId] = useState(MOCK.cases[0].id);
  const [tweaksOpen, setTweaksOpen] = useState(false);
  const [tweaks, setTweaks] = useState(DEFAULTS);

  useEffect(() => {
    localStorage.setItem("page", page);
  }, [page]);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", tweaks.theme);
    document.documentElement.setAttribute("data-density", tweaks.density);
  }, [tweaks.theme, tweaks.density]);

  useEffect(() => {
    const handler = (e) => {
      if (e.data?.type === "__activate_edit_mode") setTweaksOpen(true);
      if (e.data?.type === "__deactivate_edit_mode") setTweaksOpen(false);
    };
    window.addEventListener("message", handler);
    window.parent.postMessage({ type: "__edit_mode_available" }, "*");
    return () => window.removeEventListener("message", handler);
  }, []);

  const crumbs = {
    dashboard: ["The Witcher 3: Wild Hunt - Evaluation", "overview"],
    upload: [
      "The Witcher 3: Wild Hunt - Evaluation",
      "sources",
      "w3_main_quest_vX.json",
    ],
    world: ["The Witcher 3: Wild Hunt - Evaluation", "world", "The Continent"],
    characters: ["The Witcher 3: Wild Hunt - Evaluation", "characters"],
    chat: ["The Witcher 3: Wild Hunt - Evaluation", "chat", "geralt_of_rivia"],
    configure: ["The Witcher 3: Wild Hunt - Evaluation", "cases"],
    results: ["The Witcher 3: Wild Hunt - Evaluation", "runs", "run_1"],
    guardrails: ["The Witcher 3: Wild Hunt - Evaluation", "rubrics"],
  }[page];

  const pageEl = {
    dashboard: <OverviewPage goto={setPage} />,
    upload: <UploadPage onParse={() => setPage("world")} />,
    world: <WorldPage onPickChar={() => setPage("characters")} />,
    characters: <CharactersPage onPick={() => setPage("chat")} />,
    chat: <ChatPage />,
    configure: <ConfigurePage onRun={() => setPage("results")} />,
    results: (
      <ResultsPage
        selectedCaseId={selectedCaseId}
        setSelectedCaseId={setSelectedCaseId}
        comparisonLayout={tweaks.comparisonLayout}
      />
    ),
    guardrails: <GuardrailsPage />,
  }[page];

  return (
    <div className="app" data-screen-label={page}>
      <Topbar crumbs={crumbs} />
      <Sidebar page={page} setPage={setPage} />
      <div className="main">{pageEl}</div>
      <Tweaks
        state={tweaks}
        setState={setTweaks}
        open={tweaksOpen}
        setOpen={setTweaksOpen}
      />
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
