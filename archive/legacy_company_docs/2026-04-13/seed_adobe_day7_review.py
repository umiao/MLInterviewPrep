"""Seed script: Insert Adobe Prep Day7 -- Review Checklist + Concept Map + Error Cards.

Uses StudyNoteBuilder for typed content generation with FormulaBlock,
auto-bolded terms, prerequisites, and fail-fast single-dollar detection.

Creates a CompanyDocument under Adobe (company_id=23) in mle_prep.db.
Idempotent: deletes old raw-string version, inserts Builder-generated version.
"""

import importlib.util
import sys
from pathlib import Path

# Import StudyNoteBuilder from scripts/study_note_builder.py
_BUILDER_PATH = Path(__file__).resolve().parent / "study_note_builder.py"
_spec = importlib.util.spec_from_file_location("study_note_builder", _BUILDER_PATH)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
sys.modules["study_note_builder"] = _mod
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]
StudyNoteBuilder = _mod.StudyNoteBuilder
FormulaBlock = _mod.FormulaBlock

COMPANY_ID = 23  # Adobe
DOC_TITLE = "Adobe Prep Day7: Review Checklist + Concept Map + Error Cards"

# ---------------------------------------------------------------------------
# HTML Diagrams
# ---------------------------------------------------------------------------

# -- Domain 1: Diffusion Models Checklist --
CHECKLIST_DIFFUSION = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<div style="font-size:15px; font-weight:bold; color:#4a90d9; '
    'margin-bottom:12px;">Diffusion Models Checklist</div>\n'
    '<table style="border-collapse:collapse; color:#e0e0e0; font-size:13px; width:100%;">\n'
    '<tr style="border-bottom:1px solid #444;">\n'
    '<th style="padding:6px 12px; text-align:left; width:30px;"></th>\n'
    '<th style="padding:6px 12px; text-align:left;">Topic</th>\n'
    '<th style="padding:6px 12px; text-align:left;">Key Point to Verify</th>\n'
    '</tr>\n'
    '<tr><td style="padding:6px 12px;">[ ]</td><td>DDPM Forward Process</td>\n'
    '<td>Can write x_t = sqrt(alpha_bar_t) * x_0 + sqrt(1 - alpha_bar_t) * epsilon from memory</td></tr>\n'
    '<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>DDPM Reverse Process</td>\n'
    '<td>Know that model predicts noise epsilon_theta(x_t, t), not x_0 directly</td></tr>\n'
    '<tr><td style="padding:6px 12px;">[ ]</td><td>Training Objective</td>\n'
    '<td>Simple MSE loss: E[||epsilon - epsilon_theta(x_t, t)||^2], t sampled uniformly</td></tr>\n'
    '<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>Noise Schedules</td>\n'
    '<td>Linear vs Cosine -- cosine preserves more signal at early steps, better for high-res</td></tr>\n'
    '<tr><td style="padding:6px 12px;">[ ]</td><td>DDIM Sampler</td>\n'
    '<td>Same trained model, deterministic sampling, 50 steps vs DDPM 1000 steps</td></tr>\n'
    '<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>Latent Diffusion / Stable Diffusion</td>\n'
    '<td>VAE encodes 512x512x3 to 64x64x4 (8x spatial compression), diffusion in latent space</td></tr>\n'
    '<tr><td style="padding:6px 12px;">[ ]</td><td>Classifier-Free Guidance (CFG)</td>\n'
    '<td>epsilon_hat = epsilon_uncond + w * (epsilon_cond - epsilon_uncond), typical w=7.5</td></tr>\n'
    '<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>Score-Based / SDE View</td>\n'
    '<td>Score = grad log p(x), forward SDE + reverse SDE framework unifies DDPM/SMLD</td></tr>\n'
    '</table>\n'
    '</div>'
)

# -- Domain 2: Alignment + Distillation Checklist --
CHECKLIST_ALIGNMENT = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<div style="font-size:15px; font-weight:bold; color:#2d6a4f; '
    'margin-bottom:12px;">Alignment + Distillation Checklist</div>\n'
    '<table style="border-collapse:collapse; color:#e0e0e0; font-size:13px; width:100%;">\n'
    '<tr style="border-bottom:1px solid #444;">\n'
    '<th style="padding:6px 12px; text-align:left; width:30px;"></th>\n'
    '<th style="padding:6px 12px; text-align:left;">Topic</th>\n'
    '<th style="padding:6px 12px; text-align:left;">Key Point to Verify</th>\n'
    '</tr>\n'
    '<tr><td style="padding:6px 12px;">[ ]</td><td>RLHF 3-Stage Pipeline</td>\n'
    '<td>SFT -> Reward Model (Bradley-Terry) -> PPO fine-tuning with KL penalty</td></tr>\n'
    '<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>Bradley-Terry Model</td>\n'
    '<td>P(y_w > y_l) = sigma(r(y_w) - r(y_l)), trained on human preference pairs</td></tr>\n'
    '<tr><td style="padding:6px 12px;">[ ]</td><td>DPO Closed-Form</td>\n'
    '<td>L_DPO = -E[log sigma(beta * (log pi/pi_ref(y_w) - log pi/pi_ref(y_l)))], no reward model needed</td></tr>\n'
    '<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>RLHF vs DPO Tradeoffs</td>\n'
    '<td>RLHF: more flexible, reward hacking risk, 3 models. DPO: simpler, needs reference model, beta-sensitive</td></tr>\n'
    '<tr><td style="padding:6px 12px;">[ ]</td><td>Reward Hacking</td>\n'
    '<td>Model exploits reward model flaws (verbosity, formatting). Fix: KL constraint, reward ensemble</td></tr>\n'
    '<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>Variants (RLAIF, IPO, KTO)</td>\n'
    '<td>RLAIF: AI-generated preferences. IPO: removes log sigmoid. KTO: single-response (no pairs)</td></tr>\n'
    '<tr><td style="padding:6px 12px;">[ ]</td><td>LLM Distillation</td>\n'
    '<td>L_KD = alpha*T^2*KL(p_teacher || p_student) + (1-alpha)*CE. Higher T = softer distribution</td></tr>\n'
    '<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>Distillation Architecture</td>\n'
    '<td>70B to 7B: reduce layers, hidden_dim, num_heads. Keep vocab_size, tokenizer</td></tr>\n'
    '</table>\n'
    '</div>'
)

