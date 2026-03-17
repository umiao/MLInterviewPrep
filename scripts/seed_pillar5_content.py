"""Seed Pillar 5 (ML Infrastructure & MLOps) framework node descriptions.

Usage:
    python scripts/seed_pillar5_content.py

Populates the `description` field for all 15 Pillar 5 leaf nodes
in the framework_nodes table. Idempotent -- overwrites existing content.
"""
import sys
from pathlib import Path

# Ensure project root on path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.backend.database import SessionLocal, get_engine  # noqa: E402
from src.backend.models.framework import FrameworkNode  # noqa: E402, F401

# ---------------------------------------------------------------------------
# Content for each leaf topic, keyed by path
# ---------------------------------------------------------------------------

CONTENT: dict[str, str] = {}

# ===== TRAINING INFRASTRUCTURE =====

CONTENT["pillar5.training_infra.distributed_training"] = r"""# Distributed Training

## Overview
Distributed training enables model training across multiple GPUs and nodes, essential for large-scale models that cannot fit in a single device's memory. Senior MLE interviews focus on the trade-offs between parallelism strategies, communication overhead, and fault tolerance in production training pipelines.

## Core Concepts

### Data Parallelism
Each worker holds a full model replica and processes a different data shard. Gradients are synchronized across workers after each backward pass.

**Synchronous SGD**: All workers compute gradients, perform an AllReduce, then update. Effective batch size = per-worker batch x num_workers.

$$
\theta_{t+1} = \theta_t - \eta \cdot \frac{1}{N} \sum_{i=1}^{N} \nabla \mathcal{L}_i(\theta_t)
$$

**Asynchronous SGD**: Workers push gradients independently to a parameter server. Faster but introduces stale gradients, which can hurt convergence.

### Model Parallelism
Split the model across devices when it exceeds single-GPU memory.

**Tensor parallelism**: Split individual layers (e.g., partition weight matrices column-wise or row-wise). Used heavily in Megatron-LM for transformer layers. Requires high-bandwidth interconnect (NVLink).

**Pipeline parallelism**: Split model by layers across stages. Each stage processes a micro-batch, forming a pipeline. GPipe and PipeDream are canonical approaches. Bubble time (idle GPU cycles) is the key inefficiency.

### ZeRO (Zero Redundancy Optimizer)
DeepSpeed's ZeRO partitions optimizer states (Stage 1), gradients (Stage 2), and parameters (Stage 3) across data-parallel ranks, reducing per-GPU memory from $O(1)$ to $O(1/N)$ while maintaining data parallelism semantics.

### Communication Primitives
- **AllReduce**: Sum gradients across all workers. Ring AllReduce has bandwidth cost $O(2(N-1)/N \cdot M)$ where $M$ is message size.
- **AllGather**: Reconstruct full tensors from shards (used in ZeRO Stage 3 forward pass).
- **NCCL**: NVIDIA's collective communication library optimized for GPU topology.

## Implementation

```python
# PyTorch DDP: minimal distributed training setup
import torch
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP

def setup(rank: int, world_size: int) -> None:
    # Initialize distributed process group.
    dist.init_process_group("nccl", rank=rank, world_size=world_size)
    torch.cuda.set_device(rank)

def train(rank: int, world_size: int) -> None:
    # Train loop with DDP.
    setup(rank, world_size)
    model = MyModel().to(rank)
    model = DDP(model, device_ids=[rank])
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    for batch in dataloader:
        loss = model(batch.to(rank))
        loss.backward()  # gradients auto-synced by DDP
        optimizer.step()
        optimizer.zero_grad()
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| DDP (Data Parallel) | Model fits on 1 GPU, need throughput | Linear scaling with gradient sync overhead |
| FSDP / ZeRO | Model barely fits on 1 GPU | Shard optimizer + params across ranks |
| Pipeline Parallel | Very deep models (100+ layers) | Trade bubble time for memory savings |
| Tensor Parallel | Single large layers (huge embeddings) | Needs NVLink-class interconnect |
| 3D Parallelism | LLM pretraining (GPT-3 scale) | Combine data + pipeline + tensor parallel |

### Common Interview Questions
- [ ] How does gradient synchronization work in DDP and what is the communication cost?
- [ ] Compare ZeRO Stage 1/2/3 -- when would you pick each?
- [ ] How do you handle stragglers in synchronous distributed training?
- [ ] What is the difference between pipeline parallelism in GPipe vs PipeDream?
- [ ] How would you scale training from 8 GPUs to 1024 GPUs?

## Comparisons

| Aspect | Data Parallel | Model Parallel | Pipeline Parallel |
|--------|--------------|----------------|-------------------|
| Memory per GPU | Full model | Partial model | Partial model |
| Communication | AllReduce gradients | Point-to-point activations | Inter-stage activations |
| Scaling limit | Batch size / comm | Interconnect bandwidth | Pipeline bubble |
| Complexity | Low (DDP handles it) | High (manual sharding) | Medium (framework support) |

## Key Takeaways
- [ ] DDP is the default starting point; only add model/pipeline parallelism when memory-constrained
- [ ] Communication overhead is the bottleneck -- overlap computation with communication (DDP does this automatically)
- [ ] Learning rate scaling and warmup are critical when increasing effective batch size
- [ ] Fault tolerance (checkpointing, elastic training) is a must for long-running jobs
- [ ] Profile with torch.profiler or NVIDIA Nsight to identify bottlenecks before adding complexity
"""

CONTENT["pillar5.training_infra.mixed_precision"] = r"""# Mixed Precision Training

## Overview
Mixed precision training uses lower-precision numerical formats (FP16 or BF16) for most operations while keeping critical accumulations in FP32. It reduces memory usage by ~50%, increases throughput via Tensor Cores, and is essential knowledge for any MLE working with large models. Interviews focus on numerical stability trade-offs and when to apply it.

## Core Concepts

### Floating-Point Formats

| Format | Bits | Exponent | Mantissa | Range | Precision |
|--------|------|----------|----------|-------|-----------|
| FP32 | 32 | 8 | 23 | ~1e38 | ~7 decimal digits |
| FP16 | 16 | 5 | 10 | ~65504 | ~3 decimal digits |
| BF16 | 16 | 8 | 7 | ~1e38 | ~2 decimal digits |
| TF32 | 19 | 8 | 10 | ~1e38 | ~3 decimal digits |

**BF16 vs FP16**: BF16 has the same exponent range as FP32 (no overflow issues) but less precision. FP16 has better precision but much smaller range, requiring loss scaling. For LLM training, BF16 is strongly preferred on Ampere+ GPUs.

### Loss Scaling
FP16 gradients can underflow to zero for small values. Loss scaling multiplies the loss by a large factor $S$ before backward pass, then divides gradients by $S$ after:

$$
\nabla_\theta \mathcal{L}_{\text{scaled}} = S \cdot \nabla_\theta \mathcal{L}
$$

**Dynamic loss scaling**: Start with large $S$ (e.g., $2^{16}$), halve on NaN/Inf, double every $N$ steps without overflow.

### Master Weights
Maintain FP32 copy of weights (master weights) for the optimizer update. Forward/backward use FP16/BF16 copies. This prevents small updates from being rounded to zero:

If $\eta \cdot g \ll w$ in FP16, the update $w - \eta g = w$ due to rounding. FP32 master weights preserve the update.

### Tensor Cores
NVIDIA Tensor Cores perform $D = A \times B + C$ where $A, B$ are FP16/BF16 and $C, D$ are FP32. Achieve 2-8x throughput vs FP32 CUDA cores. Require dimensions divisible by 8 (FP16) or 16 (INT8) for optimal utilization.

## Implementation

```python
# PyTorch AMP (Automatic Mixed Precision) training loop
import torch
from torch.cuda.amp import autocast, GradScaler

model = MyModel().cuda()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
scaler = GradScaler()  # dynamic loss scaling for FP16

for batch in dataloader:
    optimizer.zero_grad()
    with autocast(dtype=torch.float16):  # or torch.bfloat16
        loss = model(batch.cuda())

    scaler.scale(loss).backward()  # scaled FP16 gradients
    scaler.unscale_(optimizer)     # unscale before clipping
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    scaler.step(optimizer)         # skip step if NaN/Inf
    scaler.update()                # adjust scale factor
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| AMP with FP16 | Pre-Ampere GPUs (V100) | Must use loss scaling to avoid underflow |
| BF16 native | Ampere+ GPUs (A100, H100) | No loss scaling needed, simpler code |
| FP8 (Hopper) | H100 training | 2x throughput over BF16, needs careful recipe |
| Selective precision | Numerically sensitive layers | Keep softmax, layernorm, loss in FP32 |

### Common Interview Questions
- [ ] Why does BF16 not need loss scaling while FP16 does?
- [ ] Which operations should always remain in FP32 and why?
- [ ] How does mixed precision interact with gradient accumulation?
- [ ] What happens if you train with FP16 without loss scaling?
- [ ] How do Tensor Cores exploit mixed precision for throughput?

## Comparisons

| Aspect | FP32 Only | AMP (FP16 + FP32) | BF16 + FP32 |
|--------|-----------|-------------------|-------------|
| Memory | Baseline | ~50% reduction | ~50% reduction |
| Throughput | 1x | 2-3x on Tensor Cores | 2-3x on Tensor Cores |
| Stability | Best | Needs loss scaling | Stable (same range as FP32) |
| GPU support | All | Volta+ | Ampere+ |
| Code complexity | None | GradScaler required | Minimal changes |

## Key Takeaways
- [ ] Always use mixed precision for GPU training -- the memory and speed gains are free with modern frameworks
- [ ] BF16 is the default choice on Ampere+ GPUs; FP16 + GradScaler for older hardware
- [ ] Keep reduction operations (softmax, layernorm, loss computation) in FP32 for numerical stability
- [ ] Align tensor dimensions to multiples of 8 for Tensor Core utilization
- [ ] Profile actual throughput -- mixed precision gains depend on model being compute-bound, not memory-bound
"""

