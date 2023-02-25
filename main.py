import threading
import json
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
import base64
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
from Crypto.Signature import PKCS1_v1_5 as PKCS1_signature
import ctypes
import locale
import zipfile
import traceback
import io

ctypes.windll.shcore.SetProcessDpiAwareness(1)
ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)


def q(func):
    def wrapper(*args, **kwargs):
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
            a = tk.messagebox.askyesnocancel(lang["title"], lang["ask_save"])
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
    if not url:
        url = tk.filedialog.askopenfilename(title=lang["open_file_title"],
                                            filetypes=[(lang["txt_name"], ".txt"), (lang["all_name"], ".*")])
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
                tk.messagebox.showerror(lang["error"], lang["decoding_error"])
        else:
            with open(url, encoding=encoding.get(), errors="ignore" if ignore.get() else None) as f:
                try:
                    text = f.read()
                    file_coding = encoding.get()
                except UnicodeDecodeError:
                    tk.messagebox.showerror(lang["error"], lang["decoding_error"])
                except UnicodeError:
                    tk.messagebox.showerror(lang["error"], lang["decoding_error"])
    file_url = url
    window.title(lang["title2"] + file_url)
    e.insert('end', text)


def save():
    global window
    global file_url
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
                    tk.messagebox.showerror(lang["error"], lang["encoding_error"])
        else:
            if encoding.get() == "auto":
                with open(file_url, "w", encoding=file_coding, errors="ignore" if ignore.get() else None) as f:
                    try:
                        f.write(e.get("0.0", "end")[:-1])
                        issave = True
                    except UnicodeEncodeError:
                        tk.messagebox.showerror(lang["error"], lang["encoding_error"])
            else:
                with open(file_url, "w", encoding=encoding.get(), errors="ignore" if ignore.get() else None) as f:
                    try:
                        f.write(e.get("0.0", "end")[:-1])
                        issave = True
                    except UnicodeEncodeError:
                        tk.messagebox.showerror(lang["error"], lang["encoding_error"])
        return issave


def save_as():
    issave = False
    url = tk.filedialog.asksaveasfilename(title=lang["save_as_title"],
                                          filetypes=[(lang["txt_name"], ".txt"), (lang["all_name"], ".*")])
    if b.get():
        with open(url, "wb") as f:
            try:
                f.write(eval("b'" + e.get("0.0", "end")[:-1] + "'"))
                issave = True
            except SyntaxError:
                tk.messagebox.showerror(lang["error"], lang["encoding_error"])
    else:
        if encoding.get() == "auto":
            with open(url, 'w', encoding=file_coding, errors="ignore" if ignore.get() else None) as f:
                try:
                    f.write(e.get("0.0", "end")[:-1])
                    issave = True
                except UnicodeEncodeError:
                    tk.messagebox.showerror(lang["error"], lang["encoding_error"])
        else:
            with open(url, 'w', encoding=encoding.get(), errors="ignore" if ignore.get() else None) as f:
                try:
                    f.write(e.get("0.0", "end")[:-1])
                    issave = True
                except UnicodeEncodeError:
                    tk.messagebox.showerror(lang["error"], lang["encoding_error"])

    global file_url
    file_url = url
    window.title(lang["title2"] + file_url)
    return issave


@q
def exit_window():
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
    pt.title(lang["print_file"])
    pt.iconbitmap(lang["ico"])
    printer = tk.StringVar()
    tk.ttk.Label(pt, text=lang["sel_printer"]).pack()
    prcombo = tk.ttk.Combobox(pt, width=35, textvariable=printer, state="readonly")
    print_list = []
    for i in win32print.EnumPrinters(2):
        print_list.append(i[2])
    prcombo['values'] = print_list
    printer.set(win32print.GetDefaultPrinter())
    prcombo.pack()
    pt.transient(window)

    def p():
        filename = tempfile.mktemp(".txt")
        with open(filename, "w", errors="ignore" if ignore.get() else None) as f:
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

    tk.ttk.Button(pt, text=lang["print_button"], command=p).pack()


