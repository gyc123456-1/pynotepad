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
import windnd


def q(func):
    def wrapper(*args, **kwargs):
        if file_url != "<new>":
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
            a = tk.messagebox.askyesnocancel('pynotepad', '你想将更改保存吗?')
            if a is None:
                return
            elif a:
                if file_url == "<new>":
                    save_as()
                else:
                    save()
                func(*args, **kwargs)
            else:
                func(*args, **kwargs)

    return wrapper


@q
def make_new():
    e.delete('0.0', 'end')
    global file_url
    file_url = "<new>"


def d_open(files):
    url = [i.decode("gbk") for i in files]
    open_file(url[0])


@q
def open_file(url=""):
    if not url:
        url = tk.filedialog.askopenfilename(title="打开文件", filetypes=[("文本文档", ".txt"), ("所有类型", ".*")])
    e.delete('0.0', 'end')
    global file_url
    global file_coding
    file_url = "<new>"
    text = ""
    file_url = url
    if encoding.get() == "auto":
        for i in reversed(encodings):
            if b.get():
                with open(url, "rb") as f:
                    text = str(f.read())[2:-1]
                    break
            else:
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
            tk.messagebox.showerror("pynotepad", "解码错误, 请到编码菜单换一种解码方式!")
    else:
        if b.get():
            with open(url, "rb") as f:
                text = str(f.read())[2:-1]
        else:
            with open(url, encoding=encoding.get(), errors="ignore" if ignore.get() else None) as f:
                try:
                    text = f.read()
                    file_coding = encoding.get()
                except UnicodeDecodeError:
                    tk.messagebox.showerror("pynotepad", "解码错误, 请到编码菜单换一种解码方式!")
                except UnicodeError:
                    tk.messagebox.showerror("pynotepad", "解码错误, 请到编码菜单换一种解码方式!")
    file_url = url
    window.title('pynotepad - ' + file_url)
    e.insert('end', text)


def save():
    global window
    global file_url
    if file_url == "<new>":
        save_as()
    else:
        if encoding.get() == "auto":
            if b.get():
                with open(file_url, "wb") as f:
                    f.write(eval("b'" + e.get("0.0", "end")[:-1] + "'"))
            else:
                with open(file_url, "w", encoding=file_coding, errors="ignore" if ignore.get() else None) as f:
                    try:
                        f.write(e.get("0.0", "end")[:-1])
                    except UnicodeEncodeError:
                        tk.messagebox.showerror("pynotepad", "编码错误, 可能是此编码不支持这串文本, 请到编码菜单换一种解码方式!")
        else:
            if b.get():
                with open(file_url, "wb") as f:
                    f.write(eval("b'" + e.get("0.0", "end")[:-1] + "'"))
            else:
                with open(file_url, "w", encoding=encoding.get(), errors="ignore" if ignore.get() else None) as f:
                    try:
                        f.write(e.get("0.0", "end")[:-1])
                    except UnicodeEncodeError:
                        tk.messagebox.showerror("pynotepad", "编码错误, 可能是此编码不支持这串文本, 请到编码菜单换一种解码方式!")


def save_as():
    url = tk.filedialog.asksaveasfilename(title="另存为", filetypes=[("文本文档", ".txt"), ("所有类型", ".*")])
    if encoding.get() == "auto":
        if b.get():
            with open(url, "wb") as f:
                f.write(eval("b'" + e.get("0.0", "end")[:-1] + "'"))
        else:
            with open(url, 'w', encoding=file_coding, errors="ignore" if ignore.get() else None) as f:
                try:
                    f.write(e.get("0.0", "end")[:-1])
                except UnicodeEncodeError:
                    tk.messagebox.showerror("pynotepad", "编码错误, 可能是此编码不支持这串文本, 请到编码菜单换一种解码方式!")
    else:
        if b.get():
            with open(url, "wb") as f:
                f.write(eval("b'" + e.get("0.0", "end")[:-1] + "'"))
        else:
            with open(url, 'w', encoding=encoding.get(), errors="ignore" if ignore.get() else None) as f:
                try:
                    f.write(e.get("0.0", "end")[:-1])
                except UnicodeEncodeError:
                    tk.messagebox.showerror("pynotepad", "编码错误, 可能是此编码不支持这串文本, 请到编码菜单换一种解码方式!")

    global file_url
    file_url = url
    window.title('pynotepad -' + file_url)


