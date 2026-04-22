# ============================================================
# ADD THESE IMPORTS at the top of main_fixed_v2.py
# ============================================================
# from pydantic import BaseModel
# import re

# ============================================================
# PASTE THIS BLOCK anywhere after your existing imports/setup
# ============================================================

# ─────────────────────────────────────────────
#  QuantaCure Knowledge Base (RAG Source Data)
# ─────────────────────────────────────────────
QUANTACURE_KNOWLEDGE = """
PROJECT OVERVIEW
================
Project Name: QuantaCure
Type: Final Year Project (FYP) — AI-Driven Drug Discovery System
Developer: Sami
Institution: Academic FYP submission

QuantaCure is an AI-powered molecular binding affinity prediction system that integrates
Graph Neural Networks (specifically Graph Isomorphism Networks using GINEConv layers)
with quantum-mechanical feature augmentation for computational drug discovery.

SYSTEM ARCHITECTURE
===================
QuantaCure uses a three-tier architecture:

1. Frontend: React-based UI built and managed via Lovable.
   - Displays prediction results, molecule visualisations, and virtual screening tables.
   - Communicates with the backend via REST API over ngrok tunnel.

2. Backend: FastAPI (Python), run locally via VS Code.
   - Hosts the /predict endpoint (trimodal: Classical, Hybrid, Quantum).
   - Hosts the /virtual-screening endpoint for batch molecule evaluation.
   - Hosts the /chat endpoint for this RAG chatbot.
   - Uses CORS middleware and ngrok bypass headers.

3. ML Core: Graph Isomorphism Network (GINEConv, 5 layers).
   - Pre-trained on ChEMBL 36 (large-scale bioactivity database).
   - Fine-tuned on PDBbind v2013 core set (protein-ligand binding affinity data).
   - Predicts binding affinity (pKd), energy scores, and stability scores.

PREDICTION MODES
================
QuantaCure supports three prediction modes via the /predict endpoint:

1. Classical Mode:
   - Uses the GIN model with standard molecular graph features.
   - Atom features: atomic number, degree, hybridisation, aromaticity, hydrogen count.
   - Bond features: bond type, conjugation, ring membership.
   - Output: binding affinity (pKd), energy (kcal/mol), stability score (QED).

2. Hybrid Mode:
   - Combines Classical GIN features with simulated quantum-mechanical descriptors.
   - Adds features such as HOMO-LUMO gap approximation, molecular polarisability,
     electron density distribution estimates, and dipole moment proxies.
   - More computationally intensive than Classical mode.

3. Quantum Mode:
   - Extends Hybrid mode with additional quantum circuit-inspired feature augmentation.
   - Quantum features are currently simulated (not run on real quantum hardware) —
     this is a known limitation acknowledged in the FYP report.
   - Intended to approximate how real quantum computing could enhance drug prediction.

MACHINE LEARNING DETAILS
========================
Model Architecture: Graph Isomorphism Network with Edge Features (GINEConv)
- 5 GINEConv message-passing layers
- Hidden dimension: 256
- Output: single scalar (predicted pKd / binding affinity)
- Activation: ReLU
- Pooling: Global mean pooling over node embeddings

Training Data:
- Pre-training: ChEMBL 36 — ~2 million bioactivity data points
- Fine-tuning: PDBbind v2013 core set — ~2,764 protein-ligand complexes

Molecular Featurisation:
- RDKit used for molecule parsing (SMILES → graph)
- Atoms become graph nodes; bonds become graph edges
- Atom features: atomic number, degree, formal charge, num Hs, hybridisation, aromaticity
- Edge features: bond type (single/double/triple/aromatic), conjugation, ring flag

Stability Score:
- Computed using RDKit's Quantitative Estimate of Drug-likeness (QED)
- Continuous score 0–1 (higher = more drug-like)
- Replaced earlier binary Lipinski pass/fail logic

PROTEIN TARGET IDENTIFICATION
==============================
QuantaCure identifies protein targets through two mechanisms:

1. PDB ID Lookup Dictionary (Virtual Screening):
   - An 80+ entry dictionary maps known PDB IDs to human-readable protein names.
   - Example: "1HVR" → "HIV-1 Protease", "1OYT" → "CDK2 (Cyclin-Dependent Kinase 2)"

2. Rule-Based Structural Classifier — infer_protein_target() (Live Predictions):
   - Infers the likely protein target from a SMILES string.
   - Uses substructure matching and molecular property rules.
   - Example rules: beta-lactam ring → Beta-Lactamase, purine scaffold → Kinase family,
     sulfonamide group → Carbonic Anhydrase.

VIRTUAL SCREENING
=================
The Virtual Screening module (located on the Molecule Lab page) allows users to:
- Input a target protein (by PDB ID or name).
- Run batch predictions across multiple SMILES strings.
- View results in a sortable table with affinity, energy, stability, and protein name.
- The table reads protein names directly from the API response.

KNOWN LIMITATIONS
=================
1. Quantum features are simulated, not run on real quantum hardware.
2. The system uses ngrok for dev tunneling — not suitable for production.
3. Protein classification for novel molecules relies on rule-based heuristics.
4. The model was fine-tuned on PDBbind v2013 (not the latest version).

FUTURE ROADMAP
==============
Phase 1: Google Cloud Run Deployment (Sami has Google for Developers access)
Phase 2: Live ChEMBL Search Integration
Phase 3: ADMET Prediction Tab (Absorption, Distribution, Metabolism, Excretion, Toxicity)
Phase 4: PDF Report Export

KEY TECHNOLOGIES USED
=====================
- PyTorch Geometric (GINEConv layers)
- RDKit (cheminformatics, QED, SMILES parsing)
- FastAPI (Python backend)
- React / Lovable (frontend)
- ChEMBL 36 (pre-training dataset)
- PDBbind v2013 (fine-tuning dataset)
- ngrok (dev tunneling)
- Google Cloud Run (planned deployment)

GLOSSARY
========
- pKd: Negative log of dissociation constant — higher value = stronger binding.
- SMILES: Simplified Molecular Input Line Entry System — text representation of molecules.
- GIN: Graph Isomorphism Network — a type of GNN that can distinguish graph structures.
- GINEConv: GIN with Edge features — extends GIN to incorporate bond-level information.
- QED: Quantitative Estimate of Drug-likeness — 0 to 1 score for drug-likeness.
- HOMO-LUMO Gap: Energy gap between highest occupied and lowest unoccupied molecular orbitals.
- PDBbind: A database of experimentally measured protein-ligand binding affinities.
- ChEMBL: A manually curated database of bioactive drug-like small molecules.
- RAG: Retrieval-Augmented Generation — combining a knowledge base with a language model.
- ADMET: Absorption, Distribution, Metabolism, Excretion, Toxicity — drug property profile.
- Virtual Screening: Computationally evaluating large sets of compounds against a target.
"""