def font_settings():
    setings = tk.Toplevel()
    setings.geometry("220x20")
    setings.title(lang["font_settings"])
    setings.resizable(False, False)
    setings.iconbitmap(lang["ico"])
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
    menubar.add_cascade(label=lang["font_setting"][0], menu=fontnamemenu, underline=lang["font_setting"][1])
    fontsizemenu = tk.Menu(menubar, tearoff=0)
    for i in range(10, 51):
        if i - 10 != 0 and (i - 10) % 10 == 0:
            fontsizemenu.add_radiobutton(label=str(i), variable=fontsize, value=i, command=font_, columnbreak=True)
        else:
            fontsizemenu.add_radiobutton(label=str(i), variable=fontsize, value=i, command=font_)
    menubar.add_cascade(label=lang["size_setting"][0], menu=fontsizemenu, underline=lang["size_setting"][1])
    fonteffectmenu = tk.Menu(menubar, tearoff=0)
    fonteffectmenu.add_checkbutton(label=lang["bold"][0], variable=B, underline=lang["bold"][1], command=font_)
    fonteffectmenu.add_checkbutton(label=lang["italic"][0], variable=I, underline=lang["italic"][1], command=font_)
    fonteffectmenu.add_checkbutton(label=lang["underline"][0], variable=U, underline=lang["underline"][1],
                                   command=font_)
    menubar.add_cascade(label=lang["font_effect"][0], menu=fonteffectmenu, underline=lang["font_effect"][1])
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
                tk.messagebox.showerror(lang["error"], str(err))
                return
        if use_regexpr.get():
            try:
                re.compile(key)
            except re.error as err:
                tk.messagebox.showerror(lang["error"], str(err))
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
    find_window.title(lang["replace1"])
    find_window.resizable(False, False)
    find_window.iconbitmap(lang["ico"])
    find_window.transient(window)
    frame = tk.Frame(find_window)
    tk.ttk.Button(frame, text=lang["find_next"], command=findnext).pack()
    frame.pack(side=tk.RIGHT, fill=tk.Y)
    inputbox = tk.Frame(find_window)
    tk.ttk.Label(inputbox, text=lang["find_tip"]).pack(side=tk.LEFT)
    keyword_text = tk.StringVar()
    keyword = tk.ttk.Entry(inputbox, textvariable=keyword_text)
    keyword.pack(side=tk.LEFT, expand=True, fill=tk.X)
    keyword.bind("<Key-Return>", search)
    keyword.focus_force()
    inputbox.pack(fill=tk.X)
    options = tk.Frame(find_window)
    tk.ttk.Label(options, text=lang["options"]).pack(side=tk.LEFT)
    use_regexpr = tk.BooleanVar()
    tk.ttk.Checkbutton(options, text=lang["use_regexpr"], variable=use_regexpr).pack(side=tk.LEFT)
    match_case = tk.BooleanVar()
    tk.ttk.Checkbutton(options, text=lang["match_case"], variable=match_case).pack(side=tk.LEFT)
    use_escape_char = tk.BooleanVar()
    tk.ttk.Checkbutton(options, text=lang["use_escape_char"], variable=use_escape_char).pack(side=tk.LEFT)
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
                tk.messagebox.showerror(lang["error"], str(err))
                return
        if use_regexpr.get():
            try:
                re.compile(key)
            except re.error as err:
                tk.messagebox.showerror(lang["error"], str(err))
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
            tk.messagebox.showerror(lang["error"], str(err))
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
    find_window.title(lang["replace1"])
    find_window.resizable(False, False)
    find_window.iconbitmap(lang["ico"])
    find_window.transient(window)
    frame = tk.Frame(find_window)
    tk.ttk.Button(frame, text=lang["find_next"], command=_findnext).pack()
    tk.ttk.Button(frame, text=lang["replace1"], command=replace_f).pack()
    tk.ttk.Button(frame, text=lang["replace_all"], command=replace_all).pack()
    frame.pack(side=tk.RIGHT, fill=tk.Y)
    inputbox = tk.Frame(find_window)
    tk.ttk.Label(inputbox, text=lang["find_tip"]).pack(side=tk.LEFT)
    keyword_text = tk.StringVar()
    keyword = tk.ttk.Entry(inputbox, textvariable=keyword_text)
    keyword.pack(side=tk.LEFT, expand=True, fill=tk.X)
    keyword.focus_force()
    inputbox.pack(fill=tk.X)

    replace = tk.Frame(find_window)
    tk.ttk.Label(replace, text=lang["replace_tip"]).pack(side=tk.LEFT)
    text_to_replace = tk.StringVar()
    replace_text = tk.ttk.Entry(replace, textvariable=text_to_replace)
    replace_text.pack(side=tk.LEFT, expand=True, fill=tk.X)
    replace_text.bind("<Key-Return>", replace)
    replace.pack(fill=tk.X)

    options = tk.Frame(find_window)
    tk.ttk.Label(options, text=lang["options"]).pack(side=tk.LEFT)
    use_regexpr = tk.BooleanVar()
    tk.ttk.Checkbutton(options, text=lang["use_regexpr"], variable=use_regexpr).pack(side=tk.LEFT)
    match_case = tk.BooleanVar()
    tk.ttk.Checkbutton(options, text=lang["match_case"], variable=match_case).pack(side=tk.LEFT)
    use_escape_char = tk.BooleanVar()
    tk.ttk.Checkbutton(options, text=lang["use_escape_char"], variable=use_escape_char).pack(side=tk.LEFT)
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