@q
def exit():
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


def send_printer():
    pt = tk.Toplevel()
    pt.geometry("250x80")
    pt.title("打印文件")
    pt.iconbitmap(r'ico\Notepad.ico')
    printer = tk.StringVar()
    tk.Label(pt, text="选择打印机").pack()
    PRCOMBO = tk.ttk.Combobox(pt, width=35, textvariable=printer, state="readonly")
    print_list = []
    for i in win32print.EnumPrinters(2):
        print_list.append(i[2])
    PRCOMBO['values'] = print_list
    printer.set(win32print.GetDefaultPrinter())
    PRCOMBO.pack()
    pt.transient(window)

    def p():
        filename = tempfile.mktemp(".txt")
        with open(filename, "w") as f:
            f.write(e.get("0.0", "end")[:-1])

        win32api.ShellExecute(
            0,
            "printto",
            filename,
            '"%s"' % printer.get(),
            ".",
            0
        )
        pt.destroy()

    # def p():
    #     if sys.version_info >= (3,):
    #         raw_data = bytes(e.get("0.0", "end"), "utf-8")
    #     else:
    #         raw_data = e.get("0.0", "end")
    #     hPrinter = win32print.OpenPrinter(printer.get())
    #     try:
    #         hJob = win32print.StartDocPrinter(hPrinter, 1, (file_url.split("/")[-1], None, "RAW"))
    #         try:
    #             win32print.StartPagePrinter(hPrinter)
    #             win32print.WritePrinter(hPrinter, raw_data)
    #             win32print.EndPagePrinter(hPrinter)
    #         finally:
    #             win32print.EndDocPrinter(hPrinter)
    #     finally:
    #         win32print.ClosePrinter(hPrinter)
    #     pt.destroy()

    tk.Button(pt, text="打印", command=p).pack()


def font_settings():
    setings = tk.Toplevel()
    setings.geometry("220x20")
    setings.title("字体设置")
    setings.resizable(False, False)
    setings.iconbitmap(r'ico\Notepad.ico')
    setings.transient(window)
    menubar = tk.Menu(setings)
    fontnamemenu = tk.Menu(menubar, tearoff=0)
    for i in [i for i in tkinter.font.families() if not i.startswith("@")]:
        fontnamemenu.add_radiobutton(label=i, variable=fontname, value=i, command=font_, font=(i, 10))
    menubar.add_cascade(label='字体(F)', menu=fontnamemenu, underline=3)
    fontsizemenu = tk.Menu(menubar, tearoff=0)
    for i in range(10, 51):
        fontsizemenu.add_radiobutton(label=str(i), variable=fontsize, value=i, command=font_)
    menubar.add_cascade(label='大小(S)', menu=fontsizemenu, underline=3)
    fonteffectmenu = tk.Menu(menubar, tearoff=0)
    fonteffectmenu.add_checkbutton(label="加粗(B)", variable=B, underline=3, command=font_)
    fonteffectmenu.add_checkbutton(label="斜体(I)", variable=I, underline=3, command=font_)
    fonteffectmenu.add_checkbutton(label="下划线(U)", variable=U, underline=4, command=font_)
    menubar.add_cascade(label='显示效果(T)', menu=fonteffectmenu, underline=5)
    setings.config(menu=menubar)


