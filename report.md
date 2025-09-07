# AI Agent 技术报告

## 项目概述

本项目是一个模块化的AI代理框架，包含两个核心模块：

1. **ai_agent** - 核心代理执行引擎，实现ReAct（推理+行动）模式
2. **agent_eval** - 代理评估框架，用于批量测试和评估AI代理

## 架构设计

### 整体架构
```
src/
├── ai_agent/          # 核心代理引擎
│   ├── agent.py       # ReActEngine - 核心执行引擎
│   ├── model.py       # AI客户端抽象和OpenAI实现
│   ├── tools.py       # 工具注册和执行系统
│   ├── trajectory.py  # 执行轨迹记录
│   ├── performance.py # 性能跟踪和成本计算
│   └── __init__.py    # 模块初始化和配置加载
└── agent_eval/        # 代理评估框架
    ├── schema.py      # 数据模型定义
    ├── client.py      # 模型客户端抽象
    ├── runner.py      # 异步执行引擎
    ├── evaluator.py   # 评分系统
    ├── analyzer.py    # 指标分析器
    ├── storage.py     # 数据存储层
    └── cases/         # 测试用例管理
```

## ai_agent 模块详解

### 1. ReActEngine (agent.py:26)

**核心概念**: ReAct（Reasoning + Acting）模式，通过思考-行动-观察循环解决问题

**执行流程**:
1. 初始化工具和模型客户端
2. 为给定任务执行ReAct循环
3. 每个迭代步骤：生成思考 → 决定行动 → 执行行动 → 记录观察
4. 直到找到最终答案或达到最大迭代次数

**关键数据结构**:
```python
@dataclass
class ReActStep:
    thought: str          # 思考过程
    action: str           # 执行动作  
    action_input: Dict[str, Any]  # 动作输入参数
    observation: str      # 观察结果
    result: str           # 执行结果
```

**设计理由**: 采用ReAct模式因为它结合了推理和工具使用，适合复杂任务解决。每个步骤都记录完整轨迹，便于调试和分析。

### 2. AIClient 抽象 (model.py:20)

**核心接口**:
```python
class AIClient(ABC):
    async def complete(self, prompt: str, **kwargs) -> str
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str
    def get_performance_stats(self) -> Dict[str, Any]
```

**OpenAIClient实现**:
- 封装OpenAI API调用
- 自动记录token使用和延迟
- 支持自定义base_url（用于本地模型）

**设计理由**: 抽象化模型客户端使得可以轻松切换不同的AI提供商，同时统一性能指标收集。

### 3. 工具系统 (tools.py)

**工具注册表**:
```python
class ToolRegistry:
    def register_tool(self, name: str, tool: Any)
    def get_tool(self, name: str) -> Any
    def get_available_tools(self) -> List[str]
```

**内置工具**:
- FileTool: 文件操作
- CalculatorTool: 数学计算  
- WebSearchTool: 网络搜索
- PythonCodeTool: Python代码执行
- MemoryDBTool: 内存数据库操作

**设计理由**: 模块化工具系统允许动态添加和移除工具，代理可以根据任务需求选择适当的工具。

### 4. 性能跟踪 (performance.py)

**关键指标**:
- Token使用量（提示、补全、总计）
- API调用延迟
- 成本计算（基于模型定价）
- 成功率统计

**设计理由**: 详细的性能指标对于优化和成本控制至关重要，特别是在生产环境中。

## agent_eval 模块详解

### 1. 数据模型 (schema.py)

**核心数据结构**:

```python
@dataclass
class TestCase:
    id: str                    # 用例唯一标识
    prompt: str                # 输入提示
    expected: Optional[str]    # 预期输出
    meta: Optional[Dict[str, Any]]  # 元数据

@dataclass  
class ExecutionRecord:
    run_id: str                # 运行标识
    test_case_id: str          # 用例标识
    prompt: Dict[str, Any]     # 完整提示信息
    response: Dict[str, Any]   # 模型响应
    scoring: Dict[str, Any]    # 评分结果
    status: str                # 执行状态
    created_at: str            # 创建时间
```

**设计理由**: 清晰的数据模型确保执行记录的一致性和可序列化，便于存储和分析。

### 2. 模型客户端抽象 (client.py)

**ModelClient接口**:
```python
class ModelClient(ABC):
    async def call(self, prompt: str, **params) -> Dict[str, Any]
```

**MockModelClient特性**:
- 模拟API响应，避免真实API调用
- 缓存机制减少重复计算
- 模拟延迟和token使用
- 返回结构化响应格式

**设计理由**: Mock客户端允许离线开发和测试，同时保持与真实客户端相同的接口。

### 3. 异步执行引擎 (runner.py)

