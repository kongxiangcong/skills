# Repo-to-book · 图书视觉约定

这是本项目的自定义书籍皮肤，不覆盖 diagram-design 的全局默认文件。

| 角色 | 值 |
|---|---|
| paper | #ffffff |
| paper-2 | #f3f6f8 |
| ink | #182b3a |
| muted / soft | #526472 / #617484 |
| rule / rule-solid | #d6e0e6 |
| accent | #176a83 |
| accent-tint | #e8f3f6 |
| link | #176a83 |
| 字体来源 | system，禁止远程 Google Fonts |
| 中文正文与节点 | Noto Sans CJK SC, Microsoft YaHei, PingFang SC, sans-serif |
| 代码／符号 | DejaVu Sans Mono, Consolas, monospace；中文回退到中文无衬线 |

图书模式为浅色、静态、无阴影。每图最多强调一至两个焦点；实线表示当前主路径，虚线含义应由图例声明，不把“可选”和“异步”混为一个语义。全书重复对象保持同色同名。

参考画布 960×560；最终宽度约 170mm。主要节点文字 22px，辅助文字 18px，节点内不放长句。复杂图可以更高，但不要无限变宽后缩进书页。读者需要精确追踪的文字不能用低对比小号字。
