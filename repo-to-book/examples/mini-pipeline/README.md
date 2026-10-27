# 双阶段最小示例

source/ 是教学代码；research/ 是可移植分章材料；publication/ 是从材料目录 prepare 后的写作源稿。
这不是外部推理项目，不含性能评测。

```bash
python skills/repo-to-research/scripts/research.py check examples/mini-pipeline/research
python skills/repo-to-research/scripts/research.py export examples/mini-pipeline/research --out /tmp/research.zip
python skills/repo-to-write/scripts/book.py build examples/mini-pipeline/publication
```

素材可复制到完全独立的位置，结合单独写作技能使用。示例里的四张 SVG 真实来源是旧版测试 fixture，
未实际调用 diagram-design、imagegen、多 agent 调研或另一模型写作。它验证的是接口和出版，不是模型效果。
