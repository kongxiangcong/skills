# Winson

以温和、鼓励而判断明确的方式，陪你讨论研究方向、技术路线和投入取舍，也帮助你逐步理解复杂概念。

语气来自对Winson交流习惯的整理：看见具体进步，认真提出建议，把下一步变得可行。实际回答根据当前问题生成，不机械复读原话。

## 安装

### 让 Codex 安装

将下面这段话发给 Codex：

```text
$skill-installer 请从 https://github.com/kongxiangcong/skills/tree/main/Winson 安装 Winson 技能到全局技能目录，目标文件夹命名为 winson，并保留 references 下的所有配套文档。
```

如果已经安装，可以直接要求 Codex 从该地址更新现有的 `winson` 技能。

### 手动安装

1. 克隆或下载本仓库。
2. 将整个 `Winson` 文件夹复制到 `$CODEX_HOME/skills/winson`。未设置 `CODEX_HOME` 时，使用用户主目录下的 `.codex/skills/winson`；Windows 示例为 `C:\Users\你的用户名\.codex\skills\winson`。
3. 确认目录结构如下，尤其保留 `references` 中的两份文档：

```text
winson/
├── SKILL.md
├── README.md
└── references/
    ├── winson-voice.md
    └── winson-source-notes.md
```

已有同名技能时，先保留自己的修改，再更新对应文件。安装后在下一轮对话中尝试调用；如果尚未识别，可重新打开 Codex 后再试。

## 使用

在 Codex 输入 `$winson`，接着描述你的问题即可。例如：

```text
$winson 我想研究 NPU 架构评估，但范围太大。请结合我已有的算子模型，和我一起判断先做哪一部分。
```

```text
$winson 我不理解流水线和并行的区别。请从一个简单例子开始，一次讲清一个概念，等我理解后再继续。
```

```text
$winson 这是我的方案和实验结果。请帮我判断哪些结论已经成立，哪些还需要验证，以及下一步最值得做什么。
```

提供当前目标、已有材料和最困惑的地方，会让讨论更具体。可以随时说“这里我还不理解”“先回到主线”或“这次请直接给完整方案”，调整讨论的节奏。

长程讨论会按需维护 `winson-whiteboard.md`，记录目标、证据、判断和下一步，方便后续接着讨论；简单问答无需创建记录。

## 配套文档

- [技能入口](SKILL.md)：研究协作、渐进解释和讨论记录的规则。
- [讨论语气指南](references/winson-voice.md)：不同情境下的表达方式与改写示例。
- [Winson的表达与语境](references/winson-source-notes.md)：原话、背景和风格依据。

使用技能不需要原始聊天导出文件。技能借鉴Winson的表达习惯，不自称他本人，也不把新生成的话当作他的原话。

Codex 技能机制可参考 [OpenAI 官方说明](https://learn.chatgpt.com/docs/build-skills)。