**执行流程**:
1. 使用asyncio.Semaphore控制并发度
2. 为每个测试用例创建异步任务
3. 调用ModelClient处理提示
4. 使用Scorer评分响应
5. 存储执行记录
6. 处理错误和重试

**并发控制**:
```python
semaphore = asyncio.Semaphore(self.concurrency)
async def run_case_with_semaphore(case: TestCase):
    async with semaphore:
        return await self._run_single_case(case, run_meta, storage, scorer)
```

**设计理由**: 异步执行大幅提高测试效率，信号量控制防止过度并发导致API限制。

### 4. 评分系统 (evaluator.py)

**评分策略**:

1. **ExactMatchScorer**: 精确字符串匹配
   ```python
   def score(self, data: Dict[str, Any]) -> Dict[str, Any]:
       expected = data["expected"]
       actual = data["actual"]
       score = 1.0 if expected == actual else 0.0
       return {"exact_match": expected == actual, "score": score}
   ```

2. **NormalizedMatchScorer**: 标准化匹配（忽略大小写、空格、标点）

3. **BinaryContainmentScorer**: 二进制包含检查

**设计理由**: 多种评分策略适应不同的评估需求，从严格精确匹配到宽松包含检查。

### 5. 存储系统 (storage.py)

**JSONLStore特性**:
- 基于JSON Lines格式，每行一个完整记录
- 支持追加写入，适合流式数据
- 支持查询和过滤
- 自动文件轮换（按时间戳）

**设计理由**: JSONL格式易于处理和分析，同时支持大型数据集的流式处理。

### 6. 分析器 (analyzer.py)

**分析功能**:
- 聚合统计（平均值、中位数、标准差）
- 成功率计算
- 性能指标分析（延迟、token使用）
- 失败用例识别

**报告生成**: 支持Markdown格式报告，包含表格和摘要统计。

## 执行流程详解

### 单个测试用例执行流程

1. **输入**: TestCase对象（包含prompt和expected）
2. **处理**: ModelClient.call() 方法处理提示
3. **响应**: 获取结构化响应（文本、使用量、延迟、原始数据）
4. **评分**: Scorer.score() 方法评估响应质量
5. **记录**: 创建ExecutionRecord并存储
6. **输出**: 返回评分结果和执行记录

### 批量测试流程

1. **加载配置**: 从环境变量或配置文件加载设置
2. **读取用例**: 从JSONL文件加载测试用例
3. **初始化组件**: 创建Runner、Storage、Scorer实例
4. **并发执行**: 使用asyncio并发处理所有用例
5. **收集结果**: 聚合所有执行记录
6. **生成报告**: 分析结果并生成评估报告

## 设计哲学和最佳实践

### 1. 抽象化设计
- **模型客户端抽象**: 允许轻松切换不同的AI提供商
- **存储抽象**: 支持多种存储后端（JSONL、SQLite等）
- **评分抽象**: 可插拔的评分策略

### 2. 可观测性
- **完整轨迹记录**: 记录每个决策步骤
- **性能指标**: 详细的token使用和延迟统计
- **错误处理**: 完整的错误记录和恢复机制

### 3. 可扩展性
- **模块化架构**: 每个组件都可以独立替换或扩展
- **配置驱动**: 通过配置而非代码修改来调整行为
- **插件系统**: 易于添加新工具、评分器、存储后端

### 4. 生产就绪特性
- **并发控制**: 防止API速率限制
- **缓存机制**: 减少重复计算和成本
- **重试逻辑**: 处理临时性错误
- **详细日志**: 完整的执行日志和调试信息

## 性能考虑

### 并发优化
- 使用asyncio进行异步I/O操作
- 信号量控制最大并发数
- 连接池和会话复用

### 内存管理
- 流式处理大型数据集
- 增量数据持久化
- 缓存策略优化

### 存储效率
- JSONL格式适合追加写入
- 压缩存储减少磁盘空间
- 索引优化查询性能

## 使用场景

### 1. 开发测试
- 单元测试AI代理功能
- 回归测试确保更改不破坏现有功能
- 性能基准测试

### 2. 模型评估
- 比较不同模型的性能
- A/B测试新模型版本
- 评估提示工程效果

### 3. 生产监控
- 监控模型性能下降
- 检测数据漂移
- 成本控制和优化

## 总结

本项目的架构设计体现了现代AI应用开发的最佳实践：

1. **清晰的关注点分离**: 核心引擎与评估框架分离
2. **抽象化和模块化**: 每个组件都有明确的接口和责任
3. **可观测性**: 完整的指标收集和日志记录
4. **可扩展性**: 易于添加新功能和集成
5. **生产就绪**: 包含错误处理、并发控制、缓存等生产特性

这种设计使得框架既适合快速原型开发，也适合生产环境部署，为构建可靠的AI代理系统提供了坚实基础。