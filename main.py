from fastapi import FastAPI, UploadFile, File
from openai import OpenAI
import os

app = FastAPI()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# ====== 规则直接写在这里 ======
PRINCIPLE = """
所有的内容需要依赖我导入的文件
格式书写为Rmarkdown
不能进行任何推测和创造
"""
# ==============================

@app.get("/")
def root():
    return {
        "status": "Ethanyy Agent 运行中 ✅",
        "principle": PRINCIPLE
    }

@app.post("/run")
async def run_agent(
    question: str,
    file: UploadFile = File(...)
):
    # 1. 读取用户上传的文件
    file_content = await file.read()
    file_text = file_content.decode("utf-8")

    # 2. 构建消息，直接使用上面的 PRINCIPLE
    messages = [
        {
            "role": "system",
            "content": PRINCIPLE
        },
        {
            "role": "user",
            "content": f"""
【文件内容开始】
{file_text}
【文件内容结束】

问题：{question}
"""
        }
    ]

    # 3. 调用 OpenAI，temperature=0 禁止推测
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0
    )

    return {
        "result": response.choices[0].message.content,
        "source_file": file.filename
    }
