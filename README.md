# Skills

个人 skills 库。

| 技能 | 作用 |
| --- | --- |
| [Winson](Winson/README.md) | 温和、鼓励而判断明确的导师式科研协作，帮助讨论研究方向、技术路线与复杂概念。 |
| [Editorial UI](editorial-ui/README.md) | 面向内容型界面、经授权的产品 UI 重构与自包含交互式 HTML，保留业务契约并按选定设计规范实现与验收。 |
| [Repo to Book](repo-to-book/README.md) | 两阶段图解技术书：`repo-to-research` 完成规划、证据、配图与独立核验；`repo-to-book` 独立写作与 HTML/PDF 出版，支持补包返修和交付检查。 |

## Repo to Book

两个可独立安装的技能位于 `repo-to-book/skills/`。在 `repo-to-book` 目录运行 `python scripts/install.py` 安装；其他模型也可直接读取写作技能的说明和离线研究包。研究完成后由用户另行启动写作，默认 HTML，PDF 按需。

[使用说明](repo-to-book/README.md) · [实际验证与限制](repo-to-book/docs/VALIDATION.md) · [真实两章案例](repo-to-book/examples/priority-queue/README.md)

### 导入来源

v2.1 当前源码快照，来源提交 `9e5b3ef884e347ac78e950c0bc250955e89fd9d3`。原包文件逐字节保留，交付时的状态记录不代表后续 GitHub 发布状态。

- ZIP：`repo-to-book-latest-20261027-9e5b3ef.zip`
- SHA-256：`5300f2daa7c8e48b2d56fcb7b60991e26c1deaed817125bdd927d3496a56254c`
- [交付清单](repo-to-book/DELIVERY_STATUS.md) · [快照清单](repo-to-book/SNAPSHOT.json) · [校验值](repo-to-book/SHA256SUMS)
- 独立安装路径：`repo-to-book/skills/repo-to-research/`、`repo-to-book/skills/repo-to-book/`。
- 原包 CI 保留在嵌套的 `repo-to-book/.github/workflows/`，不会被本仓库 GitHub Actions 自动发现。
