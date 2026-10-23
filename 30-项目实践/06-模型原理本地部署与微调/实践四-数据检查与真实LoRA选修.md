# 实践四：数据检查与真实 LoRA 选修

[项目入口](README.md) · [上一项](实践三-Ollama本地模型调用.md)

本实践先检查数据，再按需在真实模型上训练。plan 无需依赖；train/evaluate 会加载模型，并可能联网下载权重。此次整理未执行真实训练，不把下面的选修流程标为已跑通。

## 1. 明确这次适配什么

只学习把概念输出为“概念：…；一句话：…”的格式。示例20条全部为本库自写，train/validation/test 为12/4/4。数量很少，仅用于检查流程；基座可能已能完成任务，微调可能无收益或退步。

不自动读取 MindVault、不把私人笔记送去训练。自己的数据要核对使用权、正确性、敏感内容与跨分组近义重复。

## 2. 只做数据与配置计划

```powershell
$advanced = '.\30-项目实践\06-模型原理本地部署与微调'
python "$advanced\lora_experiment.py" --mode plan --output '.local/advanced/lora-plan-v1'
```

查看 plan.json 的数量、摘要与默认设置：CPU、FP32、8步、batch size1、学习率2e-4、max_length256、rank4、alpha8。8步不等于完整跑完12条数据，也不是训练效果推荐值。

plan 检查角色、字段和完全重复问题，不安装依赖、不验证真实 Tokenizer、不读取模型、不训练。它会检查测试文件格式，但不会用测试集更新参数或请求模型。

## 3. 准备独立真实训练环境

先确认资源，再创建环境。CPU 方式可参考[PyTorch 安装选择器](https://pytorch.org/get-started/locally/)选择当前 Windows/Pip/Python/CPU 对应命令；下面是 CPU 索引安装方式，实际兼容性需核对：

```powershell
python -m venv '.local/lora-venv'
$loraPython = '.\.local\lora-venv\Scripts\python.exe'
& $loraPython -m pip install torch --index-url https://download.pytorch.org/whl/cpu
& $loraPython -m pip install transformers peft
& $loraPython -m pip freeze > '.local/lora-dependencies.txt'
```

如果使用 CUDA，改按 PyTorch 选择器匹配驱动与运行库，不复用 CPU 安装命令。Datawhale self-llm 主线为 Linux；不能把其服务器路径和显卡编号直接复制到当前 Windows 环境。依赖安装失败时先解决版本支持，不影响前面的标准库练习。

基座为 [Qwen/Qwen2.5-0.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct)，固定 revision `7ae557604adf67be50417f59c2c2f167def9a775`。2026-10-23 从[官方模型元数据](https://huggingface.co/api/models/Qwen/Qwen2.5-0.5B-Instruct)核查为公开、非 gated 模型；模型卡标示 Apache-2.0。使用时仍需按当前许可证与依赖条件核对。

FP32 的权重本身约为参数数×4字节，还需激活、优化器和运行空间；CPU训练可能较慢，当前未测资源或耗时。不要求先租 GPU，也不自动创建云资源。默认不使用 QLoRA/bitsandbytes。

## 4. 准备好后显式训练

```powershell
& $loraPython "$advanced\lora_experiment.py" --mode train --device cpu --steps 8 --output '.local/advanced/real-lora-v1'
```

仅此步骤进入真实模型加载/训练。脚本使用官方聊天模板，确认问题前缀一致，将问题 labels 设为-100，只对回答计算损失；超长样本报错，不静默截断回答。

它先测基座验证损失，再冻结基座、训练 q_proj/v_proj 的 LoRA，最后再测验证损失。训练只使用 train；validation 只评估；test 没有进入模型。CPU最多使用4个 PyTorch线程，CUDA模式需明确指定且先验证可用性。

输出包含 adapter、tokenizer 和 run.json（基座、revision、数据摘要、依赖版本、超参数和训练记录）。当前只保存最终适配器，不支持优化器断点续训；失败时保留目录排查，再用新输出名重试。

## 5. 固定方案后单独评估测试集

```powershell
& $loraPython "$advanced\lora_experiment.py" --mode evaluate --device cpu --run-dir '.local/advanced/real-lora-v1' --output '.local/advanced/real-lora-test-v1'
```

必须保留同一数据版本、max_length 和依赖版本；脚本校验产物摘要与基座兼容，再用相同测试题分别生成基座/适配后答案。训练用自定义 max_length 时，评估也传相同值。

comparison.json 同时记录平均示例回答 Token 损失与实际答案，人工评分留空。该 loss 是各样本平均，不是事实正确率。检查格式、事实、遗漏、拒答和通用能力退步，不只看 loss 是否下降。

## 6. 保存与后续扩展

权重、适配器、Tokenizer 与环境都保留在 `.local/`。将[实验记录](进阶实验记录模板.md)复制到复盘目录，只保存摘要、来源和结论；不要把模型缓存推到笔记仓库。

适配器不能直接导入当前 Ollama 分支。合并、转格式、量化、导出与特定引擎适配需另行核对工具支持，当前未实现。偏好对齐、多卡、完整预训练留作后续阅读，不混入本次验收。

## 验收

- [ ] plan 数量与数据内容核对通过，人工排除泄漏与错误。
- [ ] 真实运行后核对冻结参数、日志、依赖与产物；未运行写未实测。
- [ ] 对同一测试题比较基座和适配后结果，保留一个改善或退步案例。
