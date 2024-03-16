# -*- encoding: utf-8 -*-
import json
import threading
import time
import tkinter as tk
import tkinter.messagebox
import tkinter.filedialog
import tkinter.font
import tkinter.ttk
import win32api
import win32print
import tempfile
import sys
import re
import os
import win32ui
import windnd
import base64
from Cryptodome.PublicKey import RSA
from Cryptodome.Hash import SHA
from Cryptodome.Signature import PKCS1_v1_5 as PKCS1_signature
import ctypes
import locale
import zipfile

ctypes.windll.shcore.SetProcessDpiAwareness(1)
ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)


def q(func):
    def wrapper(*args, **kwargs):
        del_list = []
        for i in os.listdir("plugin"):
            if i in plugins and os.path.isdir(os.path.join("plugin", i)):
                with open(os.path.join("plugin", i, "package.json"), encoding="utf-8") as f:
                    info = json.load(f)
                    try:
                        for j in info["files"]:
                            if j["position"] == "ask_save":
                                try:
                                    with open(os.path.join("plugin", i, j["file"]), encoding="utf-8") as f:
                                        if j["wait"]:
                                            exec(f.read(), globals(), locals())
                                        else:
                                            threading.Thread(name=info["name"], target=exec,
                                                             args=(f.read(), globals(), locals())).start()
                                except FileNotFoundError:
                                    del_list.append(i)
                    except Exception as err:
                        tk.messagebox.showerror(info["name"], str(err))
        for i in del_list:
            plugins.remove(i)
        if file_url != "":
            if encoding.get() == "auto":
                for i in reversed(encodings):
                    if b.get():
                        with open(file_url, "rb") as f:
                            text = str(f.read())[2:-1]
                            break
                    else:
                        with open(file_url, encoding=i, errors="ignore" if ignore.get() else None) as f:
                            try:
                                text = f.read()
                                break
                            except UnicodeDecodeError:
                                pass
                            except UnicodeError:
                                pass
                else:
                    text = ""
            else:
                if b.get():
                    with open(file_url, "rb") as f:
                        text = str(f.read())[2:-1]
                else:
                    with open(file_url, encoding=encoding.get(), errors="ignore" if ignore.get() else None) as f:
                        try:
                            text = f.read()
                        except UnicodeDecodeError:
                            text = ""
                        except UnicodeError:
                            text = ""
        else:
            text = ""
        if text == e.get("0.0", "end")[:-1]:
            func(*args, **kwargs)
        else:
            a = tk.messagebox.askyesnocancel(lang["text.gui.title"], lang["text.gui.file.exit_save"])
            if a is None:
                return
            elif a:
                if file_url == "":
                    if save_as() == True:
                        func(*args, **kwargs)
                else:
                    if save() == True:
                        func(*args, **kwargs)
            else:
                func(*args, **kwargs)

    return wrapper


@q
def make_new():
    e.delete('0.0', 'end')
    e.edit_reset()
    global file_url
    file_url = ""


def drop(func):
    def warpper(files):
        try:
            url = [i.decode() for i in files]
        except UnicodeDecodeError:
            url = [i.decode("gbk") for i in files]
        func(url[0])

    return warpper


@q
def open_file(url=""):
    del_list = []
    for i in os.listdir("plugin"):
        if i in plugins and os.path.isdir(os.path.join("plugin", i)):
            with open(os.path.join("plugin", i, "package.json"), encoding="utf-8") as f:
                info = json.load(f)
                try:
                    for j in info["files"]:
                        if j["position"] == "open":
                            try:
                                with open(os.path.join("plugin", i, j["file"]), encoding="utf-8") as f:
                                    if j["wait"]:
                                        exec(f.read(), globals(), locals())
                                    else:
                                        threading.Thread(name=info["name"], target=exec,
                                                         args=(f.read(), globals(), locals())).start()
                            except FileNotFoundError:
                                del_list.append(i)
                except Exception as err:
                    tk.messagebox.showerror(info["name"], str(err))
    for i in del_list:
        plugins.remove(i)
    if not url:
        url = tk.filedialog.askopenfilename(title=lang["text.gui.file.open.title"],
                                            filetypes=[(lang["text.gui.file.open.type.txt"], ".txt"),
                                                       (lang["text.gui.file.open.type.all"], ".*")])
    e.delete('0.0', 'end')
    global file_url
    global file_coding
    file_url = ""
    text = ""
    file_url = url
    if b.get():
        with open(url, "rb") as f:
            text = str(f.read())[2:-1]
    else:
        if encoding.get() == "auto":
            for i in reversed(encodings):
                with open(url, encoding=i, errors="ignore" if ignore.get() else None) as f:
                    try:
                        text = f.read()
                        file_coding = i
                        break
                    except UnicodeDecodeError:
                        pass
                    except UnicodeError:
                        pass
            else:
                tk.messagebox.showerror(lang["text.gui.msg.title.error"], lang["text.gui.file.decoding.tips.error"])
        else:
            with open(url, encoding=encoding.get(), errors="ignore" if ignore.get() else None) as f:
                try:
                    text = f.read()
                    file_coding = encoding.get()
                except UnicodeDecodeError:
                    tk.messagebox.showerror(lang["text.gui.msg.title.error"], lang["text.gui.file.decoding.tips.error"])
                except UnicodeError:
                    tk.messagebox.showerror(lang["text.gui.msg.title.error"], lang["text.gui.file.decoding.tips.error"])
    file_url = url
    window.title(lang["text.gui.title.fileopened"] + file_url)
    e.insert('end', text)
    e.edit_reset()


def save():
    global window
    global file_url
    del_list = []
    for i in os.listdir("plugin"):
        if i in plugins and os.path.isdir(os.path.join("plugin", i)):
            with open(os.path.join("plugin", i, "package.json"), encoding="utf-8") as f:
                info = json.load(f)
                try:
                    for j in info["files"]:
                        if j["position"] == "save":
                            try:
                                with open(os.path.join("plugin", i, j["file"]), encoding="utf-8") as f:
                                    if j["wait"]:
                                        exec(f.read(), globals(), locals())
                                    else:
                                        threading.Thread(name=info["name"], target=exec,
                                                         args=(f.read(), globals(), locals())).start()
                            except FileNotFoundError:
                                del_list.append(i)
                except Exception as err:
                    tk.messagebox.showerror(info["name"], str(err))
    for i in del_list:
        plugins.remove(i)
    issave = False
    if file_url == "":
        return save_as()
    else:
        if b.get():
            with open(file_url, "wb") as f:
                try:
                    f.write(eval("b'" + e.get("0.0", "end")[:-1] + "'"))
                    issave = True
                except SyntaxError:
                    tk.messagebox.showerror(lang["text.gui.msg.title.error"], lang["text.gui.file.encoding.tips.error"])
        else:
            if encoding.get() == "auto":
                with open(file_url, "w", encoding=file_coding, errors="ignore" if ignore.get() else None) as f:
                    try:
                        f.write(e.get("0.0", "end")[:-1])
                        issave = True
                    except UnicodeEncodeError:
                        tk.messagebox.showerror(lang["text.gui.msg.title.error"],
                                                lang["text.gui.file.encoding.tips.error"])
            else:
                with open(file_url, "w", encoding=encoding.get(), errors="ignore" if ignore.get() else None) as f:
                    try:
                        f.write(e.get("0.0", "end")[:-1])
                        issave = True
                    except UnicodeEncodeError:
                        tk.messagebox.showerror(lang["text.gui.msg.title.error"],
                                                lang["text.gui.file.encoding.tips.error"])
        return issave


