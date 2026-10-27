# v2：研究与写作分离

## 已确认需求

两个技能独立安装和调用。repo-to-research 运行于 Codex，主 agent 规划，
源码/外部研究子 agent 深挖各章，默认使用 diagram-design 与内置 imagegen 按语义完成实际图像。
阶段一交付完整素材后停止。repo-to-book 由用户另行调用，可以交给其他模型，
只写作、衔接、图文编排和出版；源稿目录保留，默认 HTML，PDF 可选。

## 接口选择

普通文件目录作为边界：plan.md 定范围，sources.md 定来源，materials.md 定每章依据，
assets/ 存实际图片，research.json 只做顺序/文件/状态索引，review.md 记录实际执行和局限。
不把整个源码项目、聊天或工具会话传给写作模型。不以纯 URL/提示词替代素材。

只保留 draft/ready 和图片 pending/ready。ready 是执行者对齐备性的声明，
程序检查实际文件与引用，不证明事实、模型质量和工具身份。没有新的任务状态机或代理服务。

## 职责

研究主 agent 不再是最终作者。源码/外部调查按问题切分，研究员交证据，主 agent 合并冲突和图义。
独立核验者回原始依据，不只审摘要。不同 agent 不等于不同独立来源。
写作主编统一叙事；不默认让每个章节由一个新 agent 各写一篇，不重新搜集资料。

## 图解

精确机制优先 diagram-design；概念性位图优先内置 imagegen。
图与标题、来源、读图说明、简化范围一起交接；imagegen 不证明源码或数值。
外部工具缺失时不自动偷偷回退。需要用户批准的替代显式记录，不能伪造原工具完成记录。

## 出版

写作目录是输入材料的独立副本，加 manuscript/、book.json、writing-review.md、dist/。
HTML 使用本地图片内嵌，首次安装只需 Markdown 解析库；PDF 另加浏览器。
纯聊天模型可写 Markdown，执行出版需要有文件/终端的环境；跨平台能力不等于无工具限制。

## 不做

不增加模型 API runner、多 agent 调度库、数据库、RAG、自动续写服务或阶段自动串联。
不复制金融专用闸门、固定图片配额和风格禁词库。术语、主线、证据和图义由模型负责。

## 迁移

旧版一体式 repo-to-book 改为 skills/ 下两个独立包；旧书稿仍能由 book.py 构建。
旧素材若只有 plan/sources/chapters，需要实际补分章材料和图片索引，不机械“迁移”成 ready。
安装时不覆盖旧技能，用户先备份移开。两个运行包各含相同 handoff.py，以便独立分发；测试核对一致。
