# LLM-Driven NPC Behavioural Consistency Framework

**Honours Thesis — Ontario Tech University**  
Supervised by Cristiano Politowski & Mariana Shimabukuro

---

## About

This repository contains the prototype and evaluation framework for an Honours thesis investigating **behavioural consistency in LLM-driven NPCs**. The testbed character is Geralt of Rivia from _The Witcher 3: Wild Hunt_, evaluated against a multi-dimensional framework across 37 single-turn adversarial probes.

The framework measures four dimensions of NPC behavioural consistency:

| Code   | Dimension             | What It Tests                                                |
| ------ | --------------------- | ------------------------------------------------------------ |
| **PA** | Personality Alignment | Does the NPC stay in character under pressure?               |
| **KF** | Knowledge Filtration  | Does the NPC reject out-of-world or meta knowledge?          |
| **BM** | Bias Mitigation       | Does the NPC resist player-introduced biased framings?       |
| **NA** | Narrative Adherence   | Does the NPC respect lore and temporal knowledge boundaries? |
| **GC** | Guideline Compliance  | Cumulative score derived from the four dimensions above.     |

---

## Repository Structure

```
├── evaluation.py                        # Main evaluation runner (single-turn adversarial suite)
├── WorldCreation.py                     # Hierarchical world/region/character generator
├── build_data_js.py                     # Builds data file for the prototype dashboard
├── RunChat-Witcher.py                   # Witcher-specific chat interface (Gradio)
├── RunChat-General.py                   # General-purpose chat interface (Gradio)
├── LLM.py                               # Ollama API wrapper
├── rag.py                               # RAG module for script indexing and retrieval
├── helper_template.py                   # Template for helper.py (copy and configure)
├── requirements.txt                     # Python dependencies
│
├── validators/
│   ├── narrative_adherence_validator.py
│   ├── meta_knowledge_filtration_validator.py
│   ├── bias_mitigation_validator.py
│   └── personality_alignment_validator.py
│
├── interface/                           # Prototype evaluation dashboard
├── scriptData/                          # Witcher 3 script text + RAG index
├── saved_worlds/                        # Output from WorldCreation.py
```

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/SaffronBirch/LLM-Driven_NPC_Framework.git
cd LLM-Driven_NPC_Framework
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your environment

Copy `helper_template.py` to `helper.py` and fill in your API keys:

```bash
cp helper_template.py helper.py
```

Then edit `helper.py` to set your keys. Create a `.env` file in the project root if needed:

```
GOOGLE_API_KEY=your_gemini_key_here
```

### 5. Ensure Ollama and Gemini (or other API) are running

The NPC model (`deepseek-v3.2:cloud`) is served via Ollama. The validator model (`gemini-2.5-flash`) is served via Google AI Studio. Make sure they are running locally before executing any scripts:

```bash
ollama serve
```

---

## Running the Prototype Dashboard

The prototype is an interactive evaluation dashboard that visualises results from the adversarial test suite. Follow these steps in order:

### Step 1 — Generate the world

```bash
python WorldCreation.py
```

This produces a JSON file (e.g. `saved_worlds/TheContinent_<timestamp>.json`) containing the world, regions, and per-region character descriptions used by the NPC and validators.

### Step 2 — Run the evaluation

```bash
python evaluation.py \
    --tests adversarial-single \
    --region "White Orchard" \
    --act prologue \
    --na-guardrail --mkf-guardrail --bm-guardrail --pa-guardrail \
    --no-judge \
    --regenerate-on-fail
```

This produces an `eval_Geralt_<region>_<timestamp>.json` results file.

### Step 3 — Build the dashboard data

```bash
python build_data_js.py
```

This reads the most recent evaluation JSON and writes a `data.js` file used by the dashboard interface.

### Step 4 — Move the data file into the interface folder

```bash
mv data.js interface/
```

### Step 5 — Open the prototype dashboard

```bash
cd interface
python -m http.server 8000
```

Then open your browser and navigate to `http://localhost:8000`.

---

## Running the Chat Interface

Two chat interfaces are available, both powered by Gradio:

**Witcher-specific** (Geralt of Rivia, region-aware knowledge boundaries):

```bash
python RunChat-Witcher.py
```

**General** (any character from any generated world):

```bash
python RunChat-General.py
```

Both will print a local URL to open in your browser. Type `Hello` (or `Hello Geralt`) to begin the conversation. Use the region dropdown to change Geralt's location — this updates his knowledge boundary automatically.

---

## Running the Evaluation Directly

```bash
python evaluation.py \
    --tests adversarial-single \
    --seed 123 \
    --region "White Orchard" \
    --act prologue \
    --na-guardrail --mkf-guardrail --bm-guardrail --pa-guardrail \
    --regenerate-on-fail
```

**Key flags:**

| Flag                   | Description                                               |
| ---------------------- | --------------------------------------------------------- |
| `--tests`              | `all`, `adversarial`, or `adversarial-single`             |
| `--region`             | Starting region for Geralt                                |
| `--act`                | Narrative act (`prologue`, `act_1`, `act_2`, `act_3`)     |
| `--na-guardrail`       | Enable Narrative Adherence guardrail                      |
| `--mkf-guardrail`      | Enable Meta-Knowledge Filtration guardrail                |
| `--bm-guardrail`       | Enable Bias Mitigation guardrail                          |
| `--pa-guardrail`       | Enable Personality Alignment guardrail                    |
| `--no-judge`           | Skip LLM-as-judge scoring (for validator scoring only)    |
| `--regenerate-on-fail` | Re-prompt NPC with a correction hint on guardrail failure |
| `--seed`               | Random seed for reproducibility                           |

Results are saved as both a full JSON log and a flat CSV for review.

---

## Models Used

| Role      | Provider | Model                 |
| --------- | -------- | --------------------- |
| NPC       | Ollama   | `deepseek-v3.2:cloud` |
| Validator | Gemini   | `gemini-2.5-flash`    |

---

## External Dependencies

- [Ollama](https://ollama.com) — local LLM serving
- [Guardrails AI](https://www.guardrailsai.com) — validator framework
- [Gradio](https://www.gradio.app) — chat interface
- [sentence-transformers](https://www.sbert.net) — RAG embeddings (`all-MiniLM-L6-v2`)
- [Google Generative AI](https://ai.google.dev) — Gemini validator