def write_config(path=os.path.join(os.environ["appdata"], "pynotepad")):
    with open(os.path.join(path, "config.ini"), "w") as f:
        json.dump({"font": font,
                   "wrap": wrap.get(),
                   "bold": B.get(),
                   "italic": I.get(),
                   "underline": U.get(),
                   "ignore": ignore.get(),
                   "plugins": plugins}, f)


def read_config(path=os.path.join(os.environ["appdata"], "pynotepad")):
    global font
    global plugins
    if os.path.isdir(path):
        with open(os.path.join(path, "config.ini")) as f:
            config = json.load(f)
        font = config["font"]
        wrap.set(config["wrap"])
        B.set(config["bold"])
        I.set(config["italic"])
        U.set(config["underline"])
        ignore.set(config["ignore"])
        plugins = config["plugins"]
    else:
        os.mkdir(path)
        write_config()


def install_plugin(file):
    with zipfile.ZipFile(file) as f:
        corrupt_file = f.testzip()
        if not (corrupt_file is None):
            tk.messagebox.showerror(lang["error"], lang["corrupt_file"].format(corrupt_file))
            return
        plugin_dirname = f.filelist[0].filename.split("/")[0]
        tempdir = os.path.join(tempfile.gettempdir(), "pynotepad", plugin_dirname)
        os.makedirs(tempdir)
        f.extractall(tempdir)
        try:
            if os.path.isfile(os.path.join(tempdir, "package.json")):
                with open(os.path.join(tempdir, "package.json"), encoding="utf-8") as i:
                    info = json.load(i)
                keys = ["name", "version", "description", "minsdk", "files", "dependencies"]
                for i in keys:
                    if not (i in info):
                        tk.messagebox.showerror(lang["error"], lang["incorrect_plugin"])
                        return
                if "maxsdk" in info:
                    if version > info["maxsdk"]:
                        tk.messagebox.showerror(lang["error"], lang["low_plugin"])
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
        except Exception:
            fp = io.StringIO()
            traceback.print_exc(file=fp)
            message = fp.getvalue()
            tk.messagebox.showerror(lang["error"], message)
        else:
            tk.messagebox.showinfo(lang["finish"], lang["plugin_install_finish"])
            plugin()


