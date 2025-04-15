import os
import shutil
import tempfile
import gradio as gr
from git import Repo
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not set")

client = OpenAI(api_key=OPENAI_API_KEY)
SUPPORTED_EXTS = [".py", ".java", ".js", ".jsx", ".ts", ".tsx", ".html", ".cs"]

# Clone repo to temp dir and return list of supported files
def clone_repo(github_url):
    repo_dir = tempfile.mkdtemp()
    Repo.clone_from(github_url, repo_dir)
    supported_files = []
    for root, _, files in os.walk(repo_dir):
        for file in files:
            if any(file.endswith(ext) for ext in SUPPORTED_EXTS):
                rel_path = os.path.relpath(os.path.join(root, file), repo_dir)
                supported_files.append(rel_path)
    return repo_dir, supported_files

# Gradio callback: update dropdown
def update_files_ui(github_url):
    try:
        repo_dir, supported_files = clone_repo(github_url)
        return gr.update(choices=["(Whole repo)"] + supported_files, value="(Whole repo)"), repo_dir
    except Exception as e:
        return gr.update(choices=["(Error)"], value="(Error)"), ""

# Gradio callback: respond to question
def respond_question(question, file_path, repo_dir):
    if file_path == "(Whole repo)":
        contents = []
        for root, _, files in os.walk(repo_dir):
            for file in files:
                if any(file.endswith(ext) for ext in SUPPORTED_EXTS):
                    full_path = os.path.join(root, file)
                    try:
                        with open(full_path, "r", encoding="utf-8") as f:
                            contents.append(f"\n\n# File: {os.path.relpath(full_path, repo_dir)}\n" + f.read())
                    except Exception:
                        continue
        context = "\n".join(contents)
    else:
        full_path = os.path.join(repo_dir, file_path)
        with open(full_path, "r", encoding="utf-8") as f:
            context = f.read()

    if len(context) > 12000:
        context = context[:12000]  # trim to avoid rate limits

    prompt = [
        {"role": "system", "content": "You are a senior developer helping analyze a codebase."},
        {"role": "user", "content": f"Given the following code:\n{context}\n\nQuestion: {question}"}
    ]

    response = client.chat.completions.create(
        model="gpt-4",
        messages=prompt,
        temperature=0.2
    )
    return response.choices[0].message.content

# Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("## 🔍 GitHub Code Analyzer (A Senior Developer Bot Helping Analyze a Codebase.)")
    github_url = gr.Textbox(label="GitHub Repository URL")
    get_files_btn = gr.Button("Load Files")
    file_dropdown = gr.Dropdown(label="Select File (Optional)", choices=["(Whole repo)"], value="(Whole repo)")
    question = gr.Textbox(label="Ask a question about the code")
    answer = gr.Textbox(label="Answer", lines=10)
    repo_state = gr.State()

    get_files_btn.click(update_files_ui, inputs=github_url, outputs=[file_dropdown, repo_state])
    question.submit(respond_question, inputs=[question, file_dropdown, repo_state], outputs=answer)

demo.launch()
