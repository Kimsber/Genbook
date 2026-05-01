# -*- coding: utf-8 -*-
"""
Created on Sat Feb  8 02:21:02 2025

@author: kim21
"""

import google.generativeai as genai  # 第一次需安裝
from markdown_pdf import MarkdownPdf
from markdown_pdf import Section
from bs4 import BeautifulSoup
from markdown import markdown
import re

# 需由輸入列取得Key，GUI整合時加入

model = None
chat = None

def _model_sort_key(model_info):
    """Ranks models for deterministic auto-selection."""
    model_id = model_info["id"].lower()
    is_experimental = any(tag in model_id for tag in ["exp", "experimental", "preview"])

    if "flash" in model_id:
        family_rank = 0
    elif "pro" in model_id:
        family_rank = 1
    else:
        family_rank = 2

    return (family_rank, 1 if is_experimental else 0, model_id)


def get_supported_model_metadata(key):
    """Returns supported chat models with normalized metadata for UI use."""
    genai.configure(api_key=key)
    supported = []

    for m in genai.list_models():
        methods_raw = (
            getattr(m, "supported_generation_methods", None)
            or getattr(m, "supportedGenerationMethods", None)
            or []
        )
        methods = [str(method) for method in methods_raw]
        supports_chat = any(
            method == "generateContent" or method.endswith("generateContent")
            for method in methods
        )
        if not supports_chat:
            continue

        model_id = getattr(m, "name", "") or getattr(m, "model_name", "")
        if not model_id:
            continue

        supported.append(
            {
                "id": model_id,
                "label": model_id.replace("models/", "", 1),
                "input_token_limit": getattr(m, "input_token_limit", None),
                "output_token_limit": getattr(m, "output_token_limit", None),
                "supported_methods": methods,
            }
        )

    supported.sort(key=_model_sort_key)
    return supported


def get_supported_models(key):
    """Returns supported model IDs for backward compatibility."""
    return [m["id"] for m in get_supported_model_metadata(key)]

def init(key, model_name=None):
    global chat, model
    genai.configure(api_key=key)
    supported_models = get_supported_model_metadata(key)
    if not supported_models:
        raise RuntimeError("No supported models found for this API key.")

    supported_ids = {m["id"] for m in supported_models}

    if model_name is not None:
        if model_name not in supported_ids:
            raise ValueError(f"Model '{model_name}' is not supported for this API key.")
        selected_model = model_name
    else:
        selected_model = supported_models[0]["id"]

    model = genai.GenerativeModel(selected_model)
    chat = reset_history()
    return selected_model

def reset_history():
    global chat, model #宣告全域才能在response使用
    chat = model.start_chat(history=[])  # 重新執行會重置紀錄
    return chat

# 需由輸入列取得問題，GUI整合時加入
#question = "Do you know which those R functions are essential for data management, functional and object-oriented paradigms, operators, tooling and visualizations?"

def get_response(question):
    response = chat.send_message(question)
    response = response.text
    return response

#response = get_response(question)

def new_pdf():
    pdf = MarkdownPdf(toc_level=2)
    return pdf


pdf = None


# 物件操作建議直接寫在main.py
def new_section(question, response, pdf_obj=None):
    target_pdf = pdf_obj if pdf_obj is not None else pdf
    if target_pdf is None:
        raise ValueError("PDF object is required. Call new_pdf() first.")
    target_pdf.add_section(Section("### " + question + "\n\n" + response, toc=False))

# new_section()

# 注意:pdf必須有內容才能存檔
def save_pdf(title, author, fdir, pdf_obj=None):
    target_pdf = pdf_obj if pdf_obj is not None else pdf
    if target_pdf is None:
        raise ValueError("PDF object is required. Call new_pdf() first.")
    target_pdf.meta["title"] = title
    target_pdf.meta["author"] = author
    target_pdf.save(f"{fdir}.pdf")


# save_pdf('title','kim','R cookbook')

# Markdown轉文字
def markdown_to_text(markdown_string):
    """Converts a markdown string to plaintext"""

    # md -> html -> text since BeautifulSoup can extract text cleanly
    html = markdown(markdown_string)

    # remove code snippets
    html = re.sub(r"<pre>(.*?)</pre>", " ", html)
    html = re.sub(r"<code>(.*?)</code>", " ", html)

    # extract text
    soup = BeautifulSoup(html, "html.parser")
    text = "".join(soup.findAll(text=True))

    return text
