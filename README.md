# JLU_Grab

## 重要提醒

- 本脚本仅用于个人学习用途，请遵守学校规定
- 如果脚本不能正常工作，检查 `COURSES` 和 `HEADERS` 

---

## 第一步：准备工作

### 1. 安装 Python
- 推荐 `Python 3.9.11`
- 安装时勾选 `Add to PATH`

### 2. 安装依赖库
打开命令提示符，运行：
```bash
pip install requests
```

> 如果提示 `pip` 未找到，请先运行 `python -m ensurepip --upgrade`

---

## 第二步：获取参数

你需要从已登录的选课页面中获取 `请求标头` 和 `课程信息` （详见F12）