def find_str():
    def search(event=None, mark=True):
        key = keyword_text.get()
        if not key:
            return
        if use_escape_char.get():
            try:
                key = eval('"""' + key + '"""')
            except Exception as err:
                tk.messagebox.showerror("错误", str(err))
                return
        if use_regexpr.get():
            try:
                re.compile(key)
            except re.error as err:
                tk.messagebox.showerror("错误", str(err))
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
    find_window.title("查找")
    find_window.resizable(False, False)
    find_window.iconbitmap(r'ico\Notepad.ico')
    find_window.transient(window)
    frame = tk.Frame(find_window)
    tk.ttk.Button(frame, text="查找下一个", command=findnext).pack()
    frame.pack(side=tk.RIGHT, fill=tk.Y)
    inputbox = tk.Frame(find_window)
    tk.Label(inputbox, text="查找内容:").pack(side=tk.LEFT)
    keyword_text = tk.StringVar()
    keyword = tk.ttk.Entry(inputbox, textvariable=keyword_text)
    keyword.pack(side=tk.LEFT, expand=True, fill=tk.X)
    keyword.bind("<Key-Return>", search)
    keyword.focus_force()
    inputbox.pack(fill=tk.X)
    options = tk.Frame(find_window)
    tk.Label(options, text="选项: ").pack(side=tk.LEFT)
    use_regexpr = tk.BooleanVar()
    tk.ttk.Checkbutton(options, text="使用正则表达式", variable=use_regexpr).pack(side=tk.LEFT)
    match_case = tk.BooleanVar()
    tk.ttk.Checkbutton(options, text="区分大小写", variable=match_case).pack(side=tk.LEFT)
    use_escape_char = tk.BooleanVar()
    tk.ttk.Checkbutton(options, text="使用转义字符", variable=use_escape_char).pack(side=tk.LEFT)
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
                tk.messagebox.showerror("错误", str(err))
                return
        if use_regexpr.get():
            try:
                re.compile(key)
            except re.error as err:
                tk.messagebox.showerror("错误", str(err))
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
            tk.messagebox.showerror("错误", str(err))
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
    find_window.title("替换")
    find_window.resizable(False, False)
    find_window.iconbitmap(r'ico\Notepad.ico')
    find_window.transient(window)
    frame = tk.Frame(find_window)
    tk.ttk.Button(frame, text="查找下一个", command=_findnext).pack()
    tk.ttk.Button(frame, text="替换", command=replace_f).pack()
    tk.ttk.Button(frame, text="全部替换", command=replace_all).pack()
    frame.pack(side=tk.RIGHT, fill=tk.Y)
    inputbox = tk.Frame(find_window)
    tk.Label(inputbox, text="查找内容:").pack(side=tk.LEFT)
    keyword_text = tk.StringVar()
    keyword = tk.ttk.Entry(inputbox, textvariable=keyword_text)
    keyword.pack(side=tk.LEFT, expand=True, fill=tk.X)
    keyword.focus_force()
    inputbox.pack(fill=tk.X)

    replace = tk.Frame(find_window)
    tk.Label(replace, text="替换为:").pack(side=tk.LEFT)
    text_to_replace = tk.StringVar()
    replace_text = tk.ttk.Entry(replace, textvariable=text_to_replace)
    replace_text.pack(side=tk.LEFT, expand=True, fill=tk.X)
    replace_text.bind("<Key-Return>", replace)
    replace.pack(fill=tk.X)

    options = tk.Frame(find_window)
    tk.Label(options, text="选项: ").pack(side=tk.LEFT)
    use_regexpr = tk.BooleanVar()
    tk.ttk.Checkbutton(options, text="使用正则表达式", variable=use_regexpr).pack(side=tk.LEFT)
    match_case = tk.BooleanVar()
    tk.ttk.Checkbutton(options, text="区分大小写", variable=match_case).pack(side=tk.LEFT)
    use_escape_char = tk.BooleanVar()
    tk.ttk.Checkbutton(options, text="使用转义字符", variable=use_escape_char).pack(side=tk.LEFT)
    options.pack(fill=tk.X)


def get_size():
    if b.get():
        size = len(eval("b'" + e.get("0.0", "end") + "'"))
    else:
        size = len(e.get("0.0", "end")[:-1].encode(file_coding))
    if size > (1024 * 1024):
        return "{.2f}MB".format(size / 1024 / 1024)
    elif size > 1024:
        return "{.2f}KB".format(size / 1024)
    else:
        return "{}字节".format(size)


def bin_mode():
    b.set(not b.get())
    q(lambda: b.set(not b.get()))()
    if file_url != "<new>":
        open_file(file_url)