CONTENT["pillar5.training_infra.training_frameworks"] = r"""# Training Frameworks

## Overview
Training frameworks abstract the complexity of distributed training, mixed precision, and hardware optimization. Senior MLE interviews test your ability to choose the right framework for a given scale and workload, and to reason about the trade-offs between flexibility, performance, and ecosystem maturity.

## Core Concepts

### PyTorch Ecosystem
PyTorch dominates ML research and increasingly production training. Key components:

- **torch.distributed**: Low-level primitives (init_process_group, AllReduce, broadcast)
- **DistributedDataParallel (DDP)**: Single-program multi-data wrapper; gradient sync via AllReduce
- **FullyShardedDataParallel (FSDP)**: ZeRO-3 style sharding native in PyTorch
- **torch.compile**: Graph capture + compilation for 1.5-2x speedup (PyTorch 2.0+)
- **TorchElastic**: Fault-tolerant training with dynamic membership

### DeepSpeed
Microsoft's library for efficient large model training:

- **ZeRO Stages 1-3**: Progressively shard optimizer states, gradients, parameters
- **ZeRO-Offload**: Offload optimizer states to CPU memory
- **ZeRO-Infinity**: Offload to NVMe SSDs for trillion-parameter models
- **DeepSpeed-MoE**: Mixture-of-experts training support
- **Activation checkpointing**: Trade compute for memory in backward pass

### Megatron-LM
NVIDIA's framework for large-scale transformer training:

- **Tensor parallelism**: Shard attention heads and MLP columns across GPUs
- **Sequence parallelism**: Distribute LayerNorm and dropout along sequence dim
- **3D parallelism**: Combine data + tensor + pipeline parallelism
- Optimized for NVIDIA hardware (NVLink, InfiniBand)

### Ray Train
Distributed training framework from Anyscale:

- Hardware-agnostic (GPU, TPU, multi-cloud)
- Integrates with Ray Tune for hyperparameter search
- Fault tolerance via checkpoint-based recovery
- Supports PyTorch, TensorFlow, Hugging Face Trainer

### Hugging Face Accelerate
Lightweight wrapper that adapts training code for any distributed setup:

```python
# Minimal change to single-GPU code
from accelerate import Accelerator
accelerator = Accelerator(mixed_precision="bf16")
model, optimizer, dataloader = accelerator.prepare(
    model, optimizer, dataloader
)
# Training loop stays the same
loss.backward()  # accelerator handles gradient sync
```

## Implementation

```python
# DeepSpeed ZeRO-3 config (ds_config.json)
{
    "bf16": {"enabled": True},
    "zero_optimization": {
        "stage": 3,
        "offload_optimizer": {"device": "cpu"},
        "offload_param": {"device": "cpu"},
        "overlap_comm": True,
        "contiguous_gradients": True
    },
    "gradient_accumulation_steps": 4,
    "train_micro_batch_size_per_gpu": 2
}
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| DDP | < 10B params, multi-GPU | Simplest distributed setup, hard to beat for small models |
| FSDP | 10-70B params, PyTorch native | Good ZeRO-3 with less config than DeepSpeed |
| DeepSpeed ZeRO | 70B+ params, memory constrained | Most mature large-model training library |
| Megatron-LM | LLM pretraining on NVIDIA clusters | Best throughput for transformer pretraining |
| Ray Train | Multi-cloud, heterogeneous infra | Best portability and fault tolerance |
| Accelerate | Quick prototyping | Minimal code change from single-GPU |

### Common Interview Questions
- [ ] When would you choose FSDP over DeepSpeed and vice versa?
- [ ] How does activation checkpointing reduce memory and what is the compute overhead?
- [ ] Describe how you would set up training for a 70B parameter model on 64 A100 GPUs
- [ ] What is torch.compile and how does it improve training throughput?
- [ ] How do you handle fault tolerance in a multi-day training run?

## Comparisons

| Aspect | DDP | FSDP | DeepSpeed | Megatron-LM |
|--------|-----|------|-----------|-------------|
| Max model scale | ~10B | ~70B | Trillion+ | ~1T |
| Setup complexity | Low | Medium | Medium | High |
| PyTorch native | Yes | Yes | Plugin | Separate codebase |
| CPU offload | No | Yes | Yes (ZeRO-Offload) | No |
| Tensor parallel | No | No | No | Yes |
| Community | Largest | Growing | Large | NVIDIA-focused |

## Key Takeaways
- [ ] Start with DDP + AMP for models under 10B params -- do not over-engineer
- [ ] FSDP is the PyTorch-native answer to DeepSpeed ZeRO; prefer it when staying in PyTorch ecosystem
- [ ] DeepSpeed excels for very large models with CPU/NVMe offloading
- [ ] Megatron-LM delivers best throughput for LLM pretraining but requires NVIDIA-specific infra
- [ ] Always profile memory and throughput before choosing a framework -- the bottleneck determines the solution
"""

CONTENT["pillar5.training_infra.experiment_tracking"] = r"""# Experiment Tracking

## Overview
Experiment tracking systems record hyperparameters, metrics, artifacts, and code versions for every training run. In production ML, reproducibility and auditability are non-negotiable. Interviews test your ability to design tracking systems that scale across teams and integrate with CI/CD pipelines.

## Core Concepts

### What to Track
Every training run should capture:
- **Hyperparameters**: Learning rate, batch size, architecture config, data preprocessing params
- **Metrics**: Training loss, validation metrics at each checkpoint, evaluation results
- **Artifacts**: Model checkpoints, training curves, confusion matrices, sample predictions
- **Environment**: Code commit hash, dependency versions, hardware config, random seeds
- **Data lineage**: Dataset version, preprocessing pipeline hash, train/val split

### MLflow
Open-source platform with four components:
- **Tracking**: Log params, metrics, artifacts via REST API
- **Projects**: Reproducible run packaging (MLproject file + conda env)
- **Models**: Model packaging with inference API (MLmodel file)
- **Model Registry**: Versioned model store with stage transitions (Staging -> Production)

### Weights & Biases (W&B)
Cloud-native experiment tracking with strong visualization:
- Real-time metric dashboards and run comparison
- Hyperparameter importance analysis
- Artifact versioning with data/model lineage
- Sweeps: distributed hyperparameter search
- Tables: structured evaluation logging

### Design Considerations for Scale
- **Storage backend**: Metrics in time-series DB (or relational), artifacts in object store (S3/GCS)
- **Naming conventions**: `{project}/{model_type}/{date}-{short_hash}` for runs
- **Tagging strategy**: Tag runs with `dataset_version`, `experiment_group`, `owner`
- **Retention policy**: Auto-archive runs older than N days, keep only best checkpoints
- **Access control**: Team-level projects, run-level permissions

## Implementation

```python
# MLflow experiment tracking example
import mlflow

mlflow.set_experiment("recommendation-model-v2")

with mlflow.start_run(run_name="bert-base-lr1e4"):
    # Log hyperparameters
    mlflow.log_params({
        "model": "bert-base",
        "lr": 1e-4,
        "batch_size": 32,
        "epochs": 10,
        "optimizer": "adamw",
    })

    for epoch in range(10):
        train_loss, val_auc = train_epoch(model, dataloader)
        mlflow.log_metrics({
            "train_loss": train_loss,
            "val_auc": val_auc,
        }, step=epoch)

    # Log model artifact
    mlflow.pytorch.log_model(model, "model")
    # Log evaluation artifacts
    mlflow.log_artifact("confusion_matrix.png")
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Run comparison | Hyperparameter tuning | Log enough granularity to explain metric differences |
| Model registry | Production deployment | Stage transitions (dev -> staging -> prod) with approval gates |
| Artifact lineage | Debugging model regressions | Trace from prediction back to training data version |
| Automated logging | Team-wide adoption | Auto-log framework defaults (LR schedule, gradient norms) |

### Common Interview Questions
- [ ] How would you design an experiment tracking system for a team of 50 ML engineers?
- [ ] What is the relationship between experiment tracking and model registry?
- [ ] How do you ensure reproducibility when training depends on external data sources?
- [ ] How would you handle experiment tracking for hyperparameter sweeps with 1000+ runs?
- [ ] Describe how you would integrate experiment tracking into a CI/CD pipeline for ML.

## Comparisons

| Aspect | MLflow | W&B | TensorBoard | Neptune |
|--------|--------|-----|-------------|---------|
| Hosting | Self-hosted or Databricks | Cloud (SaaS) | Local / TF ecosystem | Cloud (SaaS) |
| Model Registry | Built-in | Linked artifacts | No | Built-in |
| Visualization | Basic | Rich (tables, media) | Scalars + graphs | Good |
| HP Sweeps | No (use Optuna) | Built-in Sweeps | No | Built-in |
| Cost | Free (OSS) | Free tier + paid | Free | Paid |
| Team features | Basic | Strong (reports, teams) | Minimal | Good |

## Key Takeaways
- [ ] Track everything from day one -- retrofitting experiment tracking is painful
- [ ] Use a model registry to decouple training from deployment; never deploy a checkpoint directly
- [ ] Automate logging with framework callbacks to reduce developer friction and ensure consistency
- [ ] Data versioning (DVC, Delta Lake, or artifact hashes) is as important as code versioning
- [ ] Design for querying: you will search for "best run with config X on dataset Y" -- make that easy
"""

