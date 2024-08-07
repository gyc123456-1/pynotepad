import hashlib
import json
import threading
import time
import tkinter as tk
import tkinter.messagebox
import tkinter.filedialog
import tkinter.font
import tkinter.ttk
import chardet
import win32api
import win32con
import win32print
import tempfile
import sys
import re
import requests
import os
import win32ui
import windnd
import base64
from Cryptodome.PublicKey import RSA
from Cryptodome.Hash import SHA
from Cryptodome.Signature import PKCS1_v1_5 as PKCS1_signature
import ctypes
from ctypes import wintypes
import locale
import zipfile
import typing
import typing_extensions

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
ctypes.windll.shcore.SetProcessDpiAwareness(1)
ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)  # 针对 Windows 老终端颜色代码的修复（可能用不上，先放这）
# 类型注解用
Path = typing.Union[str, typing_extensions.LiteralString]
Info = typing.Dict[str, typing.Union[str, typing.List[typing.Union[str, typing.Dict[str, typing.Union[bool, str]]]]]]


def q(func: typing.Callable) -> typing.Callable[..., bool]:
    """
    装饰器，在被装饰的函数执行前会询问是否保存，函数已执行返回 True，反之为 False
    :param func: 被装饰的函数
    :return: 装饰后的函数
    """

    def wrapper(*args, **kwargs) -> bool:
        plugin_object.run_plugins("ask_save", globals(), locals())
        if issave():
            func(*args, **kwargs)
            return True
        else:
            a = tk.messagebox.askyesnocancel(lang["text.gui.title"], lang["text.gui.file.exit_save"])
            if a is None:
                return False
            elif a:
                if file_path == "":
                    if save_as():
                        func(*args, **kwargs)
                        return True
                    else:
                        return False
                else:
                    if save():
                        func(*args, **kwargs)
                        return True
                    else:
                        return False
            else:
                func(*args, **kwargs)
                return True

    return wrapper


@q
def make_new() -> None:
    """
    新建文件
    """
    plugin_object.run_plugins("before_new", globals(), locals())
    e.delete('0.0', 'end')
    e.edit_reset()
    global file_path
    file_path = ""
    plugin_object.run_plugins("after_new", globals(), locals())


def drop(func: typing.Callable[[str], typing.Any]) -> typing.Callable[[typing.Sequence[bytes]], None]:
    """
    装饰器，用来处理 windnd.hook_dropfiles 的拖放事件，将拖动的文件的第一个传递给被装饰的函数
    :param func: 被装饰的函数
    :return: 装饰后的函数
    """

    def warpper(files: typing.Sequence[bytes]) -> None:
        try:
            path = [i.decode() for i in files]
        except UnicodeDecodeError:
            path = [i.decode("gbk") for i in files]
        func(path[0])

    return warpper


def detect_encoding(path: Path) -> str:
    """
    检测指定文件的编码
    :param path: 文件路径
    :return: 检测到时返回正确编码，否则返回 file_encoding
    """
    # noinspection PyBroadException
    try:
        with open(path, 'rb') as f:
            return chardet.detect(f.read())['encoding']
    except Exception:
        return file_encoding


def issave() -> bool:
    """
    检测当前文件是否保存
    :return: True 为已保存，False 为未保存
    """
    plugin_object.run_plugins("is_save", globals(), locals())
    if file_path != "":
        if encoding.get() == "auto":
            with open(file_path, encoding=detect_encoding(file_path), errors="ignore" if ignore.get() else None) as f:
                try:
                    text = f.read()
                except UnicodeDecodeError:
                    text = ""
                except UnicodeError:
                    text = ""
        else:
            if isbin_mode.get():
                with open(file_path, "rb") as f:
                    text = str(f.read())[2:-1]
            else:
                with open(file_path, encoding=encoding.get(), errors="ignore" if ignore.get() else None) as f:
                    try:
                        text = f.read()
                    except UnicodeDecodeError:
                        text = ""
                    except UnicodeError:
                        text = ""
    else:
        text = ""
    if text == e.get("0.0", "end")[:-1]:
        return True
    else:
        return False


@q
def open_file(path: Path = "") -> None:
    """
    打开文件
    :param path: 文件路径，为空时打开文件选择器
    """
    global file_path
    global file_encoding
    plugin_object.run_plugins("before_open", globals(), locals())
    if not path:
        path = tk.filedialog.askopenfilename(title=lang["text.gui.file.open.title"],
                                             filetypes=[(lang["text.gui.file.open.type.txt"], ".txt"),
                                                        (lang["text.gui.file.open.type.all"], ".*")])
    e.delete('0.0', 'end')
    file_path = ""
    text = ""
    file_path = path
    if isbin_mode.get():
        with open(path, "rb") as f:
            text = str(f.read())[2:-1]
    else:
        if encoding.get() == "auto":
            with open(path, encoding=detect_encoding(path), errors="ignore" if ignore.get() else None) as f:
                try:
                    text = f.read()
                    file_encoding = f.encoding
                except UnicodeDecodeError:
                    tk.messagebox.showerror(lang["text.gui.msg.title.error"], lang["text.gui.file.decoding.tips.error"])
                except UnicodeError:
                    tk.messagebox.showerror(lang["text.gui.msg.title.error"], lang["text.gui.file.decoding.tips.error"])
        else:
            with open(path, encoding=encoding.get(), errors="ignore" if ignore.get() else None) as f:
                try:
                    text = f.read()
                    file_encoding = f.encoding
                except UnicodeDecodeError:
                    tk.messagebox.showerror(lang["text.gui.msg.title.error"], lang["text.gui.file.decoding.tips.error"])
                except UnicodeError:
                    tk.messagebox.showerror(lang["text.gui.msg.title.error"], lang["text.gui.file.decoding.tips.error"])
    file_path = path
    window.title(lang["text.gui.title.fileopened"] + file_path)
    e.insert('end', text)
    e.edit_reset()
    plugin_object.run_plugins("after_open", globals(), locals())


