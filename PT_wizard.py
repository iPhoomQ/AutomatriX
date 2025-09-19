
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python Action Wizard — a Tkinter step-by-step GUI to run common Python-powered tasks.
Extensible via a simple Action registry. Safe-ish defaults; no external internet access required.
Author: ChatGPT (GPT-5 Thinking)
"""

import os
import sys
import io
import re
import csv
import json
import math
import queue
import shutil
import zipfile
import threading
import subprocess
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

# Optional deps
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_OK = True
except Exception:
    PIL_OK = False

try:
    import requests
    REQUESTS_OK = True
except Exception:
    REQUESTS_OK = False

try:
    import moviepy.editor as mpy
    MOVIEPY_OK = True
except Exception:
    MOVIEPY_OK = False

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    MPL_OK = True
except Exception:
    MPL_OK = False

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

APP_TITLE = "Python Action Wizard"
APP_VERSION = "1.0.0"

# -----------------------------
# Action registry
# -----------------------------

@dataclass
class Param:
    key: str
    label: str
    kind: str = "str"   # str, int, float, bool, file, folder, text, choice
    required: bool = False
    default: Any = None
    choices: Optional[List[str]] = None
    help: str = ""

@dataclass
class Action:
    name: str
    category: str
    description: str
    params: List[Param]
    runner: Callable[[Dict[str, Any], "WizardApp"], Dict[str, Any]]
    out_hint: str = ""  # e.g., "Text", "File path", "Image path"


REGISTRY: Dict[str, Action] = {}
CATEGORIES: Dict[str, List[str]] = {}

def register(action: Action):
    REGISTRY[action.name] = action
    CATEGORIES.setdefault(action.category, []).append(action.name)

# -----------------------------
# Helpers
# -----------------------------

def safe_open(path, mode="w", encoding="utf-8"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return open(path, mode, encoding=encoding)

def write_text_file(path: str, text: str) -> str:
    with safe_open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path

def to_bool(v: Any) -> bool:
    if isinstance(v, bool): return v
    s = str(v).strip().lower()
    return s in ("1","true","yes","y","on")

def inform(msg: str):
    print(msg, file=sys.stderr)

# -----------------------------
# Built-in actions
# -----------------------------

# ---- TEXT / STRINGS ----
def run_word_count(args, app):
    text = args["text"]
    chars = len(text)
    words = len(re.findall(r"\b\w+\b", text, flags=re.UNICODE))
    lines = text.count("\n") + (1 if text else 0)
    out = f"Chars: {chars}\nWords: {words}\nLines: {lines}\n"
    return {"text": out, "preview": out}

register(Action(
    name="Word / Line Counter",
    category="Text",
    description="Count characters, words, and lines in given text.",
    params=[Param("text","Input Text","text",True,help="Paste or type text here.")],
    runner=run_word_count,
    out_hint="Text summary"
))

def run_regex_find(args, app):
    text = args["text"]
    pattern = args["pattern"]
    flags = 0
    if to_bool(args.get("ignore_case")): flags |= re.IGNORECASE
    if to_bool(args.get("multiline")): flags |= re.MULTILINE
    matches = list(re.finditer(pattern, text, flags))
    lines = [f"{i+1}. {m.group(0)} @ {m.start()}..{m.end()}" for i,m in enumerate(matches)]
    out = "Matches:\n" + ("\n".join(lines) if lines else "(none)")
    return {"text": out, "preview": out}

register(Action(
    name="Regex Find",
    category="Text",
    description="Find regex matches in text with optional flags.",
    params=[
        Param("text","Input Text","text",True),
        Param("pattern","Regex Pattern","str",True),
        Param("ignore_case","Ignore Case","bool",False,False),
        Param("multiline","Multiline (^$)","bool",False,False),
    ],
    runner=run_regex_find,
    out_hint="Text"
))

def run_text_transform(args, app):
    text = args["text"]
    mode = args["mode"]
    if mode == "upper": out = text.upper()
    elif mode == "lower": out = text.lower()
    elif mode == "title": out = text.title()
    elif mode == "swapcase": out = text.swapcase()
    else: out = text
    return {"text": out, "preview": out[:500] + ("..." if len(out)>500 else "")}

register(Action(
    name="Text Transform",
    category="Text",
    description="Upper/Lower/Title/Swapcase transformations.",
    params=[
        Param("text","Input Text","text",True),
        Param("mode","Mode","choice",True,"lower",["lower","upper","title","swapcase"]),
    ],
    runner=run_text_transform,
    out_hint="Transformed text"
))

# ---- FILES ----
def run_list_dir(args, app):
    path = args["folder"]
    if not os.path.isdir(path):
        raise ValueError("Folder does not exist")
    entries = sorted(os.listdir(path))
    out = "\n".join(entries)
    return {"text": out, "preview": out[:1000]}

register(Action(
    name="List Directory",
    category="Files",
    description="List files/folders in a directory.",
    params=[Param("folder","Folder","folder",True)],
    runner=run_list_dir,
    out_hint="Text list"
))

def run_zip_folder(args, app):
    folder = args["folder"]
    outpath = args["output_zip"] or os.path.join(os.path.dirname(folder), os.path.basename(folder) + ".zip")
    with zipfile.ZipFile(outpath, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(folder):
            for fn in files:
                full = os.path.join(root, fn)
                rel = os.path.relpath(full, folder)
                z.write(full, arcname=rel)
    return {"file": outpath, "preview": f"Created ZIP: {outpath}"}

register(Action(
    name="Zip Folder",
    category="Files",
    description="Zip a folder recursively into .zip",
    params=[
        Param("folder","Folder to Zip","folder",True),
        Param("output_zip","Output .zip path","str",False,"")
    ],
    runner=run_zip_folder,
    out_hint="File path (.zip)"
))

# ---- IMAGES ----
def run_image_resize(args, app):
    if not PIL_OK:
        raise RuntimeError("Pillow (PIL) not installed. pip install pillow")
    inp = args["input_image"]
    w = int(args["width"])
    h = int(args["height"])
    outpath = args["output_image"] or os.path.splitext(inp)[0] + f"_{w}x{h}.png"
    im = Image.open(inp)
    im = im.resize((w,h))
    im.save(outpath)
    return {"file": outpath, "preview": f"Saved: {outpath}"}

register(Action(
    name="Image Resize (PIL)",
    category="Images",
    description="Resize an image to a specific width/height.",
    params=[
        Param("input_image","Input Image","file",True),
        Param("width","Width","int",True,512),
        Param("height","Height","int",True,512),
        Param("output_image","Output Image Path","str",False,""),
    ],
    runner=run_image_resize,
    out_hint="Image path"
))

def run_add_text(args, app):
    if not PIL_OK:
        raise RuntimeError("Pillow (PIL) not installed. pip install pillow")
    inp = args["input_image"]
    text = args["text"]
    x = int(args["x"]); y = int(args["y"])
    size = int(args["font_size"])
    outpath = args["output_image"] or os.path.splitext(inp)[0] + "_text.png"
    im = Image.open(inp).convert("RGBA")
    draw = ImageDraw.Draw(im)
    try:
        font = ImageFont.truetype(args.get("font_path") or "", size)
    except Exception:
        font = ImageFont.load_default()
    draw.text((x,y), text, font=font, fill=(255,255,255,255))
    im.save(outpath)
    return {"file": outpath, "preview": f"Saved: {outpath}"}

register(Action(
    name="Image Add Text (PIL)",
    category="Images",
    description="Draw text onto an image at x,y.",
    params=[
        Param("input_image","Input Image","file",True),
        Param("text","Text","str",True),
        Param("x","X","int",True,10),
        Param("y","Y","int",True,10),
        Param("font_size","Font Size","int",True,24),
        Param("font_path","Font Path (.ttf)","str",False,""),
        Param("output_image","Output Image Path","str",False,""),
    ],
    runner=run_add_text,
    out_hint="Image path"
))

# ---- VIDEO ----
def run_video_info(args, app):
    if not MOVIEPY_OK:
        raise RuntimeError("moviepy not installed. pip install moviepy")
    path = args["input_video"]
    clip = mpy.VideoFileClip(path)
    info = {
        "duration_s": clip.duration,
        "fps": clip.fps,
        "size": clip.size,
        "audio_fps": getattr(clip.audio, "fps", None) if clip.audio else None,
    }
    clip.close()
    out = json.dumps(info, indent=2)
    return {"text": out, "preview": out}

register(Action(
    name="Video Info (moviepy)",
    category="Video",
    description="Quick video metadata: duration, fps, size.",
    params=[Param("input_video","Input Video","file",True)],
    runner=run_video_info,
    out_hint="JSON"
))

def run_extract_audio(args, app):
    if not MOVIEPY_OK:
        raise RuntimeError("moviepy not installed. pip install moviepy")
    path = args["input_video"]
    out_audio = args["output_audio"] or os.path.splitext(path)[0] + ".mp3"
    clip = mpy.VideoFileClip(path)
    clip.audio.write_audiofile(out_audio, verbose=False, logger=None)
    clip.close()
    return {"file": out_audio, "preview": f"Saved: {out_audio}"}

register(Action(
    name="Extract Audio (moviepy)",
    category="Video",
    description="Extract audio track to .mp3 via moviepy.",
    params=[
        Param("input_video","Input Video","file",True),
        Param("output_audio","Output Audio Path","str",False,""),
    ],
    runner=run_extract_audio,
    out_hint="Audio path"
))

# ---- WEB (local HTTP client) ----
def run_http_get(args, app):
    if not REQUESTS_OK:
        raise RuntimeError("requests not installed. pip install requests")
    url = args["url"]
    timeout = int(args.get("timeout", 10))
    r = requests.get(url, timeout=timeout)
    hdrs = "\n".join(f"{k}: {v}" for k,v in r.headers.items())
    head = f"Status: {r.status_code}\n{hdrs}\n\n"
    preview = (head + r.text[:2000]) if r.text else head + "(binary)"
    save_path = args.get("save_as") or ""
    saved = None
    if save_path:
        mode = "wb" if isinstance(r.content, (bytes, bytearray)) else "w"
        with open(save_path, "wb") as f:
            f.write(r.content)
        saved = save_path
    return {"text": head + r.text, "file": saved, "preview": preview}

register(Action(
    name="HTTP GET (requests)",
    category="Web",
    description="Fetch a URL and optionally save the response body.",
    params=[
        Param("url","URL","str",True,"https://example.com"),
        Param("timeout","Timeout (s)","int",False,10),
        Param("save_as","Save Body As (optional)","str",False,""),
    ],
    runner=run_http_get,
    out_hint="Response text or file"
))

# ---- DATA ----
def run_csv_head(args, app):
    path = args["csv_file"]
    n = int(args["rows"])
    buf = io.StringIO()
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            buf.write(",".join(row) + "\n")
            if i+1 >= n: break
    out = buf.getvalue()
    return {"text": out, "preview": out}

register(Action(
    name="CSV Head",
    category="Data",
    description="Preview first N rows of a CSV.",
    params=[
        Param("csv_file","CSV File","file",True),
        Param("rows","Rows","int",True,10),
    ],
    runner=run_csv_head,
    out_hint="Text"
))

def run_plot_numbers(args, app):
    if not MPL_OK:
        raise RuntimeError("matplotlib not installed. pip install matplotlib")
    nums_s = args["numbers"].strip()
    nums = []
    for token in re.split(r"[\s,;]+", nums_s):
        if token:
            nums.append(float(token))
    outpng = args["output_image"] or os.path.join(os.getcwd(), "plot.png")
    plt.figure()
    plt.plot(nums)
    plt.xlabel("Index")
    plt.ylabel("Value")
    plt.title("Line Plot")
    plt.savefig(outpng, bbox_inches="tight")
    plt.close()
    return {"file": outpng, "preview": f"Saved: {outpng}"}

register(Action(
    name="Plot Numbers (matplotlib)",
    category="Data",
    description="Simple line plot from numbers separated by space/comma/semicolon.",
    params=[
        Param("numbers","Numbers","text",True,"1 2 3 5 8 13 21"),
        Param("output_image","Output Image Path","str",False,""),
    ],
    runner=run_plot_numbers,
    out_hint="Image path"
))

# ---- SYSTEM ----
def run_shell_command(args, app):
    cmd = args["command"]
    timeout = int(args.get("timeout", 30))
    proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    out = f"$ {cmd}\n\n[stdout]\n{proc.stdout}\n[stderr]\n{proc.stderr}\n(exit {proc.returncode})"
    return {"text": out, "preview": out[-1000:]}

register(Action(
    name="Run Shell Command",
    category="System",
    description="Run a shell command (use carefully).",
    params=[
        Param("command","Command","str",True,"echo Hello"),
        Param("timeout","Timeout (s)","int",False,30),
    ],
    runner=run_shell_command,
    out_hint="Console text"
))

# -----------------------------
# GUI
# -----------------------------

class WizardApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_TITLE} v{APP_VERSION}")
        self.geometry("980x700")
        self.minsize(900,600)
        self.selected_action_name: Optional[str] = None
        self.param_vars: Dict[str, Any] = {}
        self.output: Dict[str, Any] = {}
        self.task_thread: Optional[threading.Thread] = None
        self.task_queue: "queue.Queue[Tuple[str, Any]]" = queue.Queue()
        self._build_ui()
        self.after(100, self._poll_queue)

    # ----- UI builders -----
    def _build_ui(self):
        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        self.container = ttk.Notebook(self)
        self.container.pack(fill="both", expand=True)

        self.page1 = ttk.Frame(self.container)
        self.page2 = ttk.Frame(self.container)
        self.page3 = ttk.Frame(self.container)

        self.container.add(self.page1, text="1) Choose Action")
        self.container.add(self.page2, text="2) Configure")
        self.container.add(self.page3, text="3) Run & Output")

        self._build_page1()
        self._build_page2()
        self._build_page3()

    def _build_page1(self):
        # Left: categories; Right: actions list + description
        left = ttk.Frame(self.page1, padding=10)
        left.pack(side="left", fill="y")
        right = ttk.Frame(self.page1, padding=10)
        right.pack(side="left", fill="both", expand=True)

        ttk.Label(left, text="Categories", font=("TkDefaultFont", 12, "bold")).pack(anchor="w")
        self.cat_list = tk.Listbox(left, height=20, exportselection=False)
        for cat in sorted(CATEGORIES.keys()):
            self.cat_list.insert("end", cat)
        self.cat_list.pack(fill="y", expand=True)
        self.cat_list.bind("<<ListboxSelect>>", self._on_cat_select)

        ttk.Label(right, text="Actions", font=("TkDefaultFont", 12, "bold")).pack(anchor="w")
        self.action_list = tk.Listbox(right, height=15, exportselection=False)
        self.action_list.pack(fill="x")
        self.action_list.bind("<<ListboxSelect>>", self._on_action_select)

        self.action_desc = tk.Text(right, height=10, wrap="word")
        self.action_desc.pack(fill="both", expand=True)
        self.action_desc.insert("1.0", "Select a category on the left, then an action.")
        self.action_desc.config(state="disabled")

        bottom = ttk.Frame(self.page1, padding=10)
        bottom.pack(side="bottom", fill="x")
        self.btn_next1 = ttk.Button(bottom, text="Next ▶", command=self.goto_page2, state="disabled")
        self.btn_next1.pack(side="right")

    def _build_page2(self):
        container = ttk.Frame(self.page2, padding=10)
        container.pack(fill="both", expand=True)

        self.param_frame = ttk.Frame(container)
        self.param_frame.pack(fill="both", expand=True)

        nav = ttk.Frame(container)
        nav.pack(fill="x")
        self.btn_back2 = ttk.Button(nav, text="◀ Back", command=lambda: self.container.select(self.page1))
        self.btn_back2.pack(side="left")
        self.btn_next2 = ttk.Button(nav, text="Next ▶", command=self.goto_page3)
        self.btn_next2.pack(side="right")

    def _build_page3(self):
        container = ttk.Frame(self.page3, padding=10)
        container.pack(fill="both", expand=True)

        top = ttk.Frame(container)
        top.pack(fill="x")
        self.btn_run = ttk.Button(top, text="▶ Run", command=self.run_action)
        self.btn_run.pack(side="left")

        self.btn_save_text = ttk.Button(top, text="Save Text Output...", command=self.save_text_output)
        self.btn_save_text.pack(side="left", padx=5)
        self.btn_open_file = ttk.Button(top, text="Open Output File", command=self.open_output_file, state="disabled")
        self.btn_open_file.pack(side="left", padx=5)

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(top, textvariable=self.status_var).pack(side="right")

        self.output_text = tk.Text(container, wrap="word")
        self.output_text.pack(fill="both", expand=True)

        nav = ttk.Frame(container)
        nav.pack(fill="x")
        self.btn_back3 = ttk.Button(nav, text="◀ Back", command=lambda: self.container.select(self.page2))
        self.btn_back3.pack(side="left")

    # ----- Events -----
    def _on_cat_select(self, event=None):
        sel = self.cat_list.curselection()
        self.action_list.delete(0, "end")
        if not sel: return
        cat = self.cat_list.get(sel[0])
        for name in sorted(CATEGORIES.get(cat, [])):
            self.action_list.insert("end", name)
        self._set_desc("")

    def _on_action_select(self, event=None):
        sel = self.action_list.curselection()
        if not sel:
            self.selected_action_name = None
            self.btn_next1.config(state="disabled")
            self._set_desc("")
            return
        name = self.action_list.get(sel[0])
        self.selected_action_name = name
        self.btn_next1.config(state="normal")
        act = REGISTRY[name]
        self._set_desc(f"{act.name}\n\n{act.description}\n\nOutput: {act.out_hint}")

    def _set_desc(self, text: str):
        self.action_desc.config(state="normal")
        self.action_desc.delete("1.0", "end")
        self.action_desc.insert("1.0", text)
        self.action_desc.config(state="disabled")

    # ----- Navigation -----
    def goto_page2(self):
        if not self.selected_action_name:
            return
        self._render_params()
        self.container.select(self.page2)

    def goto_page3(self):
        self.output_text.delete("1.0", "end")
        self.status_var.set("Ready")
        self.btn_open_file.config(state="disabled")
        self.container.select(self.page3)

    # ----- Params rendering -----
    def _clear_frame(self, frame):
        for w in frame.winfo_children():
            w.destroy()

    def _render_params(self):
        self._clear_frame(self.param_frame)
        act = REGISTRY[self.selected_action_name]
        ttk.Label(self.param_frame, text=act.name, font=("TkDefaultFont", 13, "bold")).pack(anchor="w", pady=(0,8))

        form = ttk.Frame(self.param_frame)
        form.pack(fill="both", expand=True)

        self.param_vars = {}

        for i, p in enumerate(act.params):
            ttk.Label(form, text=p.label + (" *" if p.required else "")).grid(row=i, column=0, sticky="w", padx=4, pady=4)
            var = None
            entry = None

            if p.kind in ("str","int","float"):
                var = tk.StringVar(value="" if p.default is None else str(p.default))
                entry = ttk.Entry(form, textvariable=var, width=60)
                entry.grid(row=i, column=1, sticky="we", padx=4, pady=4)

            elif p.kind == "bool":
                var = tk.BooleanVar(value=bool(p.default))
                entry = ttk.Checkbutton(form, variable=var)
                entry.grid(row=i, column=1, sticky="w", padx=4, pady=4)

            elif p.kind == "text":
                var = tk.StringVar(value="" if p.default is None else str(p.default))
                txt = tk.Text(form, height=6, width=60, wrap="word")
                txt.insert("1.0", var.get())
                txt.grid(row=i, column=1, sticky="we", padx=4, pady=4)
                entry = txt

            elif p.kind == "choice":
                var = tk.StringVar(value=p.default if p.default is not None else (p.choices[0] if p.choices else ""))
                entry = ttk.Combobox(form, textvariable=var, values=p.choices or [], state="readonly", width=57)
                entry.grid(row=i, column=1, sticky="we", padx=4, pady=4)

            elif p.kind in ("file","folder"):
                var = tk.StringVar(value="" if p.default is None else str(p.default))
                rowf = ttk.Frame(form)
                rowf.grid(row=i, column=1, sticky="we", padx=4, pady=4)
                ent = ttk.Entry(rowf, textvariable=var, width=55)
                ent.pack(side="left", fill="x", expand=True)
                btn = ttk.Button(rowf, text="Browse…", command=(lambda v=var, k=p.kind: self._browse(v, k)))
                btn.pack(side="left", padx=4)
                entry = ent

            else:
                var = tk.StringVar(value="" if p.default is None else str(p.default))
                entry = ttk.Entry(form, textvariable=var, width=60)
                entry.grid(row=i, column=1, sticky="we", padx=4, pady=4)

            if p.help:
                ttk.Label(form, text=p.help, foreground="#666").grid(row=i, column=2, sticky="w", padx=4)

            self.param_vars[p.key] = (p, var, entry)

        form.columnconfigure(1, weight=1)

    def _browse(self, var: tk.StringVar, kind: str):
        if kind == "file":
            path = filedialog.askopenfilename()
        else:
            path = filedialog.askdirectory()
        if path:
            var.set(path)

    # ----- Run & Output -----
    def _collect_params(self) -> Dict[str, Any]:
        act = REGISTRY[self.selected_action_name]
        args = {}
        for key, (p, var, entry) in self.param_vars.items():
            if p.kind == "text":
                # pull from text widget content
                try:
                    val = entry.get("1.0", "end-1c")
                except Exception:
                    val = var.get()
            elif p.kind == "bool":
                val = bool(var.get())
            else:
                val = var.get()

            if p.required and (val is None or str(val).strip() == ""):
                raise ValueError(f"Missing required parameter: {p.label}")
            if p.kind == "int" and val != "":
                val = int(val)
            if p.kind == "float" and val != "":
                val = float(val)
            args[key] = val
        return args

    def run_action(self):
        if self.task_thread and self.task_thread.is_alive():
            messagebox.showinfo("Busy", "An action is already running.")
            return

        try:
            args = self._collect_params()
        except Exception as e:
            messagebox.showerror("Invalid input", str(e))
            return

        act = REGISTRY[self.selected_action_name]
        self.status_var.set("Running…")
        self.output_text.delete("1.0", "end")

        def worker():
            try:
                result = act.runner(args, self)
                self.task_queue.put(("ok", result))
            except Exception as e:
                self.task_queue.put(("err", str(e)))

        self.task_thread = threading.Thread(target=worker, daemon=True)
        self.task_thread.start()

    def _poll_queue(self):
        try:
            while True:
                kind, payload = self.task_queue.get_nowait()
                if kind == "ok":
                    self.output = payload or {}
                    preview = self.output.get("preview") or self.output.get("text") or "(no preview)"
                    self.output_text.insert("1.0", preview)
                    self.status_var.set("Done")
                    if self.output.get("file"):
                        self.btn_open_file.config(state="normal")
                else:
                    self.output = {}
                    self.output_text.insert("1.0", f"[Error]\n{payload}")
                    self.status_var.set("Error")
        except queue.Empty:
            pass
        self.after(100, self._poll_queue)

    def save_text_output(self):
        if not self.output or not self.output.get("text"):
            messagebox.showinfo("No text", "No text output available.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text","*.txt"),("All files","*.*")])
        if not path: return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.output["text"])
            messagebox.showinfo("Saved", f"Saved to {path}")
        except Exception as e:
            messagebox.showerror("Save failed", str(e))

    def open_output_file(self):
        f = self.output.get("file")
        if not f:
            messagebox.showinfo("No file", "No file output available.")
            return
        if sys.platform.startswith("darwin"):
            subprocess.call(["open", f])
        elif os.name == "nt":
            os.startfile(f)  # type: ignore[attr-defined]
        else:
            subprocess.call(["xdg-open", f])


def main():
    # Populate categories (ensure consistent order for listbox)
    if not CATEGORIES:
        for act in REGISTRY.values():
            CATEGORIES.setdefault(act.category, []).append(act.name)
    app = WizardApp()
    app.mainloop()

if __name__ == "__main__":
    main()