# ===== SERVING INFRASTRUCTURE =====

CONTENT["pillar5.serving_infra.model_serving"] = r"""# Model Serving Systems

## Overview
Model serving is the infrastructure layer that turns trained models into production prediction services. Senior MLE interviews focus on system design for low-latency, high-throughput serving at scale, including batching strategies, model management, and multi-model architectures. This is where ML meets systems engineering.

## Core Concepts

### Serving Architectures

**Online serving (synchronous)**: Request-response pattern with strict latency SLAs (p50 < 10ms, p99 < 50ms). Used for real-time recommendations, search ranking, fraud detection.

**Offline serving (batch)**: Process large datasets periodically. Spark/MapReduce jobs that score millions of items. Results cached in key-value store for lookup.

**Streaming serving (near-real-time)**: Consume events from Kafka/Kinesis, score in micro-batches. Used for real-time personalization with feature freshness requirements.

### NVIDIA Triton Inference Server
Production-grade serving with:
- **Dynamic batching**: Accumulate requests within a time window, batch for GPU efficiency
- **Model ensemble**: Chain preprocessing -> model -> postprocessing as a DAG
- **Concurrent model execution**: Multiple models share GPU with instance groups
- **Backend support**: ONNX, TensorRT, PyTorch, TensorFlow, custom Python

### TorchServe
PyTorch-native serving:
- **MAR (Model Archive)**: Package model + handler + dependencies
- **Custom handlers**: Preprocess/inference/postprocess pipeline per model
- **Batch inference**: Configurable batch size and timeout
- **Versioned models**: A/B testing and canary deployments

### Model Format Optimization
- **ONNX**: Portable format across frameworks; use `torch.onnx.export()` for graph capture
- **TensorRT**: NVIDIA's optimizer; fuses layers, selects optimal kernels per GPU
- **OpenVINO**: Intel CPU optimization; quantization + graph optimization
- **CoreML**: Apple device deployment

## Implementation

```python
# Triton model repository structure
# model_repository/
#   my_model/
#     config.pbtxt
#     1/              # version 1
#       model.onnx

# config.pbtxt for Triton:
# name: "my_model"
# platform: "onnxruntime_onnx"
# max_batch_size: 64
# input [{ name: "input" data_type: TYPE_FP32 dims: [768] }]
# output [{ name: "output" data_type: TYPE_FP32 dims: [1] }]
# dynamic_batching {
#     preferred_batch_size: [16, 32, 64]
#     max_queue_delay_microseconds: 5000
# }
# instance_group [{ count: 2 kind: KIND_GPU }]
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Dynamic batching | GPU serving with variable request rate | Trade latency for throughput; tune max_queue_delay |
| Model ensemble | Multi-step inference (embed -> rank -> rerank) | Reduce network hops by co-locating in serving DAG |
| Shadow deployment | Validating new model in production | Dual-write predictions, compare offline; no user impact |
| Multi-armed bandit | Gradual rollout | Explore-exploit between model versions |

### Common Interview Questions
- [ ] How would you design a serving system for 100K QPS with p99 < 20ms?
- [ ] What is dynamic batching and how does it improve GPU utilization?
- [ ] How do you handle model versioning and rollback in production?
- [ ] Compare CPU vs GPU serving -- when is each appropriate?
- [ ] How would you serve an ensemble of 5 models with different latency profiles?

## Comparisons

| Aspect | Triton | TorchServe | TF Serving | Seldon Core |
|--------|--------|------------|------------|-------------|
| GPU optimization | Excellent (TensorRT) | Good | Good | Framework-dependent |
| Multi-framework | Yes (ONNX, TF, PT) | PyTorch only | TensorFlow only | Any (container-based) |
| Dynamic batching | Built-in | Built-in | Built-in | Limited |
| K8s integration | Triton + KServe | Native | TF ecosystem | Native (K8s-first) |
| Model ensemble | DAG pipelines | Workflow API | No | Inference graph |

## Key Takeaways
- [ ] Choose serving infrastructure based on latency SLA and QPS requirements, not model framework
- [ ] Dynamic batching is critical for GPU economics -- a single request wastes most GPU cycles
- [ ] Convert models to ONNX or TensorRT for 2-5x inference speedup over native PyTorch
- [ ] Design for graceful degradation: fallback models, circuit breakers, request shedding
- [ ] Separate model serving from business logic -- serving infra should be model-agnostic
"""

CONTENT["pillar5.serving_infra.optimization"] = r"""# Serving Optimization (Quantization, Pruning)

## Overview
Model optimization reduces inference cost without unacceptable accuracy loss. Quantization and pruning are the two primary techniques, and senior MLEs must understand when each applies, the accuracy-latency trade-off, and how to validate optimized models in production. This is a high-signal interview topic because it directly impacts serving cost.

## Core Concepts

### Quantization
Reduce numerical precision of weights and activations from FP32 to INT8, INT4, or lower.

**Post-Training Quantization (PTQ)**: Apply quantization after training without retraining. Fast but may lose accuracy for sensitive models.

A tensor $x$ is quantized to $b$-bit integer as:

$$
x_q = \text{round}\left(\frac{x - z}{s}\right), \quad s = \frac{x_{\max} - x_{\min}}{2^b - 1}
$$

where $s$ is the scale factor and $z$ is the zero-point.

**Quantization-Aware Training (QAT)**: Simulate quantization during training using fake quantization nodes. Model learns to be robust to quantization noise. Higher accuracy than PTQ but requires retraining.

**Weight-only quantization**: Quantize weights to INT4/INT8 but compute in FP16. Popular for LLMs (GPTQ, AWQ, GGUF). Reduces memory bandwidth bottleneck without touching activations.

### Pruning
Remove weights or structures from the model to reduce computation.

**Unstructured pruning**: Zero out individual weights below a threshold. Creates sparse matrices. Requires sparse compute support (limited hardware acceleration).

**Structured pruning**: Remove entire neurons, attention heads, or channels. Produces a smaller dense model that runs on standard hardware. More practical for deployment.

**Magnitude pruning**: Remove weights with smallest absolute values. Simple but effective baseline.

### Knowledge Distillation
Train a smaller "student" model to mimic a larger "teacher":

$$
\mathcal{L} = \alpha \cdot \mathcal{L}_{\text{CE}}(y, \hat{y}_s) + (1 - \alpha) \cdot T^2 \cdot \text{KL}\left(\sigma\left(\frac{z_t}{T}\right) \| \sigma\left(\frac{z_s}{T}\right)\right)
$$

where $T$ is temperature and $\sigma$ is softmax. Higher $T$ reveals more information about teacher's learned structure.

## Implementation

```python
# PyTorch static quantization
import torch.quantization as quant

model.eval()
# Fuse conv-bn-relu patterns for better quantization
model_fused = quant.fuse_modules(model, [["conv", "bn", "relu"]])
# Attach quantization config
model_fused.qconfig = quant.get_default_qconfig("x86")
# Insert observers
quant.prepare(model_fused, inplace=True)
# Calibrate with representative data
with torch.no_grad():
    for batch in calibration_loader:
        model_fused(batch)
# Convert to quantized model
model_int8 = quant.convert(model_fused)
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| PTQ INT8 | CNN/transformer with <1% accuracy budget | Fastest path; calibrate on 100-1000 samples |
| QAT | Accuracy-sensitive models | 2-3x effort but recovers most PTQ accuracy loss |
| Weight-only INT4 | LLM serving (memory-bound) | GPTQ/AWQ: 4-bit weights, FP16 compute |
| Structured pruning | Reduce FLOPs on standard hardware | Remove attention heads or FFN neurons |
| Distillation | Deploy on edge / mobile | Train task-specific small model from large teacher |

### Common Interview Questions
- [ ] Compare PTQ vs QAT -- when is each appropriate?
- [ ] Why is weight-only quantization effective for LLMs but less so for CNNs?
- [ ] How do you validate that a quantized model is safe to deploy?
- [ ] What is the difference between symmetric and asymmetric quantization?
- [ ] How would you reduce a 70B LLM to run on a single A100?

## Comparisons

| Aspect | INT8 PTQ | INT8 QAT | INT4 Weight-Only | Structured Pruning |
|--------|----------|----------|-------------------|-------------------|
| Accuracy loss | 0.5-2% | < 0.5% | 1-3% (LLMs) | 1-5% (depends on sparsity) |
| Speedup | 2-4x (INT8 HW) | 2-4x | 1.5-2x (memory-bound) | Proportional to removed params |
| Retraining | No | Yes (expensive) | No (PTQ variant) | Optional (fine-tune helps) |
| Hardware needs | INT8 support | INT8 support | Standard GPU | Standard hardware |
| Best for | CNNs, BERT-class | Production-critical models | LLMs (7B-70B) | Edge deployment |

## Key Takeaways
- [ ] Start with PTQ INT8 -- it is free performance for most models and requires no retraining
- [ ] For LLMs, weight-only quantization (GPTQ/AWQ) is the primary optimization lever
- [ ] Always validate quantized models on a holdout set AND production traffic (shadow mode)
- [ ] Structured pruning produces real speedups; unstructured pruning needs sparse hardware support
- [ ] Combine techniques: distill to smaller model, then quantize -- multiplicative savings
"""

