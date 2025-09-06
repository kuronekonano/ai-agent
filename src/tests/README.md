# AI Agent Framework - 测试指南

## 测试目录结构

```
tests/
├── unit/                 # 单元测试
│   ├── test_agent.py     # Agent核心功能测试
│   ├── test_performance.py # 性能跟踪测试
│   └── test_tools.py     # 工具功能测试
├── integration/          # 集成测试
│   └── test_single_run.py # 完整运行测试
├── conftest.py          # Pytest配置和fixtures
├── run_tests.py         # 测试运行脚本
└── README.md           # 本文件
```

## 运行测试

### 使用测试运行脚本
```bash
# 运行所有测试
python tests/run_tests.py

# 只运行单元测试
python tests/run_tests.py --unit

# 只运行集成测试
python tests/run_tests.py --integration

# 运行特定测试文件
python tests/run_tests.py --test tests/unit/test_agent.py

# 带覆盖率报告
python tests/run_tests.py --coverage

# 详细输出
python tests/run_tests.py --verbose
```

### 直接使用pytest
```bash
# 运行所有测试
pytest tests/

# 运行单元测试
pytest tests/unit/

# 运行特定测试文件
pytest tests/unit/test_agent.py

# 运行带标记的测试
pytest -m integration
```

## 环境变量配置

测试使用环境变量来配置API密钥，避免硬编码：

```bash
# 设置OpenAI API密钥（可选）
export OPENAI_API_KEY=your-api-key
export OPENAI_MODEL=gpt-4  # 或留空使用默认值

# 设置Anthropic API密钥（可选）
export ANTHROPIC_API_KEY=your-api-key
export ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

如果没有设置API密钥，测试会使用mock对象来避免真实的API调用。

## 测试分类

### 单元测试 (`tests/unit/`)
- **test_agent.py**: ReActEngine核心功能测试
- **test_performance.py**: 性能跟踪系统测试
- **test_tools.py**: 工具功能测试（计算器、文件操作等）

### 集成测试 (`tests/integration/`)
- **test_single_run.py**: 完整agent运行测试
  - 使用mock的AI客户端进行测试
  - 可选的真实API测试（需要设置环境变量）

## 测试配置

测试配置在 `conftest.py` 中定义：

- **mock_config**: 提供测试用的配置
- **performance_tracker**: 提供PerformanceTracker实例
- **mock_ai_client**: 模拟AI客户端避免真实API调用
- **react_engine**: 提供配置好的ReActEngine实例

## 编写新测试

### 单元测试示例
```python
def test_some_functionality():
    """测试描述"""
    # 准备测试数据
    
    # 执行测试
    
    # 验证结果
    assert result == expected_result
```

### 使用fixtures
```python
def test_with_fixture(performance_tracker):
    """使用fixture的测试"""
    # performance_tracker 是自动提供的fixture
    tracker.record_api_call(...)
    assert tracker.get_statistics()["total_api_calls"] == 1
```

## 测试最佳实践

1. **使用环境变量**而不是硬编码API密钥
2. **Mock外部依赖**避免真实的API调用
3. **测试错误处理**而不仅仅是成功路径
4. **保持测试独立**，每个测试应该可以单独运行
5. **使用有意义的测试名称**清楚地描述测试目的

## 持续集成

测试可以在CI环境中运行，确保设置适当的环境变量：

```yaml
# GitHub Actions示例
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

## 故障排除

### 常见问题

1. **导入错误**: 确保 `PYTHONPATH` 包含项目根目录
2. **API密钥错误**: 检查环境变量设置
3. **测试超时**: 调整集成测试的超时时间

### 调试测试

```bash
# 进入调试模式
pytest --pdb tests/

# 显示详细输出
pytest -v tests/

# 只显示失败测试
pytest -x tests/
```