# 实际图像制作与核对记录

2026-10-27，研究整合 agent。父任务委派已指定真实 diagram-design 导出与离线静态图。

- 从 GitHub connector 按 97d795138448f6a739a0cebc3d9beb37a42077f1 读取 diagram-design SKILL.md，type-flowchart、type-state、semantic-patterns、style-guide、output-spec、export 规范。实际保存 scripts/self_check.py 和 scripts/export_svg.py 到临时上游目录，无代码修改。
- 绘图风格采用 repo-to-research/assets/diagram-style.md 已有中文书籍自定义皮肤（白纸、蓝灰墨、青色强调、系统字体），未套用需询问的默认品牌皮肤、未修改用户全局样式。960×600 画布；22/18px 本地书籍字号覆盖上游通用小字阶。图 1-1 为流程图；图 2-1 为普通状态图，未虚构等待/失败/执行状态。
- 实际命令（在仓库根，用绝对路径也执行过）：

```sh
python skills/repo-to-research/scripts/figure.py import examples/priority-queue/research/chapters/01-lifecycle/assets/fig-01-01.html --diagram-skill /workspace/scratch/068517fd0265/diagram-upstream
python skills/repo-to-research/scripts/figure.py import examples/priority-queue/research/chapters/02-removal/assets/fig-02-01.html --diagram-skill /workspace/scratch/068517fd0265/diagram-upstream
```

两次实际返回 OK，并调用上游 export_svg.py --system-fonts 生成真实 SVG；没有自制导出器或 mock。

- 浏览器预览失败：初始无 playwright；pip install playwright 成功（1.64.1），但 `python -m playwright install chromium` 下载 zip 截断（End of central directory record signature not found）；figure.py preview 随后因浏览器不存在退出 2。未把失败当成功。
- 为视觉校对，安装 CairoSVG 2.9.1；从 notofonts/noto-cjk 官方 raw 路径取得 NotoSansCJKsc-Regular.otf 到环境字体目录并 fc-cache。字体未打包。实际 `cairosvg.svg2png(url=..., write_to=...)` 分别生成 /workspace/scratch/068517fd0265/pq-01.png 和 pq-02.png。仅渲染器换成 CairoSVG，不改变 diagram-design 方法或导出的 SVG。
- 用 view_image 实际查看两张 PNG：中文无缺字，三步主路径与两个后续访问节点清楚；状态图的逻辑删除/物理清理分开，三条箭头无交叉、文字没有遮挡。章节 1 pop 节点文字较满但完整且可读。未验证浏览器窄屏交互、印刷实机与所有 SVG 客户端。
- imagegen 由父任务 /root 实际调用，真实生成位图复制到 fig-01-02.png，实际 prompt 保存。研究整合 agent 再用 view_image 查看：调度员挑红卡、蓝卡等待，无字、无代码、无箭头。此图是概念隐喻；不能证明源码排序结构或精确数量。

## 上游脚本 SHA-256
- self_check.py: `779e914fef1f1b19b9cc08d649e8afbd169e8574fba39ed724de89084b7dcede`
- export_svg.py: `331fee38c37ea4e6003176b5b68252fc5775f2940a7e32fdd5348febaf002f82`
