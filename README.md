# AI Agent 框架

一个基于 Python 的模块化 AI 智能体框架，实现了 ReAct（推理+行动）模式，用于自主任务执行。

## ✨ 核心特性

- **ReAct 引擎**: 自主智能体的核心推理和行动循环
- **多模型支持**: 支持多种 AI 模型（OpenAI、DeepSeek 等）
- **工具系统**: 可扩展的工具系统，支持：
  - 文件操作（读写、列表、存在性检查）
  - 数学计算（加减乘除、幂运算、平方根、表达式求值）
  - **Python代码执行**（带安全限制的沙箱环境）
  - **记忆数据库**（SQLite长期记忆存储，支持丰富的元数据）
  - 网络搜索（占位符实现）
- **轨迹追踪**: 完整的执行历史记录和分析，**支持数据持久化**
- **数据持久化**: 使用 TinyDB 实现完整的指标、轨迹、性能数据存储
- **可视化工具**: CLI 和 notebook 可视化工具
- **模块化设计**: 易于扩展和定制

## 🚀 快速开始

### 环境要求
- Python 3.13+
- uv (推荐) 或 pip

### 安装方式

**使用 uv (推荐):**
```bash
# 安装依赖
uv sync

# 开发模式安装
uv pip install -e .
```

**使用 pip:**
```bash
pip install -e .
```

### 快速体验

**CLI 方式运行:**
```bash
# 查看帮助
python -m ai_agent --help

# 运行任务
python -m ai_agent "帮我分析这个项目的代码结构"
```

**Python 代码方式:**
```python
from ai_agent import AIClient, ReActEngine

# 创建智能体（需要先配置 config/config.yaml）
agent = ReActEngine({
    "openai": {
        "api_key": "your-api-key",
        "model": "gpt-4"
    },
    "tools": {
        "enable_python_code": True,
        "enable_memory_db": True
    }
})

# 执行任务
result = agent.run("请帮我分析这个项目的代码结构并记录重要发现到内存数据库")
print(result)

# 获取执行轨迹和性能统计
trajectory = agent.get_trajectory()
stats = agent.get_performance_stats()
```

**运行演示:**
```bash
make demo
```

## 📁 项目结构

```
ai-agent/
├── README.md                 # 项目说明文档
├── pyproject.toml           # Python 项目配置
├── Makefile                 # 构建和开发脚本
├── uv.lock                  # 依赖锁文件
├── src/                     # 源代码目录
│   ├── main.py              # 主入口文件
│   └── ai_agent/            # 核心模块
│       ├── __init__.py      # 模块初始化
│       ├── agent.py         # 智能体核心类
│       ├── model.py         # 模型接口
│       ├── planner.py       # 任务规划器
│       ├── tools.py         # 工具系统（文件、计算、Python代码、内存数据库等）
│       ├── trajectory.py    # 执行轨迹（支持持久化）
│       ├── analyzer.py      # 分析器
│       ├── visualizer.py    # 可视化工具
│       ├── performance.py   # 性能跟踪和成本计算
│       ├── database.py      # **数据持久化管理器（TinyDB）**
│       └── memory_db.py     # **记忆数据库工具（SQLite长期记忆）**
├── tests/                   # 测试代码
├── notebooks/               # Jupyter 笔记本
│   └── demo_analysis.ipynb  # 演示分析
├── scripts/                 # 脚本目录
│   └── run_demo.py          # 演示脚本
├── config/                  # 配置文件目录
│   └── config.yaml          # 应用配置
└── data/                    # **数据存储目录（自动创建）**
    ├── ai_agent_metrics.json  # TinyDB 数据文件
    └── memory.db            # SQLite 内存数据库文件
```

## ⚙️ 配置说明

编辑 `config/config.yaml` 文件配置 API 密钥和模型参数:

```yaml
openai:
  api_key: your-openai-api-key
  model: gpt-4

# 工具配置选项
tools:
  enable_file_operations: true
  enable_calculator: true
  enable_web_search: false
  enable_python_code: true    # 启用Python代码执行工具
  enable_memory_db: true      # 启用内存数据库工具

# 代理配置
agent:
  max_iterations: 10
  timeout_seconds: 300

# 数据库配置
database:
  path: "data/ai_agent_metrics.json"  # TinyDB 数据文件路径

# 其他配置选项...
```

## 🛠️ 开发指南

### Makefile 命令速查