CONTENT["pillar5.serving_infra.llm_serving"] = r"""# LLM Serving

## Overview
Serving large language models presents unique challenges compared to traditional ML models: autoregressive generation means latency scales with output length, KV-cache management dominates memory, and batch scheduling must handle variable-length sequences. This is one of the hottest interview topics for senior MLE roles at companies deploying LLMs.

## Core Concepts

### KV-Cache Management
During autoregressive generation, attention keys and values from previous tokens are cached to avoid recomputation. For a model with $L$ layers, $H$ heads, dimension $d$, and sequence length $S$:

$$
\text{KV-cache memory} = 2 \times L \times H \times d \times S \times \text{bytes\_per\_element}
$$

For a 70B model (80 layers, 64 heads, d=128) with 4K context in FP16: ~40 GB per sequence. KV-cache, not model weights, is often the memory bottleneck for concurrent requests.

### Continuous Batching
Traditional static batching pads all sequences to max length and waits for all to finish. Continuous batching (iteration-level scheduling) allows:
- New requests to join the batch at any decode step
- Completed requests to leave immediately, freeing their KV-cache slots
- GPU utilization stays high even with variable-length outputs

### PagedAttention (vLLM)
Inspired by OS virtual memory: KV-cache is stored in non-contiguous physical blocks mapped via a page table. Benefits:
- Near-zero memory waste (no padding or pre-allocation)
- Efficient memory sharing for beam search and parallel sampling
- Enables ~2-4x more concurrent sequences vs naive allocation

### Speculative Decoding
Use a small draft model to generate $k$ candidate tokens, then verify all $k$ in a single forward pass of the large model. Accepts correct tokens, rejects and resamples from the large model's distribution at the first divergence. Achieves 2-3x speedup with zero quality loss when draft model matches well.

## Implementation

```python
# vLLM serving example
from vllm import LLM, SamplingParams

llm = LLM(
    model="meta-llama/Llama-2-70b-chat-hf",
    tensor_parallel_size=4,         # 4 GPUs
    gpu_memory_utilization=0.90,
    max_num_seqs=256,               # max concurrent sequences
    enable_prefix_caching=True,     # cache common prompt prefixes
)

params = SamplingParams(
    temperature=0.7,
    top_p=0.9,
    max_tokens=512,
)

# vLLM handles continuous batching internally
outputs = llm.generate(prompts, params)
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Continuous batching | Any LLM serving | 10-20x throughput vs static batching |
| PagedAttention | Memory-constrained serving | Near-optimal KV-cache utilization |
| Speculative decoding | Latency-sensitive applications | Speed up decoding without quality loss |
| Prefix caching | Shared system prompts | Cache KV for common prefixes across requests |
| Tensor parallel | Model exceeds single GPU memory | Split attention heads across GPUs |

### Common Interview Questions
- [ ] How does continuous batching improve LLM serving throughput?
- [ ] Explain PagedAttention and why it reduces memory waste
- [ ] How would you design an LLM serving system for 1000 concurrent users?
- [ ] What are the trade-offs between throughput and latency in LLM serving?
- [ ] How does speculative decoding achieve speedup without changing output distribution?

## Comparisons

| Aspect | vLLM | TGI (HuggingFace) | Triton + TensorRT-LLM | Ollama |
|--------|------|--------------------|-----------------------|--------|
| PagedAttention | Yes (original) | Yes | Yes | Yes (llama.cpp) |
| Continuous batching | Yes | Yes | Yes | Limited |
| Tensor parallel | Yes | Yes | Yes (optimized) | No |
| Quantization | GPTQ, AWQ, FP8 | GPTQ, AWQ, EETQ | FP8, INT4, INT8 | GGUF (CPU/GPU) |
| Throughput | High | High | Highest (NVIDIA optimized) | Low (single-user focus) |
| Ease of use | High (Python API) | Medium (Docker) | Low (complex setup) | Highest |

## Key Takeaways
- [ ] KV-cache management is the central challenge of LLM serving -- not model computation
- [ ] Continuous batching is non-negotiable for production LLM serving; static batching wastes 80%+ of GPU cycles
- [ ] vLLM's PagedAttention is the current standard for memory-efficient LLM serving
- [ ] Time-to-first-token (prefill) and time-per-output-token (decode) are separate optimization targets
- [ ] For maximum throughput, combine tensor parallelism + continuous batching + quantization (INT4/FP8)
"""

CONTENT["pillar5.serving_infra.latency_optimization"] = r"""# Latency Optimization

## Overview
Latency optimization is the art of reducing end-to-end inference time while maintaining throughput and accuracy. For production ML systems, p99 latency matters more than mean latency. Senior MLE interviews test your ability to identify bottlenecks, apply systematic optimization, and make principled trade-offs between latency, cost, and accuracy.

## Core Concepts

### Latency Breakdown
A typical ML inference request:
1. **Network**: Request routing, load balancing (1-5ms)
2. **Preprocessing**: Tokenization, feature lookup, normalization (1-10ms)
3. **Model inference**: Forward pass on GPU/CPU (5-100ms)
4. **Postprocessing**: Decoding, filtering, ranking (1-5ms)
5. **Feature store lookup**: Redis/DynamoDB calls (2-10ms, can be parallelized)

**Amdahl's Law applies**: If model inference is 50% of total latency, a 2x model speedup only yields 33% end-to-end improvement. Always profile before optimizing.

### GPU Optimization
- **Operator fusion**: Combine sequential ops (e.g., Conv+BN+ReLU) into single kernel launch. TensorRT does this automatically.
- **Kernel selection**: TensorRT benchmarks multiple kernel implementations per layer and selects fastest for your specific GPU.
- **Memory layout**: NCHW vs NHWC layout matters. Tensor Cores prefer channels-last (NHWC) on NVIDIA GPUs.
- **CUDA graphs**: Capture and replay a sequence of GPU operations, eliminating CPU kernel launch overhead. Critical for small models where launch latency dominates.

### Caching Strategies
- **Result caching**: Cache predictions for identical inputs (embedding lookups, repeated queries). Hit rates of 30-80% common in recommendation systems.
- **Feature caching**: Pre-compute expensive features; cache in Redis with TTL.
- **KV-cache reuse**: For LLMs, cache KV states of common prefixes (system prompts).
- **Approximate caching**: For embedding-based models, cache results for similar (not identical) inputs using locality-sensitive hashing.

### Async and Parallel Execution
- **Pipeline parallelism at serving time**: Overlap preprocessing of request N+1 with inference of request N.
- **Parallel feature fetches**: Fan out to multiple feature stores concurrently using asyncio.
- **Prefetching**: Predict next likely request and pre-compute (works for autocomplete, next-page recommendations).

## Implementation

```python
# CUDA graphs for eliminating launch overhead
import torch

model = model.cuda().eval()
static_input = torch.randn(32, 768, device="cuda")

# Warmup
for _ in range(3):
    model(static_input)

# Capture graph
graph = torch.cuda.CUDAGraph()
with torch.cuda.graph(graph):
    static_output = model(static_input)

# Replay (near-zero CPU overhead)
def infer(x: torch.Tensor) -> torch.Tensor:
    # Run inference using captured CUDA graph.
    static_input.copy_(x)
    graph.replay()
    return static_output.clone()
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| TensorRT conversion | GPU serving with fixed input shapes | 2-5x speedup from op fusion + kernel optimization |
| CUDA graphs | Small models, high QPS | Eliminates CPU-GPU launch overhead |
| Request batching | GPU serving | Amortize fixed costs across batch; tune batch timeout |
| Result caching | Repeated or similar inputs | Check cache hit rate before investing in model optimization |
| Async feature fetch | Multi-source feature lookup | Parallelize I/O to reduce critical path |

### Common Interview Questions
- [ ] Walk through how you would reduce p99 latency from 100ms to 20ms for a ranking model
- [ ] What is the difference between optimizing for throughput vs latency?
- [ ] How do CUDA graphs improve inference latency and when can you NOT use them?
- [ ] How would you design a caching layer for an embedding-based retrieval system?
- [ ] What metrics do you monitor for a latency-sensitive ML service?

## Comparisons

| Optimization | Latency Reduction | Effort | Accuracy Impact | Applicability |
|-------------|-------------------|--------|-----------------|---------------|
| TensorRT | 2-5x | Medium | None to minimal | Fixed-shape GPU models |
| INT8 quantization | 2-4x | Low | < 1% typically | Most models |
| CUDA graphs | 1.5-3x (small models) | Low | None | Fixed computation graph |
| Result caching | Proportional to hit rate | Low | None | Repeated inputs |
| Distillation | Model-dependent | High | 1-5% | When smaller arch exists |
| Batching | Throughput up, latency trade-off | Low | None | GPU serving |

## Key Takeaways
- [ ] Profile first: use torch.profiler, NVIDIA Nsight, or custom timers to find the actual bottleneck
- [ ] p99 latency is what matters in production, not mean -- tail latencies cause cascading failures
- [ ] Caching is often the highest-ROI optimization; check cache hit rates before touching the model
- [ ] TensorRT + CUDA graphs can deliver 5-10x combined speedup for fixed-shape models
- [ ] Design latency budgets: allocate ms to each component and optimize the largest contributor first
"""