# -- Domain 3: Distributed Training Checklist --
CHECKLIST_DISTRIBUTED = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<div style="font-size:15px; font-weight:bold; color:#d4a017; '
    'margin-bottom:12px;">Distributed Training Checklist</div>\n'
    '<table style="border-collapse:collapse; color:#e0e0e0; font-size:13px; width:100%;">\n'
    '<tr style="border-bottom:1px solid #444;">\n'
    '<th style="padding:6px 12px; text-align:left; width:30px;"></th>\n'
    '<th style="padding:6px 12px; text-align:left;">Topic</th>\n'
    '<th style="padding:6px 12px; text-align:left;">Key Point to Verify</th>\n'
    '</tr>\n'
    '<tr><td style="padding:6px 12px;">[ ]</td><td>Data Parallelism (DP/DDP)</td>\n'
    '<td>Replicate model on each GPU, AllReduce gradients. Memory: 16P per GPU (no savings)</td></tr>\n'
    '<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>Tensor Parallelism (TP)</td>\n'
    '<td>Split weight matrices within a layer. MLP: column-parallel then row-parallel. Needs NVLink</td></tr>\n'
    '<tr><td style="padding:6px 12px;">[ ]</td><td>Pipeline Parallelism (PP)</td>\n'
    '<td>Assign layers to GPUs sequentially. Bubble fraction: (N-1)/(N+M-1). Micro-batches reduce bubble</td></tr>\n'
    '<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>FSDP / ZeRO</td>\n'
    '<td>Shard optimizer+gradients+params across GPUs. Memory: 16P/N. All-gather before forward, reduce-scatter after backward</td></tr>\n'
    '<tr><td style="padding:6px 12px;">[ ]</td><td>ZeRO Stages</td>\n'
    '<td>Stage1: optimizer states. Stage2: +gradients. Stage3: +parameters. Progressive memory reduction</td></tr>\n'
    '<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>Memory Formula</td>\n'
    '<td>Per-param: 2 (fp16 weight) + 2 (fp16 grad) + 12 (Adam: fp32 weight + momentum + variance) = 16 bytes</td></tr>\n'
    '<tr><td style="padding:6px 12px;">[ ]</td><td>3D Parallelism</td>\n'
    '<td>TP (intra-node NVLink) x PP (cross-node) x DP (remaining). GPT-3: TP=8, PP=16, DP=8</td></tr>\n'
    '<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>Selection Guide</td>\n'
    '<td>Fits 1 GPU: DDP. Fits 1 node: FSDP. Exceeds 1 node: 3D parallelism (TP+PP+DP)</td></tr>\n'
    '</table>\n'
    '</div>'
)

# -- Domain 4: RoPE + Long Context + Video Checklist --
CHECKLIST_ROPE_VIDEO = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<div style="font-size:15px; font-weight:bold; color:#8b5cf6; '
    'margin-bottom:12px;">RoPE + Long Context + Video Checklist</div>\n'
    '<table style="border-collapse:collapse; color:#e0e0e0; font-size:13px; width:100%;">\n'
    '<tr style="border-bottom:1px solid #444;">\n'
    '<th style="padding:6px 12px; text-align:left; width:30px;"></th>\n'
    '<th style="padding:6px 12px; text-align:left;">Topic</th>\n'
    '<th style="padding:6px 12px; text-align:left;">Key Point to Verify</th>\n'
    '</tr>\n'
    '<tr><td style="padding:6px 12px;">[ ]</td><td>RoPE Core Idea</td>\n'
    '<td>Rotate q,k by position-dependent angle: theta_i = 1/10000^(2i/d). q_m^T k_n depends only on (m-n)</td></tr>\n'
    '<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>RoPE vs Other PE</td>\n'
    '<td>RoPE: fixed (not learned), relative position, no max length. Sinusoidal: absolute, fixed. ALiBi: linear bias</td></tr>\n'
    '<tr><td style="padding:6px 12px;">[ ]</td><td>Position Interpolation (PI)</td>\n'
    '<td>Scale position: m\' = m * (L_train / L_target). Simple but needs fine-tuning</td></tr>\n'
    '<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>NTK-Aware Scaling</td>\n'
    '<td>Scale base frequency: theta_i\' = 1/(b*alpha)^(2i/d). No fine-tuning needed for moderate extension</td></tr>\n'
    '<tr><td style="padding:6px 12px;">[ ]</td><td>YaRN</td>\n'
    '<td>Per-dimension PI/NTK blend + attention temperature scaling. Best quality for large extensions</td></tr>\n'
    '<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>Video Diffusion Architecture</td>\n'
    '<td>3D VAE (T*H*W to T\'*H\'*W\'), temporal + spatial attention layers, frame consistency</td></tr>\n'
    '<tr><td style="padding:6px 12px;">[ ]</td><td>DiT (Diffusion Transformer)</td>\n'
    '<td>Spacetime patches, AdaLN-Zero conditioning. Replaces U-Net with transformer backbone</td></tr>\n'
    '<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>Adobe Firefly Context</td>\n'
    '<td>Firefly Image to Firefly Video: add temporal layers. Key challenges: temporal consistency, motion, memory</td></tr>\n'
    '</table>\n'
    '</div>'
)

# -- Domain 5: Inference Optimization Checklist --
CHECKLIST_INFERENCE = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<div style="font-size:15px; font-weight:bold; color:#e07a5f; '
    'margin-bottom:12px;">Inference Optimization Checklist</div>\n'
    '<table style="border-collapse:collapse; color:#e0e0e0; font-size:13px; width:100%;">\n'
    '<tr style="border-bottom:1px solid #444;">\n'
    '<th style="padding:6px 12px; text-align:left; width:30px;"></th>\n'
    '<th style="padding:6px 12px; text-align:left;">Topic</th>\n'
    '<th style="padding:6px 12px; text-align:left;">Key Point to Verify</th>\n'
    '</tr>\n'
    '<tr><td style="padding:6px 12px;">[ ]</td><td>FlashAttention</td>\n'
    '<td>Tiled computation in SRAM (19 TB/s). IO: O(N^2*d^2/M) vs standard O(N^2*d + N^2). Online softmax trick</td></tr>\n'
    '<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>GPTQ</td>\n'
    '<td>Layer-wise OBS, sequential error compensation, INT4 weight-only. Post-training, no retraining</td></tr>\n'
    '<tr><td style="padding:6px 12px;">[ ]</td><td>AWQ</td>\n'
    '<td>Protect 1% salient channels via per-channel scaling. INT4. Observation: 1% weights matter 10x more</td></tr>\n'
    '<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>SmoothQuant (W8A8)</td>\n'
    '<td>Migrate quantization difficulty from activations to weights. Per-channel smooth factor s_j</td></tr>\n'
    '<tr><td style="padding:6px 12px;">[ ]</td><td>KV-Cache</td>\n'
    '<td>Size: 2*L*N*H*d bytes per sequence. Biggest inference memory consumer for long sequences</td></tr>\n'
    '<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>PagedAttention</td>\n'
    '<td>Virtual memory for KV-cache: blocks + page tables. Eliminates fragmentation. Copy-on-write for beam search</td></tr>\n'
    '<tr><td style="padding:6px 12px;">[ ]</td><td>Continuous Batching</td>\n'
    '<td>Iteration-level scheduling: new requests join mid-batch. No idle GPU slots waiting for longest sequence</td></tr>\n'
    '<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>Speculative Decoding</td>\n'
    '<td>Draft model proposes K tokens, target verifies in parallel. Lossless (rejection sampling). ~2-3x speedup</td></tr>\n'
    '</table>\n'
    '</div>'
)

# -- Domain 6: Interview Skills Checklist --
CHECKLIST_INTERVIEW = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<div style="font-size:15px; font-weight:bold; color:#ff6b6b; '
    'margin-bottom:12px;">Interview Skills Checklist</div>\n'
    '<table style="border-collapse:collapse; color:#e0e0e0; font-size:13px; width:100%;">\n'
    '<tr style="border-bottom:1px solid #444;">\n'
    '<th style="padding:6px 12px; text-align:left; width:30px;"></th>\n'
    '<th style="padding:6px 12px; text-align:left;">Topic</th>\n'
    '<th style="padding:6px 12px; text-align:left;">Key Point to Verify</th>\n'
    '</tr>\n'
    '<tr><td style="padding:6px 12px;">[ ]</td><td>STAR-T Framework</td>\n'
    '<td>Situation(15s) -> Task(15s) -> Approach(60s) -> Result(15s) -> Transfer(15s). Total ~2min</td></tr>\n'
    '<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>Story 1: Inference Pipeline</td>\n'
    '<td>KV-cache + operator fusion + INT8 + continuous batching -> 63% P99 reduction, 2.4x throughput</td></tr>\n'
    '<tr><td style="padding:6px 12px;">[ ]</td><td>Story 2: Distributed Training</td>\n'
    '<td>FSDP + mixed precision + gradient checkpointing -> 6.7x speedup, 84% scaling efficiency on 8 GPUs</td></tr>\n'
    '<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>Story 3: Data Quality + DPO</td>\n'
    '<td>Preference pipeline + reward model + DPO -> +18% satisfaction, 3x cheaper than RLHF</td></tr>\n'
    '<tr><td style="padding:6px 12px;">[ ]</td><td>Opening Template</td>\n'
    '<td>30-second elevator pitch: background, current focus, why Adobe. Practice it smooth</td></tr>\n'
    '<tr style="background:#222;"><td style="padding:6px 12px;">[ ]</td><td>Handling Unknowns</td>\n'
    '<td>3 options: reason from first principles, relate to known concept, say "I\'d look into X because Y"</td></tr>\n'
    '</table>\n'
    '</div>'
)

