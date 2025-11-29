# TodoList 智能任务管理系统

一个功能完善的智能任务管理系统，集成了任务管理、计时功能、AI智能建议以及硬件交互功能。

## 📋 项目简介

本项目是一个基于Flask框架开发的智能任务管理系统，不仅提供基本的任务管理功能，还集成了AI智能建议和硬件交互功能，可以帮助用户更高效地管理时间和任务。

## ✨ 核心功能

- **任务管理**：添加、删除、重命名、标记完成任务
- **计时功能**：为任务设置预计时长并进行计时
- **AI智能建议**：基于任务内容和完成情况提供智能时间建议
- **完成率统计**：实时计算和显示任务完成率
- **硬件交互**：将任务完成率数据发送到51开发板显示
- **音频提醒**：任务计时结束时播放提醒音频
- **响应式界面**：提供友好的用户界面和交互体验

## 🛠 技术栈

### 后端
- Python 3.11 +
- Flask - Web框架
- OpenAI API - AI智能交互
- PySerial - 串口通信（与51开发板）
- python-dotenv - 环境变量管理

### 前端
- HTML5/CSS3
- JavaScript (原生)
- 响应式设计

### 硬件
- 51开发板（A4+，可选，用于显示任务完成率）

## 📦 安装部署

### 1. Star, Fork, 克隆项目
给我们一个Star并Fork项目
```bash
git clone https://github.com/yourusername/todolist.git
cd todolist
```

### 2. 创建虚拟环境（推荐）

```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

> 如果没有requirements.txt文件，可以手动安装所需依赖：
> ```bash
> pip install flask openai pyserial python-dotenv requests
> ```

### 4. 配置环境变量

创建`.env`文件，添加以下内容：

```dotenv
# AI API配置
API_KEY="your_api_key_here"
AI_MODEL="your_model_here"
AI_API_URL="your_api_url_here"
```

### 5. 运行项目

```bash
python app.py
```

项目将在 http://localhost:80 上运行。

## 📁 项目结构

```
todolist/
├── .env              # 环境变量配置
├── .venv/            # 虚拟环境
├── 51/               # 51开发板相关代码
├── ├── main.c        # 51开发板主程序
├── app.py            # 主应用程序
├── tasks.json        # 任务数据存储
├── static/           # 静态资源
│   ├── css/          # CSS样式
│   ├── js/           # JavaScript代码
│   └── sounds/       # 音频文件
├── templates/        # HTML模板
│   └── index.html    # 主页
└── README.md         # 项目文档

# 此处未列出的会在以后版本实现
```

## 🚀 使用指南

### 基本任务操作

1. **添加任务**：点击"+ 新增任务"按钮，输入任务名称和预计时长
2. **删除任务**：点击任务旁的"删除"按钮
3. **重命名任务**：点击任务旁的"重命名"按钮
4. **标记完成**：勾选任务复选框
5. **修改时长**：在时长输入框中修改数字
6. **开始/暂停计时**：点击"开始"/"暂停"按钮

### AI智能建议

当任务标记为完成时，系统会自动调用AI获取关于任务完成时间的建议，并通过弹窗显示。AI会根据以下信息提供建议：
- 用户设置的预计时长
- AI计算的推荐时长
- 实际完成时间
- 任务名称

### 硬件显示（可选）

如果连接了51开发板，系统会自动将任务完成率发送到开发板进行显示。请确保：
1. 开发板正确连接到计算机
2. `.env`文件中的串口配置正确
3. 开发板已上传相应的接收程序

## ⚠️ 注意事项

1. 确保已正确配置API密钥，否则AI功能将无法使用
2. 任务数量上限为8个，超过上限将无法添加新任务
3. 计时功能依赖后端服务器，请确保服务器稳定运行
4. 硬件交互功能需要正确连接51开发板并配置串口
5. 音频提醒功能需要浏览器支持音频播放

## 🔧 开发说明

### 添加新功能

1. 后端逻辑在`app.py`中实现
2. 前端界面在`templates/index.html`中定义
3. 前端交互逻辑在`static/js/progress.js`中实现
4. 样式调整在`static/css/progress.css`中进行

### 调试模式

默认以调试模式运行，如需关闭调试模式，请修改`app.py`中的：

```python
app.run(debug=False, port=80, host="0.0.0.0", threaded=True)
```

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进本项目！

## 📝 许可证

[MIT License](LICENSE)