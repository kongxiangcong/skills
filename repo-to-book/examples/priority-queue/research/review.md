# 研究审查与交接

状态：ready。两章材料、两个 diagram-design 实际 SVG/HTML、一个真实 imagegen PNG 与实际提示词齐备。仅交付研究，不撰写最终书稿。

## 实际角色分工

- /root/real_research：主线、计划、综合、两张图制作、实际图像查看、结构检查与交接。
- /root/real_research/source：独立源码调查；GitHub connector 固定源码获取、原始许可保留、真实探针与上游两测试函数直接执行。详见 evidence/source-notes.md。
- /root/real_research/external：独立外部调查；官方 Python heapq、float、比较语义背景与反证。详见 evidence/external-notes.md；不以文档替代项目证据。
- /root/real_research/review：未参与事实采集的独立复核；重新读原始 queueutils.py、相关类型/测试、材料与图，独立重跑探针输出一致，实际查看两张渲染图和生成插画。详见 evidence/independent-review.md。
- 父任务 /root：实际内置 imagegen 调用，并提供真实 PNG 路径与 prompt；整合 agent 复制并再次查看。不把父任务调用改写成本子 agent 调用。

角色分离不是不同证据来源，同模型子 agent 的检查也不能消除所有共享偏差。

## 核验发现与修正

核心发现：PriorityQueue 默认是 SortedPriorityQueue/BarrelList，非 HeapPriorityQueue；peek 可清墓碑；len 只数映射；更新另建 entry 与新 count。逐项定位、具体输入、中间状态已写入两章。独立审查无核心阻断项。根据审查小建议，已将默认值案例分清“pop(None) 实测”和“peek(None) 静态源码确认”。

实际两个图经上游 self_check.py + export_svg.py --system-fonts 通过，之后用 CairoSVG 实际渲染并由整合 agent/独立 reviewer 看图，不能将程序返回 0 单独当审图结论。图 1-1 的后续调用箭头可能被误读为 add 内部调用，已在图例与材料双重说明；图 2-1 追踪旧 entry，更新新 entry 在材料说明。图 1-2 仅作优先选择隐喻，无数据结构断言。

## 工具真实性与限制

详见 evidence/figure-production.md。浏览器安装下载损坏，浏览器预览失败；以 CairoSVG 完成真实视觉校对，不声称浏览器测试通过。使用官方 Noto CJK 环境字体，未打包字体。上游工具真实版本/脚本哈希已记。两张图均为 diagram-design 实际导出，不是 static-svg 假冒。

源码测试环境 CPython 3.12.14；pytest 未安装，实际直接调用两个上游测试函数成功；未声称全套 pytest、性能、线程安全或安装测试。证据非完整 checkout，Git blob SHA 与固定 URL 可核对。

非核心未知：NaN 实际返回序列、恶意比较/hash 对象、异常回滚实验、BarrelList 精确复杂度、不同 Python 环境结果。材料明确区分静态推断与运行观察；不阻止窄范围两章写作。

## 最终交接

结构检查与 export 成功才可交付。研究包包含来源文本/必要源码及 BSD 许可；外部文档仅自写摘要，不整包复制受限资料。写作者应以 research.json 顺序阅读，复用现成图，保持上述证据边界。可另行调用 repo-to-book 或交给其他模型；本任务到此停止。
