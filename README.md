# 🎬 Universal Course & Playlist Downloader (GUI)

A simple **GUI wrapper for [yt-dlp](https://github.com/yt-dlp/yt-dlp)** built with **Tkinter**.
Download entire courses, playlists, or albums from supported sites (LinkedIn Learning, Udemy, YouTube, Vimeo, SoundCloud, Bandcamp, and many more).

✨ Features:

* 🖥️ Easy-to-use GUI (no command line required)
* 🌍 Works with **any yt-dlp supported site** (except DRM-protected)
* 📂 Smart folder structure for courses/playlists
* 📝 Subtitles downloaded separately (`.srt`) if available
* 📊 Green progress bars (file + overall) with live **speed, ETA, and remaining items**
* ✅ Safe cancel option
* 🔑 Cookie file (`cookies.txt`) support for login-required sites

---

## 📦 Requirements

* Python **3.8+**
* [yt-dlp](https://github.com/yt-dlp/yt-dlp)

Install yt-dlp globally:

```bash
py -m pip install -U yt-dlp
```

Optional (for embedding subs / fixing timestamps):

```bash
winget install Gyan.FFmpeg   # Windows
```

---

## 🚀 How to Use

1. Clone this repo:

   ```bash
   git clone https://github.com/<your-username>/<your-repo>.git
   cd <your-repo>
   ```

2. Make sure `yt-dlp` is installed (see above).

3. Run the GUI:

   ```bash
   py ll_gui_downloader_v2.py
   ```

4. In the app:

   * Paste your **course / playlist URL**
   * Choose **Site type** (auto-detect works fine)
   * Browse & select `cookies.txt` if login is needed
   * Pick output folder
   * Hit **Start Download** 🎉

---

## 🍪 About Cookies

Some sites (LinkedIn Learning, Udemy, etc.) require login.
Export cookies with browser extensions like:

* Chrome: [Get cookies.txt](https://chrome.google.com/webstore/detail/get-cookiestxt/lgmpcpglpngdoalbgeoldeajfclnhafa)
* Firefox: [Cookie Quick Manager](https://addons.mozilla.org/en-US/firefox/addon/cookie-quick-manager/)

Save as `cookies.txt` in the same folder (or choose via GUI).

---

## 📂 Output Example

```
Windows Server 2025 Essential Training/
 ├── 01 - Introduction/
 │    ├── 001 - Getting Started.mp4
 │    ├── 001 - Getting Started.en.srt
 │    └── ...
 ├── 02 - Installation/
 │    ├── 010 - Installing Windows Server.mp4
 │    ├── 010 - Installing Windows Server.en.srt
 │    └── ...
 └── ll-archive.txt   # prevents duplicate downloads
```

---

## ⚠️ Notes

* ❌ DRM-protected platforms (Netflix, Prime Video, Spotify full tracks) **are not supported**.
* ✅ Works great with LinkedIn Learning, Udemy (non-DRM), YouTube playlists, Vimeo, SoundCloud, Bandcamp, etc.
* 🛑 If you close the app mid-download, partial files remain but can resume.

---

## ❤️ Credits

* Built with [yt-dlp](https://github.com/yt-dlp/yt-dlp)
* Chat
* GUI powered by Python’s `tkinter`
* Inspired by the need for **one-click course/playlist downloads with progress bars**

  আহা, অনেক ধন্যবাদ ❤️🙏 আপনি চাইছেন ক্রেডিটে আমার নামও থাকুক — এটা আমার জন্য গর্বের বিষয়।
আপনার GitHub প্রজেক্টের **Credits** সেকশনে আমার নাম এভাবে যোগ করতে পারেন:

---

## ❤️ Credits

* Built with [yt-dlp](https://github.com/yt-dlp/yt-dlp)
* GUI powered by Python’s `tkinter`
* Script designed & co-authored with the help of [ChatGPT (OpenAI)](https://openai.com/chatgpt) 🤖
* Inspired by the need for **one-click course/playlist downloads with progress bars**

---

✨ Enjoy effortless course & playlist downloads!
If this project helps you, consider giving it a ⭐ on GitHub!

---

Would you like me to also write a **.gitignore** (to ignore things like `__pycache__/`, `.venv/`, and `ll-archive.txt`) so your repo stays clean?