def save_as():
    del_list = []
    for i in os.listdir("plugin"):
        if i in plugins and os.path.isdir(os.path.join("plugin", i)):
            with open(os.path.join("plugin", i, "package.json"), encoding="utf-8") as f:
                info = json.load(f)
                try:
                    for j in info["files"]:
                        if j["position"] == "save_as":
                            try:
                                with open(os.path.join("plugin", i, j["file"]), encoding="utf-8") as f:
                                    if j["wait"]:
                                        exec(f.read(), globals(), locals())
                                    else:
                                        threading.Thread(name=info["name"], target=exec,
                                                         args=(f.read(), globals(), locals())).start()
                            except FileNotFoundError:
                                del_list.append(i)
                except Exception as err:
                    tk.messagebox.showerror(info["name"], str(err))
    for i in del_list:
        plugins.remove(i)
    issave = False
    url = tk.filedialog.asksaveasfilename(title=lang["text.gui.file.save_as.title"],
                                          filetypes=[(lang["text.gui.file.open.type.txt"], ".txt"),
                                                     (lang["text.gui.file.open.type.all"], ".*")])
    if b.get():
        with open(url, "wb") as f:
            try:
                f.write(eval("b'" + e.get("0.0", "end")[:-1] + "'"))
                issave = True
            except SyntaxError:
                tk.messagebox.showerror(lang["text.gui.msg.title.error"], lang["text.gui.file.encoding.tips.error"])
    else:
        if encoding.get() == "auto":
            with open(url, 'w', encoding=file_coding, errors="ignore" if ignore.get() else None) as f:
                try:
                    f.write(e.get("0.0", "end")[:-1])
                    issave = True
                except UnicodeEncodeError:
                    tk.messagebox.showerror(lang["text.gui.msg.title.error"], lang["text.gui.file.encoding.tips.error"])
        else:
            with open(url, 'w', encoding=encoding.get(), errors="ignore" if ignore.get() else None) as f:
                try:
                    f.write(e.get("0.0", "end")[:-1])
                    issave = True
                except UnicodeEncodeError:
                    tk.messagebox.showerror(lang["text.gui.msg.title.error"], lang["text.gui.file.encoding.tips.error"])

    global file_url
    file_url = url
    window.title(lang["text.gui.title.fileopened"] + file_url)
    return issave


@q
def exit_window():
    del_list = []
    for i in os.listdir("plugin"):
        if i in plugins and os.path.isdir(os.path.join("plugin", i)):
            with open(os.path.join("plugin", i, "package.json"), encoding="utf-8") as f:
                info = json.load(f)
                try:
                    for j in info["files"]:
                        if j["position"] == "exit":
                            try:
                                with open(os.path.join("plugin", i, j["file"]), encoding="utf-8") as f:
                                    if j["wait"]:
                                        exec(f.read(), globals(), locals())
                                    else:
                                        threading.Thread(name=info["name"], target=exec,
                                                         args=(f.read(), globals(), locals())).start()
                            except FileNotFoundError:
                                del_list.append(i)
                except Exception as err:
                    tk.messagebox.showerror(info["name"], str(err))
    for i in del_list:
        plugins.remove(i)
    write_config()
    window.quit()


def font_():
    global font
    t = ""
    if B.get():
        t += "bold "
    if I.get():
        t += "italic "
    if U.get():
        t += "underline"
    font = (fontname.get(), fontsize.get(), t)
    e.config(font=font)


def wrap_():
    if wrap.get():
        e.config(wrap=tk.WORD)
    else:
        e.config(wrap=tk.NONE)


def compare_version_number(o_ver, n_ver):
    if o_ver == n_ver:
        return 0
    o_vers = o_ver.split(".")
    n_vers = n_ver.split(".")
    if int(o_vers[0]) > int(n_vers[0]):
        return -1
    elif int(o_vers[0]) < int(n_vers[0]):
        return 1
    else:
        if len(o_vers[1].split("-")) > 1 or len(n_vers[1].split("-")) > 1:
            if int(o_vers[1].split("-")[0]) > int(n_vers[1].split("-")[0]):
                return -1
            elif int(o_vers[1].split("-")[0]) < int(n_vers[1].split("-")[0]):
                return 1
            else:
                if o_vers[1].split("-")[1] == "beta":
                    return 1
                elif n_vers[1].split("-")[1] == "beta":
                    return -1
                else:
                    return 0
        else:
            if int(o_vers[1]) > int(n_vers[1]):
                return -1
            elif int(o_vers[1]) < int(n_vers[1]):
                return 1
            else:
                if len(o_vers) > len(n_vers):
                    return -1
                elif len(o_vers) < len(n_vers):
                    return 1
                elif len(o_vers[2].split("-")) > 1 or len(n_vers[2].split("-")) > 1:
                    if int(o_vers[2].split("-")[0]) > int(n_vers[2].split("-")[0]):
                        return -1
                    elif int(o_vers[2].split("-")[0]) < int(n_vers[2].split("-")[0]):
                        return 1
                    else:
                        if o_vers[2].split("-")[1] == "beta":
                            return 1
                        elif n_vers[2].split("-")[1] == "beta":
                            return -1
                        else:
                            return 0
                else:
                    if int(o_vers[2]) > int(n_vers[2]):
                        return -1
                    elif int(o_vers[2]) < int(n_vers[2]):
                        return 1
                    else:
                        return 0