# -- Concept Map --
CONCEPT_MAP_DIAGRAM = (
    '<div style="background:#0d1117; padding:24px; border-radius:12px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0; overflow-x:auto;">\n'
    '<div style="text-align:center; font-size:16px; font-weight:bold; color:#fff; '
    'margin-bottom:20px;">\n'
    'Adobe ML Interview Concept Map\n'
    '</div>\n'
    '\n'
    '<pre style="color:#e0e0e0; font-size:12px; line-height:1.6; text-align:center;">\n'
    '                          +-------------------+\n'
    '                          |   DIFFUSION (D1)  |\n'
    '                          |  DDPM / CFG / LDM |\n'
    '                          +--------+----------+\n'
    '                                   |\n'
    '                    +--------------+--------------+\n'
    '                    |                             |\n'
    '                    v                             v\n'
    '          +-----------------+           +------------------+\n'
    '          | VIDEO GEN (D4)  |           | LATENT SPACE     |\n'
    '          | 3D VAE + DiT    |           | VAE compression  |\n'
    '          | Temporal attn   |           | 8x downsample    |\n'
    '          +--------+--------+           +--------+---------+\n'
    '                   |                             |\n'
    '                   |    +------------------------+\n'
    '                   |    |\n'
    '                   v    v\n'
    '          +-----------------+           +------------------+\n'
    '          | INFERENCE (D5)  |<--------->| DISTRIBUTED (D3) |\n'
    '          | FlashAttn, KV   |  train    | DP / TP / PP     |\n'
    '          | Quant, vLLM     |  vs serve | FSDP / ZeRO      |\n'
    '          +--------+--------+           +--------+---------+\n'
    '                   |                             |\n'
    '                   |         +---------+         |\n'
    '                   +-------->| MEMORY  |<--------+\n'
    '                             | MGMT    |\n'
    '                             +---------+\n'
    '                             | Train: 16P/N    |\n'
    '                             | Serve: KV-cache  |\n'
    '                             | Both: activation |\n'
    '                             +--------+---------+\n'
    '                                      |\n'
    '                   +------------------+------------------+\n'
    '                   |                                     |\n'
    '                   v                                     v\n'
    '          +-----------------+           +------------------+\n'
    '          | ROPE / PE (D4)  |           | ALIGNMENT (D2)   |\n'
    '          | theta_i formula |           | RLHF / DPO       |\n'
    '          | PI / NTK / YaRN |           | Distillation      |\n'
    '          +--------+--------+           +--------+---------+\n'
    '                   |                             |\n'
    '                   +----------+    +-------------+\n'
    '                              |    |\n'
    '                              v    v\n'
    '                    +-------------------+\n'
    '                    | LONG CONTEXT (D4) |\n'
    '                    | RoPE extension    |\n'
    '                    | KV-cache growth   |\n'
    '                    | FlashAttn needed  |\n'
    '                    +-------------------+\n'
    '</pre>\n'
    '\n'
    '<div style="margin-top:16px; padding:12px; background:#1a1a2e; border-radius:8px;">\n'
    '<div style="font-weight:bold; color:#4a90d9; margin-bottom:8px;">Key Cross-Topic Connections</div>\n'
    '<table style="border-collapse:collapse; color:#e0e0e0; font-size:12px; width:100%;">\n'
    '<tr style="border-bottom:1px solid #333;">\n'
    '<th style="padding:6px 10px; text-align:left;">Connection</th>\n'
    '<th style="padding:6px 10px; text-align:left;">Why It Matters</th>\n'
    '</tr>\n'
    '<tr><td style="padding:6px 10px;">Diffusion -> Video Gen</td>\n'
    '<td style="padding:6px 10px;">Video diffusion adds temporal layers to image diffusion (Firefly Image -> Firefly Video)</td></tr>\n'
    '<tr style="background:#222;"><td style="padding:6px 10px;">Latent Space -> Inference</td>\n'
    '<td style="padding:6px 10px;">VAE compression reduces diffusion compute. Same principle: work in compact space</td></tr>\n'
    '<tr><td style="padding:6px 10px;">Inference <-> Distributed</td>\n'
    '<td style="padding:6px 10px;">Training uses TP/PP/FSDP; serving uses TP + KV-cache sharding. Both manage GPU memory</td></tr>\n'
    '<tr style="background:#222;"><td style="padding:6px 10px;">Memory Management (shared)</td>\n'
    '<td style="padding:6px 10px;">Training: 16P bytes/param. Serving: KV-cache dominates. Both: activation checkpointing</td></tr>\n'
    '<tr><td style="padding:6px 10px;">RoPE -> Long Context</td>\n'
    '<td style="padding:6px 10px;">RoPE extension (PI/NTK/YaRN) enables longer sequences, but KV-cache grows linearly</td></tr>\n'
    '<tr style="background:#222;"><td style="padding:6px 10px;">Long Context -> FlashAttention</td>\n'
    '<td style="padding:6px 10px;">Longer sequences make O(N^2) attention critical. FlashAttention makes it feasible</td></tr>\n'
    '<tr><td style="padding:6px 10px;">Alignment -> Distillation</td>\n'
    '<td style="padding:6px 10px;">Aligned large model (teacher) distilled to small model (student). DPO + KD pipeline</td></tr>\n'
    '<tr style="background:#222;"><td style="padding:6px 10px;">DPO -> Project Story 3</td>\n'
    '<td style="padding:6px 10px;">Your data quality project used DPO for alignment -- direct interview connection</td></tr>\n'
    '</table>\n'
    '</div>\n'
    '</div>'
)

