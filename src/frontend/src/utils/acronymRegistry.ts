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
  topicAnchorId: string;
  entries: AcronymEntry[];
}

export const acronymRegistry: AcronymGroup[] = [
  {
    topic: "Diffusion Models",
    topicAnchorId: "diffusion-models-深度指南-adobe-prep-day-1",
    entries: [
      { abbr: "DDPM", full: "Denoising Diffusion Probabilistic Models", anchorId: "采样算法-ddpm-denoising-diffusion-probabilistic-models" },
      { abbr: "DDIM", full: "Denoising Diffusion Implicit Models", anchorId: "10-ddim-denoising-diffusion-implicit-models-与-sde-统一框架" },
      { abbr: "CFG", full: "Classifier-Free Guidance", anchorId: "7-classifier-free-guidance-cfg" },
      { abbr: "VAE", full: "Variational Autoencoder", anchorId: "14-vae-深度解析-stable-diffusion-的潜在空间引擎" },
      { abbr: "ControlNet", full: "Zero-Conv Conditional Control", anchorId: "9-controlnet-zero-convolution-conditional-control-的设计哲学" },
      { abbr: "IP-Adapter", full: "Image Prompt Adapter", anchorId: "155-ip-adapter-image-prompt-adapter-图像作为-prompt" },
    ],
  },
  {
    topic: "Alignment & Distillation",
    topicAnchorId: "rlhf-dpo-alignment-llm-distillation-adobe-prep-day-2",
    entries: [
      { abbr: "RLHF", full: "Reinforcement Learning from Human Feedback", anchorId: "1-rlhf-reinforcement-learning-from-human-feedback-三阶段-pipeline" },
      { abbr: "SFT", full: "Supervised Fine-Tuning", anchorId: "stage-1-supervised-fine-tuning-sft" },
      { abbr: "PPO", full: "Proximal Policy Optimization", anchorId: "stage-3-ppo-proximal-policy-optimization" },
      { abbr: "DPO", full: "Direct Preference Optimization", anchorId: "2-dpo-direct-preference-optimization-直接偏好优化" },
      { abbr: "KTO", full: "Kahneman-Tversky Optimization", anchorId: "dpo-变体" },
      { abbr: "GRPO", full: "Group Relative Policy Optimization", anchorId: "rlhf-变体" },
    ],
  },
  {
    topic: "Distributed Training",
    topicAnchorId: "distributed-training-dp-tp-pp-fsdp-adobe-prep-day-3",
    entries: [
      { abbr: "DP/DDP", full: "Data Parallel / Distributed DP", anchorId: "4-dp-data-parallelism-数据并行" },
      { abbr: "TP", full: "Tensor Parallelism", anchorId: "5-tp-tensor-parallelism-张量并行" },
      { abbr: "PP", full: "Pipeline Parallelism", anchorId: "6-pp-pipeline-parallelism-流水线并行" },
      { abbr: "FSDP", full: "Fully Sharded Data Parallel", anchorId: "7-fsdp-fully-sharded-data-parallel-zero-zero-redundancy-optimizer" },
      { abbr: "ZeRO", full: "Zero Redundancy Optimizer", anchorId: "zero-zero-redundancy-optimizer-three-stages" },
    ],
  },
  {
    topic: "Position & Video",
    topicAnchorId: "rope-长上下文扩展-视频生成-面试复习笔记",
    entries: [
      { abbr: "RoPE", full: "Rotary Position Embedding", anchorId: "2-rope-rotary-position-embedding旋转位置编码" },
      { abbr: "PI", full: "Position Interpolation", anchorId: "41-position-interpolation-pi-压缩所有位置" },
      { abbr: "NTK", full: "Neural Tangent Kernel Scaling", anchorId: "42-ntk-aware-scaling-只拉伸低频" },
      { abbr: "YaRN", full: "Yet another RoPE extensioN", anchorId: "43-yarn-分维度精细处理-调温度" },
      { abbr: "DiT", full: "Diffusion Transformer (Sora)", anchorId: "54-ditdiffusion-transformersora-架构" },
      { abbr: "ALiBi", full: "Attention with Linear Biases", anchorId: "rope-vs-sinusoidal-的本质区别" },
    ],
  },
  {
    topic: "Inference Optimization",
    topicAnchorId: "一flashattention-io-aware-tiling-attention",
    entries: [
      { abbr: "FlashAttention", full: "IO-Aware Tiling Attention", anchorId: "一flashattention-io-aware-tiling-attention" },
      { abbr: "GPTQ", full: "Hessian-Based Post-Training Quantization", anchorId: "24-gptq-hessian-based-post-training-quantization-基于-hessian-的量化" },
      { abbr: "AWQ", full: "Activation-Aware Weight Quantization", anchorId: "23-awq-activation-aware-weight-quantization-激活感知权重量化" },
      { abbr: "SmoothQuant", full: "W8A8 Smooth Quantization", anchorId: "26-smoothquant-w8a8-smooth-quantization" },
      { abbr: "KV-Cache", full: "Key-Value Cache", anchorId: "31-kv-cache" },
      { abbr: "PagedAttention", full: "Paged Attention (vLLM)", anchorId: "33-pagedattention-paged-attention-vllm" },
      { abbr: "Spec. Decoding", full: "Speculative Decoding (Lossless)", anchorId: "35-speculative-decoding-投机解码-lossless" },
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
      { abbr: "CLIP", full: "Contrastive Language-Image Pre-training", anchorId: "b-multimodal-ai-clip-llava" },
      { abbr: "LLaVA", full: "Large Language and Vision Assistant", anchorId: "b2-llava-large-language-and-vision-assistant-架构" },
      { abbr: "LoRA", full: "Low-Rank Adaptation", anchorId: "c-lora-low-rank-adaptation-qlora-quantized-lora" },
      { abbr: "QLoRA", full: "Quantized LoRA", anchorId: "c-lora-low-rank-adaptation-qlora-quantized-lora" },
      { abbr: "AdamW", full: "Decoupled Weight Decay Adam", anchorId: "e2-adam-vs-adamw-decoupled-weight-decay" },
      { abbr: "GAN", full: "Generative Adversarial Network", anchorId: "f-gan-generative-adversarial-network-相关" },
      { abbr: "BPE", full: "Byte Pair Encoding", anchorId: "a-transformer-基础" },
    ],
  },
  {
    topic: "Core Concepts (Day 8)",
    topicAnchorId: "扩散模型与深度学习核心概念精要",
    entries: [
      { abbr: "UNet", full: "SD Denoising Backbone (860M)", anchorId: "一unet-在-stable-diffusion-中的角色与架构细节" },
      { abbr: "MQA/GQA", full: "Multi/Grouped Query Attention", anchorId: "八mqa-与-gqa" },
      { abbr: "V-Pred", full: "Velocity Prediction Parameterization", anchorId: "九v-prediction" },
      { abbr: "LPIPS", full: "Learned Perceptual Image Patch Similarity", anchorId: "四stable-diffusion-的-vae极端侧重重建" },
      { abbr: "PatchGAN", full: "Patch Discriminator for VAE", anchorId: "四stable-diffusion-的-vae极端侧重重建" },
      { abbr: "Score/SDE", full: "Score Function + SDE Framework", anchorId: "七score-functionsde-与统一框架" },
    ],
  },
];
