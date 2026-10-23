# 实践二：小矩阵 LoRA 与适配器

[项目入口](README.md) · [上一项](实践一-注意力与损失数值实验.md) · [下一项](实践三-Ollama本地模型调用.md)

目标：真正更新一对低秩矩阵，观察基座保持不变、增量可以保存重载。这里只处理二维数值，不是语言模型微调，也不是 QLoRA。

## 1. 先看模型与数据

W0 为2×2单位矩阵，rank=1，alpha=1。A 为1×2，B 为2×1；实际代码用长度2列表表示。预测为 `W0x + B(Ax)`。目标映射是自写的 `y=[2x0+2x1, 2x0+5x1]`。

训练用4个输入，验证用另外2个输入；A 使用固定seed的小随机值、B从0开始。脚本手写 MSE 梯度，只更新 A/B，不更新 W0。

## 2. 训练并看报告

```powershell
$advanced = '.\30-项目实践\06-模型原理本地部署与微调'
python "$advanced\toy_lora.py" train --steps 400 --learning-rate 0.03 --output '.local/advanced/toy-v1'
```

打开 report.json，比较 before/after 的 train_mse 和 validation_mse，观察 history。默认例子的目标恰好可以用 rank1 增量表示，误差下降很容易；这不代表真实大模型用少量数据也会得到类似结果。

adapter.json 包含本库格式的 A、B、基座 ID 和基座矩阵。报告中的 base_frozen 对应本实现固定的 W0；不能把该文件交给 PEFT、Ollama 或真实模型。

## 3. 重载并预测

```powershell
python "$advanced\toy_lora.py" infer --adapter '.local/advanced/toy-v1/adapter.json' --x 2 1
```

原始基座输出应为 `[2,1]`，目标为 `[6,9]`，适配后应接近目标。换一个输入，观察数值；本任务是可精确表示的线性映射，不是自然语言泛化评测。

## 4. 做一个小对照

```powershell
python "$advanced\toy_lora.py" train --steps 50 --learning-rate 0.01 --output '.local/advanced/toy-small-lr'
```

这同时改变了步数和学习率，只适合观察流程。要作单变量比较，应固定步数只改学习率，或固定学习率只改步数，再用相同验证输入判断。

## 验收

- [ ] 能说明 A、B 与 W0 的形状与作用。
- [ ] 保存、重载后得到一致预测。
- [ ] 能解释玩具矩阵训练与真实 LoRA 的差异，再读[PEFT LoRA](https://huggingface.co/docs/peft/en/conceptual_guides/lora)。