# ===== DATA INFRASTRUCTURE =====

CONTENT["pillar5.data_infra.data_processing"] = r"""# Data Processing (Spark, Flink)

## Overview
Large-scale data processing frameworks are the backbone of ML feature engineering and training data pipelines. Senior MLE interviews test your ability to choose between batch and stream processing, optimize data pipelines for ML workloads, and design systems that handle terabytes of data reliably. Spark and Flink are the two dominant frameworks.

## Core Concepts

### Apache Spark
Distributed batch processing engine with in-memory computation:

- **RDD (Resilient Distributed Dataset)**: Immutable, partitioned collections with lazy evaluation and lineage-based fault tolerance
- **DataFrame API**: SQL-like operations on structured data with Catalyst optimizer
- **Spark MLlib**: Distributed ML algorithms (useful for feature engineering at scale)
- **Spark SQL**: Query data with SQL; unified API for batch and structured streaming

**Key architecture**: Driver program creates DAG of stages, scheduler assigns tasks to executors. Shuffle operations (groupBy, join) are the primary performance bottleneck.

### Apache Flink
True stream processing engine with batch as a special case:

- **DataStream API**: Process unbounded event streams with exactly-once semantics
- **Event time processing**: Handle out-of-order events with watermarks
- **State management**: Keyed state (per-key aggregations), operator state (parallel state)
- **Checkpointing**: Async barrier-based snapshots for fault tolerance (Chandy-Lamport algorithm)

### Batch vs Stream Processing for ML

| Aspect | Batch (Spark) | Stream (Flink) |
|--------|--------------|----------------|
| Feature freshness | Hours to daily | Seconds to minutes |
| Complexity | Lower | Higher (state, watermarks) |
| Use case | Training data, daily features | Real-time features, online aggregations |
| Exactly-once | Via idempotent writes | Built-in (checkpointing) |

### Data Processing Patterns for ML
- **Feature backfill**: Recompute historical features with updated logic using batch processing
- **Point-in-time joins**: Join features with labels at the exact timestamp to prevent label leakage
- **Sliding window aggregations**: Compute rolling statistics (7-day avg, 30-day count) for training
- **Data skew handling**: Salted keys, broadcast joins, adaptive query execution (Spark 3.0+)

## Implementation

```python
# PySpark: Feature engineering pipeline
from pyspark.sql import SparkSession, Window
import pyspark.sql.functions as F

spark = SparkSession.builder.appName("feature_eng").getOrCreate()

# Point-in-time feature join (avoid label leakage)
user_features = (
    events_df
    .withWatermark("event_time", "1 hour")
    .groupBy("user_id", F.window("event_time", "7 days"))
    .agg(
        F.count("*").alias("events_7d"),
        F.avg("amount").alias("avg_amount_7d"),
    )
)

# Repartition by user_id for efficient downstream joins
user_features = user_features.repartition(200, "user_id")
user_features.write.parquet("s3://features/user_7d/")
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Lambda architecture | Need both real-time and historical features | Batch layer for accuracy, speed layer for freshness |
| Kappa architecture | Simplify by using stream for everything | Replay stream for reprocessing; simpler ops |
| Broadcast join | Small table joined with large table | Avoid shuffle by broadcasting small side |
| Bucketed tables | Frequent joins on same key | Pre-partition to eliminate shuffle at join time |

### Common Interview Questions
- [ ] How would you design a feature pipeline that needs both real-time and batch features?
- [ ] What causes data skew in Spark and how do you mitigate it?
- [ ] Compare Spark Structured Streaming vs Flink for real-time ML features
- [ ] How do you prevent label leakage when creating training datasets?
- [ ] How would you process 10TB of clickstream data daily for model training?

## Comparisons

| Aspect | Spark | Flink | Kafka Streams | Beam |
|--------|-------|-------|---------------|------|
| Primary mode | Batch (+ streaming) | Stream (+ batch) | Stream only | Unified (runner-agnostic) |
| Latency | Seconds to minutes | Milliseconds | Milliseconds | Runner-dependent |
| State management | Limited | Rich (keyed, operator) | Local RocksDB | Runner-dependent |
| Ecosystem | Largest (MLlib, SQL, GraphX) | Growing | Kafka-native | Multi-runner |
| ML integration | MLlib, Spark + PyTorch | FlinkML (limited) | None | TFX |

## Key Takeaways
- [ ] Spark for batch feature engineering and training data prep; Flink for real-time feature computation
- [ ] Point-in-time correctness is critical for ML data pipelines -- always join features at label timestamp
- [ ] Shuffle is the enemy of Spark performance; minimize it with partitioning, bucketing, and broadcast joins
- [ ] Design for reprocessing: you will need to recompute features when logic changes
- [ ] Monitor data quality metrics (null rates, distribution shifts) at every pipeline stage
"""

CONTENT["pillar5.data_infra.feature_store"] = r"""# Feature Store Systems

## Overview
A feature store is a centralized platform for storing, managing, and serving ML features. It bridges the gap between feature engineering (data team) and model serving (ML team), ensuring consistency between training and inference. Interviews test your ability to design feature stores that serve features at low latency while maintaining training-serving parity.

## Core Concepts

### Training-Serving Skew
The most critical problem feature stores solve: features computed differently at training time (batch) vs serving time (online). This causes silent model degradation. A feature store ensures the same transformation logic produces features for both paths.

### Dual Storage Architecture
- **Offline store**: Columnar storage (Parquet on S3, Delta Lake, BigQuery) for training data retrieval. Optimized for throughput: scan millions of rows for dataset creation.
- **Online store**: Low-latency key-value store (Redis, DynamoDB, Bigtable) for serving. Optimized for point lookups: get features for one user/item in < 5ms.
- **Materialization**: Batch or streaming job that syncs features from offline to online store.

### Feature Definitions
Features are defined once and registered with metadata:
- **Entity**: The primary key (user_id, item_id, session_id)
- **Feature view**: A group of related features from the same data source
- **TTL (Time-to-Live)**: How stale a feature can be before it is considered invalid
- **Schema**: Data types, allowed ranges, validation rules

### Point-in-Time Joins
When creating training datasets, features must be joined at the exact time the label was generated. Feature stores handle this automatically by maintaining feature timestamps and performing as-of joins.

## Implementation

```python
# Feast feature store definition
from feast import Entity, Feature, FeatureView, FileSource
from feast.types import Float32, Int64

# Define entity
user = Entity(name="user_id", join_keys=["user_id"])

# Define feature view
user_features = FeatureView(
    name="user_activity_features",
    entities=[user],
    schema=[
        Feature(name="purchase_count_7d", dtype=Int64),
        Feature(name="avg_session_duration", dtype=Float32),
        Feature(name="days_since_last_visit", dtype=Int64),
    ],
    source=FileSource(
        path="s3://features/user_activity.parquet",
        timestamp_field="event_timestamp",
    ),
    online=True,
    ttl=timedelta(days=1),
)

# Retrieve online features at serving time
features = store.get_online_features(
    features=["user_activity_features:purchase_count_7d"],
    entity_rows=[{"user_id": 12345}],
).to_dict()
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| On-demand features | Features that depend on request context | Compute at serving time (e.g., time since last action) |
| Pre-computed features | Expensive aggregations (30-day stats) | Materialize offline, serve from online store |
| Streaming features | Near-real-time freshness needed | Flink/Spark Streaming writes to online store |
| Feature sharing | Multiple models use same features | Central registry prevents redundant computation |

### Common Interview Questions
- [ ] How would you design a feature store for a company with 50 ML models?
- [ ] What is training-serving skew and how does a feature store prevent it?
- [ ] How do you handle feature freshness requirements for real-time models?
- [ ] What storage backends would you choose for online vs offline feature stores?
- [ ] How do you handle schema evolution when a feature definition changes?

## Comparisons

| Aspect | Feast | Tecton | Hopsworks | Databricks Feature Store |
|--------|-------|--------|-----------|--------------------------|
| Hosting | Self-hosted (OSS) | Managed (SaaS) | Self-hosted / managed | Databricks-native |
| Streaming ingestion | Via Spark/Flink | Built-in (Rift) | Built-in | Structured Streaming |
| Online store | Redis, DynamoDB | DynamoDB, Redis | RonDB (custom) | Cosmos DB, DynamoDB |
| Offline store | S3/GCS Parquet | Delta Lake | Hudi | Delta Lake |
| Feature transforms | External (dbt, Spark) | Built-in Python/SQL | Built-in | SQL / Python |
| Cost | Low (OSS) | High (enterprise) | Medium | Databricks pricing |

## Key Takeaways
- [ ] A feature store's primary value is eliminating training-serving skew, not just feature reuse
- [ ] Design online store for p99 < 5ms lookups; batch precompute expensive features offline
- [ ] Point-in-time correctness is non-negotiable -- incorrect joins cause silent model degradation
- [ ] Start simple (Feast + Redis + S3) and add complexity (streaming, transforms) as needed
- [ ] Feature monitoring (null rates, distribution drift, staleness) is as important as model monitoring
"""

