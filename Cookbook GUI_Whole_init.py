# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 02:28:11 2025

@author: kim21
"""
import tkinter as tk
import json
import os
from tkinter import messagebox, ttk
#import google.generativeai as genai
# from markdown_pdf import MarkdownPdf
from markdown_pdf import Section
from Cookbook_Func_init import (
    get_supported_model_metadata,
    get_response,
    init,
    markdown_to_text,
    new_pdf,
)

# 文字設定
font1 = ("Arial", 12)
font3 = ("Times New Roman", 16, "bold")

# 統一按鈕樣式
BTN_BG = "MistyRose3"
BTN_FG = "grey12"
BTN_ACTIVE_BG = "MistyRose2"
BTN_ACTIVE_FG = "grey12"

# 創立兩介面:API Key & Chatbox
response = ""
question = ""  ###確認用API key用

### Chatbox 主介面基本創建
chatbox = tk.Tk()
chatbox.resizable(False, False)
chatbox.title("Gemini Chat Note")
chatbox.configure(background="MistyRose4")

# 指定視窗大小並畫面置中
window_width = 1080
window_height = 720

screen_width = chatbox.winfo_screenwidth()
screen_height = chatbox.winfo_screenheight()

x_cordinate = int((screen_width / 2) - (window_width / 2))
y_cordinate = int((screen_height / 4) - (window_height / 4))

chatbox.geometry(
    "{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate)
)

model_status_var = tk.StringVar(value="Connected model: (not connected)")
model_status_label = tk.Label(
    chatbox,
    textvariable=model_status_var,
    font=font1,
    bg="MistyRose4",
    fg="grey18",
)
model_status_label.pack(pady=(6, 2))

### API Key 置頂視窗創建
key = tk.Toplevel(chatbox, relief="raised", bd=3, bg="MistyRose2")
key.title("Please enter your Gemini API Key")
key.resizable(False, False)

top_width = 400
top_height = 220

top_x_cordinate = int((screen_width / 2) - (top_width / 2))
top_y_cordinate = int((3 * screen_height / 7) - (3 * top_height / 7))

key.geometry(
    "{}x{}+{}+{}".format(top_width, top_height, top_x_cordinate, top_y_cordinate)
)
key.attributes("-topmost", True)
key.grab_set()

api_key=None
AUTO_MODEL_LABEL = "Auto (Recommended)"
model_display_to_id = {}
model_selector_var = tk.StringVar(value="")
CONFIG_FILE = "genbook_config.json"


def load_model_selection_config():
    default = {"mode": "auto", "model_id": ""}
    if not os.path.exists(CONFIG_FILE):
        return default

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        selection = data.get("model_selection", {})
        mode = selection.get("mode", "auto")
        model_id = selection.get("model_id", "")
        if mode not in ["auto", "manual"]:
            return default
        return {"mode": mode, "model_id": model_id}
    except Exception:
        return default


def save_model_selection_config(mode, model_id):
    data = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}

    data["model_selection"] = {"mode": mode, "model_id": model_id}
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


model_selection_config = load_model_selection_config()


def refresh_models():
    global model_display_to_id, model_selection_config
    entered_key = key_entry.get().strip()
    if not entered_key:
        messagebox.showwarning(
            "Missing API Key", "Please enter your API key first.", parent=key
        )
        return

    btn_refresh.config(state=tk.DISABLED)
    btn_key_y.config(state=tk.DISABLED)
    key_entry.config(state=tk.DISABLED)
    model_selector.config(state="disabled")

    try:
        model_info = get_supported_model_metadata(entered_key)
        if not model_info:
            raise RuntimeError("No models supporting generateContent were found.")

        model_display_to_id = {m["label"]: m["id"] for m in model_info}
        options = [AUTO_MODEL_LABEL] + list(model_display_to_id.keys())
        model_selector["values"] = options

        saved_mode = model_selection_config.get("mode", "auto")
        saved_model_id = model_selection_config.get("model_id", "")
        id_to_label = {model_id: label for label, model_id in model_display_to_id.items()}
        saved_label = id_to_label.get(saved_model_id)
        if saved_mode == "manual" and saved_label:
            model_selector_var.set(saved_label)
            status_text = (
                f"Loaded {len(model_info)} supported models. Restored: {saved_label}."
            )
        else:
            model_selector_var.set(AUTO_MODEL_LABEL)
            status_text = f"Loaded {len(model_info)} supported models."

        model_selector.config(state="readonly")
        status_model_fetch.config(text=status_text, fg="darkgreen")
        btn_key_y.config(state=tk.NORMAL)
    except Exception as e:
        model_display_to_id = {}
        model_selector["values"] = ()
        model_selector_var.set("")
        status_model_fetch.config(
            text="Failed to load models. Please check API key/network.",
            fg="firebrick",
        )
        messagebox.showerror("Model Discovery Error", str(e), parent=key)
    finally:
        key_entry.config(state=tk.NORMAL)
        btn_refresh.config(state=tk.NORMAL)


# Key Checking function
def check_key():
    try:
        global api_key, model_selection_config
        btn_key_y.config(state=tk.DISABLED)
        btn_refresh.config(state=tk.DISABLED)
        key_entry.config(state=tk.DISABLED)
        model_selector.config(state="disabled")

        api_key = key_entry.get().strip()
        if not api_key:
            raise ValueError("API key cannot be empty.")

        selected_label = model_selector_var.get().strip()
        if not selected_label:
            raise ValueError("Please click 'Load Models' first.")

        selected_model_id = None
        if selected_label != AUTO_MODEL_LABEL:
            selected_model_id = model_display_to_id.get(selected_label)
            if selected_model_id is None:
                raise ValueError("Selected model is unavailable. Please reload models.")

        selected_model = init(api_key, selected_model_id)
        model_status_var.set(f"Connected model: {selected_model}")

        if selected_label == AUTO_MODEL_LABEL:
            save_model_selection_config("auto", "")
            model_selection_config = {"mode": "auto", "model_id": ""}
        else:
            save_model_selection_config("manual", selected_model_id)
            model_selection_config = {"mode": "manual", "model_id": selected_model_id}
        
        chatbox.lift()
        button1.config(state=tk.NORMAL)
        button2.config(state=tk.NORMAL)
        question_text.config(state=tk.NORMAL)
        question_text.delete(1.0, "end")
        question_text.insert(1.0, 'Press "Ctrl+Enter" to send message...')
        key.destroy()

    except Exception as e:
        messagebox.showerror(
            "Error", f"{e},\n Please check your API key and try again.", parent=key
        )
        btn_key_y.config(state=tk.NORMAL)
        btn_refresh.config(state=tk.NORMAL)
        key_entry.config(state=tk.NORMAL)
        if model_selector["values"]:
            model_selector.config(state="readonly")

def close_app():
    key.destroy()
    chatbox.destroy()

# key輸入框: 統一排版與樣式
key_body = tk.Frame(key, bg="MistyRose2", padx=14, pady=10)
key_body.pack(fill="both", expand=True)

tk.Label(
    key_body,
    text="Enter Gemini API Key",
    font=font3,
    bg="MistyRose2",
    fg="grey18",
).pack(anchor="w", pady=(0, 3))

key_entry = tk.Entry(
    key_body,
    justify="left",
    font=font1,
    show="*",
    width=42,
    bg="white",
    relief="groove",
)
key_entry.pack(fill="x", pady=(0, 8))

tk.Label(
    key_body,
    text="Select Model",
    font=font1,
    bg="MistyRose2",
    fg="grey18",
).pack(anchor="w", pady=(0, 3))

model_selector = ttk.Combobox(
    key_body,
    textvariable=model_selector_var,
    state="disabled",
    width=42,
)
model_selector.pack(fill="x", pady=(0, 8))

status_model_fetch = tk.Label(
    key_body,
    text="Load models to continue.",
    font=("Arial", 10),
    bg="MistyRose2",
    fg="grey28",
    wraplength=360,
    justify="left",
)
status_model_fetch.pack(anchor="w", pady=(0, 8))

action_row = tk.Frame(key_body, bg="MistyRose2")
action_row.pack(fill="x")

btn_refresh = tk.Button(
    action_row,
    text="Load Models",
    font=font1,
    width=12,
    command=refresh_models,
    bg=BTN_BG,
    fg=BTN_FG,
    activebackground=BTN_ACTIVE_BG,
    activeforeground=BTN_ACTIVE_FG,
    relief="raised",
)
btn_refresh.pack(side="left")

btn_key_n = tk.Button(
    action_row,
    text="Leave",
    font=font1,
    width=10,
    command=close_app,
    bg=BTN_BG,
    fg=BTN_FG,
    activebackground=BTN_ACTIVE_BG,
    activeforeground=BTN_ACTIVE_FG,
    relief="raised",
)
btn_key_n.pack(side="right")

btn_key_y = tk.Button(
    action_row,
    text="Confirm",
    font=font1,
    width=10,
    command=check_key,
    bg=BTN_BG,
    fg=BTN_FG,
    activebackground=BTN_ACTIVE_BG,
    activeforeground=BTN_ACTIVE_FG,
    relief="raised",
    state=tk.DISABLED,
)
btn_key_y.pack(side="right", padx=(0, 8))

# Allow normal window controls so warnings and focus behavior remain usable.
key.protocol("WM_DELETE_WINDOW", close_app)

##### 置頂視窗測試行:chatbox.mainloop() #####

# Chatbox 主要功能創建
query = ""
current_context_markdown = ""
edited_context_markdown = ""


def build_current_context(question_text_value, response_text_value):
    return "### " + question_text_value + "\n\n" + response_text_value


def open_context_editor():
    global edited_context_markdown
    source_text = edited_context_markdown or current_context_markdown
    if not source_text.strip():
        messagebox.showwarning(
            "No Context",
            "No current context to edit. Send a message first.",
            parent=chatbox,
        )
        return

    editor = tk.Toplevel(chatbox, bg="MistyRose2")
    editor.title("Edit Current Context")
    editor.geometry("760x520")
    editor.transient(chatbox)

    tk.Label(
        editor,
        text="Edit context before adding to PDF",
        font=font1,
        bg="MistyRose2",
        fg="grey20",
    ).pack(pady=(8, 4))

    editor_frame = tk.Frame(editor)
    editor_frame.pack(fill="both", expand=True, padx=10, pady=6)

    editor_scroll = tk.Scrollbar(editor_frame)
    editor_scroll.pack(side="right", fill="y")

    editor_text = tk.Text(
        editor_frame,
        font=font1,
        yscrollcommand=editor_scroll.set,
        wrap="word",
        relief="groove",
        bg="grey98",
        fg="grey12",
    )
    editor_scroll.config(command=editor_text.yview)
    editor_text.pack(fill="both", expand=True)
    editor_text.insert("1.0", source_text)

    action_bar = tk.Frame(editor, bg="MistyRose2")
    action_bar.pack(fill="x", padx=10, pady=(0, 10))

    def save_context_edit():
        global edited_context_markdown
        edited_context_markdown = editor_text.get("1.0", "end").strip()
        if not edited_context_markdown:
            messagebox.showwarning(
                "Empty Context",
                "Context cannot be empty.",
                parent=editor,
            )
            return
        editor.destroy()

    tk.Button(
        action_bar,
        text="Save Context",
        font=font1,
        command=save_context_edit,
        bg=BTN_BG,
        fg=BTN_FG,
        activebackground=BTN_ACTIVE_BG,
        activeforeground=BTN_ACTIVE_FG,
        relief="raised",
    ).pack(side="left", padx=(0, 8))

    tk.Button(
        action_bar,
        text="Cancel",
        font=font1,
        command=editor.destroy,
        bg=BTN_BG,
        fg=BTN_FG,
        activebackground=BTN_ACTIVE_BG,
        activeforeground=BTN_ACTIVE_FG,
        relief="raised",
    ).pack(side="left")


def get_question(event):
    question_text.config(state=tk.DISABLED)
    question = question_text.get(1.0, "end").strip()
    if not question:
        question_text.config(state=tk.NORMAL)
        return
    global response, query, current_context_markdown, edited_context_markdown
    query = question #pdf記錄用，綁定題目與答案用
    response = get_response(question)
    current_context_markdown = build_current_context(query, response)
    edited_context_markdown = ""
    # print for test
    # print(question)
    # print(response)
    label_chatbox.config(state=tk.NORMAL)
    label_chatbox.insert("end", "\n" + question + "\n")
    label_chatbox.insert("end", markdown_to_text(response) + "\n")
    label_chatbox.config(state=tk.DISABLED)
    question_text.config(state=tk.NORMAL)
    question_text.delete(1.0, "end")
    button3.config(state=tk.NORMAL)
    button_context.config(state=tk.NORMAL)


# 新筆記
pdf = None


def new_note():
    global pdf
    pdf = new_pdf()
    button2.config(state=tk.DISABLED)
    button4.config(state=tk.NORMAL)


# 抄錄筆記
def note_down():
    button3.config(state=tk.DISABLED)
    button_context.config(state=tk.DISABLED)
    global pdf, current_context_markdown, edited_context_markdown
    content = edited_context_markdown or current_context_markdown
    if not content.strip():
        messagebox.showwarning(
            "No Context",
            "No current context to add. Send a message first.",
            parent=chatbox,
        )
        button3.config(state=tk.NORMAL)
        button_context.config(state=tk.NORMAL)
        return
    pdf.add_section(Section(content, toc=False))
    # print('### '+query+'\n\n'+response)


# 儲存筆記
entry_title = None
entry_author = None


def save_note():
    button5.config(state=tk.DISABLED)
    global pdf, entry_title, entry_author
    title = entry_title.get()
    author = entry_author.get()
    # print(title,author)
    pdf.meta["title"] = title
    pdf.meta["author"] = author
    pdf.save(f"{title}.pdf")
    pdf = None
    button2.config(state=tk.NORMAL)
    saving.title("Save PDF - Successed")


# 離開存檔
def exit_saving():
    button2.config(state=tk.NORMAL)
    button4.config(state=tk.NORMAL)
    saving.destroy()


# 存檔介面功能
saving = None
button5 = None
button6 = None


def save_setting():
    global pdf, saving, entry_title, entry_author, button5, button6
    button4.config(state=tk.DISABLED)
    # Create widget
    saving = tk.Toplevel(bg="grey20")

    # define title for window
    saving.title("Save PDF")

    # specify size
    saving.geometry("300x120")

    # Create entry: title & author
    entry_title = tk.Entry(
        saving, width=60, justify="center", font=font1, bg="MistyRose2"
    )
    entry_title.insert("end", "Please enter title (filename)")

    entry_author = tk.Entry(
        saving, width=60, justify="center", font=font1, bg="MistyRose2"
    )
    entry_author.insert("end", "Please enter author")

    # Create save button.
    button5 = tk.Button(
        saving,
        text="Save",
        bg=BTN_BG,
        fg=BTN_FG,
        activebackground=BTN_ACTIVE_BG,
        activeforeground=BTN_ACTIVE_FG,
        relief="raised",
        font=font1,
        command=save_note,
    )

    # Create exit button.
    button6 = tk.Button(
        saving,
        text="Exit",
        bg=BTN_BG,
        fg=BTN_FG,
        activebackground=BTN_ACTIVE_BG,
        activeforeground=BTN_ACTIVE_FG,
        relief="raised",
        font=font1,
        command=exit_saving,
    )

    entry_title.pack(pady=6)
    entry_author.pack(pady=6)
    button5.pack(side="left", anchor="s", padx=36, pady=6)
    button6.pack(side="right", anchor="s", padx=36, pady=6)

    # Display until closed manually.
    saving.mainloop()


# Chatbox 介面排版

# 0) 導覽列
nav_bar = tk.Frame(chatbox, bg=BTN_BG, relief="raised", bd=1)
nav_bar.pack(side="bottom", fill="x", padx=2, pady=(0, 2))

# Create New PDF button
button2 = tk.Button(
    nav_bar,
    text="New Note",
    state=tk.DISABLED,
    font=font1,
    bg=BTN_BG,
    fg=BTN_FG,
    activebackground=BTN_ACTIVE_BG,
    activeforeground=BTN_ACTIVE_FG,
    relief="raised",
    command=new_note,
)

# Create Add Section button
button3 = tk.Button(
    nav_bar,
    text="Note down current answer",
    state=tk.DISABLED,
    font=font1,
    bg=BTN_BG,
    fg=BTN_FG,
    activebackground=BTN_ACTIVE_BG,
    activeforeground=BTN_ACTIVE_FG,
    relief="raised",
    command=note_down,
)

button_context = tk.Button(
    nav_bar,
    text="Edit Context",
    state=tk.DISABLED,
    font=font1,
    bg=BTN_BG,
    fg=BTN_FG,
    activebackground=BTN_ACTIVE_BG,
    activeforeground=BTN_ACTIVE_FG,
    relief="raised",
    command=open_context_editor,
)

# Create Save PDF button
button4 = tk.Button(
    nav_bar,
    text="Save Note",
    state=tk.DISABLED,
    font=font1,
    bg=BTN_BG,
    fg=BTN_FG,
    activebackground=BTN_ACTIVE_BG,
    activeforeground=BTN_ACTIVE_FG,
    relief="raised",
    command=save_setting,
)

# Create Exit button
button1 = tk.Button(
    nav_bar,
    text="Exit",
    state=tk.DISABLED,
    font=font1,
    bg=BTN_BG,
    fg=BTN_FG,
    activebackground=BTN_ACTIVE_BG,
    activeforeground=BTN_ACTIVE_FG,
    relief="raised",
    command=chatbox.destroy,
)

button2.pack(side="left", padx=16, pady=6)
button3.pack(side="left", padx=8, pady=6)
button_context.pack(side="left", padx=8, pady=6)
button4.pack(side="left", padx=16, pady=6)
button1.pack(side="right", padx=16, pady=6)

# 1) 對話框區分為: 回應區 及 填答區
# a) 回應區
# Set a frame to 回應區(for respective scroll bar)
fm1 = tk.Frame(chatbox)  # 長寬依textbox為主，故不設長寬
fm1.pack(fill="both", expand=True, padx=2, pady=(2, 0))

# Add scroll bar to 回應區
response_scrollbar = tk.Scrollbar(fm1)
response_scrollbar.pack(side="right", fill="y")

# Response Area
label_chatbox = tk.Text(
    fm1,
    font=font1,
    yscrollcommand=response_scrollbar.set,
    width=118,
    height=22,
    relief="groove",
    fg="grey88",
    bg="grey12",
)  # 高度及寬度隨字元
response_scrollbar.config(command=label_chatbox.yview)

label_chatbox.insert(1.0, "How may I help you?\n")
label_chatbox.config(state=tk.DISABLED)

label_chatbox.pack(fill="both", expand=True)
# b) 填答區
# Set a frame to 填答區(for respective scroll bar)
fm2 = tk.Frame(chatbox)
fm2.pack(fill="x", padx=2, pady=(0, 2))

# Add scroll bar to chatbox
question_scrollbar = tk.Scrollbar(fm2)
question_scrollbar.pack(side="right", fill="y")

# Question Area
# global question_text #需要轉出供外部程式使用
question_text = tk.Text(
    fm2,
    font=font1,
    yscrollcommand=question_scrollbar.set,
    width=120,
    height=7,
    relief="groove",
    fg="grey82",
    bg="grey18",
    state=tk.DISABLED,
)
question_scrollbar.config(command=question_text.yview)


# Bind Enter key to function
# 一鍵兩步: 1.)送出問題 2.)取得回應
question_text.focus()
# global question
question_text.bind("<Control-Return>", get_question)

question_text.pack(fill="x")

chatbox.mainloop()