# -- Error Correction Cards --
ERROR_CARDS_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<div style="font-size:15px; font-weight:bold; color:#ff6b6b; '
    'margin-bottom:12px;">Error Correction Cards (7 Common Misunderstandings)</div>\n'
    '\n'
    '<div style="margin-bottom:16px; padding:12px; background:#2a1a1a; '
    'border-left:4px solid #ff4444; border-radius:4px;">\n'
    '<div style="color:#ff6b6b; font-weight:bold;">Card 1: "DDPM generates images from random noise in one step"</div>\n'
    '<div style="color:#888; margin:4px 0;">WRONG. DDPM uses T=1000 iterative denoising steps. '
    'Each step removes a small amount of noise.</div>\n'
    '<div style="color:#4a90d9;">CORRECT: x_T (pure noise) -> x_{T-1} -> ... -> x_0 (clean image). '
    'DDIM can reduce to ~50 steps but still iterative.</div>\n'
    '</div>\n'
    '\n'
    '<div style="margin-bottom:16px; padding:12px; background:#2a1a1a; '
    'border-left:4px solid #ff4444; border-radius:4px;">\n'
    '<div style="color:#ff6b6b; font-weight:bold;">Card 2: "DPO eliminates the need for any reference model"</div>\n'
    '<div style="color:#888; margin:4px 0;">WRONG. DPO eliminates the REWARD model, '
    'but still requires a REFERENCE policy (pi_ref).</div>\n'
    '<div style="color:#4a90d9;">CORRECT: DPO loss uses log(pi_theta/pi_ref) for both y_w and y_l. '
    'pi_ref is the SFT checkpoint, frozen during DPO training.</div>\n'
    '</div>\n'
    '\n'
    '<div style="margin-bottom:16px; padding:12px; background:#2a1a1a; '
    'border-left:4px solid #ff4444; border-radius:4px;">\n'
    '<div style="color:#ff6b6b; font-weight:bold;">Card 3: "Tensor Parallelism = Data Parallelism across layers"</div>\n'
    '<div style="color:#888; margin:4px 0;">WRONG. TP splits weight MATRICES within a single layer. '
    'DP replicates the full model and splits DATA.</div>\n'
    '<div style="color:#4a90d9;">CORRECT: TP splits columns/rows of W. DP splits mini-batch. '
    'PP assigns whole layers to different GPUs. FSDP shards parameters.</div>\n'
    '</div>\n'
    '\n'
    '<div style="margin-bottom:16px; padding:12px; background:#2a1a1a; '
    'border-left:4px solid #ff4444; border-radius:4px;">\n'
    '<div style="color:#ff6b6b; font-weight:bold;">Card 4: "RoPE is a learned positional embedding"</div>\n'
    '<div style="color:#888; margin:4px 0;">WRONG. RoPE is deterministic (fixed), not learned. '
    'Angles are computed from position and dimension index.</div>\n'
    '<div style="color:#4a90d9;">CORRECT: theta_i = 1/10000^(2i/d) is a fixed formula. '
    'No learnable parameters. This is what enables length extrapolation via PI/NTK.</div>\n'
    '</div>\n'
    '\n'
    '<div style="margin-bottom:16px; padding:12px; background:#2a1a1a; '
    'border-left:4px solid #ff4444; border-radius:4px;">\n'
    '<div style="color:#ff6b6b; font-weight:bold;">Card 5: "Speculative decoding changes the output distribution"</div>\n'
    '<div style="color:#888; margin:4px 0;">WRONG. Speculative decoding is LOSSLESS -- '
    'the output distribution is identical to the target model.</div>\n'
    '<div style="color:#4a90d9;">CORRECT: Rejection sampling ensures accepted tokens match '
    'the target model\'s distribution exactly. Speed gain comes from parallel verification, not approximation.</div>\n'
    '</div>\n'
    '\n'
    '<div style="margin-bottom:16px; padding:12px; background:#2a1a1a; '
    'border-left:4px solid #ff4444; border-radius:4px;">\n'
    '<div style="color:#ff6b6b; font-weight:bold;">Card 6: "FSDP is the same as Pipeline Parallelism"</div>\n'
    '<div style="color:#888; margin:4px 0;">WRONG. FSDP shards all parameters across GPUs '
    '(any param can be on any GPU). PP assigns whole layers sequentially.</div>\n'
    '<div style="color:#4a90d9;">CORRECT: FSDP = each GPU holds 1/N of every parameter, '
    'all-gathers before compute. PP = GPU 0 has layers 0-3, GPU 1 has layers 4-7, etc. '
    'Different communication patterns.</div>\n'
    '</div>\n'
    '\n'
    '<div style="margin-bottom:16px; padding:12px; background:#2a1a1a; '
    'border-left:4px solid #ff4444; border-radius:4px;">\n'
    '<div style="color:#ff6b6b; font-weight:bold;">Card 7: "FlashAttention reduces the computational complexity of attention"</div>\n'
    '<div style="color:#888; margin:4px 0;">WRONG. FlashAttention does NOT change the O(N^2*d) compute '
    '(same number of FLOPs).</div>\n'
    '<div style="color:#4a90d9;">CORRECT: FlashAttention reduces IO complexity from O(N^2*d + N^2) to '
    'O(N^2*d^2/M) by tiling in SRAM. Same math, fewer memory round-trips. '
    'It is an IO optimization, not a compute optimization.</div>\n'
    '</div>\n'
    '</div>'
)

# -- Daily Time Allocation Table --
TIME_ALLOCATION_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<div style="font-size:15px; font-weight:bold; color:#fff; '
    'margin-bottom:12px;">7-Day Prep Schedule</div>\n'
    '<table style="border-collapse:collapse; color:#e0e0e0; font-size:13px; width:100%;">\n'
    '<tr style="border-bottom:2px solid #444;">\n'
    '<th style="padding:8px 12px; text-align:left;">Day</th>\n'
    '<th style="padding:8px 12px; text-align:left;">Domain</th>\n'
    '<th style="padding:8px 12px; text-align:center;">Study (min)</th>\n'
    '<th style="padding:8px 12px; text-align:center;">Practice (min)</th>\n'
    '<th style="padding:8px 12px; text-align:center;">Total (min)</th>\n'
    '<th style="padding:8px 12px; text-align:left;">Focus</th>\n'
    '</tr>\n'
    '<tr style="background:#333;">\n'
    '<td style="padding:8px 12px;">Day 1</td>\n'
    '<td style="padding:8px 12px;">Diffusion Models</td>\n'
    '<td style="padding:8px 12px; text-align:center;">50</td>\n'
    '<td style="padding:8px 12px; text-align:center;">20</td>\n'
    '<td style="padding:8px 12px; text-align:center;">70</td>\n'
    '<td style="padding:8px 12px;">Formulas, DDPM/DDIM, CFG, Stable Diffusion pipeline</td>\n'
    '</tr>\n'
    '<tr>\n'
    '<td style="padding:8px 12px;">Day 2</td>\n'
    '<td style="padding:8px 12px;">RLHF/DPO + Distill</td>\n'
    '<td style="padding:8px 12px; text-align:center;">45</td>\n'
    '<td style="padding:8px 12px; text-align:center;">15</td>\n'
    '<td style="padding:8px 12px; text-align:center;">60</td>\n'
    '<td style="padding:8px 12px;">3-stage RLHF, DPO loss, comparison, distillation</td>\n'
    '</tr>\n'
    '<tr style="background:#333;">\n'
    '<td style="padding:8px 12px;">Day 3</td>\n'
    '<td style="padding:8px 12px;">Distributed Training</td>\n'
    '<td style="padding:8px 12px; text-align:center;">50</td>\n'
    '<td style="padding:8px 12px; text-align:center;">15</td>\n'
    '<td style="padding:8px 12px; text-align:center;">65</td>\n'
    '<td style="padding:8px 12px;">DP/TP/PP/FSDP, memory math, 3D parallelism</td>\n'
    '</tr>\n'
    '<tr>\n'
    '<td style="padding:8px 12px;">Day 4</td>\n'
    '<td style="padding:8px 12px;">RoPE + Video Gen</td>\n'
    '<td style="padding:8px 12px; text-align:center;">45</td>\n'
    '<td style="padding:8px 12px; text-align:center;">15</td>\n'
    '<td style="padding:8px 12px; text-align:center;">60</td>\n'
    '<td style="padding:8px 12px;">RoPE math, PI/NTK/YaRN, video diffusion, DiT</td>\n'
    '</tr>\n'
    '<tr style="background:#333;">\n'
    '<td style="padding:8px 12px;">Day 5</td>\n'
    '<td style="padding:8px 12px;">Inference Optim</td>\n'
    '<td style="padding:8px 12px; text-align:center;">50</td>\n'
    '<td style="padding:8px 12px; text-align:center;">15</td>\n'
    '<td style="padding:8px 12px; text-align:center;">65</td>\n'
    '<td style="padding:8px 12px;">FlashAttn, quant, KV-cache, PagedAttn, spec decode</td>\n'
    '</tr>\n'
    '<tr>\n'
    '<td style="padding:8px 12px;">Day 6</td>\n'
    '<td style="padding:8px 12px;">Mock Interview</td>\n'
    '<td style="padding:8px 12px; text-align:center;">20</td>\n'
    '<td style="padding:8px 12px; text-align:center;">40</td>\n'
    '<td style="padding:8px 12px; text-align:center;">60</td>\n'
    '<td style="padding:8px 12px;">STAR-T stories, 13 Q&A drill, speech templates</td>\n'
    '</tr>\n'
    '<tr style="background:#333; border-top:2px solid #4a90d9;">\n'
    '<td style="padding:8px 12px; font-weight:bold;">Day 7</td>\n'
    '<td style="padding:8px 12px; font-weight:bold;">Review</td>\n'
    '<td style="padding:8px 12px; text-align:center; font-weight:bold;">30</td>\n'
    '<td style="padding:8px 12px; text-align:center; font-weight:bold;">30</td>\n'
    '<td style="padding:8px 12px; text-align:center; font-weight:bold;">60</td>\n'
    '<td style="padding:8px 12px; font-weight:bold;">This note: checklist, concept map, error cards, formulas</td>\n'
    '</tr>\n'
    '<tr style="border-top:2px solid #666;">\n'
    '<td style="padding:8px 12px;" colspan="2"><b>Total</b></td>\n'
    '<td style="padding:8px 12px; text-align:center;"><b>290</b></td>\n'
    '<td style="padding:8px 12px; text-align:center;"><b>150</b></td>\n'
    '<td style="padding:8px 12px; text-align:center;"><b>440</b></td>\n'
    '<td style="padding:8px 12px;">~7.3 hours total across 7 days</td>\n'
    '</tr>\n'
    '</table>\n'
    '</div>'
)