def write_config(path=os.path.join(os.environ["appdata"], "pynotepad")):
    with open(os.path.join(path, "config.ini"), "w") as f:
        f.write(str({"font": font,
                     "wrap": wrap.get(),
                     "bold": B.get(),
                     "italic": I.get(),
                     "underline": U.get(),
                     "ignore": ignore.get()}))


def read_config(path=os.path.join(os.environ["appdata"], "pynotepad")):
    global font
    if os.path.isdir(path):
        with open(os.path.join(path, "config.ini")) as f:
            config = eval(f.read())
        font = config["font"]
        wrap.set(config["wrap"])
        B.set(config["bold"])
        I.set(config["italic"])
        U.set(config["underline"])
        ignore.set(config["ignore"])
    else:
        os.mkdir(path)
        write_config()


window = tk.Tk()
window.title('pynotepad')
window.geometry('400x500')
window.iconbitmap(r'ico\Notepad.ico')
if len(sys.argv) > 1:
    open_file(sys.argv[1])
else:
    file_url = "<new>"

font = ("微软雅黑", 10, "")
printerdef = ''
wrap = tk.BooleanVar(value=False)
B = tk.BooleanVar(value=False)
I = tk.BooleanVar(value=False)
U = tk.BooleanVar(value=False)
b = tk.BooleanVar(value=False)
ignore = tk.BooleanVar(value=False)
encoding = tk.StringVar(value="auto")
read_config()
fontname = tk.StringVar(value=font[0])
fontsize = tk.IntVar(value=font[1])
encodings = ["GBK", "UTF-8", "UTF-16", "BIG5"]
file_coding = encodings[0]
f = tk.Frame(window)
s1 = tk.Scrollbar(f, orient=tk.VERTICAL)
s2 = tk.Scrollbar(f, orient=tk.HORIZONTAL)
e = tk.Text(f, wrap=tk.NONE, yscrollcommand=s1.set, xscrollcommand=s2.set, font=font, undo=True)
s1.pack(side=tk.RIGHT, fill=tk.BOTH)
s1.config(command=e.yview)
s2.pack(side=tk.BOTTOM, fill=tk.BOTH)
s2.config(command=e.xview)
f.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
e.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
menubar = tk.Menu(window)
filemenu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label='文件(F)', menu=filemenu, underline=3)
filemenu.add_command(label='新建(N)', command=make_new, underline=3, accelerator="Ctrl+N")
filemenu.add_command(label='打开(O)...', command=open_file, underline=3, accelerator="Ctrl+O")
filemenu.add_command(label='保存(S)', command=save, underline=3, accelerator="Ctrl+S")
filemenu.add_command(label='另存为(A)...', command=save_as, accelerator="Ctrl+Shift+S")
filemenu.add_separator()
filemenu.add_command(label='打印(P)', command=send_printer, underline=3, accelerator="Ctrl+P")
filemenu.add_separator()
filemenu.add_command(label='退出(X)', command=exit, underline=3)
editmenu = tk.Menu(menubar, tearoff=0)
editmenu.add_command(label="撤销(U)", command=lambda: e.edit_undo(), underline=3, accelerator="Ctrl+Z")
editmenu.add_command(label="重做(R)", command=lambda: e.edit_redo(), underline=3, accelerator="Ctrl+Shift+Z")
editmenu.add_separator()
editmenu.add_command(label="剪切(P)", command=lambda: e.event_generate("<<Cut>>"), underline=3, accelerator="Ctrl+X")
editmenu.add_command(label="复制(C)", command=lambda: e.event_generate("<<Copy>>"), underline=3, accelerator="Ctrl+C")
editmenu.add_command(label="粘贴(P)", command=lambda: e.event_generate("<<Paste>>"), underline=3,
                     accelerator="Ctrl+V")
editmenu.add_command(label="删除(D)", command=lambda: e.delete(tk.SEL_FIRST, tk.SEL_LAST), underline=3,
                     accelerator="Del")
editmenu.add_command(label="全选(A)", command=lambda: e.tag_add("sel", "0.0", "end"), underline=3,
                     accelerator="Ctrl+A")