def plugin():
    pluginwindow = tk.Toplevel()
    pluginwindow.title(lang["plugin_settings"])
    pluginwindow.resizable(False, False)
    pluginwindow.iconbitmap(lang["ico"])
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
                with open(os.path.join("plugin", info["url"], i["file"])) as f:
                    rdata = f.read()
                a = rsa_public_check_sign(rdata, i["sign"], pubkey)
            return a
        except:
            return False

    def enable():
        info = pluginlist[pluginname.cget("text")]
        if enable_button.cget("text") == lang["enable"] or enable_button.cget("text") == lang["update"]:
            if is_signature(info):
                plugins[info["url"]] = info
            else:
                if tk.messagebox.askquestion(lang["warning"], lang["enable_warning"]) == "yes":
                    no_dependencies = []
                    for i in info["dependencies"]:
                        for j in plugins.values():
                            if i == j["name"]:
                                break
                        else:
                            no_dependencies.append(i)
                    if no_dependencies:
                        tk.messagebox.showerror(lang["error"],
                                                lang["no_dependencies"].format(",".join(no_dependencies)))
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
                        plugins[info["url"]] = info
        else:
            del plugins[info["url"]]
        enable_button.config(text=lang["disable"] if info["url"] in plugins.keys() else lang["enable"])

    def show_info(e=None):
        info = pluginlist[pluginchoose.selection_get()]
        pluginname.config(text=info["name"])
        pluginversion.config(text=lang["plugin_version"] + info["version"])
        enable_button.config(text=lang["disable"] if info["url"] in plugins.keys() else lang["enable"])
        if enable_button.cget("text") == lang["disable"]:
            if plugins[info["url"]] != info:
                enable_button.config(text=lang["update"])
        e_.config(state='normal')
        e_.delete("0.0", "end")
        e_.insert("end", info["description"])
        e_.config(state='disabled')

    def install(file=""):
        if file == "":
            file = tk.filedialog.askopenfilename(title="选择插件", filetypes=[('插件文件', '.zip')], parent=pluginwindow)
        install_plugin(file)
        refresh()

    def delete():
        info = pluginlist[pluginname.cget("text")]
        if tk.messagebox.askquestion(lang["title"], lang["delete_warning"]) == "yes":
            try:
                for j in info["files"]:
                    if j["position"] == "delete":
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

            rmdir(os.path.join("plugin", info["url"]))
            os.rmdir(os.path.join("plugin", info["url"]))
            del plugins[info["url"]]
            refresh()

    f_s = tk.Frame(pluginwindow)
    s1 = tk.ttk.Scrollbar(f_s, orient=tk.VERTICAL)
    pluginchoose = tk.Listbox(f_s, yscrollcommand=s1.set, width=30)

    def refresh():
        for i in os.listdir("plugin"):
            if os.path.isdir(os.path.join("plugin", i)):
                with open(os.path.join("plugin", i, "package.json"), encoding="utf-8") as f:
                    info = json.load(f)
                    pluginlist[info["name"]] = info
                    pluginlist[info["name"]]["url"] = i
        if pluginchoose.size() > 0:
            pluginchoose.delete(0, pluginchoose.size())
        [pluginchoose.insert("end", j) for j in pluginlist.keys()]

    refresh()
    f_s.pack(side=tk.LEFT, fill=tk.BOTH)
    s1.pack(side=tk.RIGHT, fill=tk.BOTH)
    s1.config(command=pluginchoose.yview)
    install_button = tk.ttk.Button(f_s, text=lang["install"], command=install).pack()
    pluginchoose.pack(side=tk.LEFT, fill=tk.BOTH)
    f1 = tk.Frame(pluginwindow)
    pluginname = tk.ttk.Label(f1, font=("Microsoft YaHei UI", 15, "bold"))
    pluginversion = tk.ttk.Label(f1, font=("Microsoft YaHei UI", 10))
    pluginname.pack()
    pluginversion.pack()
    enable_button = tk.ttk.Button(f1, text=lang["enable"], command=enable)
    enable_button.pack()
    delete_button = tk.ttk.Button(f1, text=lang["delete"], command=delete).pack()
    tk.ttk.Label(f1, text=lang["restart_tip"]).pack()
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

    # pluginchoose = tk.ttk.Combobox(pluginwindow, width=30, state="readonly")
    # pluginchoose["values"] = list(pluginlist.keys())
    # pluginchoose.pack(side=tk.TOP, fill=tk.BOTH)
    # f1 = tk.Frame(pluginwindow)
    # pluginname = tk.ttk.Label(f1, font=("Microsoft YaHei UI", 15, "bold"))
    # pluginversion = tk.ttk.Label(f1, font=("Microsoft YaHei UI", 10))
    # pluginname.pack()
    # pluginversion.pack()
    # enable_button = tk.ttk.Button(f1, text=lang["enable"], command=enable)
    # enable_button.pack()
    # tk.ttk.Label(f1, text=lang["restart_tip"]).pack()
    # f2 = tk.Frame(f1)
    # s2 = tk.ttk.Scrollbar(f2, orient=tk.VERTICAL)
    # e_ = tk.Text(f2, yscrollcommand=s2.set, font=("Microsoft YaHei UI", 10))
    # s2.pack(side=tk.RIGHT, fill=tk.BOTH)
    # s2.config(command=e_.yview)
    # f2.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
    # e_.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
    # if len(pluginlist) > 0:
    #     pluginchoose.set(list(pluginlist.keys())[0])
    #     show_info()
    #     f1.pack()
    # pluginchoose.bind("<<ComboboxSelected>>", show_info)


