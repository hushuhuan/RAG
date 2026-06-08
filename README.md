# RAG LangGraph App

一个基于 LangGraph 架构的检索增强生成（RAG）应用，支持上传本地文件并进行问答。

## 功能

- 支持上传 PDF、TXT、MD 格式的文件
- 使用 LangGraph 构建 RAG 工作流
- 使用 Chroma 向量数据库进行文档检索
- 使用 OpenAI 模型进行问答
- 使用 Streamlit 构建的现代化 Web GUI

## 技术栈

- **前端**: Streamlit + Python
- **后端**: FastAPI + Python + LangGraph
- **RAG**: LangChain + LangGraph + Chroma
- **AI**: OpenAI API

## 安装

```bash
pip install -r requirements.txt
```

## 配置

1. 复制 `.env` 文件并填写你的 OpenAI API Key：

```env
OPENAI_API_KEY=your-api-key-here
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-4o-mini
PORT=5174
```

## 运行

### 启动后端 API 服务器（终端1）：

```bash
python server/main.py
```

### 启动前端 Streamlit 应用（终端2）：

```bash
streamlit run app.py
```

## 使用说明

1. 打开浏览器访问 Streamlit 显示的地址（通常是 http://localhost:8501）
2. 在侧边栏上传你的文档文件（支持 PDF、TXT、MD）
3. 在聊天框中输入问题
4. 系统会基于上传的文档内容进行回答

## 项目结构

```
├── app.py                 # Streamlit 前端应用
├── server/                # 后端代码
│   ├── rag/               # RAG 相关模块
│   │   ├── loader.py      # 文件加载器
│   │   ├── retriever.py   # 向量检索器
│   │   └── graph.py       # LangGraph 工作流
│   └── main.py            # FastAPI 服务器入口
├── data/                  # 数据存储目录
├── .env                   # 环境配置
└── requirements.txt       # Python 依赖配置
```

## License

MIT
