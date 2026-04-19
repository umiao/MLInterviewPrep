# Computer Vision Systems

## Overview

**Computer Vision Systems** (计算机视觉系统) 设计涵盖构建生产级的图像分类、目标检测、语义分割和视觉搜索管道。常见于自动驾驶公司、Meta、Google、Amazon（视觉搜索）等。资深 MLE 必须设计能够处理高吞吐量图像处理且满足严格延迟要求的系统。

视觉系统的独特挑战在于：输入数据维度极高（一张 1080p 图像约 600 万像素），模型计算密集度远超文本模型，且对实时性要求严格（自动驾驶需要 30fps 以上的推理速度）。

## Core Concepts

### CV Pipeline Architecture

生产级视觉系统的标准管道：

```
图像输入 -> [Pre-processing（预处理）] -> [Feature Extraction / Backbone（特征提取/骨干网络）]
    -> [Task Head（任务头）] -> [Post-processing（后处理）] -> [Serving（服务）]
```

预处理包括图像解码、缩放、归一化和数据增强。骨干网络负责提取通用视觉特征，任务头针对具体任务（分类、检测等）进行预测。

### Model Architecture Choices

不同视觉任务对应的主流架构：

| 任务 | 架构 | 输出 |
|------|------|------|
| 分类 | ResNet, EfficientNet, **Vision Transformer** (ViT, 视觉变换器) | 类别概率 |
| 检测 | **You Only Look Once** (YOLO, 实时目标检测), DETR, Faster R-CNN | 边界框 + 类别 |
| 分割 | Mask R-CNN, **Segment Anything Model** (SAM, 通用分割模型) | 像素级掩码 |
| 视觉搜索 | **Convolutional Neural Network** (CNN, 卷积神经网络)/ViT 骨干网络 + Embedding | 特征向量用于 **Approximate Nearest Neighbor** (ANN, 近似最近邻) |

### Object Detection Metrics

目标检测使用 **Average Precision** (AP, 平均精度) 作为核心指标：

$$
\text{AP} = \int_0^1 p(r) \, dr
$$

其中 $p(r)$ 是在召回率 $r$ 处的精度。**mean Average Precision** (mAP, 平均精度均值) 对所有类别的 AP 取平均。

**Intersection over Union** (IoU, 交并比)：

$$
\text{IoU} = \frac{|B_{\text{pred}} \cap B_{\text{gt}}|}{|B_{\text{pred}} \cup B_{\text{gt}}|}
$$

当 $\text{IoU} \geq 0.5$ 时判定检测正确（AP@0.5），或在多个阈值上取平均（AP@[.5:.95]）。COCO 数据集标准使用 AP@[.5:.95] 作为主要评估指标。

### Non-Maximum Suppression (NMS)

**Non-Maximum Suppression** (NMS, 非极大值抑制) 是目标检测后处理的关键步骤，用于去除重复检测框：

```
1. 按置信度分数降序排列所有检测框
2. 取最高分检测框加入输出
3. 移除与已选框 IoU > 阈值（通常 0.5）的所有检测框
4. 重复直到没有剩余检测框
```

NMS 的变体包括 **Soft Non-Maximum Suppression** (Soft-NMS, 软非极大值抑制)——不直接删除重叠框而是降低其分数，在密集场景下效果更好。

### Serving Considerations

生产环境中的模型服务优化：

| 关注点 | 解决方案 |
|--------|---------|
| 延迟 | TensorRT, ONNX Runtime, 量化 (INT8) |
| 吞吐量 | 批量推理, GPU 共享 (**Multi-Process Service**, MPS, 多进程服务) |
| 图像尺寸 | 缩放/裁剪管道, 大图像分块处理 |
| 模型大小 | **Knowledge Distillation** (知识蒸馏), 剪枝, MobileNet |

量化可将模型大小和推理延迟减少 2-4 倍，精度损失通常在 1% 以内。TensorRT 通过算子融合、内核自动调优等技术进一步加速推理。

### Data Augmentation

数据增强是视觉模型训练中提升泛化能力的关键技术：

| 增强方法 | 描述 | 常用场景 |
|---------|------|---------|
| 随机裁剪/翻转 | 基础几何变换 | 所有任务 |
| Mixup | 线性混合两张图像及其标签 | 分类 |
| CutMix | 将一张图的区域替换到另一张 | 分类 |
| Mosaic | 拼接 4 张图像 | 检测（YOLO） |
| 色彩抖动 | 随机调整亮度/对比度/饱和度 | 所有任务 |

## Implementation