# ─────────────────────────────────────────────
#  Chat Request / Response Models
# ─────────────────────────────────────────────
class ChatMessage(BaseModel):
    role: str        # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []

class ChatResponse(BaseModel):
    reply: str
    sources: list[str] = []

# ─────────────────────────────────────────────
#  Simple RAG: retrieve relevant knowledge chunks
# ─────────────────────────────────────────────
def retrieve_relevant_chunks(query: str, top_k: int = 3) -> list[str]:
    """
    Splits the knowledge base into sections and returns the most relevant
    ones based on keyword overlap with the user query.
    """
    query_lower = query.lower()
    query_words = set(re.findall(r'\b\w{3,}\b', query_lower))

    # Split knowledge base into sections by double newline + heading
    sections = re.split(r'\n(?=[A-Z][A-Z ]+\n[=]+)', QUANTACURE_KNOWLEDGE)
    sections = [s.strip() for s in sections if len(s.strip()) > 30]

    scored = []
    for section in sections:
        section_lower = section.lower()
        section_words = set(re.findall(r'\b\w{3,}\b', section_lower))
        overlap = len(query_words & section_words)
        scored.append((overlap, section))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [s for _, s in scored[:top_k] if _ > 0] or [sections[0]]


# ─────────────────────────────────────────────
#  /chat Endpoint
# ─────────────────────────────────────────────
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    RAG-based chatbot endpoint for QuantaCure.
    Retrieves relevant project knowledge and generates a contextual response.
    """
    try:
        user_message = request.message.strip()
        if not user_message:
            raise HTTPException(status_code=400, detail="Message cannot be empty.")

        # Retrieve relevant knowledge chunks
        relevant_chunks = retrieve_relevant_chunks(user_message, top_k=3)
        context = "\n\n---\n\n".join(relevant_chunks)

        # Build conversation history string
        history_str = ""
        for msg in request.history[-6:]:  # keep last 6 turns
            role = "User" if msg.role == "user" else "QuantaCure Assistant"
            history_str += f"{role}: {msg.content}\n"

        # Compose the prompt for the LLM
        system_prompt = f"""You are QuantaCure Assistant, an AI helper for the QuantaCure drug discovery platform.