editmenu.add_separator()
editmenu.add_command(label="查找(F)...", command=lambda: find_str(), underline=3, accelerator="Ctrl+F")
editmenu.add_command(label="替换(R)...", command=lambda: replace_str(), underline=3, accelerator="Ctrl+H")
menubar.add_cascade(label='编辑(E)', menu=editmenu, underline=3)
contextmenu = tk.Menu(window, tearoff=0)
contextmenu.add_command(label="撤销(U)", command=lambda: e.edit_undo(), underline=3, accelerator="Ctrl+Z")
contextmenu.add_command(label="重做(R)", command=lambda: e.edit_redo(), underline=3, accelerator="Ctrl+Shift+Z")
contextmenu.add_separator()
contextmenu.add_command(label="剪切(P)", command=lambda: e.event_generate("<<Cut>>"), underline=3,
                        accelerator="Ctrl+X")
contextmenu.add_command(label="复制(C)", command=lambda: e.event_generate("<<Copy>>"), underline=3,
                        accelerator="Ctrl+C")
contextmenu.add_command(label="粘贴(P)", command=lambda: e.event_generate("<<Paste>>"), underline=3,
                        accelerator="Ctrl+V")
contextmenu.add_command(label="删除(D)", command=lambda: e.delete(tk.SEL_FIRST, tk.SEL_LAST), underline=3,
                        accelerator="Del")
contextmenu.add_command(label="全选(A)", command=lambda: e.tag_add("sel", "0.0", "end"), underline=3,
                        accelerator="Ctrl+A")
contextmenu.add_separator()
contextmenu.add_command(label="属性(I)", underline=3, command=lambda: tk.messagebox.showinfo(file_url,
                                                                                           "编码:{}\n行数:{}\n大小:{}".
                                                                                           format(
                                                                                               file_coding,
                                                                                               len(e.get("0.0",
                                                                                                         "end")[
                                                                                                   :-1]),
                                                                                               get_size())))
displaymenu = tk.Menu(menubar, tearoff=0)
displaymenu.add_command(label='字体(F)...', command=font_settings, underline=3)
displaymenu.add_separator()
displaymenu.add_checkbutton(label="自动换行(W)", underline=5, variable=wrap, command=wrap_)
displaymenu.add_command(label="文件信息(I)", underline=5, command=lambda: tk.messagebox.showinfo(file_url,
                                                                                             "编码:{}\n行数:{}\n大小:{}".
                                                                                             format(
                                                                                                 file_coding,
                                                                                                 len(e.get("0.0",
                                                                                                           "end")[
                                                                                                     :-1]),
                                                                                                 get_size())))
menubar.add_cascade(label='查看(V)', menu=displaymenu, underline=3)
encodingmenu = tk.Menu(menubar, tearoff=0)
encodingmenu.add_radiobutton(label="自动检测", variable=encoding, value="auto")
for i in encodings:
    encodingmenu.add_radiobutton(label=i, variable=encoding, value=i)
encodingmenu.add_separator()
encodingmenu.add_checkbutton(label="忽略错误(U)", variable=ignore, underline=5)
encodingmenu.add_checkbutton(label="二进制模式(B)", variable=b, underline=6, command=bin_mode)
menubar.add_cascade(label='编码(E)', menu=encodingmenu, underline=3)
infomenu = tk.Menu(menubar, tearoff=0)
infomenu.add_command(label="关于(I)", command=lambda: tk.messagebox.showinfo("pynotepad", "v2.6 2022/11/28"),
                     underline=3)
infomenu.add_command(label="版权信息(C)",
                     command=lambda: tk.messagebox.showinfo("pynotepad",
                                                            "copyright © gyc 2020-{}".format(
                                                                time.localtime(time.time())[0])),
                     underline=5)
menubar.add_cascade(label='帮助(H)', menu=infomenu, underline=3)

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
windnd.hook_dropfiles(e, func=d_open)
window.config(menu=menubar)
window.protocol('WM_DELETE_WINDOW', exit)
window.mainloop()