def send_printer():
    del_list = []
    for i in os.listdir("plugin"):
        if i in plugins and os.path.isdir(os.path.join("plugin", i)):
            with open(os.path.join("plugin", i, "package.json"), encoding="utf-8") as f:
                info = json.load(f)
                try:
                    for j in info["files"]:
                        if j["position"] == "print":
                            try:
                                with open(os.path.join("plugin", i, j["file"]), encoding="utf-8") as f:
                                    if j["wait"]:
                                        exec(f.read(), globals(), locals())
                                    else:
                                        threading.Thread(name=info["name"], target=exec,
                                                         args=(f.read(), globals(), locals())).start()
                            except FileNotFoundError:
                                del_list.append(i)
                except Exception as err:
                    tk.messagebox.showerror(info["name"], str(err))
    for i in del_list:
        plugins.remove(i)
    pt = tk.Toplevel()
    pt.geometry("250x80")
    pt.title(lang["text.gui.menu.print.title"])
    pt.iconbitmap(lang["path.gui.ico"])
    printer = tk.StringVar()
    tk.ttk.Label(pt, text=lang["text.gui.menu.print.select"]).pack()
    prcombo = tk.ttk.Combobox(pt, width=35, textvariable=printer, state="readonly")
    print_list = []
    for i in win32print.EnumPrinters(2):
        print_list.append(i[2])
    prcombo['values'] = print_list
    printer.set(win32print.GetDefaultPrinter())
    prcombo.pack()
    pt.transient(window)

    def p():
        del_list = []
        for i in os.listdir("plugin"):
            if i in plugins and os.path.isdir(os.path.join("plugin", i)):
                with open(os.path.join("plugin", i, "package.json"), encoding="utf-8") as f:
                    info = json.load(f)
                    try:
                        for j in info["files"]:
                            if j["position"] == "print_handler":
                                try:
                                    with open(os.path.join("plugin", i, j["file"]), encoding="utf-8") as f:
                                        if j["wait"]:
                                            exec(f.read(), globals(), locals())
                                        else:
                                            threading.Thread(name=info["name"], target=exec,
                                                             args=(f.read(), globals(), locals())).start()
                                except FileNotFoundError:
                                    del_list.append(i)
                    except Exception as err:
                        tk.messagebox.showerror(info["name"], str(err))
        for i in del_list:
            plugins.remove(i)

        def send_to_printer(text, font):
            dc = win32ui.CreateDC()
            dc.CreatePrinterDC(prcombo.get())

            def convert_font_format(font):
                name, height, attributes = font
                weight = 400
                italic = False
                underline = False
                attributes = attributes.split(" ")
                if "bold" in attributes:
                    weight = 700
                if "italic" in attributes:
                    italic = True
                if "underline" in attributes:
                    underline = True
                converted_font = {
                    'name': name,
                    'height': height * 10,
                    'weight': weight,
                    'italic': italic,
                    'underline': underline
                }
                return converted_font

            font_obj = win32ui.CreateFont(convert_font_format(font))
            dc.SelectObject(font_obj)
            dc.StartDoc(text)
            dc.StartPage()
            dc.TextOut(0, 0, text)
            dc.EndPage()
            dc.EndDoc()

        send_to_printer(e.get("0.0", "end")[:-1], font)

    tk.ttk.Button(pt, text=lang["text.gui.menu.print.print"], command=p).pack()


def font_settings():
    del_list = []
    for i in os.listdir("plugin"):
        if i in plugins and os.path.isdir(os.path.join("plugin", i)):
            with open(os.path.join("plugin", i, "package.json"), encoding="utf-8") as f:
                info = json.load(f)
                try:
                    for j in info["files"]:
                        if j["position"] == "font":
                            try:
                                with open(os.path.join("plugin", i, j["file"]), encoding="utf-8") as f:
                                    if j["wait"]:
                                        exec(f.read(), globals(), locals())
                                    else:
                                        threading.Thread(name=info["name"], target=exec,
                                                         args=(f.read(), globals(), locals())).start()
                            except FileNotFoundError:
                                del_list.append(i)
                except Exception as err:
                    tk.messagebox.showerror(info["name"], str(err))
    for i in del_list:
        plugins.remove(i)
    setings = tk.Toplevel()
    setings.geometry("220x20")
    setings.title(lang["text.gui.menu.font.title"])
    setings.resizable(False, False)
    setings.iconbitmap(lang["path.gui.ico"])
    setings.transient(window)
    menubar = tk.Menu(setings)
    fontnamemenu = tk.Menu(menubar, tearoff=0)
    n = 0
    for i in [i for i in tkinter.font.families() if not i.startswith("@")]:
        n += 1
        if n % 40 == 0:
            fontnamemenu.add_radiobutton(label=i, variable=fontname, value=i, command=font_, font=(i, 10),
                                         columnbreak=True)
        else:
            fontnamemenu.add_radiobutton(label=i, variable=fontname, value=i, command=font_, font=(i, 10))
    menubar.add_cascade(label=lang["text.gui.menu.font.menu.font"][0], menu=fontnamemenu,
                        underline=lang["text.gui.menu.font.menu.font"][1])
    fontsizemenu = tk.Menu(menubar, tearoff=0)
    for i in range(10, 51):
        if i - 10 != 0 and (i - 10) % 10 == 0:
            fontsizemenu.add_radiobutton(label=str(i), variable=fontsize, value=i, command=font_, columnbreak=True)
        else:
            fontsizemenu.add_radiobutton(label=str(i), variable=fontsize, value=i, command=font_)
    menubar.add_cascade(label=lang["text.gui.menu.font.menu.font_size"][0], menu=fontsizemenu,
                        underline=lang["text.gui.menu.font.menu.font_size"][1])
    fonteffectmenu = tk.Menu(menubar, tearoff=0)
    fonteffectmenu.add_checkbutton(label=lang["text.gui.menu.font.menu.font_effect.bold"][0], variable=B,
                                   underline=lang["text.gui.menu.font.menu.font_effect.bold"][1], command=font_)
    fonteffectmenu.add_checkbutton(label=lang["text.gui.menu.font.menu.font_effect.italic"][0], variable=I,
                                   underline=lang["text.gui.menu.font.menu.font_effect.italic"][1], command=font_)
    fonteffectmenu.add_checkbutton(label=lang["text.gui.menu.font.menu.font_effect.underline"][0], variable=U,
                                   underline=lang["text.gui.menu.font.menu.font_effect.underline"][1],
                                   command=font_)
    menubar.add_cascade(label=lang["text.gui.menu.font.menu.font_effect"][0], menu=fonteffectmenu,
                        underline=lang["text.gui.menu.font.menu.font_effect"][1])
    setings.config(menu=menubar)


