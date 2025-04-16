# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 02:28:11 2025

@author: kim21
"""
import tkinter as tk
#import google.generativeai as genai
# from markdown_pdf import MarkdownPdf
from markdown_pdf import Section
from Cookbook_Func_init import init, get_response, new_pdf, markdown_to_text

# 文字設定
font1 = ("Arial", 12)
font2 = ("Times New Roman", 16)
font3 = ("Times New Roman", 16, "bold")

# 創立兩介面:API Key & Chatbox
model = None
chat = None
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

### API Key 置頂視窗創建
key = tk.Toplevel(chatbox, relief="raised", bd=3, bg="MistyRose2")
key.title("Please enter your Gemini API Key")
key.resizable(False, False)

top_width = 400
top_height = 120

top_x_cordinate = int((screen_width / 2) - (top_width / 2))
top_y_cordinate = int((3 * screen_height / 7) - (3 * top_height / 7))

key.geometry(
    "{}x{}+{}+{}".format(top_width, top_height, top_x_cordinate, top_y_cordinate)
)
key.attributes("-topmost", True)

api_key=None
# Key Checking function
def check_key():
    try:
        global api_key
        print('123')
        btn_key_y.config(state=tk.DISABLED)
        key_entry.config(state=tk.DISABLED)
        api_key = key_entry.get()
        init(api_key)
        
        chatbox.lift()
        button1.config(state=tk.NORMAL)
        button2.config(state=tk.NORMAL)
        question_text.config(state=tk.NORMAL)
        question_text.insert(1.0, 'Press "Crtl+Enter" to send message...')
        key.destroy()

    except Exception as e:
        tk.messagebox.showerror(
            "Error", f"{e},\n Please check your API key and try again."
        )
        btn_key_y.config(state=tk.NORMAL)
        key_entry.config(state=tk.NORMAL)

def close_app():
    key.destroy()
    chatbox.destroy()

# key輸入框: global層，物件不宣告
tk.Label(key, text="Pleas enter your API Key", font=font3, bg="MistyRose2").pack(pady=4)
key_entry = tk.Entry(
    key, justify="center", font=font1, show="*", width=40, bg="MistyRose2"
)
key_entry.pack(pady=4)

btn_key_y = tk.Button(
    key, text="Confirm", font=font3, command=check_key, bg="MistyRose3"
)
btn_key_y.pack(side="left", anchor="s", expand=1, pady=6)

btn_key_n = tk.Button(key, text="Leave", font=font3, command=close_app, bg="MistyRose3")
btn_key_n.pack(side="left", anchor="s", expand=1, pady=6)

# 關閉視窗操作欄(最小化、關閉視窗)
key.overrideredirect(True)

##### 置頂視窗測試行:chatbox.mainloop() #####

# Chatbox 主要功能創建
query = ""


def get_question(question):
    question_text.config(state=tk.DISABLED)
    question = question_text.get(1.0, "end")
    global response, query
    query = question #pdf記錄用，綁定題目與答案用
    response = get_response(question)
    # print for test
    # print(question)
    # print(response)
    label_chatbox.config(state=tk.NORMAL)
    label_chatbox.insert("end", "\n" + question + "\n")
    label_chatbox.insert("end", markdown_to_text(response) + "\n")
    label_chatbox.config(state=tk.DISABLED)
    question_text.config(state=tk.NORMAL)
    button3.config(state=tk.NORMAL)


# 新筆記
pdf = None


def new_note():
    global pdf
    pdf = new_pdf()
    button2.config(state=tk.DISABLED)
    button3.config(state=tk.NORMAL)
    button4.config(state=tk.NORMAL)


# 抄錄筆記
def note_donw():
    button3.config(state=tk.DISABLED)
    global pdf
    pdf.add_section(Section("### " + query + "\n\n" + response, toc=False))
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
    button5.config(state=tk.NORMAL)
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
        saving, text="Save", bg="MistyRose3", font=font1, command=save_note
    )

    # Create exit button.
    button6 = tk.Button(
        saving, text="Exit", bg="MistyRose3", font=font1, command=exit_saving
    )

    entry_title.pack(pady=6)
    entry_author.pack(pady=6)
    button5.pack(side="left", anchor="s", padx=36, pady=6)
    button6.pack(side="right", anchor="s", padx=36, pady=6)

    # Display until closed manually.
    saving.mainloop()


# Chatbox 介面排版

# 1) 對話框區分為: 回應區 及 填答區
# a) 回應區
# Set a frame to 回應區(for respective scroll bar)
fm1 = tk.Frame(chatbox)  # 長寬依textbox為主，故不設長寬
fm1.pack()

# Add scroll bar to 回應區
response_scrollbar = tk.Scrollbar(fm1)
response_scrollbar.pack(side="right", fill="y")

# Response Area
label_chatbox = tk.Text(
    fm1,
    font=font1,
    yscrollcommand=response_scrollbar.set,
    width=118,
    height=27,
    relief="groove",
    fg="grey88",
    bg="grey12",
)  # 高度及寬度隨字元
response_scrollbar.config(command=label_chatbox.yview)

label_chatbox.insert(1.0, "How may I help you?\n")
label_chatbox.config(state=tk.DISABLED)

label_chatbox.pack()
# b) 填答區
# Set a frame to 填答區(for respective scroll bar)
fm2 = tk.Frame(chatbox)
fm2.pack()

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
    height=10,
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

question_text.pack()

# 2) 操作欄
# global pdf
# Create Exit button
button1 = tk.Button(
    chatbox,
    text="Exit",
    state=tk.DISABLED,
    font=font1,
    bg="MistyRose3",
    relief="raised",
    command=chatbox.destroy,
)

# Create New PDF button
button2 = tk.Button(
    chatbox,
    text="New Note",
    state=tk.DISABLED,
    font=font1,
    bg="MistyRose3",
    relief="raised",
    command=new_note,
)

# Create Add Section button
button3 = tk.Button(
    chatbox,
    text="Note down current answer",
    state=tk.DISABLED,
    font=font1,
    bg="MistyRose3",
    relief="raised",
    command=note_donw,
)

# Create Save PDF button
## Run a window to set title, author, file name.
# global button4
button4 = tk.Button(
    chatbox,
    text="Save Note",
    state=tk.DISABLED,
    font=font1,
    bg="MistyRose3",
    relief="raised",
    command=save_setting,
)

button2.pack(side="left", anchor="s", padx=24, pady=8)
button3.pack(side="left", anchor="s", pady=8)
button4.pack(side="left", anchor="s", padx=24, pady=8)
button1.pack(side="right", anchor="s", padx=24, pady=8)

chatbox.mainloop()
