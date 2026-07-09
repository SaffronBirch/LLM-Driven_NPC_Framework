/* Configure Cases, Upload, World, Characters, Chat, Guardrails, Overview */

function ConfigurePage({ onRun }) {
  const [selected, setSelected] = useState(
    new Set(MOCK.cases.map((c) => c.id)),
  );
  const [editing, setEditing] = useState(MOCK.cases[0].id);
  const cur = MOCK.cases.find((c) => c.id === editing) || MOCK.cases[0];
  const toggle = (id) => {
    const s = new Set(selected);
    s.has(id) ? s.delete(id) : s.add(id);
    setSelected(s);
  };

  const [progress, setProgress] = useState(null);

  const doRun = () => {
    setProgress(0);
    let p = 0;
    const t = setInterval(() => {
      p += 7;
      setProgress(p);
      if (p >= 100) {
        clearInterval(t);
        setTimeout(onRun, 400);
      }
    }, 90);
  };

  return (
    <>
      <div className="page-head">
        <h1>Configure Evaluation Cases</h1>
        <div className="sub">
          Build test prompts, tag them by guardrail category, and choose which
          to include in the next run.
        </div>
        <div className="meta-row">
          <span>
            total cases <b>{MOCK.cases.length}</b>
          </span>
          <span>
            selected <b>{selected.size}</b>
          </span>
          <span>
            estimated runtime <b>~3m 10s</b>
          </span>
          <span>
            estimated cost <b>~$0.42</b>
          </span>
        </div>
      </div>
      <div className="page-body">
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1.1fr 1.4fr",
            gap: 20,
          }}
        >
          <div className="panel">
            <div className="panel-head">
              <span>Case Library · {MOCK.cases.length}</span>
              <div className="actions">
                <button className="btn sm">{I.plus} New case</button>
                <button className="btn sm">{I.upload} Import</button>
              </div>
            </div>
            <div style={{ maxHeight: 400, overflow: "auto" }}>
              <table className="data">
                <thead>
                  <tr>
                    <th style={{ width: 28 }}></th>
                    <th style={{ width: 62 }}>ID</th>
                    <th style={{ width: 80 }}>Cat</th>
                    <th>Prompt</th>
                  </tr>
                </thead>
                <tbody>
                  {MOCK.cases.map((c) => (
                    <tr
                      key={c.id}
                      className="clickable"
                      onClick={() => setEditing(c.id)}
                      style={
                        editing === c.id
                          ? { background: "oklch(0.55 0.13 240 / 0.07)" }
                          : {}
                      }
                    >
                      <td
                        onClick={(e) => {
                          e.stopPropagation();
                          toggle(c.id);
                        }}
                      >
                        <div
                          style={{
                            width: 14,
                            height: 14,
                            border: "1px solid var(--rule-strong)",
                            borderRadius: 2,
                            background: selected.has(c.id)
                              ? "var(--ink)"
                              : "transparent",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            color: "var(--bg)",
                          }}
                        >
                          {selected.has(c.id) && I.check}
                        </div>
                      </td>
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
                          maxWidth: 280,
                          overflow: "hidden",
                          textOverflow: "ellipsis",
                          whiteSpace: "nowrap",
                        }}
                      >
                        {c.prompt}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="panel">
            <div className="panel-head">
              <span>
                Edit ·{" "}
                <span className="mono" style={{ textTransform: "none" }}>
                  {cur.id}
                </span>
              </span>
              <div className="actions">
                <button className="btn sm ghost">Duplicate</button>
                <button
                  className="btn sm ghost"
                  style={{ color: "var(--fail)" }}
                >
                  Delete
                </button>
              </div>
            </div>
            <div
              className="panel-body"
              style={{ display: "flex", flexDirection: "column", gap: 14 }}
            >
              <div className="grid-2">
                <div>
                  <label className="field">Guardrail Dimension</label>
                  <select className="select" value={cur.category} readOnly>
                    <option value="personality">Personality Alignment</option>
                    <option value="meta">Meta-Knowledge Filtration</option>
                    <option value="bias">Bias Mitigation</option>
                    <option value="narrative">Narrative Adherence</option>
                  </select>
                </div>
                <div>
                  <label className="field">Test Category</label>
                  <select
                    className="select"
                    defaultValue="in-character decline"
                  >
                    <option>Bias Elicitation</option>
                    <option>Deep Persona Understanding</option>
                    <option>Emotional Provocation</option>
                    <option>Fabricated Events</option>
                    <option>Real World Reference</option>
                    <option>Role Confusion</option>
                    <option>System Info Prompt</option>
                    <option>Timeline Confusion</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="field">User Prompt</label>
                <textarea
                  className="textarea"
                  rows={2}
                  defaultValue={cur.prompt}
                />
              </div>

              <div>
                <label className="field">Intent / Notes</label>
                <textarea
                  className="textarea"
                  rows={2}
                  defaultValue={cur.intent}
                />
              </div>

              <div>
                <label className="field">
                  Rubric Weights (active guardrails)
                </label>
                <div
                  style={{ display: "flex", flexDirection: "column", gap: 8 }}
                >
                  {MOCK.guardrails
                    .filter((g) => g.key !== "compliance")
                    .map((g) => (
                      <div
                        key={g.key}
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: 10,
                        }}
                      >
                        <GSwatch cat={g.key} />
                        <span style={{ flex: "0 0 160px", fontSize: 12 }}>
                          {g.name}
                        </span>
                        <input
                          type="range"
                          min="0"
                          max="2"
                          step="0.1"
                          defaultValue={g.key === cur.category ? "1.5" : "1.0"}
                          style={{ flex: 1 }}
                        />
                        <span
                          className="mono tnum"
                          style={{
                            width: 32,
                            textAlign: "right",
                            fontSize: 11,
                          }}
                        >
                          {g.key === cur.category ? "1.5×" : "1.0×"}
                        </span>
                      </div>
                    ))}
                </div>
              </div>

              <div></div>
            </div>
          </div>
        </div>

        <div className="panel" style={{ marginTop: 20 }}>
          <div className="panel-head">
            <span>Run Configuration</span>
          </div>
          <div className="panel-body">
            <div className="grid-4">
              <div>
                <label className="field">Model under test</label>
                <select className="select">
                  <option>deepseek-v3.2:cloud</option>
                  <option>gpt-oss:120b-cloud</option>
                  <option>gemini-2.5-flash</option>
                </select>
              </div>
              <div>
                <label className="field">Validator model</label>
                <select className="select">
                  <option>gemini-2.5-flash</option>
                  <option>claude-opus-4-1</option>
                </select>
              </div>
              <div>
                <label className="field">Temperature</label>
                <input className="input mono" defaultValue="0.7" />
              </div>
              <div>
                <label className="field">Seed</label>
                <input className="input mono" defaultValue="123" />
              </div>
            </div>
            <hr className="rule" />
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <div style={{ fontSize: 12, color: "var(--ink-3)" }}>
                Will run <span className="strong">{selected.size}</span> cases ×
                <span className="strong"> 2</span> modes (baseline, guarded) =
                <span className="strong mono"> {selected.size * 2} </span>
                evaluations.
              </div>
              <div style={{ display: "flex", gap: 8 }}>
                <button className="btn">Save config</button>
                <button
                  className="btn primary"
                  onClick={doRun}
                  disabled={progress !== null && progress < 100}
                >
                  {I.play}{" "}
                  {progress !== null && progress < 100
                    ? "Running..."
                    : "Run evaluation"}
                </button>
              </div>
            </div>
          </div>
          {progress !== null && (
            <div style={{ marginTop: 14, marginLeft: 16, marginRight: 16 }}>
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  fontFamily: "var(--font-mono)",
                  fontSize: 11,
                  marginBottom: 4,
                }}
              >
                <span>Running · evaluating {selected.size} cases</span>
                <span className="strong">{progress}%</span>
              </div>
              <div className="score-bar">
                <span style={{ width: `${progress}%` }} />
              </div>
              <div
                className="mono"
                style={{
                  fontSize: 10.5,
                  color: "var(--ink-3)",
                  marginTop: 8,
                  lineHeight: 1.7,
                }}
              >
                <div>
                  {progress > 10 ? "✓" : "·"} loading character and world
                  context
                </div>
                <div>
                  {progress > 30 ? "✓" : "·"} generating baseline responses
                </div>
                <div>
                  {progress > 60 ? "✓" : "·"} running validator suite
                  (PA/MKF/BM/NA)
                </div>
                <div>{progress > 90 ? "✓" : "·"} aggregating scores</div>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}