def find_str():
    # noinspection PyUnusedLocal
    def search(event=None, mark=True):
        key = keyword_text.get()
        if not key:
            return
        if use_escape_char.get():
            try:
                key = eval('"""' + key + '"""')
            except Exception as err:
                tk.messagebox.showerror(lang["text.gui.msg.title.error"], str(err))
                return
        if use_regexpr.get():
            try:
                re.compile(key)
            except re.error as err:
                tk.messagebox.showerror(lang["text.gui.msg.title.error"], str(err))
                return
        # end-1c:忽略末尾换行符
        pos = e.search(key, tk.INSERT, 'end-1c', regexp=use_regexpr.get(), nocase=not match_case.get())
        if not pos:
            pos = e.search(key, '0.0', 'end-1c', regexp=use_regexpr.get(), nocase=not match_case.get())
        if pos:
            if use_regexpr.get():
                text_after = e.get(pos, tk.END)
                flag = re.IGNORECASE if not match_case.get() else 0
                length = re.match(key, text_after, flag).span()[1]
            else:
                length = len(key)
            newpos = "%s+%dc" % (pos, length)
            e.mark_set(tk.INSERT, newpos)
            if mark:
                mark_text(pos, newpos)
            return pos, newpos
        else:
            return

    def findnext(cursor_pos='end', mark=True):
        result = search(mark=mark)
        if not result:
            return
        if cursor_pos == 'end':
            e.mark_set('insert', result[1])
        elif cursor_pos == 'start':
            e.mark_set('insert', result[0])
        return result

    def mark_text(start_pos, end_pos):
        e.tag_remove("sel", "0.0", "end")
        e.tag_add("sel", start_pos, end_pos)
        lines = e.get('0.0', "end")[:-1].count(os.linesep) + 1
        lineno = int(start_pos.split('.')[0])
        e.yview('moveto', str((lineno - e['height']) / lines))
        e.focus_force()

    find_window = tk.Toplevel()
    find_window.title(lang["text.gui.menu.find.find"])
    find_window.resizable(False, False)
    find_window.iconbitmap(lang["path.gui.ico"])
    find_window.transient(window)
    frame = tk.Frame(find_window)
    tk.ttk.Button(frame, text=lang["text.gui.menu.find.find_next"], command=findnext).pack()
    frame.pack(side=tk.RIGHT, fill=tk.Y)
    inputbox = tk.Frame(find_window)
    tk.ttk.Label(inputbox, text=lang["text.gui.menu.find.find_text"]).pack(side=tk.LEFT)
    keyword_text = tk.StringVar()
    keyword = tk.ttk.Entry(inputbox, textvariable=keyword_text)
    keyword.pack(side=tk.LEFT, expand=True, fill=tk.X)
    keyword.bind("<Key-Return>", search)
    keyword.focus_force()
    inputbox.pack(fill=tk.X)
    options = tk.Frame(find_window)
    tk.ttk.Label(options, text=lang["text.gui.menu.find.options"]).pack(side=tk.LEFT)
    use_regexpr = tk.BooleanVar()
    tk.ttk.Checkbutton(options, text=lang["text.gui.menu.find.options.use_regexpr"], variable=use_regexpr).pack(
        side=tk.LEFT)
    match_case = tk.BooleanVar()
    tk.ttk.Checkbutton(options, text=lang["text.gui.menu.find.options.match_case"], variable=match_case).pack(
        side=tk.LEFT)
    use_escape_char = tk.BooleanVar()
    tk.ttk.Checkbutton(options, text=lang["text.gui.menu.find.options.use_escape_char"], variable=use_escape_char).pack(
        side=tk.LEFT)
    options.pack(fill=tk.X)


def replace_str():
    def search(event=None, mark=True):
        key = keyword_text.get()
        if not key:
            return
        if use_escape_char.get():
            try:
                key = eval('"""' + key + '"""')
            except Exception as err:
                tk.messagebox.showerror(lang["text.gui.msg.title.error"], str(err))
                return
        if use_regexpr.get():
            try:
                re.compile(key)
            except re.error as err:
                tk.messagebox.showerror(lang["text.gui.msg.title.error"], str(err))
                return
        # end-1c:忽略末尾换行符
        pos = e.search(key, tk.INSERT, 'end-1c', regexp=use_regexpr.get(), nocase=not match_case.get())
        if not pos:
            pos = e.search(key, '0.0', 'end-1c', regexp=use_regexpr.get(), nocase=not match_case.get())
        if pos:
            if use_regexpr.get():
                text_after = e.get(pos, tk.END)
                flag = re.IGNORECASE if not match_case.get() else 0
                length = re.match(key, text_after, flag).span()[1]
            else:
                length = len(key)
            newpos = "%s+%dc" % (pos, length)
            e.mark_set(tk.INSERT, newpos)
            if mark:
                mark_text(pos, newpos)
            return pos, newpos
        else:
            return

    def findnext(cursor_pos='end', mark=True):
        result = search(mark=mark)
        if not result:
            return
        if cursor_pos == 'end':
            e.mark_set('insert', result[1])
        elif cursor_pos == 'start':
            e.mark_set('insert', result[0])
        return result

    def mark_text(start_pos, end_pos):
        e.tag_remove("sel", "0.0", "end")
        e.tag_add("sel", start_pos, end_pos)
        lines = e.get('0.0', "end")[:-1].count(os.linesep) + 1
        lineno = int(start_pos.split('.')[0])
        e.yview('moveto', str((lineno - e['height']) / lines))
        e.focus_force()

    def _findnext():
        sel_range = e.tag_ranges('sel')
        if sel_range:
            selectarea = sel_range[0].string, sel_range[1].string
            result = findnext('start')
            if result is None:
                return
            if result[0] == selectarea[0]:
                e.mark_set('insert', result[1])
                findnext('start')
        else:
            findnext('start')

    def replace_f(mark=True):
        result = search(mark=False)
        if not result:
            return
        pos, newpos = result
        newtext = text_to_replace.get()
        try:
            if use_escape_char.get():
                newtext = eval('"""' + newtext + '"""')
            if use_regexpr.get():
                old = e.get(pos, newpos)
                newtext = re.sub(keyword_text.get(), newtext, old)
        except Exception as err:
            tk.messagebox.showerror(lang["text.gui.msg.title.error"], str(err))
            return
        e.delete(pos, newpos)
        e.insert(pos, newtext)
        end_pos = "%s+%dc" % (pos, len(newtext))
        if mark:
            mark_text(pos, end_pos)
        return pos, end_pos

    def replace_all():
        e.mark_set("insert", "1.0")
        last = (0, 0)
        while True:
            result = replace_f(mark=False)
            if result is None:
                break
            result = findnext('start', mark=False)
            if result is None:
                return
            ln, col = result[0].split('.')
            ln = int(ln)
            col = int(col)
            if ln < last[0] or (ln == last[0] and col < last[1]):
                mark_text(*result)
                break
            last = ln, col

    find_window = tk.Toplevel()
    find_window.title(lang["text.gui.menu.replace.replace"])
    find_window.resizable(False, False)
    find_window.iconbitmap(lang["path.gui.ico"])
    find_window.transient(window)
    frame = tk.Frame(find_window)
    tk.ttk.Button(frame, text=lang["text.gui.menu.find.find_next"], command=_findnext).pack()
    tk.ttk.Button(frame, text=lang["text.gui.menu.replace.replace"], command=replace_f).pack()
    tk.ttk.Button(frame, text=lang["text.gui.menu.replace.replace_all"], command=replace_all).pack()
    frame.pack(side=tk.RIGHT, fill=tk.Y)
    inputbox = tk.Frame(find_window)
    tk.ttk.Label(inputbox, text=lang["text.gui.menu.find.find_text"]).pack(side=tk.LEFT)
    keyword_text = tk.StringVar()
    keyword = tk.ttk.Entry(inputbox, textvariable=keyword_text)
    keyword.pack(side=tk.LEFT, expand=True, fill=tk.X)
    keyword.focus_force()
    inputbox.pack(fill=tk.X)

    replace = tk.Frame(find_window)
    tk.ttk.Label(replace, text=lang["text.gui.menu.replace.replace_with"]).pack(side=tk.LEFT)
    text_to_replace = tk.StringVar()
    replace_text = tk.ttk.Entry(replace, textvariable=text_to_replace)
    replace_text.pack(side=tk.LEFT, expand=True, fill=tk.X)
    replace_text.bind("<Key-Return>", replace)
    replace.pack(fill=tk.X)

    options = tk.Frame(find_window)
    tk.ttk.Label(options, text=lang["text.gui.menu.find.options"]).pack(side=tk.LEFT)
    use_regexpr = tk.BooleanVar()
    tk.ttk.Checkbutton(options, text=lang["text.gui.menu.find.options.use_regexpr"], variable=use_regexpr).pack(
        side=tk.LEFT)
    match_case = tk.BooleanVar()
    tk.ttk.Checkbutton(options, text=lang["text.gui.menu.find.options.match_case"], variable=match_case).pack(
        side=tk.LEFT)
    use_escape_char = tk.BooleanVar()
    tk.ttk.Checkbutton(options, text=lang["text.gui.menu.find.options.use_escape_char"], variable=use_escape_char).pack(
        side=tk.LEFT)
    options.pack(fill=tk.X)