CONTENT["pillar5.data_infra.data_quality"] = r"""# Data Quality & Validation

## Overview
Data quality is the most underappreciated factor in ML system reliability. Bad data causes silent model degradation that is harder to detect than code bugs. Senior MLE interviews test your ability to design validation pipelines that catch data issues before they corrupt models, and to build monitoring that detects drift in production data.

## Core Concepts

### Data Validation Layers
1. **Schema validation**: Column names, types, nullability, allowed value ranges
2. **Statistical validation**: Distribution checks, correlation stability, outlier detection
3. **Semantic validation**: Business logic rules (e.g., price > 0, age between 0 and 150)
4. **Cross-dataset validation**: Training/serving feature distributions should be consistent

### Great Expectations
Python framework for data validation with human-readable expectations:

- **Expectations**: Declarative assertions (e.g., `expect_column_values_to_be_between`)
- **Suites**: Groups of expectations applied to a dataset
- **Checkpoints**: Run suites against data batches with pass/fail results
- **Data Docs**: Auto-generated HTML documentation of data quality

### TensorFlow Data Validation (TFDV)
Google's library for analyzing and validating ML data:

- **Schema inference**: Automatically generate schema from training data
- **Anomaly detection**: Compare new data against schema for drift and skew
- **Training-serving skew detection**: Compare training data stats with serving data
- **Visualization**: Faceted display of feature statistics

### Data Drift Detection
Monitor whether the distribution of input features or model outputs changes over time.

**Population Stability Index (PSI)**: Measures distribution shift between reference and current data:

$$
\text{PSI} = \sum_{i=1}^{k} (p_i - q_i) \ln\left(\frac{p_i}{q_i}\right)
$$

where $p_i$ and $q_i$ are proportions in bin $i$ for new and reference distributions. PSI < 0.1 indicates no significant shift; PSI > 0.25 indicates major shift.

**Kolmogorov-Smirnov test**: Non-parametric test for continuous features. Compare CDFs of reference and current data.

## Implementation

```python
# Great Expectations validation pipeline
import great_expectations as gx

context = gx.get_context()

# Define expectations
suite = context.add_expectation_suite("feature_validation")
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToNotBeNull(column="user_id")
)
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToBeBetween(
        column="click_rate", min_value=0.0, max_value=1.0
    )
)
suite.add_expectation(
    gx.expectations.ExpectColumnMeanToBeBetween(
        column="session_length", min_value=30, max_value=600
    )
)

# Run validation
result = context.run_checkpoint("daily_feature_check")
if not result.success:
    alert_on_call_engineer(result.to_json_dict())
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Schema enforcement | Every data pipeline stage | Catch type errors and missing columns before they propagate |
| Distribution monitoring | Production feature pipelines | Detect upstream data source changes early |
| Reference window comparison | Continuous drift detection | Compare recent window to training data distribution |
| Circuit breaker | Automated retraining pipelines | Block model update if training data fails validation |

### Common Interview Questions
- [ ] How would you design a data validation pipeline for an ML system processing 1M events/day?
- [ ] What is the difference between data drift and concept drift?
- [ ] How do you set thresholds for data quality alerts without excessive false positives?
- [ ] How would you detect and handle a silent schema change from an upstream data producer?
- [ ] Design a system that prevents bad data from reaching model training.

## Comparisons

| Aspect | Great Expectations | TFDV | Deequ (AWS) | Pandera |
|--------|-------------------|------|-------------|---------|
| Framework | Python-native | TensorFlow ecosystem | Spark-native | Pandas/Polars |
| Scale | Single-node or Spark | Beam/Dataflow | Spark | Single-node |
| ML-specific | Limited | Strong (drift, skew) | Limited | Limited |
| Schema inference | Manual + profiler | Automatic | Automatic | Manual |
| Integration | Airflow, dbt, Dagster | TFX pipeline | AWS Glue | pytest |

## Key Takeaways
- [ ] Validate data at every pipeline boundary, not just at ingestion -- data quality degrades at each transformation
- [ ] Distinguish data drift (feature distribution shift) from concept drift (P(Y|X) changes) -- they require different responses
- [ ] Set validation thresholds based on historical variation, not arbitrary numbers; use adaptive thresholds
- [ ] Build circuit breakers: if data quality check fails, block downstream model training automatically
- [ ] Data quality monitoring should be as rigorous as application monitoring -- with on-call rotations and SLAs
"""

# ===== ML PIPELINE & OPS =====

CONTENT["pillar5.ml_pipeline_ops.orchestration"] = r"""# Orchestration (Airflow, Kubeflow)

## Overview
ML pipeline orchestration manages the execution of complex, multi-step workflows: data ingestion, feature engineering, model training, evaluation, and deployment. Senior MLE interviews focus on designing reliable, observable pipelines that handle failures gracefully and scale across teams. The choice between Airflow and Kubeflow reflects different philosophies about ML infrastructure.

## Core Concepts

### Apache Airflow
General-purpose workflow orchestrator that defines pipelines as DAGs (Directed Acyclic Graphs):

- **DAG**: Python code defining task dependencies and execution order
- **Operators**: Task types (BashOperator, PythonOperator, KubernetesPodOperator)
- **Scheduler**: Triggers DAG runs based on schedule or external events
- **Executor**: Runs tasks (LocalExecutor, CeleryExecutor, KubernetesExecutor)
- **XCom**: Cross-task communication for passing small metadata

**Strengths**: Mature ecosystem, extensive operator library, strong scheduling, good for data engineering teams.
**Weaknesses**: Not ML-native; no artifact tracking, experiment management, or GPU scheduling built in.

### Kubeflow Pipelines
ML-specific orchestration on Kubernetes:

- **Pipeline**: Defined in Python using KFP SDK; compiles to Argo Workflow YAML
- **Components**: Containerized steps with typed inputs/outputs and artifact tracking
- **Artifact store**: Automatic tracking of datasets, models, metrics between steps
- **Metadata**: Built-in experiment tracking and lineage
- **KFServing**: Integrated model serving with canary rollouts

**Strengths**: ML-native, artifact lineage, GPU scheduling via K8s, reproducibility.
**Weaknesses**: Requires Kubernetes expertise, steeper learning curve, smaller community than Airflow.

### Design Patterns for ML Pipelines
- **Idempotency**: Every step should produce the same output for the same input. Use deterministic seeds, versioned data, pinned dependencies.
- **Checkpoint and resume**: Long training jobs must checkpoint; orchestrator should resume from last successful step on failure.
- **Dynamic pipelines**: Generate pipeline structure based on data (e.g., train one model per region).
- **Trigger-based execution**: Retrain on data drift detection, not just on schedule.

## Implementation

```python
# Airflow DAG for ML training pipeline
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.cncf.kubernetes.operators.pod import (
    KubernetesPodOperator,
)
from datetime import datetime, timedelta

dag = DAG(
    "ml_training_pipeline",
    schedule_interval="@daily",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    default_args={"retries": 2, "retry_delay": timedelta(minutes=5)},
)

validate_data = PythonOperator(
    task_id="validate_data",
    python_callable=run_data_validation,
    dag=dag,
)

train_model = KubernetesPodOperator(
    task_id="train_model",
    image="ml-training:latest",
    arguments=["--config", "prod.yaml"],
    resources={"limits": {"nvidia.com/gpu": "4"}},
    dag=dag,
)

validate_data >> train_model
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Fan-out / fan-in | Train multiple model variants in parallel | Parallelize independent steps, merge at evaluation |
| Sensor-triggered | Retrain when new data lands in S3 | Event-driven > time-driven for data freshness |
| Branching | Conditional deployment based on eval metrics | Only deploy if model beats production baseline |
| Backfill | Reprocess historical data with updated pipeline | Must handle idempotent writes to avoid duplicates |

### Common Interview Questions
- [ ] How would you design an ML pipeline that retrains daily and auto-deploys if metrics improve?
- [ ] Compare Airflow vs Kubeflow Pipelines for ML workflows
- [ ] How do you handle a training step that takes 12 hours and might fail?
- [ ] How do you ensure reproducibility in ML pipelines?
- [ ] Design a pipeline that trains models per-region and deploys the best for each.

## Comparisons

| Aspect | Airflow | Kubeflow Pipelines | Dagster | Prefect |
|--------|---------|-------------------|---------|---------|
| ML-native | No | Yes | Partial (+ integration) | No |
| Artifact tracking | No (use MLflow) | Built-in | Built-in (assets) | No |
| GPU scheduling | Via K8s operator | Native (K8s) | Via K8s | Via K8s |
| UI | Good (DAG view, logs) | Good (run comparison) | Excellent (asset graph) | Good |
| Community | Largest | Medium | Growing | Medium |
| Learning curve | Medium | High (needs K8s) | Low-Medium | Low |

## Key Takeaways
- [ ] Airflow for data-engineering-heavy pipelines with ML steps; Kubeflow for ML-native workflows on K8s
- [ ] Every ML pipeline step must be idempotent and produce versioned artifacts
- [ ] Design for failure: retries, checkpointing, and alerting are not optional for multi-hour training jobs
- [ ] Separate orchestration from execution: orchestrator schedules, K8s/Spark/GPU clusters execute
- [ ] Monitoring pipeline health (step duration trends, failure rates) is as important as model metrics
"""