def save() -> bool:
    """
    保存文件
    :return: 是否保存成功
    """
    global file_path
    global file_encoding
    plugin_object.run_plugins("before_save", globals(), locals())
    if file_path == "":
        plugin_object.run_plugins("save_to_as", globals(), locals())
        return save_as()
    else:
        if isbin_mode.get():
            with open(file_path, "wb") as f:
                try:
                    f.write(eval("b'" + e.get("0.0", "end")[:-1] + "'"))
                except SyntaxError:
                    tk.messagebox.showerror(lang["text.gui.msg.title.error"], lang["text.gui.file.encoding.tips.error"])
        else:
            if encoding.get() == "auto":
                with open(file_path, "w", encoding=detect_encoding(file_path),
                          errors="ignore" if ignore.get() else None) as f:
                    try:
                        f.write(e.get("0.0", "end")[:-1])
                    except UnicodeEncodeError:
                        tk.messagebox.showerror(lang["text.gui.msg.title.error"],
                                                lang["text.gui.file.encoding.tips.error"])
            else:
                with open(file_path, "w", encoding=encoding.get(), errors="ignore" if ignore.get() else None) as f:
                    try:
                        f.write(e.get("0.0", "end")[:-1])
                        file_encoding = f.encoding
                    except UnicodeEncodeError:
                        tk.messagebox.showerror(lang["text.gui.msg.title.error"],
                                                lang["text.gui.file.encoding.tips.error"])
        plugin_object.run_plugins("after_save", globals(), locals())
        return issave()


def save_as() -> bool:
    """
    另存为文件
    :return: 是否保存成功
    """
    global file_path
    global file_encoding
    plugin_object.run_plugins("before_save_as", globals(), locals())
    path = tk.filedialog.asksaveasfilename(title=lang["text.gui.file.save_as.title"],
                                           filetypes=[(lang["text.gui.file.open.type.txt"], ".txt"),
                                                      (lang["text.gui.file.open.type.all"], ".*")])
    if isbin_mode.get():
        with open(path, "wb") as f:
            try:
                f.write(eval("b'" + e.get("0.0", "end")[:-1] + "'"))
            except SyntaxError:
                tk.messagebox.showerror(lang["text.gui.msg.title.error"], lang["text.gui.file.encoding.tips.error"])
    else:
        if encoding.get() == "auto":
            with open(path, 'w', encoding=detect_encoding(path), errors="ignore" if ignore.get() else None) as f:
                try:
                    f.write(e.get("0.0", "end")[:-1])
                except UnicodeEncodeError:
                    tk.messagebox.showerror(lang["text.gui.msg.title.error"], lang["text.gui.file.encoding.tips.error"])
        else:
            with open(path, 'w', encoding=encoding.get(), errors="ignore" if ignore.get() else None) as f:
                try:
                    f.write(e.get("0.0", "end")[:-1])
                    file_encoding = f.encoding
                except UnicodeEncodeError:
                    tk.messagebox.showerror(lang["text.gui.msg.title.error"], lang["text.gui.file.encoding.tips.error"])

    file_path = path
    window.title(lang["text.gui.title.fileopened"] + file_path)
    plugin_object.run_plugins("after_save_as", globals(), locals())
    return issave()


@q
def exit_window() -> None:
    """
    关闭主窗口
    """
    plugin_object.run_plugins("exit", globals(), locals())
    write_config()
    window.quit()


def font_() -> None:
    """
    将字体相关 tkinter 变量同步到 font 变量
    """
    global font
    t = ""
    if isbold.get():
        t += "bold "
    if isitalic.get():
        t += "italic "
    if isunderline.get():
        t += "underline"
    font = (fontname.get(), fontsize.get(), t)
    e.config(font=font)


def wrap_() -> None:
    """
    将自动换行相关 tkinter 变量同步到 wrap 变量
    """
    if iswrapmode.get():
        e.config(wrap=tk.WORD)
    else:
        e.config(wrap=tk.NONE)


def compare_version_number(o_ver: str, n_ver: str) -> int:
    """
    比较版本号的大小
    :param o_ver: 版本号 a
    :param n_ver: 版本号 b
    :return: -1为 a 大，0为相等，1为 b 大
    """
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