def topmost():
    window.wm_attributes('-topmost', top.get())


version = 3.9
update_date = "2023/2/18"
debug_mode = False
font = ("Microsoft YaHei UI", 10, "")
encodings = ["GBK", "UTF-8", "UTF-16", "BIG5", "shift_jis"]
file_coding = encodings[0]
Chinese = {"title": "Pynotepad",
           "title2": "Pynotepad - ",
           "ico": r'ico\Notepad.ico',
           "file": ("文件(F)", 3),
           "new": ("新建(N)", 3),
           "open": ("打开(O)...", 3),
           "save": ("保存(S)", 3),
           "save_as": ("另存为(A)...", 4),
           "print": ("打印(P)", 3),
           "plugin": ("插件(L)", 3),
           "exit": ("退出(X)", 3),
           "undo": ("撤销(U)", 3),
           "redo": ("重做(R)", 3),
           "cut": ("剪切(T)", 3),
           "copy": ("复制(C)", 3),
           "paste": ("粘贴(P)", 3),
           "del": ("删除(D)", 3),
           "sel_all": ("全选(A)", 3),
           "find": ("查找(F)...", 3),
           "replace": ("替换(R)...", 3),
           "edit": ("编辑(E)", 3),
           "file_info": ("文件信息(I)", 5),
           "file_infos": ("编码", "行数", "大小"),
           "font": ("字体(F)...", 3),
           "wrap": ("自动换行(W)", 5),
           "view": ("查看(V)", 3),
           "encoding_auto": ("自动检测(A)", 5),
           "ignore": ("忽略错误(I)", 5),
           "bin": ("二进制模式(B)", 6),
           "encoding": ("编码(E)", 3),
           "info": ("关于(I)", 3),
           "copyright": ("版权信息(C)", 5),
           "help": ("帮助(H)", 3),
           "options": "选项: ",
           "use_regexpr": "使用正则表达式",
           "match_case": "区分大小写",
           "use_escape_char": "使用转义字符",
           "replace_tip": "替换为:",
           "find_tip": "查找内容:",
           "find_next": "查找下一个",
           "replace1": "替换",
           "replace_all": "全部替换",
           "error": "错误",
           "find1": "查找",
           "warning": "警告",
           "plugin_settings": "插件设置",
           "enable": "启用",
           "update": "更新配置文件",
           "enable_warning": "启用恶意插件会导致您的计算机损坏, 是否继续?",
           "disable": "禁用",
           "plugin_version": "版本: ",
           "restart_tip": "提示: 插件更改后重启软件才能生效!",
           "font_settings": "字体设置",
           "font_setting": ("字体(F)", 3),
           "size_setting": ("大小(S)", 3),
           "bold": ("加粗(B)", 3),
           "italic": ("斜体(I)", 3),
           "underline": ("下划线(U)", 4),
           "font_effect": ("显示效果(E)", 5),
           "print_button": "打印",
           "sel_printer": "选择打印机",
           "print_file": "打印文件",
           "encoding_error": "编码错误, 可能是此编码不支持这串文本, 请到编码菜单换一种编码!",
           "txt_name": "文本文档",
           "all_name": "所有类型",
           "save_as_title": "另存为",
           "decoding_error": "解码错误, 请到编码菜单换一种编码!",
           "open_file_title": "打开文件",
           "ask_save": "你想将更改保存吗?",
           "no_dependencies": "缺少依赖项: {}",
           "topmost": ("窗口置顶(T)", 5),
           "copyright_info": "copyright © gyc 2020-{}",
           "corrupt_file": "损坏的文件: {}",
           "incorrect_plugin": "不是正确的插件!",
           "low_plugin": "此插件适用于低版本的pynotepad，当前版本过高!",
           "plugin_install_finish": "插件安装完成!",
           "install": "安装插件",
           "finish": "完成",
           "delete": "删除",
           "delete_warning": "是否要删除这个插件?"}
