# repo-to-write 更新与验证 · 2026-10-27

写作技能由 repo-to-book 改为 repo-to-write，外层项目目录和研究技能不改。读者目标决定章节/段落形式，结构检查先于措辞编辑，细则统一在写作技能 references/writing.md。方法版本与许可在根和独立写作包 THIRD_PARTY_NOTICES.md 中保留，写作运行不依赖网络或上游技能。

## 迁移

备份旧 repo-to-book 安装并移出技能发现目录，再安装 repo-to-write；或使用新的 --dest。安装器不静默覆盖，也不在安装新写作技能时留下冲突旧技能。研究技能可单装。已有研究包和书稿配置兼容，不重做研究。外层 repo-to-book/ 保持不变。

SNAPSHOT.json、SHA256SUMS、DELIVERY_STATUS.md、REPOSITORY_ROOT_README.md 及既有案例 evidence/validation 为 historical v2.1 记录，字节/哈希保持原样；不可当作当前树的校验值。历史记录使用旧技能名。当前安装与示例入口用 repo-to-write。

## 本轮验证

执行平台：Windows，Python 3.14。测试临时目录放工作区；系统沙箱 TEMP 曾拒绝访问，该次执行不能作为通过记录。

回归：79 项中 77 passed、2 skipped。跳过的是显式符号链接文件/目录拒绝用例，当前 Windows 无符号链接创建权限；普通负例及其余打包安全测试通过。没有把 skip 算作通过。新增 5 项覆盖旧名冲突/不覆写、不产生半安装、研究技能单装、发布 ZIP 与独立写作入口、技能元数据改名；不新增测试运行依赖。

两技能 quick_validate 通过。实际打包 CLI 的三份 ZIP 创建并校验，提取后的写作技能单独执行 prepare 及现有真实案例 check --delivery 通过。既有独立离线、refresh、交付拒绝测试通过。Mini-pipeline 和 priority-queue HTML 均构建通过；priority-queue 的 check --delivery 通过，这确认既有复核记录完整，不代表本轮重做研究。

浏览器检查：本机 Chrome 打开本轮重建的 priority-queue HTML，在 1440×1000 和 390×844 视口下三张图实际加载、字体状态 loaded、文档无横向溢出；390px 下四张表与五个代码块未超出内容宽度。尺寸检查后已恢复浏览器。截图接口多次超时，未获得可目视检查的截图，因此本轮视觉验收未完成，不以 DOM 尺寸检查替代。没有改写既有案例的历史 visual_review 声明。

构建刷新了 mini-pipeline HTML，使其使用源码中既有的长串换行样式；未修改出版器 CSS。原 v2.1 文件字节记录仍在历史快照内。

一页文本试验见 [输入](../examples/writing-edit/input.md)、[改前](../examples/writing-edit/before.md)、[改后](../examples/writing-edit/after.md)、[事实对照](../examples/writing-edit/review.md)。它是实际模型执行及模型自评，使用教学假设，不是项目实测、独立读者保证或大型书稿质量保证。

本轮不做新大型仓库研究、整书生成、PDF 验收、全局技能安装或额外付费调用；不更改CI权限或凭据。