def send_printer() -> None:
    """
    打印界面
    """
    plugin_object.run_plugins("before_print_gui", globals(), locals())
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

    def p() -> None:
        plugin_object.run_plugins("before_print_handler", globals(), locals())

        def send_to_printer(text: str, font: tuple) -> None:
            dc = win32ui.CreateDC()
            dc.CreatePrinterDC(prcombo.get())

            def convert_font_format(font: tuple) -> dict:
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
        plugin_object.run_plugins("after_print_handler", globals(), locals())

    tk.ttk.Button(pt, text=lang["text.gui.menu.print.print"], command=p).pack()
    plugin_object.run_plugins("after_print_gui", globals(), locals())


def font_settings() -> None:
    """
    字体设置界面
    """
    plugin_object.run_plugins("before_font_settings_gui", globals(), locals())
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
    fonteffectmenu.add_checkbutton(label=lang["text.gui.menu.font.menu.font_effect.bold"][0], variable=isbold,
                                   underline=lang["text.gui.menu.font.menu.font_effect.bold"][1], command=font_)
    fonteffectmenu.add_checkbutton(label=lang["text.gui.menu.font.menu.font_effect.italic"][0], variable=isitalic,
                                   underline=lang["text.gui.menu.font.menu.font_effect.italic"][1], command=font_)
    fonteffectmenu.add_checkbutton(label=lang["text.gui.menu.font.menu.font_effect.underline"][0], variable=isunderline,
                                   underline=lang["text.gui.menu.font.menu.font_effect.underline"][1],
                                   command=font_)
    menubar.add_cascade(label=lang["text.gui.menu.font.menu.font_effect"][0], menu=fonteffectmenu,
                        underline=lang["text.gui.menu.font.menu.font_effect"][1])
    setings.config(menu=menubar)
    plugin_object.run_plugins("after_font_settings_gui", globals(), locals())


def find_str() -> None:
    """
    查找界面
    """

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


# noinspection PyTypeChecker
def replace_str() -> None:
    """
    替换界面
    """

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


def get_size() -> str:
    """
    获取文件大小
    :return: 带单位大小
    """
    if isbin_mode.get():
        size = len(eval("b'" + e.get("0.0", "end")[:-1] + "'"))
    else:
        size = len(e.get("0.0", "end")[:-1].encode(file_encoding))
    if size > (1024 * 1024):
        return "{:.2f}MB".format(size / 1024 / 1024)
    elif size > 1024:
        return "{:.2f}KB".format(size / 1024)
    else:
        return "{}B".format(size)


def bin_mode() -> None:
    """
    切换二进制模式
    """
    isbin_mode.set(not isbin_mode.get())
    q(lambda: isbin_mode.set(not isbin_mode.get()))()
    if file_path != "":
        open_file(file_path)


def write_config(path: Path = os.path.dirname(sys.argv[0])) -> None:
    """
    保存配置文件
    :param path: 存放配置文件的文件夹的路径
    """
    with open(os.path.join(path, "config.ini"), "w") as f:
        json.dump({"font": font,
                   "wrap": iswrapmode.get(),
                   "bold": isbold.get(),
                   "italic": isitalic.get(),
                   "underline": isunderline.get(),
                   "ignore": ignore.get(),
                   "plugins": plugins}, f)


def read_config(path: Path = os.path.dirname(sys.argv[0])) -> None:
    """
    读取配置文件
    :param path: 存放配置文件的文件夹的路径
    """
    global font
    global plugins
    if os.path.isfile(os.path.join(path, "config.ini")):
        with open(os.path.join(path, "config.ini")) as f:
            config = json.load(f)
        font = config["font"]
        iswrapmode.set(config["wrap"])
        isbold.set(config["bold"])
        isitalic.set(config["italic"])
        isunderline.set(config["underline"])
        ignore.set(config["ignore"])
        plugins = config["plugins"]
        if not isinstance(plugins, list):
            plugins = []
    else:
        if not os.path.isdir(path):
            os.mkdir(path)
        write_config()


def topmost() -> None:
    """
    同步置顶变量与窗口置顶状态
    """
    window.wm_attributes('-topmost', istopmost.get())


def update_status_bar(event: typing.Union[tk.Event, str] = "") -> None:
    """
    刷新状态栏
    """
    cr, cc = map(int, e.index("insert").split("."))
    status_bar_var.set(
        lang["text.gui.status_bar.text"].format(rows=cr, rows_total=len(e.get("0.0", "end").split("\n")) - 1,
                                                columns=cc + 1,
                                                columns_total=len(e.get("{}.0".format(cr),
                                                                        "{}.0".format(cr + 1))) - 1,
                                                chars=len(e.get('0.0', 'end')) - 1, file_size=get_size(),
                                                encoding=file_encoding))


def on_modify(event: tk.Event) -> None:
    """
    文本框修改时的处理函数
    """
    e.edit_separator()
    update_status_bar()