English = {"title": "Pynotepad",
           "title2": "Pynotepad - ",
           "ico": r'ico\Notepad.ico',
           "file": ("File", 0),
           "new": ("New", 0),
           "open": ("Open", 0),
           "save": ("Save", 0),
           "save_as": ("Save As", 5),
           "print": ("Print", 0),
           "plugin": ("Plugin", 1),
           "exit": ("Exit", 1),
           "undo": ("Undo", 0),
           "redo": ("Redo", 0),
           "cut": ("Cut", 2),
           "copy": ("Copy", 0),
           "paste": ("Paste", 0),
           "del": ("Delete", 0),
           "sel_all": ("Select All", 7),
           "find": ("Find...", 0),
           "replace": ("Replace...", 0),
           "edit": ("Edit", 0),
           "file_info": ("File Info", 5),
           "file_infos": ("Encoding", "Row for total", "Size"),
           "font": ("Font...", 0),
           "wrap": ("Wrap", 0),
           "view": ("View", 0),
           "encoding_auto": ("Auto", 0),
           "ignore": ("Ignore Error", 0),
           "bin": ("Bin mode", 0),
           "encoding": ("Encoding", 0),
           "info": ("Info", 0),
           "copyright": ("Copyright", 0),
           "help": ("Help", 0),
           "options": "Options: ",
           "use_regexpr": "Use Regular Expressions",
           "match_case": "Match Case",
           "use_escape_char": "Use Escape Char",
           "replace_tip": "Replace With:",
           "find_tip": "Find What:",
           "find_next": "Find Next",
           "replace1": "Replace",
           "replace_all": "Replace All",
           "error": "Error",
           "find1": "Find",
           "warning": "Warning",
           "plugin_settings": "Plugin Settings",
           "enable": "Enable",
           "update": "Update Profile",
           "enable_warning": "Enable malicious plugins will damage your computer. Do you want to continue?",
           "disable": "Disable",
           "plugin_version": "Version: ",
           "restart_tip": "Prompt: Restart the software to take effect after the plugin is changed!",
           "font_settings": "Font Settings",
           "font_setting": ("Font", 0),
           "size_setting": ("Size", 0),
           "bold": ("Bold", 0),
           "italic": ("Italic", 0),
           "underline": ("Underline", 0),
           "font_effect": ("Font Effect", 5),
           "print_button": "Print",
           "sel_printer": "Select Printer:",
           "print_file": "Print File",
           "encoding_error": "Encoding error. This encoding may not support this string of text. Please go to the encoding menu to change the encoding!",
           "txt_name": "Text Document",
           "all_name": "All Types",
           "save_as_title": "Save As",
           "decoding_error": "Decoding error, please go to the encoding menu to change the decoding method!",
           "open_file_title": "Open File",
           "ask_save": "Do you want to save your changes?",
           "no_dependencies": "Missing dependencies: {}",
           "topmost": ("Window Topmost", 7),
           "copyright_info": "copyright © gyc 2020-{}",
           "corrupt_file": "Corrupt file: {}",
           "incorrect_plugin": "Incorrect plugin!",
           "low_plugin": "This plugin is suitable for low version of pynotepad, the current version is too high!",
           "plugin_install_finish": "The plugin installation is complete!",
           "install": "Install Plugin",
           "finish": "Finish",
           "delete": "Delete",
           "delete_warning": "Do you want to delete this plugin?"
           }
all_lang = {"zh_CN": Chinese, "en_US": English}
try:
    lang = all_lang[locale.windows_locale[win32api.GetUserDefaultLangID()]]
except KeyError:
    lang = all_lang["en_US"]