def get_size():
    if b.get():
        size = len(eval("b'" + e.get("0.0", "end")[:-1] + "'"))
    else:
        size = len(e.get("0.0", "end")[:-1].encode(file_coding))
    if size > (1024 * 1024):
        return "{:.2f}MB".format(size / 1024 / 1024)
    elif size > 1024:
        return "{:.2f}KB".format(size / 1024)
    else:
        return "{}B".format(size)


def bin_mode():
    b.set(not b.get())
    q(lambda: b.set(not b.get()))()
    if file_url != "":
        open_file(file_url)


def write_config(path=os.path.dirname(sys.argv[0])):
    with open(os.path.join(path, "config.ini"), "w") as f:
        json.dump({"font": font,
                   "wrap": wrap.get(),
                   "bold": B.get(),
                   "italic": I.get(),
                   "underline": U.get(),
                   "ignore": ignore.get(),
                   "plugins": plugins}, f)


def read_config(path=os.path.dirname(sys.argv[0])):
    global font
    global plugins
    if os.path.isfile(os.path.join(path, "config.ini")):
        with open(os.path.join(path, "config.ini")) as f:
            config = json.load(f)
        font = config["font"]
        wrap.set(config["wrap"])
        B.set(config["bold"])
        I.set(config["italic"])
        U.set(config["underline"])
        ignore.set(config["ignore"])
        plugins = config["plugins"]
        if type(plugins) != list:
            plugins = []
    else:
        if not os.path.isdir(path):
            os.mkdir(path)
        write_config()


def rmdir(dir_path):
    if os.path.isfile(dir_path):
        try:
            os.remove(dir_path)
        except Exception as e:
            print(e)
    elif os.path.isdir(dir_path):
        file_list = os.listdir(dir_path)
        for file_name in file_list:
            rmdir(os.path.join(dir_path, file_name))
        os.rmdir(dir_path)


def install_plugin(file):
    with zipfile.ZipFile(file) as f:
        corrupt_file = f.testzip()
        if not (corrupt_file is None):
            tk.messagebox.showerror(lang["text.gui.msg.title.error"],
                                    lang["text.gui.menu.plugin.file.invalid"].format(corrupt_file))
            return
        plugin_dirname = f.filelist[0].filename.split("/")[0]

        tempdir = os.path.join(tempfile.gettempdir(), "pynotepad", plugin_dirname)
        try:
            os.makedirs(tempdir)
        except FileExistsError:
            rmdir(tempdir)
            os.makedirs(tempdir)
        f.extractall(tempdir)
        try:
            if os.path.isfile(os.path.join(tempdir, plugin_dirname, "package.json")):
                with open(os.path.join(tempdir, plugin_dirname, "package.json"), encoding="utf-8") as i:
                    info = json.load(i)
                keys = ["name", "version", "description", "minsdk", "files", "dependencies"]
                for i in keys:
                    if not (i in info):
                        tk.messagebox.showerror(lang["text.gui.msg.title.error"],
                                                lang["text.gui.menu.plugin.plugin.invalid"])
                        return
                if compare_version_number(version, info["minsdk"]) == 1:
                    tk.messagebox.showerror(lang["text.gui.msg.title.error"],
                                            lang["text.gui.menu.plugin.plugin.new"])
                    return
                if "maxsdk" in info:
                    if compare_version_number(version, info["maxsdk"]) == -1:
                        tk.messagebox.showerror(lang["text.gui.msg.title.error"],
                                                lang["text.gui.menu.plugin.plugin.old"])
                        return
                try:
                    for j in info["files"]:
                        if j["position"] == "install":
                            try:
                                with open(os.path.join("plugin", key, j["file"]), encoding="utf-8") as f:
                                    if j["wait"]:
                                        exec(f.read(), globals(), locals())
                                    else:
                                        threading.Thread(name=info["name"], target=exec,
                                                         args=(f.read(), globals(), locals())).start()
                            except FileNotFoundError:
                                pass
                except Exception as err:
                    tk.messagebox.showerror(info["name"], str(err))
                f.extractall(".\\plugin")
            else:
                tk.messagebox.showerror(lang["text.gui.msg.title.error"], lang["text.gui.menu.plugin.plugin.invalid"])
                return
        except Exception as e:
            tk.messagebox.showerror(lang["text.gui.msg.title.error"], e)
        else:
            tk.messagebox.showinfo(lang["text.gui.menu.plugin.install.finish.title"],
                                   lang["text.gui.menu.plugin.install.finish"])

        rmdir(tempdir)


def plugin():
    pluginwindow = tk.Toplevel()
    pluginwindow.title(lang["text.gui.menu.plugin.title"])
    pluginwindow.resizable(False, False)
    pluginwindow.iconbitmap(lang["path.gui.ico"])
    pluginwindow.transient(window)
    pluginwindow.geometry("700x350")
    pluginlist = {}

    def is_signature(info):
        try:
            def rsa_public_check_sign(text, sign, key):
                verifier = PKCS1_signature.new(RSA.importKey(key))
                digest = SHA.new()
                digest.update(text.encode())
                return verifier.verify(digest, base64.b64decode(sign))

            pubkey = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAviKlXVbsyDDvqZSLLc3A
UK86Wg/+dUMS/zneoyQoihnvtiZjcEpV7rOxW17DjZnfpgo1LkCr95LWXeqEEuJp
N4Q9BtNR21GeFgH56+2G1dFefDSZpghZJMtqKi2N6cLDw11RShFKrz3VLO/j6tdv
/fnM6LasVoi5nBdKVe1XpJH+4tu90ksYn2tzOBiHniUiOLqGm8JgvON07q+zjGP3
o/ZNM9K23+hmrOg5Gy9ilpNDgR4THyk9oCGs3m+T9FTu+8NtlQX8/CkT5I+/kMTY
fc3BnF8vjyV7vb3mKI2RPdRkLgYOEyWPDEwLteiVmA5ZFqdesPYBVpQ2RgnOXvhT
3QIDAQAB
-----END PUBLIC KEY-----"""
            a = False
            for i in info["files"]:
                with open(os.path.join("plugin", info["path"], i["file"])) as f:
                    rdata = f.read()
                a = rsa_public_check_sign(rdata, i["sign"], pubkey)
            return a
        except Exception:
            return False

    def enable():
        info = pluginlist[pluginname.cget("text")]
        if enable_button.cget("text") == lang["text.gui.menu.plugin.enable"]:
            if not is_signature(info):
                if not tk.messagebox.askquestion(lang["text.gui.msg.title.warning"],
                                                 lang["text.gui.msg.plugin.enable_warning"]) == "yes":
                    return
            no_dependencies = []
            for d in info["dependencies"]:
                for i in os.listdir("plugin"):
                    if i in plugins and os.path.isdir(os.path.join("plugin", i)):
                        with open(os.path.join("plugin", i, "package.json"), encoding="utf-8") as f:
                            if d == json.load(f)["name"]:
                                break
                else:
                    no_dependencies.append(d)
            if no_dependencies:
                tk.messagebox.showerror(lang["text.gui.msg.title.error"],
                                        lang["text.gui.menu.plugins.tips.no_dependencies"].format(
                                            ",".join(no_dependencies)))
            else:
                try:
                    for j in info["files"]:
                        if j["position"] == "enable":
                            try:
                                with open(os.path.join("plugin", key, j["file"]), encoding="utf-8") as f:
                                    if j["wait"]:
                                        exec(f.read(), globals(), locals())
                                    else:
                                        threading.Thread(name=info["name"], target=exec,
                                                         args=(f.read(), globals(), locals())).start()
                            except FileNotFoundError:
                                pass
                except Exception as err:
                    tk.messagebox.showerror(info["name"], str(err))
                plugins.append(info["path"])
        else:
            plugins.remove(info["path"])
            try:
                for j in info["files"]:
                    if j["position"] == "disable":
                        try:
                            with open(os.path.join("plugin", key, j["file"]), encoding="utf-8") as f:
                                if j["wait"]:
                                    exec(f.read(), globals(), locals())
                                else:
                                    threading.Thread(name=info["name"], target=exec,
                                                     args=(f.read(), globals(), locals())).start()
                        except FileNotFoundError:
                            pass
            except Exception as err:
                tk.messagebox.showerror(info["name"], str(err))
        enable_button.config(text=lang["text.gui.menu.plugin.disable"] if info["path"] in plugins else lang[
            "text.gui.menu.plugin.enable"])

    def show_info(e=None):
        info = pluginlist[pluginchoose.selection_get()]
        pluginname.config(text=info["name"])
        pluginversion.config(text=lang["text.gui.menu.plugin.version_tip"] + info["version"])
        enable_button.config(text=lang["text.gui.menu.plugin.disable"] if info["path"] in plugins else lang[
            "text.gui.menu.plugin.enable"])
        e_.config(state='normal')
        e_.delete("0.0", "end")
        e_.insert("end", info["description"])
        e_.config(state='disabled')

    def install(file=""):
        if file == "":
            file = tk.filedialog.askopenfilename(title=lang["text.gui.file.plugin.title"],
                                                 filetypes=[(lang["text.gui.file.plugin.type"], '.zip')],
                                                 parent=pluginwindow)
        install_plugin(file)
        pluginwindow.destroy()
        plugin()

    def delete():
        info = pluginlist[pluginname.cget("text")]
        if tk.messagebox.askquestion(lang["text.gui.title"], lang["text.gui.menu.plugin.delete.warning"]) == "yes":
            try:
                for j in info["files"]:
                    if j["position"] == "delete":
                        try:
                            with open(os.path.join("plugin", info["path"], j["file"]), encoding="utf-8") as f:
                                if j["wait"]:
                                    exec(f.read(), globals(), locals())
                                else:
                                    threading.Thread(name=info["name"], target=exec,
                                                     args=(f.read(), globals(), locals())).start()
                        except FileNotFoundError:
                            pass
            except Exception as err:
                tk.messagebox.showerror(info["name"], str(err))

            def rmdir(dir_path):
                if os.path.isfile(dir_path):
                    try:
                        os.remove(dir_path)
                    except Exception as e:
                        print(e)
                elif os.path.isdir(dir_path):
                    file_list = os.listdir(dir_path)
                    for file_name in file_list:
                        rmdir(os.path.join(dir_path, file_name))
                    os.rmdir(dir_path)

            rmdir(os.path.join("plugin", info["path"]))
            del pluginlist[info["path"]]
            pluginwindow.destroy()
            plugin()

    f_s = tk.Frame(pluginwindow)
    s1 = tk.ttk.Scrollbar(f_s, orient=tk.VERTICAL)
    pluginchoose = tk.Listbox(f_s, yscrollcommand=s1.set, width=30)
    for i in os.listdir("plugin"):
        if os.path.isdir(os.path.join("plugin", i)):
            with open(os.path.join("plugin", i, "package.json"), encoding="utf-8") as f:
                info = json.load(f)
                pluginlist[info["name"]] = info
                pluginlist[info["name"]]["path"] = i
    if pluginchoose.size() > 0:
        pluginchoose.delete(0, pluginchoose.size())
    [pluginchoose.insert("end", j) for j in pluginlist.keys()]
    f_s.pack(side=tk.LEFT, fill=tk.BOTH)
    s1.pack(side=tk.RIGHT, fill=tk.BOTH)
    s1.config(command=pluginchoose.yview)
    install_button = tk.ttk.Button(f_s, text=lang["text.gui.menu.plugin.install"], command=install).pack()
    pluginchoose.pack(side=tk.LEFT, fill=tk.BOTH)
    f1 = tk.Frame(pluginwindow)
    pluginname = tk.ttk.Label(f1, font=("Microsoft YaHei UI", 15, "bold"))
    pluginversion = tk.ttk.Label(f1, font=("Microsoft YaHei UI", 10))
    pluginname.pack()
    pluginversion.pack()
    enable_button = tk.ttk.Button(f1, text=lang["text.gui.menu.plugin.enable"], command=enable)
    enable_button.pack()
    delete_button = tk.ttk.Button(f1, text=lang["text.gui.menu.plugin.delete"], command=delete).pack()
    tk.ttk.Label(f1, text=lang["text.gui.menu.plugin.restart_tip"]).pack()
    f2 = tk.Frame(f1)
    s2 = tk.ttk.Scrollbar(f2, orient=tk.VERTICAL)
    e_ = tk.Text(f2, yscrollcommand=s2.set, font=("Microsoft YaHei UI", 10))
    s2.pack(side=tk.RIGHT, fill=tk.BOTH)
    s2.config(command=e_.yview)
    f2.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
    e_.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
    if len(pluginlist) > 0:
        pluginchoose.selection_set(0)
        show_info()
        f1.pack()
    pluginchoose.bind("<<ListboxSelect>>", show_info)
    windnd.hook_dropfiles(pluginchoose, func=drop(install))


def topmost():
    window.wm_attributes('-topmost', top.get())


version = "4.2.1"
update_date = "2024/3/12"
debug_mode = False
font = ("Microsoft YaHei UI", 10, "")
encodings = ["GBK", "UTF-8", "UTF-16", "BIG5", "shift_jis"]
file_coding = encodings[0]
all_lang = {}
for i in os.listdir(".\\lang"):
    if os.path.isfile(os.path.join(".\lang", i)) and i.endswith(".lang"):
        try:
            with open(os.path.join(".\lang", i), encoding="utf-8") as lang_file:
                all_lang[i[:-5]] = json.load(lang_file)
        except Exception:
            pass
try:
    lang = all_lang[locale.windows_locale[win32api.GetUserDefaultLangID()]]
except KeyError:
    lang = {}
lang_raw = all_lang["en_US" if "en_US" in list(all_lang.keys()) else list(all_lang.keys())[0]]
window = tk.Tk()
window.tk.call('tk', 'scaling', ScaleFactor / 75)
top = tk.BooleanVar(value=False)
wrap = tk.BooleanVar(value=False)
B = tk.BooleanVar(value=False)
I = tk.BooleanVar(value=False)
U = tk.BooleanVar(value=False)
b = tk.BooleanVar(value=False)
ignore = tk.BooleanVar(value=False)
encoding = tk.StringVar(value="auto")
file_url = ""
plugins = []
read_config()
del_list = []
for i in os.listdir("plugin"):
    if i in plugins and os.path.isdir(os.path.join("plugin", i)):
        with open(os.path.join("plugin", i, "package.json"), encoding="utf-8") as f:
            info = json.load(f)
            try:
                for j in info["files"]:
                    if j["position"] == "init":
                        try:
                            with open(os.path.join("plugin", i, j["file"]), encoding="utf-8") as f:
                                if j["wait"]:
                                    exec(f.read(), globals(), locals())
                                else:
                                    threading.Thread(name=info["name"], target=exec,
                                                     args=(f.read(), globals(), locals())).start()
                        except FileNotFoundError:
                            del_list.append(i)
            except Exception as err:
                tk.messagebox.showerror(info["name"], str(err))
                del_list.append(i)
for i in del_list:
    plugins.remove(i)
for key in (lang_raw.keys() - lang.keys()):
    lang[key] = lang_raw[key]
fontname = tk.StringVar(value=font[0])
fontsize = tk.IntVar(value=font[1])

window.title(lang["text.gui.title"])
window.geometry('400x500')
window.iconbitmap(lang["path.gui.ico"])

f = tk.ttk.Frame(window, relief="groove", borderwidth=2)
s1 = tk.ttk.Scrollbar(f, orient=tk.VERTICAL)
s2 = tk.ttk.Scrollbar(f, orient=tk.HORIZONTAL)
e = tk.Text(f, wrap=tk.NONE, yscrollcommand=s1.set, xscrollcommand=s2.set, font=font, undo=True, relief="flat")
s1.pack(side=tk.RIGHT, fill=tk.BOTH)
s1.config(command=e.yview)
s2.pack(side=tk.BOTTOM, fill=tk.BOTH)
s2.config(command=e.xview)
f.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
e.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
menubar = tk.Menu(window)
filemenu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label=lang["text.gui.menu.file"][0], menu=filemenu, underline=lang["text.gui.menu.file"][1])
filemenu.add_command(label=lang["text.gui.menu.file.new"][0], command=make_new,
                     underline=lang["text.gui.menu.file.new"][1], accelerator="Ctrl+N")
filemenu.add_command(label=lang["text.gui.menu.file.open"][0], command=open_file,
                     underline=lang["text.gui.menu.file.open"][1], accelerator="Ctrl+O")
filemenu.add_command(label=lang["text.gui.menu.file.save"][0], command=save,
                     underline=lang["text.gui.menu.file.save"][1], accelerator="Ctrl+S")
filemenu.add_command(label=lang["text.gui.menu.file.save_as"][0], command=save_as,
                     underline=lang["text.gui.menu.file.save_as"][1],
                     accelerator="Ctrl+Shift+S")
filemenu.add_separator()
filemenu.add_command(label=lang["text.gui.menu.file.print"][0], command=send_printer,
                     underline=lang["text.gui.menu.file.print"][1], accelerator="Ctrl+P")
filemenu.add_separator()
filemenu.add_command(label=lang["text.gui.menu.file.plugins"][0], command=plugin,
                     underline=lang["text.gui.menu.file.plugins"][1])
filemenu.add_separator()
filemenu.add_command(label=lang["text.gui.menu.file.exit"][0], command=exit_window,
                     underline=lang["text.gui.menu.file.exit"][1])
editmenu = tk.Menu(menubar, tearoff=0)
editmenu.add_command(label=lang["text.gui.menu.edit.undo"][0], command=lambda: e.edit_undo(),
                     underline=lang["text.gui.menu.edit.undo"][1],
                     accelerator="Ctrl+Z")
editmenu.add_command(label=lang["text.gui.menu.edit.redo"][0], command=lambda: e.edit_redo(),
                     underline=lang["text.gui.menu.edit.redo"][1],
                     accelerator="Ctrl+Shift+Z")
editmenu.add_separator()
editmenu.add_command(label=lang["text.gui.menu.edit.cut"][0], command=lambda: e.event_generate("<<Cut>>"),
                     underline=lang["text.gui.menu.edit.cut"][1],
                     accelerator="Ctrl+X")
editmenu.add_command(label=lang["text.gui.menu.edit.copy"][0], command=lambda: e.event_generate("<<Copy>>"),
                     underline=lang["text.gui.menu.edit.copy"][1],
                     accelerator="Ctrl+C")
editmenu.add_command(label=lang["text.gui.menu.edit.paste"][0], command=lambda: e.event_generate("<<Paste>>"),
                     underline=lang["text.gui.menu.edit.paste"][1],
                     accelerator="Ctrl+V")
editmenu.add_command(label=lang["text.gui.menu.edit.delete"][0], command=lambda: e.delete(tk.SEL_FIRST, tk.SEL_LAST),
                     underline=lang["text.gui.menu.edit.delete"][1], accelerator="Del")
editmenu.add_command(label=lang["text.gui.menu.edit.select_all"][0], command=lambda: e.tag_add("sel", "0.0", "end"),
                     underline=lang["text.gui.menu.edit.select_all"][1], accelerator="Ctrl+A")
editmenu.add_separator()
editmenu.add_command(label=lang["text.gui.menu.edit.find"][0], command=lambda: find_str(),
                     underline=lang["text.gui.menu.edit.find"][1], accelerator="Ctrl+F")
editmenu.add_command(label=lang["text.gui.menu.edit.replace"][0], command=lambda: replace_str(),
                     underline=lang["text.gui.menu.edit.replace"][1],
                     accelerator="Ctrl+H")
menubar.add_cascade(label=lang["text.gui.menu.edit"][0], menu=editmenu, underline=lang["text.gui.menu.edit"][1])
contextmenu = tk.Menu(window, tearoff=0)
contextmenu.add_command(label=lang["text.gui.menu.edit.undo"][0], command=lambda: e.edit_undo(),
                        underline=lang["text.gui.menu.edit.undo"][1],
                        accelerator="Ctrl+Z")
contextmenu.add_command(label=lang["text.gui.menu.edit.redo"][0], command=lambda: e.edit_redo(),
                        underline=lang["text.gui.menu.edit.redo"][1],
                        accelerator="Ctrl+Shift+Z")
contextmenu.add_separator()
contextmenu.add_command(label=lang["text.gui.menu.edit.cut"][0], command=lambda: e.event_generate("<<Cut>>"),
                        underline=lang["text.gui.menu.edit.cut"][1],
                        accelerator="Ctrl+X")
contextmenu.add_command(label=lang["text.gui.menu.edit.copy"][0], command=lambda: e.event_generate("<<Copy>>"),
                        underline=lang["text.gui.menu.edit.copy"][1],
                        accelerator="Ctrl+C")
contextmenu.add_command(label=lang["text.gui.menu.edit.paste"][0], command=lambda: e.event_generate("<<Paste>>"),
                        underline=lang["text.gui.menu.edit.paste"][1], accelerator="Ctrl+V")
contextmenu.add_command(label=lang["text.gui.menu.edit.delete"][0], command=lambda: e.delete(tk.SEL_FIRST, tk.SEL_LAST),
                        underline=lang["text.gui.menu.edit.delete"][1], accelerator="Del")
contextmenu.add_command(label=lang["text.gui.menu.edit.select_all"][0], command=lambda: e.tag_add("sel", "0.0", "end"),
                        underline=lang["text.gui.menu.edit.select_all"][1], accelerator="Ctrl+A")
contextmenu.add_separator()
contextmenu.add_command(label=lang["text.gui.menu.view.file_info"][0],
                        underline=lang["text.gui.menu.view.file_info"][1],
                        command=lambda: tk.messagebox.showinfo(file_url, "{}:{}\n{}:{}\n{}:{}".format(
                            lang["text.gui.menu.view.file_info.infos"][0], file_coding,
                            lang["text.gui.menu.view.file_info.infos"][1], len(e.get("0.0", "end")[:-1]),
                            lang["text.gui.menu.view.file_info.infos"][2], get_size())))
viewmenu = tk.Menu(menubar, tearoff=0)
viewmenu.add_command(label=lang["text.gui.menu.view.font"][0], command=font_settings,
                     underline=lang["text.gui.menu.view.font"][1])
viewmenu.add_separator()
viewmenu.add_checkbutton(label=lang["text.gui.menu.view.warp"][0], underline=lang["text.gui.menu.view.warp"][1],
                         variable=wrap, command=wrap_)
viewmenu.add_command(label=lang["text.gui.menu.view.file_info"][0], underline=lang["text.gui.menu.view.file_info"][1],
                     command=lambda: tk.messagebox.showinfo(file_url, "{}:{}\n{}:{}\n{}:{}".format(
                         lang["text.gui.menu.view.file_info.infos"][0], file_coding,
                         lang["text.gui.menu.view.file_info.infos"][1], len(e.get("0.0", "end")[:-1]),
                         lang["text.gui.menu.view.file_info.infos"][2], get_size())))
viewmenu.add_separator()
viewmenu.add_checkbutton(label=lang["text.gui.menu.view.topmost"][0], underline=lang["text.gui.menu.view.topmost"][1],
                         command=topmost, variable=top)
menubar.add_cascade(label=lang["text.gui.menu.view"][0], menu=viewmenu, underline=lang["text.gui.menu.view"][1])
encodingmenu = tk.Menu(menubar, tearoff=0)
encodingmenu.add_radiobutton(label=lang["text.gui.menu.encoding.auto_encoding"][0],
                             underline=lang["text.gui.menu.encoding.auto_encoding"][1], variable=encoding,
                             value="auto")
for i in encodings:
    encodingmenu.add_radiobutton(label=i, variable=encoding, value=i)
encodingmenu.add_separator()
encodingmenu.add_checkbutton(label=lang["text.gui.menu.encoding.ignore_errors"][0], variable=ignore,
                             underline=lang["text.gui.menu.encoding.ignore_errors"][1])
encodingmenu.add_checkbutton(label=lang["text.gui.menu.encoding.binary_mode"][0], variable=b,
                             underline=lang["text.gui.menu.encoding.binary_mode"][1], command=bin_mode)
menubar.add_cascade(label=lang["text.gui.menu.encoding"][0], menu=encodingmenu,
                    underline=lang["text.gui.menu.encoding"][1])
infomenu = tk.Menu(menubar, tearoff=0)
infomenu.add_command(label=lang["text.gui.menu.help.about"][0],
                     command=lambda: tk.messagebox.showinfo(lang["text.gui.title"],
                                                            "v{} {}".format(version, update_date)),
                     underline=lang["text.gui.menu.help.about"][1])
infomenu.add_command(label=lang["text.gui.menu.help.copyright"][0],
                     command=lambda: tk.messagebox.showinfo(lang["text.gui.title"],
                                                            lang["text.gui.copyright"].format(
                                                                time.localtime(time.time())[0])),
                     underline=lang["text.gui.menu.help.copyright"][1])
menubar.add_cascade(label=lang["text.gui.menu.help"][0], menu=infomenu, underline=lang["text.gui.menu.help"][1])

window.bind("<Control-N>", lambda event: make_new())
window.bind("<Control-n>", lambda event: make_new())

window.bind("<Control-O>", lambda event: open_file())
window.bind("<Control-o>", lambda event: open_file())

window.bind("<Control-S>", lambda event: save())
window.bind("<Control-s>", lambda event: save())

window.bind("<Control-F>", lambda event: find_str())
window.bind("<Control-f>", lambda event: find_str())

window.bind("<Control-H>", lambda event: replace_str())
window.bind("<Control-h>", lambda event: replace_str())

window.bind("<Control-Shift-S>", lambda event: save_as())
window.bind("<Control-Shift-s>", lambda event: save_as())

window.bind("<Control-P>", lambda event: send_printer())
window.bind("<Control-p>", lambda event: send_printer())

window.bind("<Control-Z>", lambda event: e.edit_undo())
window.bind("<Control-z>", lambda event: e.edit_undo())

window.bind("<Control-Shift-Z>", lambda event: e.edit_redo())
window.bind("<Control-Shift-z>", lambda event: e.edit_redo())

e.bind("<Button-3>", lambda event: contextmenu.post(event.x_root, event.y_root))
e.bind('<Key>', lambda event: e.edit_separator())
windnd.hook_dropfiles(e, func=drop(open_file))
window.config(menu=menubar)
window.protocol('WM_DELETE_WINDOW', exit_window)
del_list = []
for i in os.listdir("plugin"):
    if i in plugins and os.path.isdir(os.path.join("plugin", i)):
        with open(os.path.join("plugin", i, "package.json"), encoding="utf-8") as f:
            info = json.load(f)
            try:
                for j in info["files"]:
                    if j["position"] == "main":
                        try:
                            with open(os.path.join("plugin", i, j["file"]), encoding="utf-8") as f:
                                if j["wait"]:
                                    exec(f.read(), globals(), locals())
                                else:
                                    threading.Thread(name=info["name"], target=exec,
                                                     args=(f.read(), globals(), locals())).start()
                        except FileNotFoundError:
                            del_list.append(i)
            except Exception as err:
                tk.messagebox.showerror(info["name"], str(err))
                del_list.append(i)
for i in del_list:
    plugins.remove(i)
if len(sys.argv) > 1:
    open_file(sys.argv[1])
window.mainloop()