def rmdir(dir_path: Path) -> None:
    """
    递归删除文件夹（夹）
    :param dir_path: 要删除的文件（夹）
    """
    if os.path.isfile(dir_path):
        try:
            os.remove(dir_path)
        except Exception as e:
            tk.messagebox.showerror(lang["text.gui.msg.title.error"], str(e))
    elif os.path.isdir(dir_path):
        file_list = os.listdir(dir_path)
        for file_name in file_list:
            rmdir(os.path.join(dir_path, file_name))
        os.rmdir(dir_path)


class Plugins:
    """
    插件类，包含相关界面及处理
    """

    def __init__(self: typing_extensions.Self, plugins_dir: str, config_file_name: str, pubkey: str) -> None:
        """
        初始化插件类
        :param plugins_dir: 插件目录名
        :param config_file_name: 插件配置文件名
        :param pubkey: 插件验证公钥
        """
        self.plugins_dir = plugins_dir
        self.config_file_name = config_file_name
        self.pubkey = pubkey
        if not os.path.isdir(plugins_dir):
            os.mkdir(plugins_dir)

    def is_signature(self: typing_extensions.Self, info: Info) -> bool:
        """
        判断是否签名是否有效
        :param info: 反序列号后的插件配置文件
        :return: True 为有效，False 为无效
        """
        try:
            # noinspection PyUnresolvedReferences
            def rsa_public_check_sign(text, sign, key):
                verifier = PKCS1_signature.new(RSA.importKey(key))
                digest = SHA.new()
                digest.update(text.encode())
                return verifier.verify(digest, base64.b64decode(sign))

            def check_files():
                for i in info["files"]:
                    with open(os.path.join(self.plugins_dir, info["path"], i["file"]),
                              encoding=detect_encoding(os.path.join(self.plugins_dir, info["path"], i["file"]))) as f:
                        yield rsa_public_check_sign(f.read(), i["sign"], self.pubkey)

            return all(check_files())
        except Exception:
            return False

    def plugin(self: typing_extensions.Self) -> None:
        """
        插件配置界面
        """
        pluginwindow = tk.Toplevel()
        pluginwindow.title(lang["text.gui.menu.plugin.title"])
        pluginwindow.resizable(False, False)
        pluginwindow.iconbitmap(lang["path.gui.ico"])
        pluginwindow.transient(window)
        pluginwindow.geometry("700x350")
        pluginlist = {}

        def enable():
            info = pluginlist[pluginname.cget("text")]
            if enable_button.cget("text") == lang["text.gui.menu.plugin.enable"]:
                if not self.is_signature(info):
                    if not tk.messagebox.askquestion(lang["text.gui.msg.title.warning"],
                                                     lang["text.gui.msg.plugin.enable_warning"]) == "yes":
                        return
                no_dependencies = []
                for d in info["dependencies"]:
                    for i in os.listdir(self.plugins_dir):
                        if i in plugins and os.path.isdir(os.path.join(self.plugins_dir, i)):
                            with open(os.path.join(self.plugins_dir, i, self.config_file_name),
                                      encoding=detect_encoding(
                                          os.path.join(self.plugins_dir, i, self.config_file_name))) as f:
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
                                    with open(os.path.join(self.plugins_dir, key, j["file"]), encoding=detect_encoding(
                                            os.path.join(self.plugins_dir, key, j["file"]))) as f:
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
                                with open(os.path.join(self.plugins_dir, key, j["file"]), encoding=detect_encoding(
                                        os.path.join(self.plugins_dir, key, j["file"]))) as f:
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
            self.install_plugin(file)
            pluginwindow.destroy()
            self.plugin()

        def delete():
            info = pluginlist[pluginname.cget("text")]
            if tk.messagebox.askquestion(lang["text.gui.title"], lang["text.gui.menu.plugin.delete.warning"]) == "yes":
                try:
                    for j in info["files"]:
                        if j["position"] == "delete":
                            try:
                                with open(os.path.join(self.plugins_dir, info["path"], j["file"]),
                                          encoding=detect_encoding(
                                              os.path.join(self.plugins_dir, info["path"], j["file"]))) as f:
                                    if j["wait"]:
                                        exec(f.read(), globals(), locals())
                                    else:
                                        threading.Thread(name=info["name"], target=exec,
                                                         args=(f.read(), globals(), locals())).start()
                            except FileNotFoundError:
                                pass
                except Exception as err:
                    tk.messagebox.showerror(info["name"], str(err))

                rmdir(os.path.join(self.plugins_dir, info["path"]))
                # noinspection PyBroadException
                try:
                    del pluginlist[info["name"]]
                    plugins.remove(info["path"])
                except Exception:
                    pass
                pluginwindow.destroy()
                self.plugin()

        f_s = tk.Frame(pluginwindow)
        s1 = tk.ttk.Scrollbar(f_s, orient=tk.VERTICAL)
        pluginchoose = tk.Listbox(f_s, yscrollcommand=s1.set, width=30)
        for i in os.listdir(self.plugins_dir):
            if os.path.isdir(os.path.join(self.plugins_dir, i)):
                with open(os.path.join(self.plugins_dir, i, self.config_file_name),
                          encoding=detect_encoding(os.path.join(self.plugins_dir, i, self.config_file_name))) as f:
                    info = json.load(f)
                    pluginlist[info["name"]] = info
                    pluginlist[info["name"]]["path"] = i
        if pluginchoose.size() > 0:
            pluginchoose.delete(0, pluginchoose.size())
        [pluginchoose.insert("end", j) for j in pluginlist.keys()]
        f_s.pack(side=tk.LEFT, fill=tk.BOTH)
        s1.pack(side=tk.RIGHT, fill=tk.BOTH)
        s1.config(command=pluginchoose.yview)
        tk.ttk.Button(f_s, text=lang["text.gui.menu.plugin.install"], command=install).pack()
        pluginchoose.pack(side=tk.LEFT, fill=tk.BOTH)
        f1 = tk.Frame(pluginwindow)
        pluginname = tk.ttk.Label(f1, font=("Microsoft YaHei UI", 15, "bold"))
        pluginversion = tk.ttk.Label(f1, font=("Microsoft YaHei UI", 10))
        pluginname.pack()
        pluginversion.pack()
        enable_button = tk.ttk.Button(f1, text=lang["text.gui.menu.plugin.enable"], command=enable)
        enable_button.pack()
        tk.ttk.Button(f1, text=lang["text.gui.menu.plugin.delete"], command=delete).pack()
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

    def run_plugins(self: typing_extensions.Self, position: str, globals_: dict, locals_: dict) -> None:
        """
        在当前位置运行插件（注：有局部变量修改问题，将在未来解决）
        :param position: 插件的运行时机
        :param globals_: globals()执行结果
        :param locals_: locals()执行结果
        吐槽：最后两个参数完全没必要
        """
        for i in os.listdir(self.plugins_dir):
            if i in plugins and os.path.isdir(os.path.join(self.plugins_dir, i)):
                with open(os.path.join(self.plugins_dir, i, self.config_file_name),
                          encoding=detect_encoding(os.path.join(self.plugins_dir, i, self.config_file_name))) as f:
                    info = json.load(f)
                try:
                    for j in info["files"]:
                        if j["position"] == position:
                            try:
                                with open(os.path.join(self.plugins_dir, i, j["file"]), encoding=detect_encoding(
                                        os.path.join(self.plugins_dir, i, j["file"]))) as f:
                                    if j["wait"]:
                                        exec(f.read(), globals_, locals_)
                                    else:
                                        threading.Thread(name=info["name"], target=exec,
                                                         args=(f.read(), globals_, locals_)).start()
                            except FileNotFoundError:
                                pass
                except Exception as err:
                    tk.messagebox.showerror(info["name"], str(err))

    def install_plugin(self: typing_extensions.Self, file: Path) -> None:
        """
        安装插件
        :param file: 要安装的插件名
        """
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
                if os.path.isfile(os.path.join(tempdir, plugin_dirname, self.config_file_name)):
                    with open(os.path.join(tempdir, plugin_dirname, self.config_file_name), encoding=detect_encoding(
                            os.path.join(tempdir, plugin_dirname, self.config_file_name))) as i:
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
                                    with open(os.path.join(self.plugins_dir, key, j["file"]), encoding=detect_encoding(
                                            os.path.join(self.plugins_dir, key, j["file"]))) as f2:
                                        if j["wait"]:
                                            exec(f2.read(), globals(), locals())
                                        else:
                                            threading.Thread(name=info["name"], target=exec,
                                                             args=(f2.read(), globals(), locals())).start()
                                except FileNotFoundError:
                                    pass
                    except Exception as err:
                        tk.messagebox.showerror(info["name"], str(err))
                    f.extractall(self.plugins_dir)
                else:
                    tk.messagebox.showerror(lang["text.gui.msg.title.error"],
                                            lang["text.gui.menu.plugin.plugin.invalid"])
                    return
            except Exception as e:
                tk.messagebox.showerror(lang["text.gui.msg.title.error"], str(e))
            else:
                tk.messagebox.showinfo(lang["text.gui.menu.plugin.install.finish.title"],
                                       lang["text.gui.menu.plugin.install.finish"])

            rmdir(tempdir)