lang_raw = lang.copy()
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
plugins = {}
read_config()
del_list = []
for key, i in plugins.items():
    try:
        for j in i["files"]:
            if j["position"] == "init":
                try:
                    with open(os.path.join("plugin", key, j["file"]), encoding="utf-8") as f:
                        if j["wait"]:
                            exec(f.read(), globals(), locals())
                        else:
                            threading.Thread(name=i["name"], target=exec, args=(f.read(), globals(), locals())).start()
                except FileNotFoundError:
                    del_list.append(key)
    except Exception as err:
        tk.messagebox.showerror(i["name"], str(err))
        del_list.append(key)
for i in del_list:
    del plugins[i]
for key in (lang_raw.keys() - lang.keys()):
    lang[key] = lang_raw[key]
fontname = tk.StringVar(value=font[0])
fontsize = tk.IntVar(value=font[1])

window.title(lang["title"])
window.geometry('400x500')
window.iconbitmap(lang["ico"])
if len(sys.argv) > 1:
    open_file(sys.argv[1])
else:
    file_url = ""

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
menubar.add_cascade(label=lang["file"][0], menu=filemenu, underline=lang["file"][1])
filemenu.add_command(label=lang["new"][0], command=make_new, underline=lang["new"][1], accelerator="Ctrl+N")
filemenu.add_command(label=lang["open"][0], command=open_file, underline=lang["open"][1], accelerator="Ctrl+O")
filemenu.add_command(label=lang["save"][0], command=save, underline=lang["save"][1], accelerator="Ctrl+S")
filemenu.add_command(label=lang["save_as"][0], command=save_as, underline=lang["save_as"][1],
                     accelerator="Ctrl+Shift+S")
filemenu.add_separator()
filemenu.add_command(label=lang["print"][0], command=send_printer, underline=lang["print"][1], accelerator="Ctrl+P")
filemenu.add_separator()
filemenu.add_command(label=lang["plugin"][0], command=plugin, underline=lang["plugin"][1])
filemenu.add_separator()
filemenu.add_command(label=lang["exit"][0], command=exit_window, underline=lang["exit"][1])
editmenu = tk.Menu(menubar, tearoff=0)
editmenu.add_command(label=lang["undo"][0], command=lambda: e.edit_undo(), underline=lang["undo"][1],
                     accelerator="Ctrl+Z")
editmenu.add_command(label=lang["redo"][0], command=lambda: e.edit_redo(), underline=lang["redo"][1],
                     accelerator="Ctrl+Shift+Z")
editmenu.add_separator()
editmenu.add_command(label=lang["cut"][0], command=lambda: e.event_generate("<<Cut>>"), underline=lang["cut"][1],
                     accelerator="Ctrl+X")
editmenu.add_command(label=lang["copy"][0], command=lambda: e.event_generate("<<Copy>>"), underline=lang["copy"][1],
                     accelerator="Ctrl+C")
editmenu.add_command(label=lang["paste"][0], command=lambda: e.event_generate("<<Paste>>"), underline=lang["paste"][1],
                     accelerator="Ctrl+V")
editmenu.add_command(label=lang["del"][0], command=lambda: e.delete(tk.SEL_FIRST, tk.SEL_LAST),
                     underline=lang["del"][1], accelerator="Del")
editmenu.add_command(label=lang["sel_all"][0], command=lambda: e.tag_add("sel", "0.0", "end"),
                     underline=lang["sel_all"][1], accelerator="Ctrl+A")
editmenu.add_separator()
editmenu.add_command(label=lang["find"][0], command=lambda: find_str(), underline=lang["find"][1], accelerator="Ctrl+F")
editmenu.add_command(label=lang["replace"][0], command=lambda: replace_str(), underline=lang["replace"][1],
                     accelerator="Ctrl+H")
menubar.add_cascade(label=lang["edit"][0], menu=editmenu, underline=lang["edit"][1])
contextmenu = tk.Menu(window, tearoff=0)
contextmenu.add_command(label=lang["undo"][0], command=lambda: e.edit_undo(), underline=lang["undo"][1],
                        accelerator="Ctrl+Z")
contextmenu.add_command(label=lang["redo"][0], command=lambda: e.edit_redo(), underline=lang["redo"][1],
                        accelerator="Ctrl+Shift+Z")
contextmenu.add_separator()
contextmenu.add_command(label=lang["cut"][0], command=lambda: e.event_generate("<<Cut>>"), underline=lang["cut"][1],
                        accelerator="Ctrl+X")
