# 实际验证 · 2026-10-27 · v2.1

本文件区分脚本契约、真实模型行为与尚未验证的范围；不把检查返回 0 当成技术审校。

## 脚本与文件契约

本次环境：Linux、CPython 3.12.14、markdown-it-py 4.2.0。
`python -m unittest discover -s tests -q`：**74 项通过**。

- 发布使用 `release-files.txt` 精确清单；人工 `.env.local`、`credentials.json`、无关笔记与未登记外部符号链接不入包。登记的符号链接文件及父目录拒绝。
- 项目和两技能独立归档、安装、研究素材登记与导出、图片格式及引用检查通过。
- 普通 check/build 支持部分稿预览；delivery 检查覆盖范围、删并拆理由、章节/统稿/视觉状态和核心缺口。
- refresh 比较完整补包，保留正文，失效相关复核，删除撤回素材与旧 dist；私改材料快照被拒绝。
- 新增复制失败和双重 rename 失败注入：后者保留原稿备份并报告恢复路径，不再删除唯一原稿。
- 三章研究缩成一章仍保留初始范围；不能删除旧 coverage 项逃避删章理由。
- 独立写作技能与素材包的脚本隔离测试禁止 Python socket；HTML 默认不调用 PDF。
- 两份 SKILL.md 通过 skill-creator quick_validate；两技能均关闭隐式调用。

## 真实研究与配图

案例：`examples/priority-queue/research`，仅研究 boltons 的优先队列模块，两章。
固定 commit：`d31d821d56c8f7756af9c30a864077f2e5855321`。

实际执行主代理综合、独立源码调查、外部一手资料调查和未参与采集的独立审校；角色与证据见研究 review.md。
源码来自固定版本，必要代码与 BSD 许可随包；直接调用上游两个测试函数及自编探针，独立审校再次运行得到一致输出。pytest 未安装，因此不声称全套 pytest 通过。

- 两张图实际采用 diagram-design，上游 commit `97d795138448f6a739a0cebc3d9beb37a42077f1`；self_check 与 export_svg 实跑。HTML/SVG 原件随包。
- 一张概念插画由内置 imagegen 实际生成，PNG 与真实提示词随包。仅作隐喻，不证明技术事实。
- 研究时浏览器 CDN 下载损坏，改用 CairoSVG 渲染，研究者与独立审校实际查看中文、箭头、图例与简化边界。
- 后续 HTML 检查使用 npm 分发的 Chromium 153.0.8010.0 与 Playwright 1.57.0；字体只安装在环境，不入发布包。

## 独立写作、错误发现与缺口恢复

写作者在全新上下文中只接收独立写作技能与研究包，没有继承研究会话。它按委托不联网、不读取其他项目，不重做研究。

1. 单独输入副本故意缺少更新异常路径的关键证据，且移除原始 evidence 内容。文件检查通过不等于材料足够。
2. 写作者识别“新优先级转换失败是否保留旧任务”的 G1，发现来源索引与实际文件不一致，继续独立内容；两章草稿与 HTML 可构建，完整交付被拒绝。
3. 完整补包经 refresh 比较并应用；两章正文 SHA-256 完全不变，旧 dist 移除，共享证据变化使两章待复核。原始记录见 validation/recovery-results.json。
4. 写作者依据补回源码/运行输出修订既有正文、题注与证据范围说明，保留叙事并处理 G1。最终结果见 publication/writing-review.md。
5. 另一个全新审校上下文从原始代码发现故意植入的“默认堆且堆数组整体有序”错误，并给出代码位置和运行反例。见 validation/claims.md、findings.md。

注入方法、原始草稿及复核记录见 `examples/priority-queue/validation/`。注入对写作者未泄漏标准答案；明确缺证的输入不等于覆盖所有隐蔽证据缺口。

## 出版视觉与边界

旧 mini-pipeline 示例本次重新构建 HTML，1440px/390px 视口均无页面级横向溢出，四图加载成功。新案例三图均加载；首次发现来源裸 URL/commit 导致 390px 下 scrollWidth=799，修复正文长文本换行后 1440px/390px 均无页面级溢出。已实际查看插图、正文、表格及来源附录；详情见 publication/writing-review.md。

独立上下文仍使用同一宿主模型，不是不同厂商模型；写作阶段的禁网是任务约束，只有脚本隔离单测硬禁 socket。未声称独立进程/权限沙箱。
尚未验证其他模型长篇写作、大型仓库、Windows/macOS 实跑、读者学习效果或多轮统计稳定性。
本次不生成 PDF；v2 曾记录的 PDF 测试不计入此次回归。