QuantaCure is an FYP project that predicts molecular binding affinity using Graph Neural Networks and quantum-mechanical features.

Use ONLY the following project knowledge to answer questions. If the answer is not in the knowledge base, say so honestly.
Be concise, friendly, and scientifically accurate. Format responses in clear paragraphs. Do not make up data.

PROJECT KNOWLEDGE:
{context}
"""
        full_prompt = ""
        if history_str:
            full_prompt += f"Conversation so far:\n{history_str}\n"
        full_prompt += f"User: {user_message}\nQuantaCure Assistant:"

        # ── Call your preferred LLM here ──
        # Option A: OpenAI-compatible (swap in your key/model)
        # Option B: Call Anthropic Claude API
        # Option C: Use a local model (Ollama etc.)
        #
        # Below is a simple template response that works WITHOUT an external LLM,
        # so you can test the endpoint immediately.
        # Replace the block below with your actual LLM call.

        reply = generate_rag_reply(system_prompt, full_prompt, user_message, relevant_chunks)

        # Identify which sections were used (first line = section title)
        sources = []
        for chunk in relevant_chunks:
            first_line = chunk.split('\n')[0].strip()
            if first_line and first_line not in sources:
                sources.append(first_line)

        return ChatResponse(reply=reply, sources=sources)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


def generate_rag_reply(system_prompt: str, full_prompt: str, user_message: str, chunks: list[str]) -> str:
    """
    Replace this function body with your actual LLM call.
    Currently returns a knowledge-grounded template reply for testing.

    Example with Anthropic Claude (install: pip install anthropic):
    ──────────────────────────────────────────────────────────────
    import anthropic
    client = anthropic.Anthropic(api_key="YOUR_API_KEY")
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=512,
        system=system_prompt,
        messages=[{"role": "user", "content": full_prompt}]
    )
    return message.content[0].text

    Example with OpenAI:
    ────────────────────
    from openai import OpenAI
    client = OpenAI(api_key="YOUR_API_KEY")
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": full_prompt}
        ],
        max_tokens=512
    )
    return response.choices[0].message.content
    """

    # ── Fallback: keyword-based response (no LLM needed for testing) ──
    q = user_message.lower()
    combined = "\n".join(chunks).lower()

    if any(w in q for w in ["what is", "what's", "explain", "describe", "overview"]):
        if "quantacure" in q or "project" in q:
            return ("QuantaCure is an AI-powered molecular binding affinity prediction system. "
                    "It combines Graph Neural Networks (GINEConv, 5 layers) pre-trained on ChEMBL 36 "
                    "and fine-tuned on PDBbind v2013, with quantum-mechanical feature augmentation. "
                    "The system supports three prediction modes: Classical, Hybrid, and Quantum.")
        if "gin" in q or "graph" in q or "neural" in q:
            return ("QuantaCure uses a Graph Isomorphism Network with Edge features (GINEConv). "
                    "Molecules are represented as graphs — atoms are nodes, bonds are edges. "
                    "The model has 5 message-passing layers with a hidden dimension of 256, "
                    "and outputs a predicted binding affinity (pKd).")
    if any(w in q for w in ["mode", "classical", "hybrid", "quantum"]):
        return ("QuantaCure offers three prediction modes:\n\n"
                "• Classical — standard GIN features from molecular graph structure.\n"
                "• Hybrid — Classical features + simulated quantum-mechanical descriptors "
                "(HOMO-LUMO gap, polarisability, dipole moment).\n"
                "• Quantum — Hybrid + additional quantum circuit-inspired augmentation "
                "(currently simulated, not run on real quantum hardware).")
    if any(w in q for w in ["protein", "target", "pdb"]):
        return ("Protein targets are identified in two ways:\n\n"
                "1. PDB ID Lookup — an 80+ entry dictionary maps known PDB IDs to protein names "
                "(e.g. '1HVR' → HIV-1 Protease).\n"
                "2. Rule-Based Classifier (infer_protein_target) — infers targets from SMILES "
                "using substructure matching (e.g. beta-lactam ring → Beta-Lactamase).")
    if any(w in q for w in ["virtual screen", "screening", "batch"]):
        return ("The Virtual Screening module (on the Molecule Lab page) allows batch evaluation "
                "of multiple SMILES strings against a target protein. Results are shown in a "
                "sortable table with binding affinity, energy, stability, and protein name, "
                "all read directly from the API response.")
    if any(w in q for w in ["stability", "qed", "drug-like"]):
        return ("The stability score is computed using RDKit's Quantitative Estimate of "
                "Drug-likeness (QED) — a continuous score from 0 to 1 where higher values "
                "indicate more drug-like molecules. This replaced an earlier binary "
                "Lipinski pass/fail approach.")
    if any(w in q for w in ["future", "roadmap", "plan", "next"]):
        return ("The QuantaCure roadmap has four planned phases:\n\n"
                "Phase 1 — Google Cloud Run Deployment\n"
                "Phase 2 — Live ChEMBL Search Integration\n"
                "Phase 3 — ADMET Prediction Tab\n"
                "Phase 4 — PDF Report Export")
    if any(w in q for w in ["limit", "limitation", "weakness", "problem"]):
        return ("Known limitations of QuantaCure:\n\n"
                "1. Quantum features are simulated (not real quantum hardware).\n"
                "2. ngrok is used for dev tunneling — not production-ready.\n"
                "3. Protein classification for novel molecules uses heuristic rules.\n"
                "4. The model was fine-tuned on PDBbind v2013, not the latest version.")
    if any(w in q for w in ["smiles", "rdkit", "featur"]):
        return ("Molecules are featurised using RDKit by converting SMILES strings into molecular "
                "graphs. Atom features include: atomic number, degree, formal charge, hydrogen count, "
                "hybridisation, and aromaticity. Edge features include: bond type, conjugation, "
                "and ring membership.")
    if any(w in q for w in ["chembl", "pdb", "train", "dataset", "data"]):
        return ("QuantaCure's model was pre-trained on ChEMBL 36 (~2 million bioactivity data points) "
                "and fine-tuned on the PDBbind v2013 core set (~2,764 protein-ligand complexes with "
                "experimentally measured binding affinities).")

    # Generic fallback
    return ("I'm the QuantaCure Assistant. I can help you understand how this system works — "
            "including prediction modes, the GIN model, virtual screening, protein targets, "
            "datasets, and the future roadmap. What would you like to know?")