class PluginMarket:
    """
    插件市场相关类，未经测试，未启用
    """

    def __init__(self: typing_extensions.Self, obj: Plugins, repo: str) -> None:
        """
        初始化插件市场类
        :param obj: 插件对象
        :param repo: 市场仓库 URL
        """
        self.obj = obj
        self.repo = repo

    def getlist(self: typing_extensions.Self) -> typing.List[dict]:
        """
        获取市场列表
        :return: 插件信息列表
        """
        return json.loads(requests.get(f"{self.repo}/list.json").text)

    def gui(self: typing_extensions.Self) -> None:
        """
        插件市场界面
        """
        pluginwindow = tk.Toplevel()
        pluginwindow.title("插件市场")
        pluginwindow.resizable(False, False)
        pluginwindow.iconbitmap(lang["path.gui.ico"])
        pluginwindow.transient(window)
        pluginwindow.geometry("700x350")

        def reload():
            pluginwindow.destroy()
            self.gui()

        def show_info(e=None):
            info = pluginlist[pluginchoose.selection_get()]
            pluginname.config(text=info["name"])
            pluginversion.config(text=lang["text.gui.menu.plugin.version_tip"] + info["version"])
            pluginauthor.config(text="作者：" + info["author"])
            if info["name"] in plugins:
                install_button.config(text="已安装", state='disabled')
            else:
                install_button.config(text="安装", state='active')
            e_.config(state='normal')
            e_.delete("0.0", "end")
            e_.insert("end", info["description"])
            e_.config(state='disabled')

        def download():
            pluginchoose.config(state='disabled')
            info = pluginlist[pluginchoose.selection_get()]
            install_button.config(text="安装中...", state='disabled')
            tempdir = os.path.join(tempfile.gettempdir(), "pynotepad", "market")
            try:
                os.makedirs(tempdir)
            except FileExistsError:
                rmdir(tempdir)
                os.makedirs(tempdir)
            head = requests.head(info["download"])
            url = head.headers.get("Location")
            head = requests.head(url)
            file_size = int(head.headers.get("Content-Length"))
            filename = head.headers.get("Content-Disposition")[21:]
            response = requests.get(url, stream=True)
            read = 0
            with open(os.path.join(tempdir, filename), "wb") as f:
                for chunk in response.iter_content(chunk_size=32767):
                    read += 32767
                    f.write(chunk)
                    progressbar["value"] = read / file_size * 100
                    pluginwindow.update()
            md5 = base64.b64decode(head.headers.get("Content-MD5")).hex()
            md5_hash = hashlib.md5()
            with open(os.path.join(tempdir, filename), "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    md5_hash.update(byte_block)
            if md5_hash.hexdigest() == md5:
                self.obj.install_plugin(os.path.join(tempdir, filename))
            else:
                tk.messagebox.showerror("插件市场", "下载失败，请重试！")
            rmdir(tempdir)
            progressbar["value"] = 0

        f_s = tk.Frame(pluginwindow)
        s1 = tk.ttk.Scrollbar(f_s, orient=tk.VERTICAL)
        pluginchoose = tk.Listbox(f_s, yscrollcommand=s1.set, width=30)
        if pluginchoose.size() > 0:
            pluginchoose.delete(0, pluginchoose.size())
        pluginlist = self.getlist()
        [pluginchoose.insert("end", j["name"]) for j in pluginlist]
        f_s.pack(side=tk.LEFT, fill=tk.BOTH)
        s1.pack(side=tk.RIGHT, fill=tk.BOTH)
        s1.config(command=pluginchoose.yview)
        tk.ttk.Button(f_s, text="刷新", command=reload).pack()
        pluginchoose.pack(side=tk.LEFT, fill=tk.BOTH)
        f1 = tk.Frame(pluginwindow)
        pluginname = tk.ttk.Label(f1, font=("Microsoft YaHei UI", 15, "bold"))
        pluginversion = tk.ttk.Label(f1, font=("Microsoft YaHei UI", 10))
        pluginauthor = tk.ttk.Label(f1, font=("Microsoft YaHei UI", 10))
        pluginname.pack()
        pluginversion.pack()
        pluginauthor.pack()
        install_button = tk.ttk.Button(f1, text="安装", command=download)
        install_button.pack()
        f2 = tk.Frame(f1)
        s2 = tk.ttk.Scrollbar(f2, orient=tk.VERTICAL)
        e_ = tk.Text(f2, yscrollcommand=s2.set, font=("Microsoft YaHei UI", 10))
        s2.pack(side=tk.RIGHT, fill=tk.BOTH)
        s2.config(command=e_.yview)
        f2.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
        e_.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
        progressbar = tk.ttk.Progressbar(pluginwindow)
        progressbar.pack(side=tk.TOP, fill="both")
        progressbar["maximum"] = 100
        progressbar["value"] = 0
        if len(pluginlist) > 0:
            pluginchoose.selection_set(0)
            show_info()
            f1.pack()
        pluginchoose.bind("<<ListboxSelect>>", show_info)


class TextPlus(tk.Text):
    """
    定制版文本框类
    """

    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)
        self._orig = self._w + '_orig'
        self.tk.call('rename', self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)

    def _proxy(self, command, *args):
        if command == 'get' and (args[0] == 'sel.first' and args[1] == 'sel.last') and not self.tag_ranges('sel'):
            return
        if command == 'delete' and (args[0] == 'sel.first' and args[1] == 'sel.last') and not self.tag_ranges('sel'):
            return
        cmd = (self._orig, command) + args
        result = self.tk.call(cmd)
        if command in ('insert', 'delete', 'replace'):
            self.event_generate('<<TextModified>>')
        return result


