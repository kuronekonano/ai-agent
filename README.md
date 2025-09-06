# AI Agent 框架

一个基于 Python 的模块化 AI 智能体框架，实现了 ReAct（推理+行动）模式，用于自主任务执行。

## ✨ 核心特性

- **ReAct 引擎**: 自主智能体的核心推理和行动循环
- **多模型支持**: 支持多种 AI 模型（OpenAI 等）
- **工具系统**: 可扩展的工具系统，支持文件操作、网络搜索、计算等
- **轨迹追踪**: 完整的执行历史记录和分析
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

# 创建智能体
agent = ReActEngine(model="gpt-4")

# 执行任务
result = agent.run("请帮我解决这个问题...")
print(result)
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
│       ├── tools.py         # 工具系统
│       ├── trajectory.py    # 执行轨迹
│       ├── analyzer.py      # 分析器
│       └── visualizer.py    # 可视化工具
├── tests/                   # 测试代码
├── notebooks/               # Jupyter 笔记本
│   └── demo_analysis.ipynb  # 演示分析
├── scripts/                 # 脚本目录
│   └── run_demo.py          # 演示脚本
└── config/                  # 配置文件目录
    └── config.yaml          # 应用配置
```

## ⚙️ 配置说明

编辑 `config/config.yaml` 文件配置 API 密钥和模型参数:

```yaml
openai:
  api_key: your-openai-api-key
  model: gpt-4

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
- 文件操作工具
- 网络搜索工具  
- 计算工具
- 自定义工具扩展

### 轨迹分析 (Trajectory)
记录完整的执行过程，支持回放和分析。

### 可视化 (Visualizer)
提供 CLI 和 notebook 两种可视化方式。

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

## 📞 支持

如有问题请提交 Issue 或联系维护团队。