#!/usr/bin/env python3
"""
Universal Course/Playlist GUI Downloader (yt-dlp + tkinter)

- Works for any yt-dlp supported site (LinkedIn Learning, Udemy, YouTube, Vimeo,
  SoundCloud/Bandcamp, etc.). DRM-protected platforms won't work.
- Paste a URL and start. Subtitles saved as separate files when available.
- Cookies: choose a cookies.txt (Netscape format). Keep per-site cookies if you want.
- Shows per-file and overall progress, live speed, ETA, and remaining items.
- Progress bars styled green.
"""

import threading
import queue
from pathlib import Path
from tkinter import Tk, StringVar, filedialog, END, DISABLED, NORMAL
from tkinter import ttk
from yt_dlp import YoutubeDL

SCRIPT_DIR = Path(__file__).parent.resolve()

def sizeof_fmt(num, suffix="B"):
    try:
        num = float(num or 0)
    except Exception:
        return "0 B/s"
    for unit in ["","K","M","G","T","P","E","Z"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f} {unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f} Y{suffix}"

def secs_fmt(s):
    try:
        s = float(s)
    except Exception:
        return "--:--"
    if s is None or s == 0 or s == float("inf"):
        return "--:--"
    m, s = divmod(int(s), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"

SITE_OPTIONS = [
    "Auto-detect (Any site)",
    "LinkedIn Learning",
    "Udemy",
    "YouTube / Vimeo",
    "SoundCloud / Bandcamp",
]

class DownloaderGUI:
    def __init__(self, master: Tk):
        self.master = master
        master.title("Universal GUI Downloader (yt-dlp)")
        master.geometry("820x560")
        master.minsize(780, 520)

        # Theming + green bars
        style = ttk.Style(master)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("green.Horizontal.TProgressbar",
                        troughcolor="#e5e7eb",  # light gray
                        bordercolor="#e5e7eb",
                        background="#22c55e",   # green-500
                        lightcolor="#22c55e",
                        darkcolor="#22c55e")
        style.configure("TButton", padding=6)

        # State vars
        self.url_var = StringVar()
        self.site_var = StringVar(value=SITE_OPTIONS[0])
        self.cookies_var = StringVar(value=str(SCRIPT_DIR / "cookies.txt"))
        self.outdir_var = StringVar(value=str(SCRIPT_DIR))
        self.status_var = StringVar(value="Idle")
        self.file_title_var = StringVar(value="—")
        self.file_pct_var = StringVar(value="0%")
        self.overall_pct_var = StringVar(value="0%")
        self.speed_var = StringVar(value="0 B/s")
        self.eta_var = StringVar(value="--:--")
        self.remain_var = StringVar(value="0")
        self.total_items = 0
        self.stop_flag = False

        pad = {"padx": 8, "pady": 6}

        # URL row
        ttk.Label(master, text="Course / Playlist URL:").grid(row=0, column=0, sticky="w", **pad)
        self.url_entry = ttk.Entry(master, textvariable=self.url_var, width=72)
        self.url_entry.grid(row=0, column=1, columnspan=2, sticky="we", **pad)
        ttk.Button(master, text="Paste", command=self._paste_url).grid(row=0, column=3, sticky="we", **pad)

        # Site + Cookies
        ttk.Label(master, text="Site type:").grid(row=1, column=0, sticky="w", **pad)
        self.site_combo = ttk.Combobox(master, values=SITE_OPTIONS, textvariable=self.site_var, state="readonly")
        self.site_combo.grid(row=1, column=1, sticky="we", **pad)
        ttk.Label(master, text="cookies.txt:").grid(row=1, column=2, sticky="e", **pad)
        self.cookies_entry = ttk.Entry(master, textvariable=self.cookies_var, width=30)
        self.cookies_entry.grid(row=1, column=3, sticky="we", **pad)
        ttk.Button(master, text="Browse…", command=self._browse_cookies).grid(row=1, column=4, sticky="we", **pad)

        # Output dir
        ttk.Label(master, text="Output folder:").grid(row=2, column=0, sticky="w", **pad)
        self.outdir_entry = ttk.Entry(master, textvariable=self.outdir_var)
        self.outdir_entry.grid(row=2, column=1, columnspan=3, sticky="we", **pad)
        ttk.Button(master, text="Choose…", command=self._browse_outdir).grid(row=2, column=4, sticky="we", **pad)

        # Buttons
        self.btn_start = ttk.Button(master, text="Start Download", command=self.start_download_thread)
        self.btn_start.grid(row=3, column=1, sticky="we", **pad)
        self.btn_cancel = ttk.Button(master, text="Cancel", command=self.cancel_download, state=DISABLED)
        self.btn_cancel.grid(row=3, column=2, sticky="we", **pad)

        # Current file title
        ttk.Label(master, text="Current item:").grid(row=4, column=0, sticky="w", **pad)
        ttk.Label(master, textvariable=self.file_title_var, anchor="w").grid(row=4, column=1, columnspan=4, sticky="we", **pad)

        # File progress (green)
        ttk.Label(master, text="File progress:").grid(row=5, column=0, sticky="w", **pad)
        self.pb_file = ttk.Progressbar(master, orient="horizontal", mode="determinate", maximum=100, style="green.Horizontal.TProgressbar")
        self.pb_file.grid(row=5, column=1, columnspan=3, sticky="we", **pad)
        ttk.Label(master, textvariable=self.file_pct_var, width=7).grid(row=5, column=4, sticky="e", **pad)

        # Overall progress (green)
        ttk.Label(master, text="Overall progress:").grid(row=6, column=0, sticky="w", **pad)
        self.pb_overall = ttk.Progressbar(master, orient="horizontal", mode="determinate", maximum=100, style="green.Horizontal.TProgressbar")
        self.pb_overall.grid(row=6, column=1, columnspan=3, sticky="we", **pad)
        ttk.Label(master, textvariable=self.overall_pct_var, width=7).grid(row=6, column=4, sticky="e", **pad)

        # Speed / ETA / Remaining
        ttk.Label(master, text="Speed:").grid(row=7, column=0, sticky="w", **pad)
        ttk.Label(master, textvariable=self.speed_var).grid(row=7, column=1, sticky="w", **pad)
        ttk.Label(master, text="ETA:").grid(row=7, column=2, sticky="e", **pad)
        ttk.Label(master, textvariable=self.eta_var).grid(row=7, column=3, sticky="w", **pad)
        ttk.Label(master, text="Remaining items:").grid(row=7, column=4, sticky="e", **pad)
        ttk.Label(master, textvariable=self.remain_var, width=6).grid(row=7, column=5, sticky="w", **pad)

        # Status + Log
        ttk.Label(master, text="Status:").grid(row=8, column=0, sticky="w", **pad)
        self.lbl_status = ttk.Label(master, textvariable=self.status_var)
        self.lbl_status.grid(row=8, column=1, columnspan=5, sticky="we", **pad)

        self.log = ttk.Treeview(master, columns=("msg",), show="headings", height=10)
        self.log.heading("msg", text="Log")
        self.log.grid(row=9, column=0, columnspan=6, sticky="nsew", padx=8, pady=(0,8))

        # Grid weights
        for c in (1,2,3):
            master.grid_columnconfigure(c, weight=1)
        master.grid_rowconfigure(9, weight=1)

        self.q = queue.Queue()
        master.after(100, self._poll_queue)

    # --- UI helpers ---
    def _paste_url(self):
        try:
            import tkinter
            t = tkinter.Tk()
            t.withdraw()
            data = t.clipboard_get()
            t.destroy()
            if data:
                self.url_var.set(data.strip())
        except Exception:
            pass

    def _browse_cookies(self):
        path = filedialog.askopenfilename(title="Select cookies.txt", filetypes=[("Text files","*.txt"), ("All files","*.*")])
        if path:
            self.cookies_var.set(path)

    def _browse_outdir(self):
        path = filedialog.askdirectory(title="Choose output folder", initialdir=self.outdir_var.get() or str(SCRIPT_DIR))
        if path:
            self.outdir_var.set(path)

    # --- Orchestration ---
    def start_download_thread(self):
        url = self.url_var.get().strip().strip('"').strip("'")
        if not url:
            self._log("Please paste a URL.")
            self.status_var.set("Need URL")
            return
        self.stop_flag = False
        self.btn_start.config(state=DISABLED)
        self.btn_cancel.config(state=NORMAL)
        self.status_var.set("Analyzing…")
        self._log(f"Starting for site: {self.site_var.get()}")
        t = threading.Thread(target=self._worker, args=(url,), daemon=True)
        t.start()

    def cancel_download(self):
        self.stop_flag = True
        self._log("Cancel requested. Finishing current fragment…")
        self.status_var.set("Cancelling…")

    def _poll_queue(self):
        try:
            while True:
                msg = self.q.get_nowait()
                kind = msg.get("kind")
                if kind == "status":
                    self.status_var.set(msg.get("text",""))
                elif kind == "log":
                    self._log(msg.get("text",""))
                elif kind == "meta":
                    self.total_items = msg.get("total", 0)
                    self.remain_var.set(str(self.total_items))
                    self.pb_overall["value"] = 0
                    self.overall_pct_var.set("0%")
                elif kind == "progress":
                    file_pct = int(msg.get("file_frac",0)*100)
                    overall_pct = int(msg.get("overall_frac",0)*100)
                    self.pb_file["value"] = file_pct
                    self.file_pct_var.set(f"{file_pct}%")
                    self.pb_overall["value"] = overall_pct
                    self.overall_pct_var.set(f"{overall_pct}%")
                    self.file_title_var.set(msg.get("title","—")[:90])
                    self.speed_var.set(msg.get("speed","0 B/s"))
                    self.eta_var.set(msg.get("eta","--:--"))
                    self.remain_var.set(str(msg.get("remaining", 0)))
                elif kind == "done":
                    self.btn_start.config(state=NORMAL)
                    self.btn_cancel.config(state=DISABLED)
                    if msg.get("cancelled"):
                        self.status_var.set(msg.get("text","Cancelled."))
                    else:
                        self.status_var.set(msg.get("text","Done."))
        except queue.Empty:
            pass
        self.master.after(100, self._poll_queue)

    def _log(self, text: str):
        self.log.insert("", END, values=(text,))
        children = self.log.get_children()
        if children:
            self.log.see(children[-1])

    # --- yt-dlp integration ---
    def _ydl_opts_common(self, outdir: Path, cookies: Path | None):
        opts = {
            "outtmpl": str(outdir / "%(playlist_title)s/%(chapter_number)s - %(chapter)s/%(playlist_index)s - %(title)s.%(ext)s"),
            "windowsfilenames": True,
            "download_archive": str(outdir / "ll-archive.txt"),
            "overwrites": False,
            "continue_dl": True,
            "writesubtitles": True,
            "allsubtitles": True,
            "subtitlesformat": "srt/best",
            "ignoreerrors": True,
            "retries": 100,
            "fragment_retries": 100,
            "concurrent_fragment_downloads": 4,
            "skip_unavailable_fragments": True,
            "noplaylist": False,
            "cookiefile": str(cookies) if cookies and Path(cookies).exists() else None,
            "prefer_ffmpeg": False,
            "quiet": True,
            "no_warnings": False,
            "http_headers": {"User-Agent": "Mozilla/5.0"},
        }
        return opts

    def _extract_entries(self, url, base_opts):
        with YoutubeDL({**base_opts, "quiet": True}) as ydl:
            info = ydl.extract_info(url, download=False)
        if not info:
            raise RuntimeError("Failed to extract metadata; check the URL or cookies.")
        if info.get("_type") == "playlist" and info.get("entries"):
            entries = [e for e in info["entries"] if e]
        else:
            entries = [info]
        return entries

    def _make_hook(self, idx, total, title):
        def hook(d):
            if self.stop_flag:
                raise KeyboardInterrupt("User cancelled.")
            status = d.get("status")
            if status == "downloading":
                downloaded = d.get("downloaded_bytes") or 0
                total_bytes = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                if total_bytes:
                    file_frac = downloaded / total_bytes
                else:
                    fi = d.get("fragment_index") or 0
                    fc = d.get("fragment_count") or 0
                    file_frac = (fi / fc) if fc else 0.0
                overall_frac = ((idx - 1) + file_frac) / total if total else file_frac
                speed = d.get("speed")
                eta = d.get("eta")
                self.q.put({
                    "kind": "progress",
                    "title": title,
                    "file_frac": max(0.0, min(1.0, file_frac)),
                    "overall_frac": max(0.0, min(1.0, overall_frac)),
                    "speed": sizeof_fmt(speed, "/s") if speed else "0 B/s",
                    "eta": secs_fmt(eta),
                    "remaining": max(0, total - idx),
                })
            elif status == "finished":
                overall_frac = (idx / total) if total else 1.0
                self.q.put({
                    "kind": "progress",
                    "title": title,
                    "file_frac": 1.0,
                    "overall_frac": overall_frac,
                    "speed": "—",
                    "eta": "00:00",
                    "remaining": max(0, total - idx),
                })
        return hook

    def _worker(self, url: str):
        cancelled = False
        try:
            outdir = Path(self.outdir_var.get()).expanduser().resolve()
            outdir.mkdir(parents=True, exist_ok=True)
            cookies_path = Path(self.cookies_var.get().strip()) if self.cookies_var.get().strip() else None

            opts = self._ydl_opts_common(outdir, cookies_path)

            self.q.put({"kind": "status", "text": "Analyzing…"})
            entries = self._extract_entries(url, opts)
            total = len(entries)
            self.q.put({"kind": "meta", "total": total})
            self.q.put({"kind": "status", "text": f"Found {total} item(s). Downloading… (Remaining {total})"})
            completed = 0

            for idx, entry in enumerate(entries, 1):
                if self.stop_flag:
                    cancelled = True
                    break
                if not entry:
                    continue
                title = entry.get("title") or entry.get("id") or f"item {idx}"
                self.q.put({"kind": "log", "text": f"[{idx}/{total}] {title}"})
                hook = self._make_hook(idx, total, title)
                run_opts = dict(opts)
                run_opts["progress_hooks"] = [hook]
                with YoutubeDL(run_opts) as ydl:
                    try:
                        url_to_dl = entry.get("webpage_url") or entry.get("url") or url
                        ydl.download([url_to_dl])
                        completed += 1
                        rem = max(0, total - idx)
                        self.q.put({"kind": "status", "text": f"Downloading… {completed}/{total} (Remaining {rem})"})
                    except KeyboardInterrupt:
                        cancelled = True
                        break
                    except Exception as e:
                        self.q.put({"kind": "log", "text": f"ERROR: {e}"})
                        continue

            if cancelled:
                self.q.put({"kind": "done", "cancelled": True, "text": f"Cancelled. {completed}/{total} done."})
            else:
                self.q.put({"kind": "done", "cancelled": False, "text": f"Done. {completed}/{total} completed."})
        except Exception as exc:
            self.q.put({"kind": "log", "text": f"FATAL: {exc}"})
            self.q.put({"kind": "done", "cancelled": True, "text": "Failed."})