# -- Formula Cheat Sheet: Diffusion --
FORMULA_SHEET_DIFFUSION = (
    '<div style="margin-bottom:16px; padding:12px; background:#222; border-radius:4px;">\n'
    '<div style="color:#4a90d9; font-weight:bold; margin-bottom:8px;">Diffusion Models</div>\n'
    '<table style="border-collapse:collapse; color:#e0e0e0; font-size:12px; width:100%;">\n'
    '<tr style="border-bottom:1px solid #333;">\n'
    '<td style="padding:6px 10px; color:#888; width:140px;">Forward process</td>\n'
    '<td style="padding:6px 10px;">x_t = sqrt(alpha_bar_t) * x_0 + sqrt(1 - alpha_bar_t) * epsilon, '
    ' epsilon ~ N(0, I)</td>\n'
    '</tr>\n'
    '<tr style="border-bottom:1px solid #333;">\n'
    '<td style="padding:6px 10px; color:#888;">Training loss</td>\n'
    '<td style="padding:6px 10px;">L = E_{t,x_0,epsilon}[ ||epsilon - epsilon_theta(x_t, t)||^2 ]</td>\n'
    '</tr>\n'
    '<tr style="border-bottom:1px solid #333;">\n'
    '<td style="padding:6px 10px; color:#888;">CFG</td>\n'
    '<td style="padding:6px 10px;">epsilon_hat = epsilon_uncond + w * (epsilon_cond - epsilon_uncond), '
    ' w = 7.5 typical</td>\n'
    '</tr>\n'
    '<tr>\n'
    '<td style="padding:6px 10px; color:#888;">VAE compression</td>\n'
    '<td style="padding:6px 10px;">512x512x3 -> 64x64x4 (8x spatial, latent diffusion)</td>\n'
    '</tr>\n'
    '</table>\n'
    '</div>'
)

# -- Formula Cheat Sheet: Alignment --
FORMULA_SHEET_ALIGNMENT = (
    '<div style="margin-bottom:16px; padding:12px; background:#222; border-radius:4px;">\n'
    '<div style="color:#2d6a4f; font-weight:bold; margin-bottom:8px;">Alignment (RLHF / DPO)</div>\n'
    '<table style="border-collapse:collapse; color:#e0e0e0; font-size:12px; width:100%;">\n'
    '<tr style="border-bottom:1px solid #333;">\n'
    '<td style="padding:6px 10px; color:#888; width:140px;">Bradley-Terry</td>\n'
    '<td style="padding:6px 10px;">P(y_w > y_l) = sigma(r_phi(y_w) - r_phi(y_l))</td>\n'
    '</tr>\n'
    '<tr style="border-bottom:1px solid #333;">\n'
    '<td style="padding:6px 10px; color:#888;">DPO loss</td>\n'
    '<td style="padding:6px 10px;">L = -E[log sigma(beta * (log(pi/pi_ref)(y_w) - log(pi/pi_ref)(y_l)))]</td>\n'
    '</tr>\n'
    '<tr style="border-bottom:1px solid #333;">\n'
    '<td style="padding:6px 10px; color:#888;">KD loss</td>\n'
    '<td style="padding:6px 10px;">L_KD = alpha * T^2 * KL(p_teacher^T || p_student^T) + (1 - alpha) * CE(y, p_student)</td>\n'
    '</tr>\n'
    '<tr>\n'
    '<td style="padding:6px 10px; color:#888;">Temperature</td>\n'
    '<td style="padding:6px 10px;">p_i^T = exp(z_i / T) / sum_j(exp(z_j / T))</td>\n'
    '</tr>\n'
    '</table>\n'
    '</div>'
)

# -- Formula Cheat Sheet: Distributed --
FORMULA_SHEET_DISTRIBUTED = (
    '<div style="margin-bottom:16px; padding:12px; background:#222; border-radius:4px;">\n'
    '<div style="color:#d4a017; font-weight:bold; margin-bottom:8px;">Distributed Training</div>\n'
    '<table style="border-collapse:collapse; color:#e0e0e0; font-size:12px; width:100%;">\n'
    '<tr style="border-bottom:1px solid #333;">\n'
    '<td style="padding:6px 10px; color:#888; width:140px;">Memory per param</td>\n'
    '<td style="padding:6px 10px;">16 bytes = 2(fp16 wt) + 2(fp16 grad) + 4(fp32 wt) + 4(momentum) + 4(variance)</td>\n'
    '</tr>\n'
    '<tr style="border-bottom:1px solid #333;">\n'
    '<td style="padding:6px 10px; color:#888;">DDP memory</td>\n'
    '<td style="padding:6px 10px;">16P bytes per GPU (no savings, full replica)</td>\n'
    '</tr>\n'
    '<tr style="border-bottom:1px solid #333;">\n'
    '<td style="padding:6px 10px; color:#888;">FSDP memory</td>\n'
    '<td style="padding:6px 10px;">16P / N bytes per GPU (N = number of GPUs)</td>\n'
    '</tr>\n'
    '<tr style="border-bottom:1px solid #333;">\n'
    '<td style="padding:6px 10px; color:#888;">PP bubble</td>\n'
    '<td style="padding:6px 10px;">(N - 1) / (N + M - 1),  N = stages, M = micro-batches</td>\n'
    '</tr>\n'
    '<tr>\n'
    '<td style="padding:6px 10px; color:#888;">3D layout</td>\n'
    '<td style="padding:6px 10px;">TP(intra-node NVLink) x PP(cross-node) x DP(remaining GPUs)</td>\n'
    '</tr>\n'
    '</table>\n'
    '</div>'
)

