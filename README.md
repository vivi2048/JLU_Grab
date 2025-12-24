# JLU_-选课助手

## ⚠️ 重要提醒

- **本脚本仅用于个人学习用途，请遵守学校规定。**
- **切勿将包含真实 `Authorization`、`Cookie` 或 `secretVal` 的代码上传至网络！**
- 脚本需在**选课开始前几秒启动**，建议提前测试。

---

## 🔧 第一步：准备工作

### 1. 安装 Python
- 推荐 Python 3.9.11
- 安装时勾选 **“Add to PATH”**

### 2. 安装依赖库
打开命令提示符，运行：
```bash
pip install requests
```

> 如果提示 `pip` 未找到，请先运行 `python -m ensurepip --upgrade`

---

## 🔑 第二步：获取你的个人参数

你需要从**已登录的选课页面**中提取以下三项：

| 参数 | 说明 |
|------|------|
| `Authorization` | 登录凭证（JWT Token） |
| `batchId` | 当前选课轮次 ID |
| 课程信息 | 每门课的 `clazzId`、`secretVal`、`clazzType` |

#### 步骤如下：

1. 复制请求标头和课程信息
2. 交给AI处理
3. 替换代码中的COURSES和HEADERS