```bash
# 代码格式化
make format          # 运行 black + isort 格式化代码

# 代码检查
make lint            # 运行 ruff + mypy 静态检查
make static_check    # lint 的别名

# 测试
make test            # 运行单元测试

# 依赖管理
make install         # 安装项目依赖

# 运行项目
make run             # 启动 AI 智能体 CLI
make demo            # 运行演示脚本

# 虚拟环境
make venv            # 激活 uv 虚拟环境

# 清理
make clean           # 清理缓存和临时文件

# 发布
make release-test    # 测试环境发布
make release-prod    # 生产环境发布
```

### 开发工作流

1. **设置开发环境:**
   ```bash
   make install
   make venv
   ```

2. **代码开发:**
   ```bash
   # 编写代码后格式化
   make format
   
   # 检查代码质量
   make lint
   ```

3. **运行测试:**
   ```bash
   make test
   ```

4. **验证功能:**
   ```bash
   make run
   make demo
   ```

## 📊 功能模块详解

### ReActEngine
核心推理引擎，实现思考-行动-观察的循环模式。

### 工具系统 (Tools)
- **文件操作工具**: 文件读写、目录列表、存在性检查
- **计算工具**: 数学运算、表达式求值
- **Python代码执行工具**: 安全沙箱环境执行Python代码
- **记忆数据库工具**: SQLite长期记忆存储，支持丰富的元数据和高级查询
- **网络搜索工具**: 网络搜索（占位符实现）
- 自定义工具扩展

### 轨迹分析 (Trajectory)
记录完整的执行过程，支持回放和分析，**集成数据持久化到TinyDB**。

### 可视化 (Visualizer)
提供 CLI 和 notebook 两种可视化方式。

### 数据持久化 (Database)
**完整的指标数据持久化系统**，使用 TinyDB 存储：
- 执行轨迹和步骤记录
- API调用统计和Token使用
- 工具使用情况和性能指标
- 成本计算和历史数据分析

### 记忆数据库 (MemoryDB)
**SQLite长期记忆存储系统**，支持：
- 丰富的元数据（标签、优先级、状态、来源）
- 高级查询（按时间范围、标签、状态、优先级）
- 事件记录和记事本功能
- 自动统计和报表生成

## 🎯 特色功能和使用场景

### Python代码执行示例
智能体可以安全执行Python代码进行数据分析、计算和自动化任务：
```python
# 智能体会使用python_code工具执行计算任务
result = agent.run("请计算1到100的和，并验证结果是否正确")
```

### 长期记忆和事件记录示例
智能体可以使用内存数据库记录重要信息和事件：
```python
# 智能体会创建记忆记录
result = agent.run("请记录今天的重要会议内容，标记为工作优先级")

# 智能体会查询相关记忆
result = agent.run("请查找上周所有关于项目进度的记录")
```

### 数据分析和报告示例
结合多个工具进行复杂任务：
```python
# 智能体会分析文件数据并生成报告
result = agent.run("请分析data.csv文件，计算统计指标，并保存结果到报告文件")
```

## 🔧 扩展开发

### 添加新工具
在 `src/ai_agent/tools.py` 中实现新工具类:

```python
class CustomTool(BaseTool):
    name = "custom_tool"
    description = "自定义工具描述"
    
    def execute(self, *args, **kwargs):
        # 工具实现逻辑
        return "执行结果"
```

### 自定义模型
在 `src/ai_agent/model.py` 中添加新的模型适配器。

## 🧪 测试

运行完整测试套件:
```bash
make test
```

运行特定测试文件:
```bash
python -m pytest tests/test_agent.py -v
```

## 📈 性能优化

- 使用 uv 加速依赖安装
- 配置合适的模型参数
- 优化工具执行效率
- 启用缓存机制

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📝 许可证

本项目采用 MIT 许可证 - 查看 LICENSE 文件了解详情。

## 🆘 常见问题

**Q: 如何配置 API 密钥?**  
A: 在 `config/config.yaml` 中设置相应的 API 密钥。

**Q: 如何添加自定义工具?**  
A: 在 `tools.py` 中实现 BaseTool 的子类。

**Q: 如何调试执行过程?**  
A: 启用详细日志或使用轨迹分析功能。

**Q: Python代码执行工具的安全限制有哪些?**  
A: 禁止文件I/O、网络访问、系统调用、导入模块和危险内置函数，代码长度限制1000字符。

**Q: 记忆数据库支持哪些查询方式?**  
A: 支持按标签、时间范围、状态、优先级查询，以及全文搜索和高级过滤。

**Q: 数据持久化存储在哪里?**  
A: 轨迹和性能数据存储在 `data/ai_agent_metrics.json`，记忆数据库存储在 `data/memory.db`。

## 📞 支持

如有问题请提交 Issue 或联系维护团队。