# -- Formula Cheat Sheet: RoPE --
FORMULA_SHEET_ROPE = (
    '<div style="margin-bottom:16px; padding:12px; background:#222; border-radius:4px;">\n'
    '<div style="color:#8b5cf6; font-weight:bold; margin-bottom:8px;">RoPE + Long Context</div>\n'
    '<table style="border-collapse:collapse; color:#e0e0e0; font-size:12px; width:100%;">\n'
    '<tr style="border-bottom:1px solid #333;">\n'
    '<td style="padding:6px 10px; color:#888; width:140px;">RoPE angle</td>\n'
    '<td style="padding:6px 10px;">theta_i = 1 / 10000^(2i / d),  rotation by m * theta_i at position m</td>\n'
    '</tr>\n'
    '<tr style="border-bottom:1px solid #333;">\n'
    '<td style="padding:6px 10px; color:#888;">Relative position</td>\n'
    '<td style="padding:6px 10px;">q_m^T k_n depends only on (m - n), not absolute positions</td>\n'
    '</tr>\n'
    '<tr style="border-bottom:1px solid #333;">\n'
    '<td style="padding:6px 10px; color:#888;">Position Interp</td>\n'
    '<td style="padding:6px 10px;">m\' = m * (L_train / L_target)</td>\n'
    '</tr>\n'
    '<tr>\n'
    '<td style="padding:6px 10px; color:#888;">NTK scaling</td>\n'
    '<td style="padding:6px 10px;">theta_i\' = 1 / (b * alpha)^(2i / d),  alpha = L_target / L_train</td>\n'
    '</tr>\n'
    '</table>\n'
    '</div>'
)

# -- Formula Cheat Sheet: Inference --
FORMULA_SHEET_INFERENCE = (
    '<div style="padding:12px; background:#222; border-radius:4px;">\n'
    '<div style="color:#e07a5f; font-weight:bold; margin-bottom:8px;">Inference Optimization</div>\n'
    '<table style="border-collapse:collapse; color:#e0e0e0; font-size:12px; width:100%;">\n'
    '<tr style="border-bottom:1px solid #333;">\n'
    '<td style="padding:6px 10px; color:#888; width:140px;">FlashAttn IO</td>\n'
    '<td style="padding:6px 10px;">O(N^2 * d^2 / M) vs standard O(N^2 * d + N^2),  M = SRAM size</td>\n'
    '</tr>\n'
    '<tr style="border-bottom:1px solid #333;">\n'
    '<td style="padding:6px 10px; color:#888;">KV-cache size</td>\n'
    '<td style="padding:6px 10px;">2 * L * N * H * d bytes per sequence (L=layers, N=seq_len, H=heads, d=head_dim)</td>\n'
    '</tr>\n'
    '<tr style="border-bottom:1px solid #333;">\n'
    '<td style="padding:6px 10px; color:#888;">SRAM vs HBM</td>\n'
    '<td style="padding:6px 10px;">SRAM: ~20 MB, 19 TB/s  |  HBM: ~80 GB, 2 TB/s  (A100)</td>\n'
    '</tr>\n'
    '<tr>\n'
    '<td style="padding:6px 10px; color:#888;">Spec decode</td>\n'
    '<td style="padding:6px 10px;">Draft K tokens, verify in 1 forward pass. Accept rate ~70-80%. Speedup ~2-3x</td>\n'
    '</tr>\n'
    '</table>\n'
    '</div>'
)

# -- Self-Check Questions --
SELF_CHECK_DIAGRAM = (
    '<div style="background:#1a1a2e; padding:20px; border-radius:8px; '
    'margin:16px 0; font-family:monospace; color:#e0e0e0;">\n'
    '<div style="font-size:15px; font-weight:bold; color:#fff; '
    'margin-bottom:12px;">Final Review Self-Check (5 Questions)</div>\n'
    '\n'
    '<div style="margin-bottom:12px; padding:8px 12px; background:#222; border-radius:4px;">\n'
    '<b style="color:#4a90d9;">Q1 (Cross-domain):</b> You\'re serving a Stable Diffusion model at Adobe scale. '
    'Which inference optimizations from Day 5 apply to diffusion models vs autoregressive LLMs? '
    'What is different about KV-cache usage in diffusion vs LLM serving?\n'
    '</div>\n'
    '\n'
    '<div style="margin-bottom:12px; padding:8px 12px; background:#222; border-radius:4px;">\n'
    '<b style="color:#2d6a4f;">Q2 (Formula):</b> Write the DPO loss from memory. Then explain: if beta is too small, '
    'what happens? If beta is too large? How does this relate to the KL constraint in RLHF?\n'
    '</div>\n'
    '\n'
    '<div style="margin-bottom:12px; padding:8px 12px; background:#222; border-radius:4px;">\n'
    '<b style="color:#d4a017;">Q3 (System Design):</b> You need to train a 70B parameter model on 64 A100 80GB GPUs. '
    'Design the parallelism strategy. Show the memory calculation. Explain why you chose each parallelism type.\n'
    '</div>\n'
    '\n'
    '<div style="margin-bottom:12px; padding:8px 12px; background:#222; border-radius:4px;">\n'
    '<b style="color:#8b5cf6;">Q4 (Connection):</b> How does RoPE\'s relative position property help with '
    'FlashAttention\'s tiling? Does the tiling strategy need to change for relative vs absolute position encodings?\n'
    '</div>\n'
    '\n'
    '<div style="margin-bottom:12px; padding:8px 12px; background:#222; border-radius:4px;">\n'
    '<b style="color:#e07a5f;">Q5 (Project Story):</b> Walk through your inference optimization project using STAR-T. '
    'Keep it under 2 minutes. Include specific numbers and bridge to Adobe Firefly serving at the end.\n'
    '</div>\n'
    '</div>'
)

# -- Quick Reference Card --
QUICK_REFERENCE_DIAGRAM = (
    '<pre style="background:#111; padding:12px; border-radius:4px; color:#ccc; font-size:13px;">\n'
    'DIFFUSION:  x_t = sqrt(a_bar)*x_0 + sqrt(1-a_bar)*eps  |  CFG: w=7.5  |  T=1000\n'
    'ALIGNMENT:  RLHF = SFT+RM+PPO  |  DPO = no reward model, yes ref model  |  beta=0.1-0.5\n'
    'DISTRIBUTED: DDP=16P  |  FSDP=16P/N  |  TP=intra-node  |  PP bubble=(N-1)/(N+M-1)\n'
    'ROPE:       theta=1/10000^(2i/d)  |  fixed, not learned  |  PI: scale m  |  NTK: scale base\n'
    'INFERENCE:  FlashAttn=IO opt  |  KV=2LNHd  |  SpecDec=lossless  |  PagedAttn=virtual mem\n'
    'STORIES:    Inference(63% P99)  |  DistTrain(6.7x)  |  DPO(+18% sat)  |  STAR-T ~2min\n'
    'TOTAL PREP: 440 minutes across 7 days (290 study + 150 practice)\n'
    '</pre>'
)