contextmenu.add_command(label=lang["copy"][0], command=lambda: e.event_generate("<<Copy>>"), underline=lang["copy"][1],
                        accelerator="Ctrl+C")
contextmenu.add_command(label=lang["paste"][0], command=lambda: e.event_generate("<<Paste>>"),
                        underline=lang["paste"][1], accelerator="Ctrl+V")
contextmenu.add_command(label=lang["del"][0], command=lambda: e.delete(tk.SEL_FIRST, tk.SEL_LAST),
                        underline=lang["del"][1], accelerator="Del")
contextmenu.add_command(label=lang["sel_all"][0], command=lambda: e.tag_add("sel", "0.0", "end"),
                        underline=lang["sel_all"][1], accelerator="Ctrl+A")
contextmenu.add_separator()
contextmenu.add_command(label=lang["file_info"][0], underline=lang["file_info"][1],
                        command=lambda: tk.messagebox.showinfo(file_url, "{}:{}\n{}:{}\n{}:{}".format(
                            lang["file_infos"][0], file_coding, lang["file_infos"][1], len(e.get("0.0", "end")[:-1]),
                            lang["file_infos"][2], get_size())))
viewmenu = tk.Menu(menubar, tearoff=0)
viewmenu.add_command(label=lang["font"][0], command=font_settings, underline=lang["font"][1])
viewmenu.add_separator()
viewmenu.add_checkbutton(label=lang["wrap"][0], underline=lang["wrap"][1], variable=wrap, command=wrap_)
viewmenu.add_command(label=lang["file_info"][0], underline=lang["file_info"][1],
                     command=lambda: tk.messagebox.showinfo(file_url, "{}:{}\n{}:{}\n{}:{}".format(
                         lang["file_infos"][0], file_coding, lang["file_infos"][1], len(e.get("0.0", "end")[:-1]),
                         lang["file_infos"][2], get_size())))
viewmenu.add_separator()
viewmenu.add_checkbutton(label=lang["topmost"][0], underline=lang["topmost"][1], command=topmost, variable=top)
menubar.add_cascade(label=lang["view"][0], menu=viewmenu, underline=lang["view"][1])
encodingmenu = tk.Menu(menubar, tearoff=0)
encodingmenu.add_radiobutton(label=lang["encoding_auto"][0], underline=lang["encoding_auto"][1], variable=encoding,
                             value="auto")
for i in encodings:
    encodingmenu.add_radiobutton(label=i, variable=encoding, value=i)
encodingmenu.add_separator()
encodingmenu.add_checkbutton(label=lang["ignore"][0], variable=ignore, underline=lang["ignore"][1])
encodingmenu.add_checkbutton(label=lang["bin"][0], variable=b, underline=lang["bin"][1], command=bin_mode)
menubar.add_cascade(label=lang["encoding"][0], menu=encodingmenu, underline=lang["encoding"][1])
infomenu = tk.Menu(menubar, tearoff=0)
infomenu.add_command(label=lang["info"][0],
                     command=lambda: tk.messagebox.showinfo(lang["title"], "v{} {}".format(version, update_date)),
                     underline=lang["info"][1])
infomenu.add_command(label=lang["copyright"][0],
                     command=lambda: tk.messagebox.showinfo(lang["title"],
                                                            lang["copyright_info"].format(
                                                                time.localtime(time.time())[0])),
                     underline=lang["copyright"][1])
menubar.add_cascade(label=lang["help"][0], menu=infomenu, underline=lang["help"][1])

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
for key, i in plugins.items():
    try:
        for j in i["files"]:
            if j["position"] == "main":
                try:
                    with open(os.path.join("plugin", key, j["file"]), encoding="utf-8") as f:
                        if j["wait"]:
                            exec(f.read(), globals(), locals())
                        else:
                            threading.Thread(name=i["name"], target=exec, args=(f.read(), globals(), locals())).start()
                except FileNotFoundError:
                    del_list.append(key)
    except Exception as err:
        tk.messagebox.showerror(i["name"], str(err))
        del_list.append(key)
for i in del_list:
    del plugins[i]
window.mainloop()
