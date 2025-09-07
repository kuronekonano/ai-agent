# Agent Evaluation Framework

代理评估框架 - AI代理的批量测试与评估系统

## 概述

Agent Evaluation Framework 是一个用于批量测试和评估AI代理的框架。它支持并发执行测试用例、记录执行轨迹、多种评分策略和生成详细报告。

## 功能特性

- ✅ **并发执行**: 支持异步并发执行大量测试用例
- ✅ **执行跟踪**: 完整的执行记录，包括提示、响应、评分和性能指标
- ✅ **存储系统**: JSONL格式的持久化存储，支持分析和复现
- ✅ **评估系统**: 多种评分机制（精确匹配、标准化匹配、二进制包含）
- ✅ **配置管理**: 集中式配置系统，支持环境变量覆盖
- ✅ **命令行界面**: 易于使用的CLI工具
- ✅ **报告生成**: 全面的指标聚合和Markdown报告

## 安装

```bash
# 确保在项目根目录
cd /path/to/ai-agent

# 安装依赖（如果需要）
pip install -r requirements.txt
```

## 快速开始

### 1. 命令行使用

```bash
# 运行测试套件
python -m src.agent_eval.cli run-suite src/agent_eval/cases/sample_cases.jsonl --concurrency 4 --output data/results

# 查看帮助
python -m src.agent_eval.cli --help
```

### 2. 编程方式使用

```python
import asyncio
from agent_eval.cases.loader import load_test_cases
from agent_eval.simple_runner import run_suite_simple
from agent_eval.analyzer import Analyzer

# 加载测试用例
test_cases = load_test_cases("src/agent_eval/cases/sample_cases.jsonl")

# 运行评估
records = run_suite_simple(
    test_cases=test_cases,
    concurrency=4,
    storage_path="data/my_test_run"
)

# 分析结果
analyzer = Analyzer()
analysis = analyzer.analyze_records([r.to_dict() for r in records])
report = analyzer.generate_report(analysis, format="markdown")

print(report)
```

### 3. 与ai_agent集成

```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agent_eval.cases.loader import load_test_cases
from agent_eval.client import MockModelClient
from agent_eval.evaluator import ExactMatchScorer
from agent_eval.schema import ExecutionRecord, now_iso
from agent_eval.analyzer import Analyzer

# 使用MockModelClient进行测试
test_cases = load_test_cases("src/agent_eval/cases/sample_cases.jsonl")
client = MockModelClient()
scorer = ExactMatchScorer()

# 处理每个测试用例
records = []
for case in test_cases:
    response = await client.call(case.prompt)
    scoring = scorer.score({
        "expected": case.expected,
        "actual": response["text"],
        "response": response
    })
    
    record = ExecutionRecord(
        run_id="test-run-001",
        test_case_id=case.id,
        prompt={"text": case.prompt},
        response=response,
        scoring=scoring,
        status="success",
        created_at=now_iso()
    )
    records.append(record)

# 生成报告
analyzer = Analyzer()
analysis = analyzer.analyze_records([r.to_dict() for r in records])
report = analyzer.generate_report(analysis, format="markdown")
```

## 项目结构

```
src/agent_eval/
├── __init__.py              # 模块初始化
├── README.md                # 说明文档
├── cli.py                   # 命令行接口
├── config.py                # 配置管理
├── client.py                # 模型客户端抽象
├── schema.py                # 数据模型
├── cases/
│   ├── loader.py            # 测试用例加载器
│   └── sample_cases.jsonl   # 示例测试用例
├── runner.py                # 异步执行引擎（使用ai_agent ReActEngine）
├── simple_runner.py         # 简单运行器（直接使用MockModelClient）
├── storage.py               # 存储层
├── evaluator.py             # 评分器
├── analyzer.py              # 分析器
├── utils.py                 # 工具函数
└── tests/                   # 单元测试
```

## 配置

通过环境变量配置框架：

```bash
export AGENT_EVAL_CONCURRENCY=8
export AGENT_EVAL_TIMEOUT=30
export AGENT_EVAL_STORAGE_PATH="data/eval_runs"
export AGENT_EVAL_MODEL_NAME="mock"
```

或在代码中配置：

```python
from agent_eval.config import get_config

config = get_config()
config.update({
    "concurrency": 8,
    "timeout_seconds": 30,
    "model": {"name": "mock", "temperature": 0.0}
})
```

## 测试用例格式

测试用例使用JSONL格式，每行一个测试用例：

```json
{"id": "case-001", "prompt": "What is the capital of France?", "expected": "Paris"}
{"id": "case-002", "prompt": "Calculate 2 + 2", "expected": "4"}
{"id": "case-003", "prompt": "Who wrote Romeo and Juliet?", "expected": "William Shakespeare"}
```

## 评分策略

框架支持多种评分策略：

1. **精确匹配 (ExactMatch)**: 完全字符串匹配
2. **标准化匹配 (NormalizedMatch)**: 忽略大小写、空格和标点
3. **二进制包含 (BinaryContainment)**: 检查预期内容是否包含在实际响应中

## 报告格式

评估报告包含以下内容：

- **摘要统计**: 总用例数、成功率、准确率
- **性能指标**: 平均延迟、Token使用情况
- **分数分布**: 平均分、中位数、标准差
- **失败用例**: 得分最低的用例详情

## 示例输出

```markdown
# Agent Evaluation Report

**Analysis Time**: 2025-09-07T20:22:09.788105

## Summary

- **Total Cases**: 10
- **Successful Cases**: 10
- **Failed Cases**: 0
- **Success Rate**: 100.0%
- **Accuracy**: 0.0%

## Performance Statistics

### Scores
- Mean: 0.000
- Median: 0.000
- Std Dev: 0.000
- Range: 0.000 - 0.000

### Latency (ms)
- Mean: 1.0
- Median: 1.0
- Std Dev: 0.0
- Range: 1.0 - 1.0

### Token Usage
- Mean: 14.6
- Median: 14.0
- Std Dev: 3.4
- Range: 11.0 - 21.0
```

## 开发指南

### 添加新的评分器

```python
from .evaluator import BaseScorer

class MyCustomScorer(BaseScorer):
    def score(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # 实现自定义评分逻辑
        return {"score": 1.0, "custom_metric": "value"}
```

### 添加新的存储后端

```python
from .storage import BaseStore

class MyCustomStore(BaseStore):
    def append(self, record: Dict[str, Any]) -> None:
        # 实现自定义存储逻辑
        pass
    
    def query(self, filter_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        # 实现自定义查询逻辑
        return []
```

### 运行测试

```bash
# 运行单元测试
python -m pytest src/agent_eval/tests/ -v

# 运行集成测试
python test_simple_integration.py

# 运行代码格式检查
make format
make static_check
```

## 限制与未来改进

### 当前限制

1. **真实模型集成**: 目前主要使用Mock客户端，真实API客户端需要实现
2. **A/B测试**: 基础框架已就位，但需要实现统计测试
3. **高级存储**: 仅实现JSONL存储，计划支持SQLite

### 推荐改进

1. **真实API客户端**: 实现OpenAIClient、ClaudeClient等
2. **统计测试**: 添加t检验、bootstrap置信区间
3. **SQLite存储**: 实现SQLiteStore以支持更好的查询能力
4. **嵌入评分器**: 使用嵌入模型添加余弦相似度评分
5. **LLM评判**: 实现基于LLM的评估评分

## 贡献

欢迎提交Issue和Pull Request来改进这个框架！

## 许可证

MIT License