def build_day7_note() -> "StudyNoteBuilder":
    """Build the Day 7 Review note using StudyNoteBuilder."""
    builder = StudyNoteBuilder()

    builder.set_title(
        "Review Checklist + Concept Map + Error Cards (Adobe Prep Day 7)"
    )

    # -- Prerequisites --
    builder.add_prerequisites([
        "Day 1: Diffusion Models Deep-Dive (DDPM, DDIM, CFG, Latent Diffusion, Score-Based/SDE)",
        "Day 2: RLHF/DPO Alignment + LLM Distillation (Bradley-Terry, PPO, DPO, KD loss)",
        "Day 3: Distributed Training (DP, TP, PP, FSDP/ZeRO, 3D parallelism, memory math)",
        "Day 4: RoPE + Long Context + Video Generation (PI, NTK-aware scaling, YaRN, DiT)",
        "Day 5: Inference Optimization (FlashAttention, GPTQ, AWQ, KV-cache, PagedAttention, speculative decoding)",
        "Day 6: Mock Interview Questions + STAR-T Project Stories (13 Q&A, speech templates)",
    ])

    # -- Term Registry --
    builder.add_term("DDPM", "Denoising Diffusion Probabilistic Model",
                     "Generates data by learning to reverse a noise process over T=1000 steps")
    builder.add_term("DDIM", "Denoising Diffusion Implicit Model",
                     "Deterministic sampler for diffusion models, enables ~50-step generation")
    builder.add_term("CFG", "Classifier-Free Guidance",
                     "Steers diffusion toward a condition by interpolating conditioned/unconditioned predictions")
    builder.add_term("LDM", "Latent Diffusion Model",
                     "Runs diffusion in compressed latent space (VAE: 512x512x3 -> 64x64x4)")
    builder.add_term("RLHF", "Reinforcement Learning from Human Feedback",
                     "3-stage alignment: SFT -> Reward Model -> PPO policy optimization")
    builder.add_term("DPO", "Direct Preference Optimization",
                     "Aligns models using preference pairs without a separate reward model")
    builder.add_term("PPO", "Proximal Policy Optimization",
                     "RL algorithm used in RLHF to optimize policy with KL constraint")
    builder.add_term("FSDP", "Fully Sharded Data Parallelism",
                     "Shards parameters, gradients, and optimizer states across GPUs (ZeRO Stage 3)")
    builder.add_term("TP", "Tensor Parallelism",
                     "Splits weight matrices within a layer across GPUs (requires NVLink)")
    builder.add_term("PP", "Pipeline Parallelism",
                     "Assigns layers to GPUs sequentially; bubble fraction = (N-1)/(N+M-1)")
    builder.add_term("RoPE", "Rotary Position Embedding",
                     "Fixed (not learned) positional encoding via rotation; enables relative position")
    builder.add_term("FlashAttention", "IO-Aware Exact Attention",
                     "Tiled attention in SRAM avoiding N x N materialization in HBM")
    builder.add_term("GPTQ", "Generative Pre-trained Transformer Quantization",
                     "Post-training INT4 weight quantization using Hessian-based error compensation")
    builder.add_term("AWQ", "Activation-Aware Weight Quantization",
                     "Protects salient weight channels based on activation magnitudes")
    builder.add_term("KV-cache", "Key-Value Cache",
                     "Stores computed K/V tensors; size = 2*L*N*H*d bytes per sequence")
    builder.add_term("DiT", "Diffusion Transformer",
                     "Replaces U-Net with transformer backbone using AdaLN-Zero conditioning")
    builder.add_term("YaRN", "Yet another RoPE extensioN",
                     "Per-dimension PI/NTK blend + attention temperature for large context extension")
    builder.add_term("STAR-T", "Situation-Task-Approach-Result-Transfer",
                     "Extended STAR framework with Transfer step to bridge experience to target role")
    builder.add_term("SmoothQuant", "Smooth Quantization",
                     "Migrates quantization difficulty from activations to weights for W8A8")
    builder.add_term("PagedAttention", "Virtual-Memory KV-Cache Management",
                     "Block-based KV-cache allocation eliminating fragmentation; copy-on-write for beam search")

    # -- Section 1: Master Review Checklist --
    builder.add_section("1. Master Review Checklist", [
        "Use this checklist on the morning of the interview. Check each box when "
        "you can explain the concept from memory, including the key formula. "
        "Final review day consolidates all 6 previous days into actionable items.",
    ])

    builder.add_section("Domain 1: Diffusion Models (Day 1)", [])
    builder.add_diagram_html(CHECKLIST_DIFFUSION)

    builder.add_section("Domain 2: RLHF/DPO Alignment + Distillation (Day 2)", [])
    builder.add_diagram_html(CHECKLIST_ALIGNMENT)

    builder.add_section("Domain 3: Distributed Training (Day 3)", [])
    builder.add_diagram_html(CHECKLIST_DISTRIBUTED)

    builder.add_section("Domain 4: RoPE + Long Context + Video Generation (Day 4)", [])
    builder.add_diagram_html(CHECKLIST_ROPE_VIDEO)

    builder.add_section("Domain 5: Inference Optimization (Day 5)", [])
    builder.add_diagram_html(CHECKLIST_INFERENCE)

    builder.add_section("Domain 6: Interview Skills (Day 6)", [])
    builder.add_diagram_html(CHECKLIST_INTERVIEW)

    # -- Section 2: Concept Map --
    builder.add_section("2. Concept Map: Cross-Topic Connections", [
        "This map shows how topics from all 6 days interconnect. Follow the arrows "
        "to see how mastering one topic strengthens understanding of related ones. "
        "Cross-references: Day 1 diffusion -> Day 4 video, Day 3 distributed <-> Day 5 inference, "
        "Day 4 RoPE -> Day 5 FlashAttention (long context), Day 2 DPO -> Day 6 Story 3.",
    ])
    builder.add_diagram_html(CONCEPT_MAP_DIAGRAM)

    # -- Section 3: Error Correction Cards --
    builder.add_section("3. Error Correction Quick-Reference Cards", [
        "These are the most common misunderstandings, compiled from all 6 days. "
        "Review each card and make sure you would NOT make these mistakes in an interview. "
        "Cross-references: Card 1 -> Day 1 (DDPM), Card 2 -> Day 2 (DPO), "
        "Card 3 -> Day 3 (TP vs DP), Card 4 -> Day 4 (RoPE), Card 5 -> Day 5 (speculative decoding), "
        "Card 6 -> Day 3 (FSDP vs PP), Card 7 -> Day 5 (FlashAttention).",
    ])
    builder.add_diagram_html(ERROR_CARDS_DIAGRAM)

    # -- Section 4: Daily Time Allocation --
    builder.add_section("4. Daily Time Allocation Table", [
        "Suggested time allocation for a 7-day prep cycle. Use this to calibrate "
        "how much time to spend on each domain during the final review.",
    ])
    builder.add_diagram_html(TIME_ALLOCATION_DIAGRAM)

    # -- Section 5: Formula Cheat Sheet --
    builder.add_section("5. Formula Cheat Sheet", [
        "All key formulas consolidated in one place. Practice writing each from memory. "
        "Cross-references provided per domain.",
    ])

    builder.add_section("Diffusion Models Formulas (Day 1)", [
        FormulaBlock(
            latex=r"x_t = \sqrt{\bar\alpha_t}\, x_0 + \sqrt{1 - \bar\alpha_t}\, \epsilon, "
                  r"\quad \epsilon \sim \mathcal{N}(0, \mathbf{I})",
            explanation="DDPM forward (closed-form jump to timestep t):",
        ),
        FormulaBlock(
            latex=r"\mathcal{L} = \mathbb{E}_{t, x_0, \epsilon}\!\left[\|\epsilon - \epsilon_\theta(x_t, t)\|^2\right]",
            explanation="DDPM training loss (simplified noise-prediction):",
        ),
        FormulaBlock(
            latex=r"\hat\epsilon = \epsilon_{\text{uncond}} + w \cdot (\epsilon_{\text{cond}} - \epsilon_{\text{uncond}})",
            explanation="Classifier-Free Guidance (typical w = 7.5):",
        ),
    ])
    builder.add_diagram_html(FORMULA_SHEET_DIFFUSION)

    builder.add_section("Alignment Formulas (Day 2)", [
        FormulaBlock(
            latex=r"P(y_w \succ y_l) = \sigma\bigl(r_\phi(y_w) - r_\phi(y_l)\bigr)",
            explanation="Bradley-Terry preference model:",
        ),
        FormulaBlock(
            latex=r"\mathcal{L}_{\text{DPO}} = -\mathbb{E}\!\left[\log \sigma\!\left("
                  r"\beta \log \frac{\pi(y_w)}{\pi_{\text{ref}}(y_w)} "
                  r"- \beta \log \frac{\pi(y_l)}{\pi_{\text{ref}}(y_l)}\right)\right]",
            explanation="DPO loss (directly optimizes policy without reward model):",
        ),
        FormulaBlock(
            latex=r"L_{\text{KD}} = \alpha \cdot T^2 \cdot \text{KL}(p_{\text{teacher}}^T \| p_{\text{student}}^T) "
                  r"+ (1 - \alpha) \cdot \text{CE}(y, p_{\text{student}})",
            explanation="Knowledge distillation loss (higher T = softer distribution):",
        ),
    ])
    builder.add_diagram_html(FORMULA_SHEET_ALIGNMENT)

    builder.add_section("Distributed Training Formulas (Day 3)", [
        FormulaBlock(
            latex=r"\text{Memory/param} = 2\,(\text{fp16 wt}) + 2\,(\text{fp16 grad}) "
                  r"+ 4\,(\text{fp32 wt}) + 4\,(\text{mom}) + 4\,(\text{var}) = 16\;\text{bytes}",
            explanation="Per-parameter memory with Adam optimizer and mixed precision:",
        ),
        FormulaBlock(
            latex=r"\text{FSDP memory/GPU} = \frac{16P}{N}",
            explanation="FSDP (ZeRO-3) per-GPU memory (N = number of GPUs, P = parameter count):",
        ),
        FormulaBlock(
            latex=r"\text{Bubble fraction} = \frac{N - 1}{N + M - 1}",
            explanation="Pipeline parallelism bubble overhead (N = stages, M = micro-batches):",
        ),
    ])
    builder.add_diagram_html(FORMULA_SHEET_DISTRIBUTED)

    builder.add_section("RoPE + Long Context Formulas (Day 4)", [
        FormulaBlock(
            latex=r"\theta_i = \frac{1}{10000^{2i/d}}",
            explanation="RoPE base frequency (rotation by m * theta_i at position m):",
        ),
        FormulaBlock(
            latex=r"m' = m \cdot \frac{L_{\text{train}}}{L_{\text{target}}}",
            explanation="Position Interpolation (PI) -- scale position index:",
        ),
        FormulaBlock(
            latex=r"\theta_i' = \frac{1}{(b \cdot \alpha)^{2i/d}}, \quad \alpha = \frac{L_{\text{target}}}{L_{\text{train}}}",
            explanation="NTK-Aware RoPE scaling -- scale base frequency:",
        ),
    ])
    builder.add_diagram_html(FORMULA_SHEET_ROPE)

    builder.add_section("Inference Optimization Formulas (Day 5)", [
        FormulaBlock(
            latex=r"\text{IO}_{\text{flash}} = O\!\left(\frac{N^2 d^2}{M}\right) "
                  r"\quad\text{vs}\quad \text{IO}_{\text{standard}} = O(N^2 d + N^2)",
            explanation="FlashAttention IO complexity (M = SRAM size):",
        ),
        FormulaBlock(
            latex=r"\text{KV-cache} = 2 \cdot L \cdot N \cdot H \cdot d \;\text{bytes/seq}",
            explanation="KV-cache size (L=layers, N=seq_len, H=heads, d=head_dim):",
        ),
        FormulaBlock(
            latex=r"P(\text{accept}) = \min\!\left(1,\, \frac{P_{\text{target}}(x)}{P_{\text{draft}}(x)}\right)",
            explanation="Speculative decoding acceptance probability (rejection sampling, lossless):",
        ),
    ])
    builder.add_diagram_html(FORMULA_SHEET_INFERENCE)

    # -- Self-Check Questions --
    builder.add_section("Self-Check Questions", [
        "Answer these without looking at the notes. If you struggle with any, "
        "go back to the relevant day's note. Cross-references are provided for each question.",
    ])
    builder.add_diagram_html(SELF_CHECK_DIAGRAM)

    builder.add_checklist("Self-Check Tracker", [
        "Q1: Cross-domain inference analysis (Stable Diffusion vs LLM serving). "
        "(Cross-ref: Day 1 diffusion + Day 5 inference)",
        "Q2: Write DPO loss from memory; explain beta sensitivity and KL constraint. "
        "(Cross-ref: Day 2 alignment)",
        "Q3: Design 70B training on 64 A100s with memory calculation. "
        "(Cross-ref: Day 3 distributed training)",
        "Q4: RoPE relative position + FlashAttention tiling interaction. "
        "(Cross-ref: Day 4 RoPE + Day 5 FlashAttention)",
        "Q5: STAR-T walkthrough of inference optimization project under 2 minutes. "
        "(Cross-ref: Day 6 Story 1 + Day 5 inference)",
    ])

    # -- Quick Reference Card --
    builder.add_section("Quick Reference Card", [
        "One-line summaries per domain for last-minute review before the interview.",
    ])
    builder.add_diagram_html(QUICK_REFERENCE_DIAGRAM)

    return builder