CONTENT["pillar5.ml_pipeline_ops.cicd_for_ml"] = r"""# CI/CD for ML

## Overview
CI/CD for ML extends traditional software CI/CD to handle the unique challenges of ML systems: code, data, and model artifacts all change independently and can each cause regressions. Senior MLE interviews test your ability to design automated pipelines that validate all three dimensions before deploying model updates to production.

## Core Concepts

### ML-Specific CI/CD Challenges
Unlike traditional software:
- **Data is a first-class artifact**: A code change can be correct but produce a bad model if data changed
- **Model quality is probabilistic**: Tests cannot deterministically assert correctness; need statistical validation
- **Training is expensive**: Full retraining on every commit is impractical; need efficient validation strategies
- **Reproducibility requires more than code**: Must pin data version, random seeds, dependency versions, hardware config

### CI Pipeline Stages for ML
1. **Code quality**: Lint, type-check, unit tests (standard CI)
2. **Data validation**: Schema checks, distribution tests on new data
3. **Fast model tests**: Train on small data subset, verify metrics are in expected range
4. **Integration tests**: End-to-end pipeline with synthetic data, verify serving compatibility
5. **Full training** (triggered, not on every commit): Train on full data, evaluate against baselines

### CD Pipeline Stages for ML
1. **Model validation**: Compare metrics against production model on holdout set
2. **Shadow deployment**: Run new model alongside production, compare predictions
3. **Canary rollout**: Route small traffic percentage to new model, monitor metrics
4. **Full rollout**: Gradually increase traffic; automated rollback on metric degradation

### Model Registry as Deployment Gate
The model registry acts as the handoff point between training and serving:
- **Staging**: Model passed automated validation
- **Production**: Model approved (manual or automated) for serving
- **Archived**: Previous production model, kept for rollback

## Implementation

```python
# GitHub Actions CI for ML (simplified .github/workflows/ml_ci.yml)
#
# name: ML CI Pipeline
# on: [push, pull_request]
# jobs:
#   code-quality:
#     runs-on: ubuntu-latest
#     steps:
#       - uses: actions/checkout@v4
#       - run: pip install ruff mypy pytest
#       - run: ruff check src/
#       - run: mypy src/ --ignore-missing-imports
#       - run: pytest tests/unit/ -v
#
#   model-smoke-test:
#     runs-on: ubuntu-latest
#     needs: code-quality
#     steps:
#       - uses: actions/checkout@v4
#       - run: pip install -r requirements.txt
#       - run: python train.py --data tests/fixtures/small.csv --smoke-test
#       - run: python evaluate.py --model output/model.pt --min-accuracy 0.5
#
#   integration-test:
#     runs-on: ubuntu-latest
#     needs: model-smoke-test
#     steps:
#       - run: python serve.py --model output/model.pt &
#       - run: python tests/integration/test_serving.py
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Smoke training | Every PR | Train on tiny data, verify pipeline does not crash |
| Metric gate | Before production deployment | New model must beat baseline by statistically significant margin |
| Shadow scoring | High-risk model changes | Compare predictions without user impact |
| Canary release | Gradual rollout | Route 1% then 5% then 25% then 100% with metric monitoring |
| Feature flag | A/B testing models | Decouple deployment from release; instant rollback |

### Common Interview Questions
- [ ] How would you design a CI/CD pipeline for an ML system with daily retraining?
- [ ] What tests should run on every PR for an ML project?
- [ ] How do you determine if a new model is "better enough" to deploy?
- [ ] How do you handle rollback when a deployed model causes metric regression?
- [ ] Design an automated system that retrains, validates, and deploys models without human intervention.

## Comparisons

| Aspect | Traditional CI/CD | ML CI/CD |
|--------|-------------------|----------|
| Artifact | Code binary | Code + Data + Model |
| Tests | Deterministic pass/fail | Statistical (metrics in range) |
| Build time | Minutes | Hours (training) |
| Rollback trigger | Crash / error | Metric degradation |
| Environment | Code + deps | Code + deps + data + hardware |
| Versioning | Git | Git + DVC + model registry |

## Key Takeaways
- [ ] CI for ML must validate code, data, AND model quality -- code passing tests is insufficient
- [ ] Use smoke training (small data, few epochs) in CI; reserve full training for scheduled or triggered runs
- [ ] Canary deployments with automated rollback are essential for production ML systems
- [ ] The model registry is the single source of truth for what is deployed and what is staged
- [ ] Version everything: code (git), data (DVC/Delta Lake), models (registry), configs (git)
"""

CONTENT["pillar5.ml_pipeline_ops.monitoring"] = r"""# Model Monitoring & Drift Detection

## Overview
Model monitoring ensures deployed models continue to perform as expected after deployment. Unlike traditional software, ML models degrade silently as the world changes around them. Senior MLE interviews test your ability to design monitoring systems that detect degradation early and trigger appropriate responses, from alerts to automated retraining.

## Core Concepts

### Types of ML Drift

**Data drift (covariate shift)**: Input feature distribution $P(X)$ changes. Example: user demographics shift after marketing campaign. Detectable without labels.

**Concept drift**: Relationship $P(Y|X)$ changes. Example: click-through patterns change due to UI redesign. Requires labels to detect directly.

**Prediction drift**: Model output distribution $P(\hat{Y})$ changes. Proxy for concept drift when labels are delayed.

**Label drift**: Target distribution $P(Y)$ changes. Example: fraud rate increases during holiday season.

### Detection Methods

**Statistical tests for continuous features**:
- Kolmogorov-Smirnov test: Compare CDFs, sensitive to any distributional change
- Wasserstein distance: Measures "earth mover's distance" between distributions
- Population Stability Index (PSI): Binned comparison, common in finance

**Statistical tests for categorical features**:
- Chi-squared test: Compare observed vs expected frequencies
- Jensen-Shannon divergence: Symmetric version of KL divergence

$$
\text{JSD}(P \| Q) = \frac{1}{2} \text{KL}(P \| M) + \frac{1}{2} \text{KL}(Q \| M), \quad M = \frac{P + Q}{2}
$$

### Monitoring Architecture
1. **Logging layer**: Capture inputs, predictions, and (eventually) ground truth labels
2. **Feature store monitoring**: Track feature freshness, null rates, distribution stats
3. **Model performance monitoring**: Track business metrics (CTR, conversion) and model metrics (accuracy, AUC)
4. **Alerting layer**: Threshold-based and anomaly-based alerts with appropriate severity levels
5. **Response layer**: Automated retraining triggers, model rollback, human escalation

### Ground Truth Delay Problem
In many applications (ad clicks, loan defaults, churn), ground truth labels arrive days or months after prediction. Strategies:
- Monitor input features and prediction distribution (no labels needed)
- Use proxy metrics with faster feedback loops
- Sample and label a subset for rapid evaluation
- Design feedback loops to accelerate label collection

## Implementation

```python
# Drift detection with Evidently AI
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset
from evidently.metrics import (
    ColumnDriftMetric,
    DatasetDriftMetric,
)

report = Report(metrics=[
    DataDriftPreset(),
    ColumnDriftMetric(column_name="user_age"),
    DatasetDriftMetric(),
])

report.run(
    reference_data=training_df,
    current_data=production_df,
)

# Extract drift results programmatically
results = report.as_dict()
dataset_drift = results["metrics"][2]["result"]["dataset_drift"]
if dataset_drift:
    trigger_retraining_pipeline()
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Feature-level drift | Continuous monitoring without labels | Detect upstream data changes early |
| Prediction distribution | When labels are delayed | Shift in P(Y-hat) suggests concept drift |
| Performance window | When labels are available (with delay) | Compare rolling metric window to baseline |
| Canary monitoring | After model deployment | Compare new model metrics to old model in real-time |

### Common Interview Questions
- [ ] How would you detect model degradation when ground truth labels are delayed by 30 days?
- [ ] What is the difference between data drift and concept drift, and how do you handle each?
- [ ] Design a monitoring system for a recommendation model serving 10M users
- [ ] How do you set alert thresholds to balance sensitivity vs false alarm rate?
- [ ] When should you retrain vs roll back a degraded model?

## Comparisons

| Aspect | Evidently | Whylogs | NannyML | Fiddler |
|--------|-----------|---------|---------|---------|
| Drift detection | Statistical tests | Profile-based | Confidence-based (CBPE) | Statistical + ML |
| Performance estimation | No (needs labels) | No | Yes (label-free) | Yes |
| Real-time | Batch reports | Streaming profiles | Batch | Real-time |
| Hosting | OSS (self-hosted) | OSS + WhyLabs SaaS | OSS + Cloud | SaaS |
| Visualization | HTML reports | WhyLabs dashboard | Built-in plots | Dashboard |

## Key Takeaways
- [ ] Monitor features AND predictions -- feature drift is detectable immediately; concept drift requires labels or proxies
- [ ] Design for delayed labels: most real-world systems cannot compute accuracy in real-time
- [ ] Set adaptive thresholds based on historical variation, not fixed values -- seasonality creates false alarms
- [ ] Automate the response: drift detected -> trigger retraining pipeline -> validate -> deploy (with human gate for high-risk models)
- [ ] Log everything: inputs, features, predictions, latency, and (eventually) outcomes -- you cannot monitor what you do not log
"""