```python
import numpy as np

def nms(
    boxes: np.ndarray,    # (N, 4) [x1, y1, x2, y2]
    scores: np.ndarray,   # (N,)
    iou_threshold: float = 0.5,
) -> list[int]:
    # 非极大值抑制
    order = scores.argsort()[::-1]
    keep = []
    while len(order) > 0:
        i = order[0]
        keep.append(int(i))
        if len(order) == 1:
            break
        rest = order[1:]
        xx1 = np.maximum(boxes[i, 0], boxes[rest, 0])
        yy1 = np.maximum(boxes[i, 1], boxes[rest, 1])
        xx2 = np.minimum(boxes[i, 2], boxes[rest, 2])
        yy2 = np.minimum(boxes[i, 3], boxes[rest, 3])
        inter = np.maximum(0, xx2 - xx1) * np.maximum(0, yy2 - yy1)
        area_i = (boxes[i, 2] - boxes[i, 0]) * (boxes[i, 3] - boxes[i, 1])
        area_r = (boxes[rest, 2] - boxes[rest, 0]) * (boxes[rest, 3] - boxes[rest, 1])
        iou = inter / (area_i + area_r - inter + 1e-8)
        order = rest[iou <= iou_threshold]
    return keep
```

## Interview Patterns

| 模式 | 适用场景 | 核心洞察 |
|------|---------|---------|
| 两阶段检测 | 高精度需求 | 区域提议 + 分类（Faster R-CNN） |
| 单阶段检测 | 实时推理 | YOLO/SSD 用速度换精度 |
| 视觉搜索管道 | 电商、相似图片 | 骨干网络 Embedding + ANN 索引 |
| 边缘部署 | 移动端/IoT | MobileNet + 量化 + TensorRT |
| **Active Learning** (主动学习) | 有限标注 | 不确定性采样优先标注最有价值的样本 |

### Common Interview Questions
- [ ] 设计基于图像的商品搜索系统（Google Lens）
- [ ] 如何构建自动驾驶的实时目标检测系统？
- [ ] 设计图像/视频内容审核系统
- [ ] 如何处理检测任务中的类别不平衡？
- [ ] 设计制造业的视觉质量检测系统

## Comparisons

| 维度 | CNN (ResNet) | ViT | YOLO v8 |
|------|-------------|-----|---------|
| 归纳偏置 | 平移等变性 | 全局注意力 | 无锚框检测 |
| 数据效率 | 好（小数据集） | 需要大量数据 | 预训练后好 |
| 推理速度 | 快 | 中等 | 非常快 |
| 最适用于 | 分类 | 大规模分类 | 实时检测 |

## Key Takeaways
- [ ] 根据延迟 vs 精度的权衡选择架构
- [ ] NMS 和后处理设计显著影响检测质量
- [ ] 模型优化（量化、蒸馏）对生产服务至关重要
- [ ] 视觉搜索 = 骨干网络 Embedding + ANN 索引（与文本搜索相同模式）
- [ ] 数据质量和标注策略通常比模型架构更重要


## Advanced Topics

### Multi-Sensor Fusion

自动驾驶等高级 CV 应用需要多传感器融合：

| 传感器 | 优势 | 劣势 | 数据格式 |
|--------|------|------|----------|
| **Camera** (摄像头) | 颜色、纹理、语义丰富 | 受光照影响大 | 2D 图像 |
| **Light Detection and Ranging** (LiDAR, 激光雷达) | 精确 3D 距离测量 | 昂贵、点云稀疏 | 3D 点云 |
| **Radar** (毫米波雷达) | 全天候、测速准确 | 分辨率低 | 距离-速度图 |

融合策略分为 **Early Fusion** (前融合)（特征级拼接）、**Late Fusion** (后融合)（决策级融合）和 **Mid Fusion** (中融合)（中间层交互），BEVFusion 等方法在统一的 **Bird's Eye View** (BEV, 鸟瞰图) 空间进行多模态融合。

### Data Flywheel for CV

**Data Flywheel** (数据飞轮) 是 CV 系统持续改进的核心机制：部署模型到生产环境 -> 自动收集模型预测困难或不确定的样本 -> 人工标注这些困难样本 -> 加入训练集重新训练 -> 部署更强的模型。Tesla 的自动驾驶系统通过全球车队持续收集数据就是数据飞轮的典型案例。关键技术包括 Active Learning 选择最有价值的样本进行标注，以及 **Auto-labeling** (自动标注) 用强模型给弱模型生成伪标签。

### Edge Deployment Optimization

CV 模型在边缘设备（手机、摄像头、车载芯片）上部署需要深度优化。MobileNet 使用 **Depthwise Separable Convolution** (深度可分离卷积) 将标准卷积的计算量减少约

$$
8\text{-}9\times
$$

倍。**Neural Architecture Search** (NAS, 神经架构搜索) 可以自动设计在特定硬件约束下最优的模型架构，EfficientNet 就是 NAS 发现的高效架构。部署工具链（TensorRT、CoreML、ONNX Runtime）提供了量化、图优化和硬件特化的推理加速。