function UploadPage({ onParse }) {
  const [progress, setProgress] = useState(null);

  const doParse = () => {
    setProgress(0);
    let p = 0;
    const t = setInterval(() => {
      p += 7;
      setProgress(p);
      if (p >= 100) {
        clearInterval(t);
        setTimeout(onParse, 400);
      }
    }, 90);
  };

  return (
    <>
      <div className="page-head">
        <h1>Script / World Source</h1>
        <div className="sub">
          Upload a game script or build the world manually. The parser extracts
          regions, factions, and characters into a normalized world JSON.
        </div>
      </div>
      <div className="page-body">
        <div
          style={{ display: "grid", gridTemplateColumns: "1.3fr 1fr", gap: 20 }}
        >
          <div className="panel">
            <div className="panel-head">
              <span>Upload</span>
              <div className="actions">
                <span className="mono muted" style={{ fontSize: 10.5 }}>
                  accepts .json
                </span>
              </div>
            </div>
            <div className="panel-body">
              <div
                style={{
                  border: "1.5px dashed var(--rule-strong)",
                  borderRadius: 8,
                  padding: "36px 20px",
                  textAlign: "center",
                  background: "var(--bg-sunk)",
                }}
              >
                <div
                  style={{
                    fontSize: 13,
                    color: "var(--ink-2)",
                    marginBottom: 6,
                  }}
                >
                  Drop{" "}
                  <span className="mono strong">TheWitcher3Script.json</span>{" "}
                  here
                </div>
                <div
                  className="mono"
                  style={{
                    fontSize: 11,
                    color: "var(--ink-3)",
                    marginBottom: 14,
                  }}
                >
                  or
                </div>
                <button className="btn primary" onClick={doParse}>
                  {I.upload} Choose file
                </button>
              </div>

              {progress !== null && (
                <div style={{ marginTop: 14 }}>
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      fontFamily: "var(--font-mono)",
                      fontSize: 11,
                      marginBottom: 4,
                    }}
                  >
                    <span>Parsing · extracting entities</span>
                    <span className="strong">{progress}%</span>
                  </div>
                  <div className="score-bar">
                    <span style={{ width: `${progress}%` }} />
                  </div>
                  <div
                    className="mono"
                    style={{
                      fontSize: 10.5,
                      color: "var(--ink-3)",
                      marginTop: 8,
                      lineHeight: 1.7,
                    }}
                  >
                    <div>✓ tokenized 2,341 lines</div>
                    <div>✓ detected 6 regions</div>
                    <div>{progress > 60 ? "✓" : "·"} resolved 4 characters</div>
                    <div>
                      {progress > 90 ? "✓" : "·"} linked dialogue → speakers
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="panel">
            <div className="panel-head">
              <span>Or Build Manually</span>
            </div>
            <div
              className="panel-body"
              style={{ display: "flex", flexDirection: "column", gap: 12 }}
            >
              <div>
                <label className="field">World name</label>
                <input className="input" />
              </div>
              <div>
                <label className="field">World Description</label>
                <input className="input" />
              </div>
              <div>
                <label className="field">World Tensions</label>
                <input className="input" />
              </div>
              <hr className="rule" />
              <button className="btn">Open manual builder</button>
            </div>
          </div>
        </div>

        <div className="panel" style={{ marginTop: 20 }}>
          <div className="panel-head">
            <span>Parsed Output Preview · world.json</span>
            <div className="actions">
              <button className="btn sm ghost">{I.copy} Copy</button>
              <button className="btn sm ghost">{I.download} Download</button>
            </div>
          </div>
          <pre
            className="mono"
            style={{
              margin: 0,
              padding: 16,
              fontSize: 11,
              lineHeight: 1.6,
              color: "var(--ink-2)",
              background: "var(--bg-sunk)",
              overflow: "auto",
              maxHeight: 280,
            }}
          >
            {`{
  "game_name": "The Witcher 3: Wild Hunt",
  "world_name": "The Continent",
  "world_description": "A gritty, war\u2011torn land where human kingdoms vie for power and monsters lurk in the shadows. Cities like Novigrad are bustling free ports, while places such as Velen and Skellige are wild, untamed wildernesses. Magic, ancient curses, and a wandering monster hunter named Geralt shape the fate of its peoples.",
  "world_tensions": {
    "nonhumans": "Elves, dwarves, and other nonhuman races face systemic persecution and scapegoating, especially by human authorities and the Church of the Eternal Fire.",
    "mages": "Mages are hunted and burned in many cities, including Novigrad, reflecting a widespread anti\u2011magic sentiment across the continent.",
    "witchers": "Witchers are distrusted and barred from places like Novigrad, seen as dangerous outsiders by both civic leaders and religious zealots.",
    "nilfgaard_vs_northern_realms": "The southern Empire of Nilfgaard and the northern kingdoms are locked in a continent\u2011wide war, with occupations, rebellions, and shifting allegiances.",
    "religious_factions": "The Church of the Eternal Fire promotes a worldview that blames mages, elves, dwarves, and other perceived deviants for conflict, creating tension with secular and non\u2011faith groups.",
    "peasants_vs_nobility": "In Redania, peasants are mobilized for war while nobles and trade guilds compete for power, generating a class\u2011based tension throughout the realm."
  },
  "regions": {
    "White Orchard": {
      "name": "White Orchard",
      "description": "A quiet agricultural settlement on the edge of the kingdom, surrounded by rolling fields and pine\u2011filled forest. It serves as the tutorial area where Geralt first battles the Beast of White Orchard. The village features a small inn, a blacksmith, and a chapel, and it is often threatened by monster attacks from the nearby woods.",
      "tensions": {}
    },
    "Vizima": {
      "name": "Vizima",
      "description": "The capital of Redania, Vizima is a bustling trade hub and political center with towering stone walls and a grand royal palace. Its crowded market streets are filled with merchants, taverns, and craftsmen, while the surrounding citadel houses the king\u2019s court. The city\u2019s architecture blends ornate spires with narrow alleys, reflecting both wealth and the looming tensions of war.",
      "tensions": {}
    },
    "Velen": {
      "name": "Velen",
      "description": "A war\u2011scarred region south of Novigrad, Velen is a landscape of swamps, marshes, and ruined villages. The Bloody Baron\u2019s estate and the Inn at the Crossroads serve as focal points for the desperate locals. Dangerous monsters and hidden secrets linger among the fog\u2011filled bogs, making travel treacherous.",
      "tensions": {}
    },
    "Novigrad": {
      "name": "Novigrad",
      "description": "Novigrad is the largest free city on the continent, built on a sprawling harbor and protected by massive stone walls. Its bustling streets host bustling markets, the notorious Butcher\u2019s Yard, and numerous guild halls. The city is a melting pot of cultures, politics, and crime, where intrigue flourishes at every corner.",
      "tensions": {}
    },
    "The Skellige Isles": {
      "name": "The Skellige Isles",
      "description": "A rugged archipelago of wind\u2011blasted islands, the Skellige Isles are home to fierce seafarers and warrior clans. Kaer Trolde fortress dominates the main island, while coastal taverns and hidden sea caves hold legends like the White Fleet. The islands\u2019 craggy cliffs, misty fjords, and volcanic peaks shape a harsh yet vibrant culture.",
      "tensions": {}
    },
    "Kaer Morhen": {
      "name": "Kaer Morhen",
      "description": "High in the mountains lies Kaer Morhen, the ancient stone keep where Witchers are trained and forged. Its courtyard holds training grounds, a forge, and storied halls echoing with the clang of steel. Surrounded by pine forests, the keep serves as a sanctuary for elder Witchers and a repository of forgotten lore.",
      "tensions": {
        "wild_hunt_defense": "Witchers are rallying allies to protect Kaer Morhen from an imminent Wild Hunt attack, creating a local urgency for defense support.",
        "command_conflict": "Emhyr proposes sending troops under General Voorhis, but the witchers reject external command, causing a dispute over who will lead the fortress\u2019s defense."
      }
    }
  },
  "characters": {
    "Geralt": {
      "name": "Geralt",
      "age": "150",
      "profession": "Witcher",
      "personality": ["stoic", "witty", "disciplined", "loyal", "pragmatic"],
      "appearance": "White hair, scarred face, golden eyes when using witcher senses, muscular frame, usually in leather armor.",
      "backstory": "Subjected to the Trial of Grasses at Kaer Morhen, he became a monster hunter who roams the Continent for contracts and allies.",
      "lifestyle": "Solitary, taking monster\u2011hunting contracts, occasionally teaming with friends for larger threats.",
      "currently": null
    },
    "Ciri": {
      "name": "Ciri",
      "age": "20",
      "profession": "Witcheress / Heir of Cintra",
      "personality": [
        "brave",
        "compassionate",
        "rebellious",
        "determined",
        "resourceful"
      ],
      "appearance": "Ashen\u2011white hair, striking green eyes, athletic build, a scar on her cheek and typical witcher armor.",
      "backstory": "Born Cirilla Fiona Ellen Riannon, heir to a throne, she was trained by Geralt after escaping a war\u2011torn world and now roams the Continent on the Path.",
      "lifestyle": "Constantly on the move, surviving in wilds, taking odd jobs, and avoiding pursuers.",
      "currently": null
    },
    "Yennefer": {
      "name": "Yennefer",
      "age": "38",
      "profession": "Sorceress",
      "personality": [
        "intelligent",
        "ambitious",
        "sarcastic",
        "protective",
        "charismatic"
      ],
      "appearance": "Raven\u2011black hair, violet eyes, strikingly beautiful, often clothed in elegant, dark robes.",
      "backstory": "Trained in Aedirn, she rose to become one of the most powerful mages on the Continent and shares a deep bond with Geralt.",
      "lifestyle": "Involved in political intrigue, searches for allies, and pursues personal quests for power and redemption.",
      "currently": null
    },
    "Triss Merigold": {
      "name": "Triss Merigold",
      "age": "35",
      "profession": "Sorceress",
      "personality": ["warm", "optimistic", "loyal", "curious", "kind"],
      "appearance": "Red hair, green eyes, freckles, dressed in practical yet elegant robes.",
      "backstory": "Member of the Lodge of Sorceresses, longtime friend of Geralt, and often involved in rescue missions across the Continent.",
      "lifestyle": "Travels between courts, helps allies, and participates in magical research and politics.",
      "currently": null
    }
  }
}`}
          </pre>
        </div>
      </div>
    </>
  );
}