class TempSave:
    """
    临时保存类
    """

    def __init__(self: typing_extensions.Self, tempdir: Path) -> None:
        """
        初始化临时保存类
        :param tempdir: 临时保存目录
        """
        self.dir = tempdir
        if not os.path.isdir(tempdir):
            os.mkdir(tempdir)

    def get_count(self: typing_extensions.Self) -> int:
        """
        获取临时保存文件数
        :return: 临时文件数
        """
        return len(os.listdir(self.dir))

    def save(self: typing_extensions.Self) -> None:
        """
        临时保存当前文件
        """
        with open(os.path.join(self.dir, f"{window_hwnd}.json"), "w") as f:
            json.dump({"encoding": file_encoding, "path": file_path, "content": e.get('0.0', 'end')[:-1]}, f)

    def load(self: typing_extensions.Self) -> None:
        """
        加载一个临时保存的文件，如有多个，将新建进程加载
        """
        global file_path
        global file_encoding
        files = os.listdir(self.dir)
        if not files:
            return
        with open(os.path.join(self.dir, files[0])) as f:
            tempfile = json.load(f)
        os.remove(os.path.join(self.dir, files[0]))
        file_path = tempfile["path"]
        file_encoding = tempfile["encoding"]
        e.delete('0.0', 'end')
        e.insert('end', tempfile["content"])
        e.edit_reset()
        if len(files) > 1:
            os.startfile(sys.argv[0])