CONTENT["pillar5.ml_pipeline_ops.containerization"] = r"""# Containerization (Docker, K8s)

## Overview
Containerization is the foundation of reproducible, scalable ML infrastructure. Docker packages ML environments into portable images, and Kubernetes orchestrates their execution across clusters. Senior MLE interviews test your ability to design containerized ML workloads that handle GPU scheduling, resource isolation, and multi-stage pipelines efficiently.

## Core Concepts

### Docker for ML
ML Docker images have unique challenges: large base images (CUDA, cuDNN), dependency conflicts between frameworks, and reproducibility requirements.

**Multi-stage builds**: Separate build dependencies from runtime to reduce image size:
- Build stage: Install compilers, build wheels
- Runtime stage: Copy only compiled packages + model artifacts
- Typical reduction: 8GB build image -> 3GB runtime image

**Layer caching strategy**: Order Dockerfile instructions from least to most frequently changed:
1. Base image (CUDA, OS)
2. System packages
3. Python dependencies (requirements.txt)
4. Application code
5. Model artifacts (or download at runtime)

### Kubernetes for ML Workloads

**GPU scheduling**: K8s supports GPU resources via device plugins (NVIDIA GPU Operator).
- Request GPUs: `resources.limits: {"nvidia.com/gpu": 4}`
- GPU sharing: MIG (Multi-Instance GPU) on A100 partitions a single GPU into isolated instances
- Topology-aware scheduling: Place pods on nodes with NVLink connectivity for distributed training

**Key K8s resources for ML**:
- **Job**: One-off training runs with completion tracking
- **CronJob**: Scheduled retraining
- **StatefulSet**: Distributed training with stable pod identities
- **PersistentVolumeClaim**: Mount shared storage for datasets and checkpoints

### ML-Specific K8s Tools
- **KServe (formerly KFServing)**: Serverless model serving on K8s with autoscaling, canary rollouts
- **Volcano**: Batch scheduling for ML/HPC; gang scheduling ensures all pods for a distributed job start together
- **NVIDIA GPU Operator**: Automates GPU driver + container toolkit installation
- **Kueue**: Job queuing and resource quota management for multi-tenant GPU clusters

### Resource Management
- **Requests vs Limits**: Set CPU/memory requests (guaranteed minimum) and limits (maximum). For GPU, request == limit (GPUs are not overcommittable).
- **Node affinity**: Pin GPU workloads to GPU nodes; prevent CPU workloads from occupying GPU nodes.
- **Priority classes**: Ensure production serving gets resources before development training jobs.
- **Spot/preemptible instances**: Use for training (with checkpointing); never for serving.

## Implementation

```dockerfile
# Multi-stage Dockerfile for ML serving
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04 AS base

# Install Python (changes rarely)
RUN apt-get update && apt-get install -y python3.11 python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies (changes occasionally)
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application code (changes frequently)
COPY src/ /app/src/

# Copy model artifact (or download from model registry)
COPY model/ /app/model/

WORKDIR /app
EXPOSE 8080
CMD ["python3", "-m", "uvicorn", "src.serve:app", "--host", "0.0.0.0", "--port", "8080"]
```

```yaml
# K8s deployment for model serving
apiVersion: apps/v1
kind: Deployment
metadata:
  name: model-serving
spec:
  replicas: 3
  selector:
    matchLabels:
      app: model-serving
  template:
    spec:
      containers:
      - name: model-server
        image: registry/model-serving:v1.2.3
        resources:
          requests:
            cpu: "2"
            memory: "8Gi"
            nvidia.com/gpu: "1"
          limits:
            cpu: "4"
            memory: "16Gi"
            nvidia.com/gpu: "1"
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
      nodeSelector:
        gpu-type: a100
```

## Interview Patterns

| Pattern | When to Use | Key Insight |
|---------|------------|-------------|
| Multi-stage Docker build | Production ML images | Separate build deps from runtime; reduce image size 2-3x |
| Init containers | Model download before serving | Download model from registry before main container starts |
| Sidecar pattern | Logging, monitoring, feature fetching | Decouple infra concerns from ML application |
| Gang scheduling | Distributed training | All workers must start together or not at all |
| HPA + GPU metrics | Auto-scale serving | Scale on GPU utilization or request queue depth |

### Common Interview Questions
- [ ] How would you containerize an ML training pipeline that requires 8 GPUs across 2 nodes?
- [ ] Design a K8s deployment strategy for a model serving system with 99.9% uptime SLA
- [ ] How do you handle GPU resource contention in a multi-tenant cluster?
- [ ] What is the difference between a K8s Job and a Deployment for ML workloads?
- [ ] How do you manage model artifacts in a containerized serving environment?

## Comparisons

| Aspect | Bare Metal | Docker + Compose | Kubernetes | Managed K8s (EKS/GKE) |
|--------|-----------|-----------------|------------|------------------------|
| Setup complexity | Low | Low | High | Medium |
| Scaling | Manual | Manual | Automatic (HPA) | Automatic |
| GPU support | Direct | nvidia-docker | GPU Operator | Pre-configured |
| Fault tolerance | None | Restart policies | Self-healing (pods) | Self-healing + node repair |
| Multi-tenancy | Shared env (conflicts) | Isolated containers | Namespaces + quotas | Namespaces + IAM |
| Best for | Single-user dev | Small team / local | Production at scale | Production (reduced ops) |

## Key Takeaways
- [ ] Optimize Docker images for ML: multi-stage builds, layer caching, and pin CUDA/cuDNN versions exactly
- [ ] K8s GPU scheduling is not-overcommittable -- plan capacity carefully and use priority classes
- [ ] Use gang scheduling (Volcano) for distributed training to prevent resource deadlocks
- [ ] Separate training (Jobs, spot instances, checkpointing) from serving (Deployments, on-demand, HA) infrastructure
- [ ] Health checks and readiness probes are critical for ML serving -- model loading can take minutes
"""

# ---------------------------------------------------------------------------
# Main: Write content to database
# ---------------------------------------------------------------------------


def main() -> None:
    """Populate framework_nodes with Pillar 5 content."""
    engine = get_engine()
    SessionLocal.configure(bind=engine)

    with SessionLocal() as db:
        updated = 0
        missing = []

        for path, content in CONTENT.items():
            node = db.query(FrameworkNode).filter(
                FrameworkNode.path == path
            ).first()
            if node is None:
                missing.append(path)
                continue

            node.description = content.strip()
            updated += 1

        db.commit()

    print(f"Updated {updated} framework nodes.")
    if missing:
        print(f"WARNING: {len(missing)} paths not found: {missing}")
    print("Done.")


if __name__ == "__main__":
    main()