function WorldPage({ onPickChar }) {
  const w = MOCK.world;
  if (!w) {
    return (
      <>
        <div className="page-head">
          <h1>World</h1>
          <div className="sub">
            No world data loaded. Pass <code>--world-json</code> when
            regenerating data.js.
          </div>
        </div>
      </>
    );
  }
  const tensionEntries = Object.entries(w.tensions || {});

  return (
    <>
      <div className="page-head">
        <h1>World · {w.name}</h1>
        <div className="sub">
          {w.game && <span>{w.game} · </span>}
          {w.regions.length} regions
        </div>
      </div>
      <div className="page-body">
        {w.description && (
          <div className="panel" style={{ marginBottom: 20 }}>
            <div className="panel-head">
              <span>Description</span>
            </div>
            <div
              className="panel-body"
              style={{ fontSize: 13, lineHeight: 1.6, color: "var(--ink-2)" }}
            >
              {w.description}
            </div>
          </div>
        )}

        {tensionEntries.length > 0 && (
          <div className="panel" style={{ marginBottom: 20 }}>
            <div className="panel-head">
              <span>World Tensions · {tensionEntries.length}</span>
            </div>
            <div
              className="panel-body"
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: 12,
              }}
            >
              {tensionEntries.map(([key, text]) => (
                <div
                  key={key}
                  style={{
                    borderLeft: "2px solid var(--warn)",
                    paddingLeft: 10,
                  }}
                >
                  <div
                    className="mono"
                    style={{
                      fontSize: 10.5,
                      color: "var(--ink-3)",
                      textTransform: "uppercase",
                      marginBottom: 3,
                    }}
                  >
                    {key.replace(/_/g, " ")}
                  </div>
                  <div
                    style={{
                      fontSize: 12,
                      color: "var(--ink-2)",
                      lineHeight: 1.5,
                    }}
                  >
                    {text}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="panel-head" style={{ marginBottom: 10 }}>
          <span>Regions · {w.regions.length}</span>
        </div>
        <div className="grid-3">
          {w.regions.map((r) => {
            const regionTensions = Object.entries(r.tensions || {});
            return (
              <div
                key={r.id}
                className="panel"
                style={{ cursor: "pointer" }}
                onClick={onPickChar}
              >
                <div className="panel-body">
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "flex-start",
                      marginBottom: 10,
                    }}
                  >
                    <div>
                      <div style={{ fontSize: 14, fontWeight: 500 }}>
                        {r.name}
                      </div>
                      <div className="mono muted" style={{ fontSize: 10.5 }}>
                        {r.id}
                      </div>
                    </div>
                    <Badge
                      kind={regionTensions.length > 0 ? "warn" : "neutral"}
                    >
                      {regionTensions.length > 0
                        ? `${regionTensions.length} tension${regionTensions.length > 1 ? "s" : ""}`
                        : "stable"}
                    </Badge>
                  </div>
                  {r.description && (
                    <div
                      style={{
                        fontSize: 11.5,
                        lineHeight: 1.5,
                        color: "var(--ink-2)",
                        marginBottom: 10,
                        display: "-webkit-box",
                        WebkitLineClamp: 4,
                        WebkitBoxOrient: "vertical",
                        overflow: "hidden",
                      }}
                    >
                      {r.description}
                    </div>
                  )}
                  {regionTensions.length > 0 && (
                    <div
                      style={{
                        marginTop: 8,
                        paddingTop: 8,
                        borderTop: "1px solid var(--rule)",
                      }}
                    >
                      {regionTensions.map(([k]) => (
                        <div
                          key={k}
                          className="mono"
                          style={{
                            fontSize: 10,
                            color: "var(--warn)",
                            marginBottom: 2,
                          }}
                        >
                          • {k.replace(/_/g, " ")}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </>
  );
}

function CharactersPage({ onPick }) {
  const activeId = MOCK.character?.id;
  const chars =
    MOCK.worldCharacters && MOCK.worldCharacters.length
      ? MOCK.worldCharacters
      : [MOCK.character]; // fallback if no world JSON was provided

  return (
    <>
      <div className="page-head">
        <h1>Characters</h1>
        <div className="sub">
          Select a character to initialize an NPC session. The active character
          is the subject of the most recent evaluation run.
        </div>
        <div className="meta-row">
          <span>
            total <b>{chars.length}</b>
          </span>
          <span>
            active <b>{activeId || "—"}</b>
          </span>
        </div>
      </div>
      <div className="page-body">
        <div className="panel">
          <table className="data">
            <thead>
              <tr>
                <th>Name</th>
                <th>Profession</th>
                <th>Backstory</th>
                <th style={{ width: 60 }}>Age</th>
                <th style={{ width: 240 }}>Traits</th>
                <th style={{ width: 120 }}></th>
              </tr>
            </thead>
            <tbody>
              {chars.map((c) => {
                const isActive = c.id === activeId;
                return (
                  <tr
                    key={c.id}
                    className="clickable"
                    style={
                      isActive
                        ? { background: "oklch(0.55 0.13 240 / 0.05)" }
                        : {}
                    }
                  >
                    <td>
                      <div style={{ fontWeight: 500 }}>{c.name}</div>
                      <div className="mono muted" style={{ fontSize: 10.5 }}>
                        {c.id}
                      </div>
                    </td>
                    <td>{c.profession || c.archetype || "—"}</td>
                    <td
                      style={{
                        fontSize: 12,
                        color: "var(--ink-2)",
                        lineHeight: 1.4,
                        maxWidth: 420,
                      }}
                    >
                      {c.backstory || "—"}
                    </td>
                    <td className="mono tnum">{c.age || "—"}</td>
                    <td>
                      <div
                        style={{ display: "flex", flexWrap: "wrap", gap: 4 }}
                      >
                        {(c.traits || c.knowledge || [])
                          .slice(0, 5)
                          .map((t) => (
                            <span
                              key={t}
                              className="tag"
                              style={{ fontSize: 10 }}
                            >
                              {t}
                            </span>
                          ))}
                      </div>
                    </td>
                    <td style={{ textAlign: "right" }}>
                      {isActive ? (
                        <Badge kind="info">active</Badge>
                      ) : (
                        <button className="btn sm" onClick={onPick}>
                          Activate
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}

function ChatPage() {
  const [msgs, setMsgs] = useState(MOCK.chatHistory);
  const [draft, setDraft] = useState("");
  const [guard, setGuard] = useState(true);
  const [typing, setTyping] = useState(false);

  const send = () => {
    if (!draft.trim()) return;
    const newMsgs = [...msgs, { role: "user", text: draft }];
    setMsgs(newMsgs);
    setDraft("");
    setTyping(true);
    setTimeout(() => {
      const reply = guard
        ? "Hmm. Depends. Witchers don't deal in hypotheticals without coin on the table."
        : "That's a great question! Let me think about it carefully. As Geralt, I would probably say...";
      setMsgs([...newMsgs, { role: "npc", text: reply }]);
      setTyping(false);
    }, 900);
  };

  return (
    <>
      <div className="page-head">
        <h1>NPC Chat · {MOCK.character.name}</h1>
        <div className="sub">
          Live session. Messages are logged and can be promoted to test cases.
        </div>
      </div>
      <div className="page-body">
        <div
          style={{ display: "grid", gridTemplateColumns: "1fr 300px", gap: 20 }}
        >
          <div
            className="panel"
            style={{ display: "flex", flexDirection: "column", height: 560 }}
          >
            <div className="panel-head">
              <span>
                Session ·{" "}
                <span className="mono" style={{ textTransform: "none" }}>
                  sess_0x9f2a
                </span>
              </span>
              <div
                className="actions"
                style={{ display: "flex", alignItems: "center", gap: 10 }}
              >
                <label
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 6,
                    fontSize: 11,
                    cursor: "pointer",
                    textTransform: "none",
                    letterSpacing: 0,
                  }}
                >
                  <input
                    type="checkbox"
                    checked={guard}
                    onChange={(e) => setGuard(e.target.checked)}
                  />
                  Guardrails
                </label>
                <Badge kind={guard ? "pass" : "fail"}>
                  {guard ? "PA+MK+BM+NA" : "baseline"}
                </Badge>
              </div>
            </div>
            <div
              style={{
                flex: 1,
                overflowY: "auto",
                padding: 16,
                display: "flex",
                flexDirection: "column",
                gap: 10,
              }}
            >
              {msgs.map((m, i) => (
                <div
                  key={i}
                  className={`chat-bubble ${m.role}`}
                  style={{
                    maxWidth: "80%",
                    alignSelf: m.role === "user" ? "flex-end" : "flex-start",
                  }}
                >
                  <div className="role">
                    {m.role === "user"
                      ? "USER"
                      : `NPC · ${MOCK.character.name}`}
                  </div>
                  {m.text}
                </div>
              ))}
              {typing && (
                <div
                  className="chat-bubble npc"
                  style={{
                    maxWidth: "80%",
                    color: "var(--ink-3)",
                    fontStyle: "italic",
                  }}
                >
                  <div className="role">NPC · {MOCK.character.name}</div>
                  typing<span className="mono">...</span>
                </div>
              )}
            </div>
            <div
              style={{
                borderTop: "1px solid var(--rule)",
                padding: 10,
                display: "flex",
                gap: 8,
              }}
            >
              <input
                className="input"
                placeholder="Say something to the witcher..."
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && send()}
              />
              <button className="btn primary" onClick={send}>
                Send
              </button>
              <button className="btn ghost" title="Save as test case">
                {I.plus} Case
              </button>
            </div>
          </div>

          <div className="col">
            <div className="panel">
              <div className="panel-head">
                <span>Character Card</span>
              </div>
              <div
                className="panel-body"
                style={{ fontSize: 12, lineHeight: 1.6 }}
              >
                <div style={{ fontWeight: 500, fontSize: 13 }}>
                  {MOCK.character.name}
                </div>
                <div
                  className="mono muted"
                  style={{ fontSize: 10.5, marginBottom: 8 }}
                >
                  {MOCK.character.id}
                </div>
                <div style={{ marginBottom: 8, color: "var(--ink-2)" }}>
                  {MOCK.character.persona}
                </div>
                <div
                  className="label"
                  style={{
                    fontSize: 10.5,
                    textTransform: "uppercase",
                    letterSpacing: "0.08em",
                    color: "var(--ink-3)",
                    fontWeight: 600,
                    marginBottom: 4,
                  }}
                >
                  Voice
                </div>
                <div
                  style={{
                    marginBottom: 10,
                    fontSize: 11.5,
                    color: "var(--ink-2)",
                  }}
                >
                  {MOCK.character.voice}
                </div>
                <div
                  className="label"
                  style={{
                    fontSize: 10.5,
                    textTransform: "uppercase",
                    letterSpacing: "0.08em",
                    color: "var(--ink-3)",
                    fontWeight: 600,
                    marginBottom: 4,
                  }}
                >
                  Knowledge
                </div>
                <div
                  style={{
                    display: "flex",
                    flexWrap: "wrap",
                    gap: 4,
                    marginBottom: 8,
                  }}
                >
                  {MOCK.character.knowledge.map((k) => (
                    <span key={k} className="tag">
                      {k}
                    </span>
                  ))}
                </div>
                <div
                  className="label"
                  style={{
                    fontSize: 10.5,
                    textTransform: "uppercase",
                    letterSpacing: "0.08em",
                    color: "var(--ink-3)",
                    fontWeight: 600,
                    marginBottom: 4,
                  }}
                >
                  Forbidden
                </div>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
                  {MOCK.character.forbidden.map((k) => (
                    <span
                      key={k}
                      className="tag"
                      style={{
                        color: "var(--fail)",
                        borderColor: "var(--fail-bg)",
                      }}
                    >
                      {k}
                    </span>
                  ))}
                </div>
              </div>
            </div>
            <div className="panel">
              <div className="panel-head">
                <span>Session Guardrails</span>
              </div>
              <div
                className="panel-body"
                style={{ display: "flex", flexDirection: "column", gap: 8 }}
              >
                {MOCK.guardrails
                  .filter((g) => g.key !== "compliance")
                  .map((g) => (
                    <div
                      key={g.key}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: 8,
                        fontSize: 11.5,
                      }}
                    >
                      <GSwatch cat={g.key} />
                      <span style={{ flex: 1 }}>{g.name}</span>
                      <Badge kind={guard ? "pass" : "neutral"}>
                        {guard ? "ON" : "off"}
                      </Badge>
                    </div>
                  ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

function GuardrailsPage() {
  return (
    <>
      <div className="page-head">
        <h1>Guardrail Rubrics</h1>
        <div className="sub">
          Criteria and failure modes used by the judge model to score NPC
          responses.
        </div>
      </div>
      <div className="page-body">
        <div className="col" style={{ gap: 16 }}>
          {MOCK.guardrails.map((g) => (
            <div key={g.key} className="panel">
              <div className="panel-head">
                <span style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <GSwatch cat={g.key} /> {g.name}{" "}
                  <span
                    className="mono muted"
                    style={{ textTransform: "none", letterSpacing: 0 }}
                  >
                    · {g.short}
                  </span>
                </span>
                <div className="actions">
                  <button className="btn sm ghost">Edit rubric</button>
                </div>
              </div>
              <div className="panel-body">
                <div
                  style={{
                    color: "var(--ink-2)",
                    marginBottom: 12,
                    maxWidth: 680,
                  }}
                >
                  {g.description}
                </div>
                <div className="grid-2">
                  <div>
                    <div
                      className="label"
                      style={{
                        fontSize: 10.5,
                        textTransform: "uppercase",
                        letterSpacing: "0.08em",
                        color: "var(--ink-3)",
                        fontWeight: 600,
                        marginBottom: 6,
                      }}
                    >
                      Rubric criteria
                    </div>
                    <ul
                      style={{
                        margin: 0,
                        paddingLeft: 16,
                        fontSize: 12,
                        lineHeight: 1.7,
                      }}
                    >
                      {g.rubric.map((r) => (
                        <li key={r}>{r}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <div
                      className="label"
                      style={{
                        fontSize: 10.5,
                        textTransform: "uppercase",
                        letterSpacing: "0.08em",
                        color: "var(--ink-3)",
                        fontWeight: 600,
                        marginBottom: 6,
                      }}
                    >
                      Failure modes
                    </div>
                    {g.failureModes.length ? (
                      <div
                        style={{ display: "flex", flexWrap: "wrap", gap: 5 }}
                      >
                        {g.failureModes.map((f) => (
                          <Badge key={f} kind="fail">
                            {f}
                          </Badge>
                        ))}
                      </div>
                    ) : (
                      <div className="muted" style={{ fontSize: 11 }}>
                        — aggregate score; no independent failure modes —
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}

function OverviewPage({ goto }) {
  return (
    <>
      <div className="page-head">
        <h1>Overview</h1>
        <div className="sub">
          Last run {MOCK.project.lastRun} · {MOCK.summary.casesRun} cases ·{" "}
          {MOCK.guardrails.length - 1} guardrails active
        </div>
      </div>
      <div className="page-body">
        <div className="grid-4" style={{ marginBottom: 20 }}>
          <div className="card-metric">
            <div className="label">Compliance (guarded)</div>
            <div className="val" style={{ color: "var(--pass)" }}>
              {pctFmt1(MOCK.summary.guarded.compliance)}
            </div>
            <div className="foot">
              <Delta
                from={MOCK.summary.baseline.compliance}
                to={MOCK.summary.guarded.compliance}
              />
            </div>
          </div>
          <div className="card-metric">
            <div className="label">Cases passed</div>
            <div className="val">
              {MOCK.summary.casesPassed.guarded}/{MOCK.summary.casesRun}
            </div>
            <div className="foot muted">
              baseline: {MOCK.summary.casesPassed.baseline}/
              {MOCK.summary.casesRun}
            </div>
          </div>
          <div className="card-metric">
            <div className="label">Tokens · run</div>
            <div className="val">
              {(MOCK.summary.tokensUsed / 1000).toFixed(1)}k
            </div>
            <div className="foot muted">runtime {MOCK.summary.runtime}</div>
          </div>
          <div className="card-metric">
            <div className="label">Cost · run</div>
            <div className="val">${MOCK.summary.costUsd.toFixed(2)}</div>
            <div className="foot muted">validator: gemini-2.5-flash</div>
          </div>
        </div>

        <div
          style={{ display: "grid", gridTemplateColumns: "1.4fr 1fr", gap: 20 }}
        >
          <div className="panel">
            <div className="panel-head">
              <span>Pipeline</span>
            </div>
            <div className="panel-body">
              {[
                {
                  step: "1",
                  label: "Upload & parse script",
                  desc: "TheContinent.json → world.json",
                  state: "done",
                  act: "upload",
                },
                {
                  step: "2",
                  label: "Browse world & regions",
                  desc: "6 regions, 4 characters indexed",
                  state: "done",
                  act: "world",
                },
                {
                  step: "3",
                  label: "Select NPC character",
                  desc: "Active: Geralt of Rivia",
                  state: "done",
                  act: "characters",
                },
                {
                  step: "4",
                  label: "Configure evaluation cases",
                  desc: "37 cases across 4 guardrail categories",
                  state: "done",
                  act: "configure",
                },
                {
                  step: "5",
                  label: "Run & inspect results",
                  state: "live",
                  act: "results",
                },
              ].map((s) => (
                <div
                  key={s.step}
                  onClick={() => goto(s.act)}
                  style={{
                    display: "flex",
                    gap: 12,
                    padding: "12px 0",
                    borderBottom: "1px solid var(--rule)",
                    cursor: "pointer",
                  }}
                >
                  <div
                    style={{
                      width: 26,
                      height: 26,
                      borderRadius: "50%",
                      border: "1.5px solid var(--rule-strong)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontFamily: "var(--font-mono)",
                      fontSize: 11,
                      fontWeight: 500,
                      background:
                        s.state === "done" ? "var(--ink)" : "var(--bg-card)",
                      color: s.state === "done" ? "var(--bg)" : "var(--ink-3)",
                      flexShrink: 0,
                    }}
                  >
                    {s.state === "done" ? "✓" : s.step}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 13, fontWeight: 500 }}>
                      {s.label}
                    </div>
                    <div className="muted" style={{ fontSize: 11.5 }}>
                      {s.desc}
                    </div>
                  </div>
                  {s.state === "live" && <Badge kind="info">latest</Badge>}
                </div>
              ))}
            </div>
          </div>
          <div className="panel">
            <div className="panel-head">
              <span>Guardrail Lift (last 8 runs)</span>
            </div>
            <div
              className="panel-body"
              style={{ display: "flex", flexDirection: "column", gap: 12 }}
            >
              {MOCK.guardrails.map((g) => (
                <div
                  key={g.key}
                  style={{ display: "flex", alignItems: "center", gap: 10 }}
                >
                  <GSwatch cat={g.key} />
                  <span style={{ flex: 1, fontSize: 12 }}>{g.name}</span>
                  <span style={{ color: "var(--ink-3)" }}>
                    <Spark data={MOCK.history[g.key]} w={70} />
                  </span>
                  <span
                    className="mono tnum"
                    style={{
                      width: 40,
                      textAlign: "right",
                      fontSize: 11,
                      color: `var(--${scoreClass(MOCK.summary.guarded[g.key])})`,
                    }}
                  >
                    {pctFmt1(MOCK.summary.guarded[g.key])}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

Object.assign(window, {
  ConfigurePage,
  UploadPage,
  WorldPage,
  CharactersPage,
  ChatPage,
  GuardrailsPage,
  OverviewPage,
});
