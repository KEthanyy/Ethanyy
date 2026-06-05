from fastapi import FastAPI, UploadFile, File
from openai import OpenAI
import httpx
import os

app = FastAPI()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# ====== 自动从 GitHub 读取 Principle 文件 ======
GITHUB_PRINCIPLE_URL = "https://raw.githubusercontent.com/KEthanyy/Ethanyy/main/Principle"

def load_principle() -> str:
    """每次启动自动加载 Principle 作为系统提示词"""
    try:
        response = httpx.get(GITHUB_PRINCIPLE_URL)
        if response.status_code == 200:
            return response.text
        else:
            return "严格按照用户上传的文件内容，格式输出为Rmarkdown，不进行任何推测和创造"
    except Exception as e:
        return f"加载失败: {e}"

# ====== API 端点 ======
@app.get("/")
def root():
    principle = load_principle()
    return {
        "status": "Ethanyy Agent 运行中 ✅",
        "principle_loaded": True,
        "principle_preview": principle[:100]
    }

@app.post("/run")
async def run_agent(
    question: str,
    file: UploadFile = File(...)
):
    # 1. 读取用户上传的文件
    file_content = await file.read()
    file_text = file_content.decode("utf-8")

    # 2. 加载 Principle 作为系统提示词
    system_prompt = load_principle()

    # 3. 构建消息
    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": f"""
【导入的文件内容如下】
{file_text}
【文件内容结束】

问题：{question}
"""
        }
    ]

    # 4. 调用 OpenAI，temperature=0 禁止推测
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0
    )

    result = response.choices[0].message.content

    return {
        "rmarkdown_output": result,
        "source_file": file.filename,
        "principle_applied": True
    }