def main() -> None:
    """Build and save Day 7 note to database."""
    import sqlite3

    db_path = Path(__file__).resolve().parent.parent / "data" / "mle_prep.db"
    if not db_path.exists():
        print(f"[FAIL] Database not found: {db_path}")
        sys.exit(1)

    conn = sqlite3.connect(str(db_path))

    # Check Adobe exists
    row = conn.execute(
        "SELECT id FROM companies WHERE id = ?", (COMPANY_ID,)
    ).fetchone()
    if not row:
        print(f"[FAIL] Company id={COMPANY_ID} not found in DB")
        conn.close()
        sys.exit(1)

    # Delete old version if present (idempotent rewrite)
    old = conn.execute(
        "SELECT id FROM company_documents WHERE company_id = ? AND title = ?",
        (COMPANY_ID, DOC_TITLE),
    ).fetchone()
    if old:
        conn.execute("DELETE FROM company_documents WHERE id = ?", (old[0],))
        conn.commit()
        print(f"[INFO] Deleted old document id={old[0]}: {DOC_TITLE}")

    # Build and insert new version
    builder = build_day7_note()
    content = builder.build()

    conn.execute(
        "INSERT INTO company_documents (company_id, title, content, source_type) "
        "VALUES (?, ?, ?, ?)",
        (COMPANY_ID, DOC_TITLE, content, "manual"),
    )
    conn.commit()

    # Verify
    doc = conn.execute(
        "SELECT id, length(content) FROM company_documents WHERE company_id = ? AND title = ?",
        (COMPANY_ID, DOC_TITLE),
    ).fetchone()
    print(
        f"[DONE] Inserted document id={doc[0]}, "
        f"title='{DOC_TITLE}', content_length={doc[1]} chars"
    )

    # Validate
    warnings = StudyNoteBuilder.validate(content)
    if warnings:
        for w in warnings:
            print(f"[WARN] {w}")
    else:
        print("[DONE] 0 validation warnings")

    # Print stats
    section_count = content.count("\n## ")
    html_count = content.count("<div ")
    term_count = len(builder._terms)
    print(f"[INFO] {section_count} sections, {html_count} HTML blocks, "
          f"{term_count} terms, {len(content)} chars")

    conn.close()


if __name__ == "__main__":
    main()
