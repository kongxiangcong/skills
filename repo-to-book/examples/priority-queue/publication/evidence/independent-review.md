# 独立技术核验

审查者：`/root/real_research/review`，2026-10-27；未参加源码或外部资料采集。审查基线：包内固定 boltons commit `d31d821d56c8f7756af9c30a864077f2e5855321` 的原始 queueutils.py 与 tests/test_queueutils.py；不以研究员摘要代替源码。

## 实际核验与结论

| 核验点 | 实际依据 | 结论 |
|---|---|---|
| 默认别名与后端 | queueutils.py L192–223；listutils.py L413 `BList = BarrelList` | 正确。默认不是 heap，素材没有混淆具体排序列表与堆数组。 |
| 输入转换、计数器、共享 entry | queueutils.py L105、L108–112、L132–138 | 正确。转换在旧项删除前；map/backend 引用相同 entry；更新获得新 count。 |
| 删除/清理/返回/len | queueutils.py L140–189 | 正确。remove 仅改标记；_cull 仅清连续队首墓碑；peek 可能物理清理；pop 返回 task；len 来自 map。 |
| A/B/C 完整走读与边界 | 原始测试函数、source_probe.py、source-runtime.txt；本审查者独立重运行探针 | 两后端的数量、count、返回顺序、错误和大整数转换一致。 |
| 异常原子性与性能限定 | queueutils.py L132–138 写入顺序；L147–156 循环；后端方法 | 正确区分静态推断与观察。没有将公开 peek/pop 简写为固定 O(1)/O(log L)，没有凭源码宣称基准性能。 |
| 图 1-1 语义 | HTML 与最终 SVG 文本/路径；L124–185 | 符合成功路径。图例明确 peek/pop 是后续调用，不是 add 自动调用；图未伪造 heap 布局。 |
| 图 2-1 语义 | HTML 与最终 SVG 文本/路径；L132–185 | 两条离队路径与标记清理条件正确。更新新 entry 明确在旧 entry 图外；没有把 pop 误称任务执行完。 |
| 图 1-2 概念图 | 实际 view_image 查看 PNG | 看见调度员选择红卡、其他蓝卡留在桌面；没有文字、数值、箭头或实现声明。材料限制其为隐喻是必要且已写明。 |

实际复运行命令（在 research 目录）：

```bash
python evidence/source_probe.py > /workspace/scratch/068517fd0265/reviewer-pq-runtime.txt
cmp evidence/source-runtime.txt /workspace/scratch/068517fd0265/reviewer-pq-runtime.txt
```

两命令退出 0，输出逐字相同。另用 ElementTree 解析两张最终 SVG 并查看全部可见文字；XML 可解析，均为 960×600。

## 问题与未覆盖范围

- 没有发现需阻断交接的核心事实错误。
- 微小措辞建议：第二章边界表“空队列显式 default=None，实际观察”可以写明“pop(None) 已观察，peek(None) 由源码确认”，因为所附探针只显式运行了前者。当前表作为空队列行为摘要不构成错误，但不应扩写为两方法都实测。
- 后续实际 view_image 查看主研究员 CairoSVG 渲染的 `/workspace/scratch/068517fd0265/pq-01.png` 与 `pq-02.png`：中文完整，箭头方向/标签正确，无明显裁切、遮挡或缺字；底部图例可读。图 1-1 右下 pop 标签接近框边但仍完整。此项是实际静态渲染核验，不是浏览器跨平台兼容性验证；PNG 隐喻也已实际查看。
- 未重新抓取 GitHub 文件或官方 Python 文档；原始来源真实性由来源采集记录承担。未审查全部 BarrelList 算法、并发、NaN 行为、恶意对象、异常注入或性能数据；这些已列为边界。
- 同模型不同角色不是不同事实来源；此次独立性来自不参与采集、回读原始源码与独立复运行，而非声称绝对独立。
