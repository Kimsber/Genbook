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
def init(key):
    global chat, model
    genai.configure(api_key=key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    chat = reset_history()

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


pdf = new_pdf()


# 物件操作建議直接寫在main.py
def new_section(question,response):
    pdf.add_section(Section("### " + question + "\n\n" + response, toc=False))

# new_section()

# 注意:pdf必須有內容才能存檔
def save_pdf(title, author, fdir):
    pdf.meta["title"] = title
    pdf.meta["author"] = author
    pdf.save(f"{fdir}.pdf")


# save_pdf('title','kim','R cookbook')

# Markdown轉文字
from bs4 import BeautifulSoup
from markdown import markdown
import re


def markdown_to_text(markdown_string):
    """Converts a markdown string to plaintext"""

    # md -> html -> text since BeautifulSoup can extract text cleanly
    html = markdown(markdown_string)

    # remove code snippets
    html = re.sub(r"<pre>(.*?)</pre>", " ", html)
    html = re.sub(r"<code>(.*?)</code >", " ", html)

    # extract text
    soup = BeautifulSoup(html, "html.parser")
    text = "".join(soup.findAll(text=True))

    return text