version: str = "4.5"
update_date: str = "2024/7/12"
font: typing.Tuple[str, int, str] = ("Microsoft YaHei UI", 10, "")
encodings: typing.List[str] = ["GBK", "UTF-16", "BIG5", "shift_jis", "UTF-8"]
file_encoding: str = sys.getdefaultencoding()
pubkey: str = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAviKlXVbsyDDvqZSLLc3A
UK86Wg/+dUMS/zneoyQoihnvtiZjcEpV7rOxW17DjZnfpgo1LkCr95LWXeqEEuJp
N4Q9BtNR21GeFgH56+2G1dFefDSZpghZJMtqKi2N6cLDw11RShFKrz3VLO/j6tdv
/fnM6LasVoi5nBdKVe1XpJH+4tu90ksYn2tzOBiHniUiOLqGm8JgvON07q+zjGP3
o/ZNM9K23+hmrOg5Gy9ilpNDgR4THyk9oCGs3m+T9FTu+8NtlQX8/CkT5I+/kMTY
fc3BnF8vjyV7vb3mKI2RPdRkLgYOEyWPDEwLteiVmA5ZFqdesPYBVpQ2RgnOXvhT
3QIDAQAB
-----END PUBLIC KEY-----"""
plugin_object: Plugins = Plugins("plugins", "plugin.json", pubkey)
tempsavefile_object: TempSave = TempSave("tempsave")
all_lang: dict = {}
user_lang: str = ""
for i in os.listdir(".\\lang"):
    if os.path.isfile(os.path.join(".\\lang", i)) and i.endswith(".lang"):
        # noinspection PyBroadException
        try:
            with open(os.path.join(".\\lang", i), encoding=detect_encoding(os.path.join(".\\lang", i))) as lang_file:
                all_lang[i[:-5]] = json.load(lang_file)
        except Exception:
            pass
try:
    # noinspection PyUnresolvedReferences
    lang: dict = all_lang[locale.windows_locale[win32api.GetUserDefaultLangID()]]
    # noinspection PyUnresolvedReferences
    user_lang = locale.windows_locale[win32api.GetUserDefaultLangID()]
except KeyError:
    lang: dict = {}
    user_lang = "en_US" if "en_US" in list(all_lang.keys()) else list(all_lang.keys())[0]
lang_raw: dict = all_lang["en_US" if "en_US" in list(all_lang.keys()) else list(all_lang.keys())[0]]
window: tk.Tk = tk.Tk()
window.tk.call('tk', 'scaling', ScaleFactor / 75)
istopmost: tk.BooleanVar = tk.BooleanVar(value=False)
iswrapmode: tk.BooleanVar = tk.BooleanVar(value=False)
isbold: tk.BooleanVar = tk.BooleanVar(value=False)
isitalic: tk.BooleanVar = tk.BooleanVar(value=False)
isunderline: tk.BooleanVar = tk.BooleanVar(value=False)
isbin_mode: tk.BooleanVar = tk.BooleanVar(value=False)
ignore: tk.BooleanVar = tk.BooleanVar(value=False)
encoding: tk.StringVar = tk.StringVar(value="auto")
file_path: Path = ""
plugins: typing.List[str] = []
read_config()
plugin_object.run_plugins("init", globals(), locals())
for key in (lang_raw.keys() - lang.keys()):
    lang[key] = lang_raw[key]
fontname: tk.StringVar = tk.StringVar(value=font[0])
fontsize: tk.IntVar = tk.IntVar(value=font[1])

window.title(lang["text.gui.title"])
window.geometry('400x500')
window.minsize(300, 20)
window.iconbitmap(lang["path.gui.ico"])
# 获取窗口句柄
window_hwnd: int = user32.GetParent(window.winfo_toplevel().winfo_id())

# 文本框初始化
f: tk.ttk.Frame = tk.ttk.Frame(window, relief="groove", borderwidth=2)
# 滚动条
s1: tk.ttk.Scrollbar = tk.ttk.Scrollbar(f, orient=tk.VERTICAL)
s2: tk.ttk.Scrollbar = tk.ttk.Scrollbar(f, orient=tk.HORIZONTAL)
# 文本框
e: TextPlus = TextPlus(f, wrap=tk.NONE, yscrollcommand=s1.set, xscrollcommand=s2.set, font=font, undo=True,
                       relief="flat")
s1.pack(side=tk.RIGHT, fill=tk.BOTH)
s1.config(command=e.yview)
s2.pack(side=tk.BOTTOM, fill=tk.BOTH)
s2.config(command=e.xview)
f.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
f.pack_propagate(False)  # 防止文本框占据状态栏的空间
e.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
e.focus()

# 菜单栏初始化
menubar: tk.Menu = tk.Menu(window)
filemenu: tk.Menu = tk.Menu(menubar, tearoff=0)
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
filemenu.add_command(label=lang["text.gui.menu.file.plugins"][0], command=plugin_object.plugin,
                     underline=lang["text.gui.menu.file.plugins"][1])
filemenu.add_separator()
filemenu.add_command(label=lang["text.gui.menu.file.exit"][0], command=exit_window,
                     underline=lang["text.gui.menu.file.exit"][1])
menubar.add_cascade(label=lang["text.gui.menu.file"][0], menu=filemenu, underline=lang["text.gui.menu.file"][1])
editmenu: tk.Menu = tk.Menu(menubar, tearoff=0)
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
contextmenu: tk.Menu = tk.Menu(window, tearoff=0)
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
viewmenu: tk.Menu = tk.Menu(menubar, tearoff=0)
viewmenu.add_command(label=lang["text.gui.menu.view.font"][0], command=font_settings,
                     underline=lang["text.gui.menu.view.font"][1])
viewmenu.add_separator()
viewmenu.add_checkbutton(label=lang["text.gui.menu.view.warp"][0], underline=lang["text.gui.menu.view.warp"][1],
                         variable=iswrapmode, command=wrap_)
viewmenu.add_separator()
viewmenu.add_checkbutton(label=lang["text.gui.menu.view.topmost"][0], underline=lang["text.gui.menu.view.topmost"][1],
                         command=topmost, variable=istopmost)
menubar.add_cascade(label=lang["text.gui.menu.view"][0], menu=viewmenu, underline=lang["text.gui.menu.view"][1])
encodingmenu: tk.Menu = tk.Menu(menubar, tearoff=0)
encodingmenu.add_radiobutton(label=lang["text.gui.menu.encoding.auto_encoding"][0],
                             underline=lang["text.gui.menu.encoding.auto_encoding"][1], variable=encoding,
                             value="auto")
for i in encodings:
    encodingmenu.add_radiobutton(label=i, variable=encoding, value=i)
encodingmenu.add_separator()
encodingmenu.add_checkbutton(label=lang["text.gui.menu.encoding.ignore_errors"][0], variable=ignore,
                             underline=lang["text.gui.menu.encoding.ignore_errors"][1])
encodingmenu.add_checkbutton(label=lang["text.gui.menu.encoding.binary_mode"][0], variable=isbin_mode,
                             underline=lang["text.gui.menu.encoding.binary_mode"][1], command=bin_mode)
menubar.add_cascade(label=lang["text.gui.menu.encoding"][0], menu=encodingmenu,
                    underline=lang["text.gui.menu.encoding"][1])
infomenu: tk.Menu = tk.Menu(menubar, tearoff=0)
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

# 状态栏初始化
status_bar_var: tk.StringVar = tk.StringVar()
status_bar: tk.Label = tk.Label(window, textvariable=status_bar_var, relief='sunken', bd=tk.TRUE, anchor=tk.W)
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

# 快捷键绑定
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
e.bind('<<TextModified>>', on_modify)
e.event_add('<<CursorEvent>>', *('<KeyPress>', '<KeyRelease>', '<ButtonPress>', '<ButtonRelease>'))
# noinspection PyTypeChecker
e.bind('<<CursorEvent>>', update_status_bar)
windnd.hook_dropfiles(e, func=drop(open_file))
window.config(menu=menubar)

WNDPROCTYPE = ctypes.WINFUNCTYPE(ctypes.c_long, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)


# 新窗口处理器（防退出）
def new_wndproc(hwnd, msg, wparam, lparam):
    if msg == win32con.WM_CLOSE:
        return exit_window()
    elif msg == win32con.WM_QUERYENDSESSION:
        return issave()
    elif msg == win32con.WM_ENDSESSION:
        if wparam:
            tempsavefile_object.save()
        return 0

    return user32.CallWindowProcW(wndproc, hwnd, msg, wparam, lparam)


wndproc: int = user32.SetWindowLongW(window_hwnd, -4, WNDPROCTYPE(new_wndproc))

window.protocol('WM_DELETE_WINDOW', exit_window)
plugin_object.run_plugins("main", globals(), locals())
if len(sys.argv) > 1:
    open_file(sys.argv[1])
    if tempsavefile_object.get_count() > 0:
        os.startfile(sys.argv[0])
else:
    tempsavefile_object.load()
window.mainloop()
