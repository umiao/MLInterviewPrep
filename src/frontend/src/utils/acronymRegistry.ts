/**
 * Curated acronym registry for the Adobe MLE Prep all-in-one document.
 * Each entry has: abbreviation, full name, and anchor ID for navigation.
 * Grouped by topic (matching Day 1-7 structure).
 */

export interface AcronymEntry {
  abbr: string;
  full: string;
  anchorId: string;
}

export interface AcronymGroup {
  topic: string;
  /** Anchor ID for the topic's main heading (Day start) */
  topicAnchorId: string;
  entries: AcronymEntry[];
}

export const acronymRegistry: AcronymGroup[] = [
  {
    topic: "Diffusion Models",
    topicAnchorId: "diffusion-models-深度指南-adobe-prep-day-1",
    entries: [
      { abbr: "DDPM", full: "Denoising Diffusion Probabilistic Models", anchorId: "采样算法-ddpm" },
      { abbr: "DDIM", full: "Denoising Diffusion Implicit Models", anchorId: "10-ddim-与-sde-统一框架" },
      { abbr: "CFG", full: "Classifier-Free Guidance", anchorId: "7-classifier-free-guidance-cfg" },
      { abbr: "VAE", full: "Variational Autoencoder", anchorId: "14-vae-深度解析-stable-diffusion-的潜在空间引擎" },
      { abbr: "ControlNet", full: "Zero-Conv Conditional Control", anchorId: "9-controlnet-的-zero-convolution-设计哲学" },
      { abbr: "IP-Adapter", full: "Image Prompt Adapter", anchorId: "155-ip-adapter-图像作为-prompt" },
    ],
  },
  {
    topic: "Alignment & Distillation",
    topicAnchorId: "rlhf-dpo-alignment-llm-distillation-adobe-prep-day-2",
    entries: [
      { abbr: "RLHF", full: "Reinforcement Learning from Human Feedback", anchorId: "1-rlhf-三阶段-pipeline" },
      { abbr: "SFT", full: "Supervised Fine-Tuning", anchorId: "stage-1-supervised-fine-tuning-sft" },
      { abbr: "PPO", full: "Proximal Policy Optimization", anchorId: "stage-3-ppo-optimization" },
      { abbr: "DPO", full: "Direct Preference Optimization", anchorId: "2-dpo-direct-preference-optimization" },
      { abbr: "KTO", full: "Kahneman-Tversky Optimization", anchorId: "dpo-变体" },
      { abbr: "GRPO", full: "Group Relative Policy Optimization", anchorId: "rlhf-变体" },
    ],
  },
  {
    topic: "Distributed Training",
    topicAnchorId: "distributed-training-dp-tp-pp-fsdp-adobe-prep-day-3",
    entries: [
      { abbr: "DP/DDP", full: "Data Parallel / Distributed DP", anchorId: "4-data-parallelism-dp" },
      { abbr: "TP", full: "Tensor Parallelism", anchorId: "5-tensor-parallelism-tp" },
      { abbr: "PP", full: "Pipeline Parallelism", anchorId: "6-pipeline-parallelism-pp" },
      { abbr: "FSDP", full: "Fully Sharded Data Parallel", anchorId: "7-fsdp-zero" },
      { abbr: "ZeRO", full: "Zero Redundancy Optimizer", anchorId: "zero-three-stages" },
    ],
  },
  {
    topic: "Position & Video",
    topicAnchorId: "rope-长上下文扩展-视频生成-面试复习笔记",
    entries: [
      { abbr: "RoPE", full: "Rotary Position Embedding", anchorId: "2-rope旋转位置编码" },
      { abbr: "PI", full: "Position Interpolation", anchorId: "41-position-interpolation-pi-压缩所有位置" },
      { abbr: "NTK", full: "Neural Tangent Kernel Scaling", anchorId: "42-ntk-aware-scaling-只拉伸低频" },
      { abbr: "YaRN", full: "Yet another RoPE extensioN", anchorId: "43-yarn-分维度精细处理-调温度" },
      { abbr: "DiT", full: "Diffusion Transformer (Sora)", anchorId: "54-ditdiffusion-transformersora-架构" },
      { abbr: "ALiBi", full: "Attention with Linear Biases", anchorId: "rope-vs-sinusoidal-的本质区别" },
      { abbr: "AdaLN", full: "Adaptive Layer Normalization", anchorId: "54-ditdiffusion-transformersora-架构" },
    ],
  },
  {
    topic: "Inference Optimization",
    topicAnchorId: "一flashattention",
    entries: [
      { abbr: "FlashAttention", full: "IO-Aware Tiling Attention", anchorId: "一flashattention" },
      { abbr: "HBM/SRAM", full: "GPU Memory Hierarchy", anchorId: "13-flashattention-算法tiling分块" },
      { abbr: "GPTQ", full: "Hessian-Based Post-Training Quantization", anchorId: "24-gptq基于-hessian-的量化" },
      { abbr: "AWQ", full: "Activation-Aware Weight Quantization", anchorId: "23-awq激活感知权重量化" },
      { abbr: "SmoothQuant", full: "W8A8 Smooth Quantization", anchorId: "26-smoothquantw8a8-量化" },
      { abbr: "KV-Cache", full: "Key-Value Cache", anchorId: "12-kv-cache-自回归推理加速的核心" },
      { abbr: "PagedAttention", full: "vLLM Paged KV-Cache", anchorId: "33-pagedattentionvllm" },
      { abbr: "Spec. Decoding", full: "Speculative Decoding (Lossless)", anchorId: "35-speculative-decoding投机解码" },
    ],
  },
  {
    topic: "Interview & STAR-T",
    topicAnchorId: "一star-t-面试框架-三个项目故事",
    entries: [
      { abbr: "STAR-T", full: "Situation-Task-Action-Result-Transfer", anchorId: "一star-t-面试框架-三个项目故事" },
    ],
  },
  {
    topic: "Gap Supplement",
    topicAnchorId: "a-transformer-基础",
    entries: [
      { abbr: "CLIP", full: "Contrastive Language-Image Pre-training", anchorId: "b-multimodal-ai" },
      { abbr: "LLaVA", full: "Large Language and Vision Assistant", anchorId: "b-multimodal-ai" },
      { abbr: "LoRA", full: "Low-Rank Adaptation", anchorId: "c-lora-qlora" },
      { abbr: "QLoRA", full: "Quantized LoRA", anchorId: "c-lora-qlora" },
      { abbr: "AdamW", full: "Decoupled Weight Decay Adam", anchorId: "e-general-ml-基础" },
      { abbr: "GAN", full: "Generative Adversarial Network", anchorId: "f-gan-相关" },
      { abbr: "BPE", full: "Byte Pair Encoding", anchorId: "a-transformer-基础" },
    ],
  },
];
