import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import ctypes
import json
import os

# --- MESIN MUSIK ---
def mci_send(command):
    buffer = ctypes.create_unicode_buffer(255)
    ctypes.windll.winmm.mciSendStringW(command, buffer, 255, 0)
    return buffer.value

class Seandfa:
    def __init__(self, root):
        self.root = root
        self.root.title("Seandfa - Premium Music Player")
        self.root.geometry("1200x850")
        
        # --- PALET WARNA COFFEE ---
        self.color_bg = "#FDF5E6"        
        self.color_sidebar = "#D2B48C"   
        self.color_header = "#8B4513"    
        self.color_search = "#A0522D"    
        self.color_btn = "#BC8F8F"       
        self.color_text_main = "#3E2723" 
        self.color_player_bar = "#8B4513" 
        
        self.root.configure(bg=self.color_bg)
        self.db_file = "seandfa_data.json" # Nama file database juga disesuaikan
        self.current_user = None
        self.current_playlist = "Semua Lagu"
        self.is_paused = False
        self.current_song_index = -1

        self.all_data = self.muat_semua_data()
        self.tampilan_login()

    def muat_semua_data(self):
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r') as f: return json.load(f)
            except: return {}
        return {}

    def simpan_semua_data(self):
        with open(self.db_file, 'w') as f: json.dump(self.all_data, f)

    def format_waktu(self, ms):
        if not ms: return "00:00"
        detik = int(ms) // 1000
        menit = detik // 60
        detik = detik % 60
        return f"{menit:02d}:{detik:02d}"

    def tampilan_login(self):
        self.login_win = tk.Toplevel(self.root)
        self.login_win.geometry("400x500")
        self.login_win.configure(bg=self.color_header)
        self.login_win.grab_set()
        # Branding di Login
        tk.Label(self.login_win, text="SEANDFA", font=("Serif", 35, "bold"), bg=self.color_header, fg=self.color_bg).pack(pady=50)
        tk.Label(self.login_win, text="Username:", font=("Arial", 10), bg=self.color_header, fg=self.color_bg).pack()
        self.ent_user = tk.Entry(self.login_win, font=("Arial", 12), bg=self.color_bg, border=0)
        self.ent_user.pack(pady=10, ipady=10, padx=50, fill=tk.X)
        tk.Button(self.login_win, text="MULAI MENDENGARKAN", command=self.proses_login, bg=self.color_btn, fg='white', border=0, pady=12, cursor="hand2").pack(pady=30)

    def proses_login(self):
        nama = self.ent_user.get().strip().lower()
        if not nama: return
        self.current_user = nama
        if self.current_user not in self.all_data: 
            self.all_data[self.current_user] = {"Semua Lagu": []}
        self.simpan_semua_data(); self.login_win.destroy(); self.bangun_ui_utama()

    def bangun_ui_utama(self):
        # --- PLAYER BAR (BAWAH) ---
        self.player_bar = tk.Frame(self.root, bg=self.color_player_bar, height=110)
        self.player_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.player_bar.pack_propagate(False)

        self.info_frame = tk.Frame(self.player_bar, bg=self.color_player_bar, padx=30)
        self.info_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.lbl_now_playing = tk.Label(self.info_frame, text="Selamat datang di Seandfa", fg=self.color_bg, bg=self.color_player_bar, font=("Arial", 11, "bold"))
        self.lbl_now_playing.pack(pady=(30,0), anchor="w")
        
        self.controls_mid = tk.Frame(self.player_bar, bg=self.color_player_bar)
        self.controls_mid.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        btns_f = tk.Frame(self.controls_mid, bg=self.color_player_bar)
        btns_f.pack(pady=(15, 5))
        
        tk.Button(btns_f, text="⏮", command=self.prev_lagu, bg=self.color_player_bar, fg=self.color_bg, font=("Arial", 16), border=0, cursor="hand2").pack(side=tk.LEFT, padx=15)
        self.btn_play_pause = tk.Button(btns_f, text="▶", command=self.putar_lagu_manual, bg=self.color_bg, fg=self.color_header, font=("Arial", 14, "bold"), width=3, border=0, cursor="hand2")
        self.btn_play_pause.pack(side=tk.LEFT, padx=15)
        tk.Button(btns_f, text="⏭", command=self.next_lagu, bg=self.color_player_bar, fg=self.color_bg, font=("Arial", 16), border=0, cursor="hand2").pack(side=tk.LEFT, padx=15)

        # Progress Bar & Timer
        prog_f = tk.Frame(self.controls_mid, bg=self.color_player_bar)
        prog_f.pack(pady=5)
        self.lbl_current_time = tk.Label(prog_f, text="00:00", fg="#F5DEB3", bg=self.color_player_bar, font=("Arial", 8))
        self.lbl_current_time.pack(side=tk.LEFT, padx=5)
        
        self.bar_width = 450
        self.progress_canvas = tk.Canvas(prog_f, bg=self.color_search, height=8, highlightthickness=0, width=self.bar_width, cursor="hand2")
        self.progress_canvas.pack(side=tk.LEFT)
        self.progress_fill = self.progress_canvas.create_rectangle(0, 0, 0, 8, fill="#F5DEB3", outline="")
        self.progress_canvas.bind("<Button-1>", self.lompat_ke_posisi)

        self.lbl_total_time = tk.Label(prog_f, text="00:00", fg="#F5DEB3", bg=self.color_player_bar, font=("Arial", 8))
        self.lbl_total_time.pack(side=tk.LEFT, padx=5)

        # --- SIDEBAR ---
        sidebar = tk.Frame(self.root, bg=self.color_sidebar, width=280)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        # Nama Aplikasi di Sidebar
        tk.Label(sidebar, text="SEANDFA", font=("Georgia", 18, "bold"), bg=self.color_sidebar, fg=self.color_header, pady=20).pack()

        tk.Button(sidebar, text=" 🏠  Semua Lagu", command=lambda: self.pindah_mode("Semua Lagu"), bg=self.color_sidebar, fg=self.color_text_main, border=0, font=("Arial", 12, "bold"), anchor='w', padx=20).pack(fill=tk.X)
        tk.Button(sidebar, text=" + Buat Playlist ", command=self.buat_playlist_baru, bg=self.color_header, fg='white', border=0, font=("Arial", 10, "bold"), pady=12).pack(pady=15, padx=25, fill=tk.X)
        self.scroll_frame = tk.Frame(sidebar, bg=self.color_sidebar)
        self.scroll_frame.pack(fill=tk.BOTH, expand=True)

        # --- MAIN CONTENT ---
        self.main_content = tk.Frame(self.root, bg=self.color_bg)
        self.main_content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.header = tk.Frame(self.main_content, bg=self.color_header, height=200)
        self.header.pack(fill=tk.X)
        self.header.pack_propagate(False)
        self.lbl_title = tk.Label(self.header, text="Semua Lagu", font=("Georgia", 35, "italic"), bg=self.color_header, fg=self.color_bg)
        self.lbl_title.place(x=40, y=40)

        # Search Area
        search_f = tk.Frame(self.header, bg=self.color_search, padx=10, pady=5)
        search_f.place(x=45, y=115, width=400)
        tk.Label(search_f, text="🔍", bg=self.color_search, fg="white", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        self.ent_search = tk.Entry(search_f, bg=self.color_search, fg='white', border=0, font=("Arial", 11), insertbackground="white")
        self.ent_search.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.ent_search.bind("<KeyRelease>", lambda e: self.refresh_songs())

        self.song_listbox = tk.Listbox(self.main_content, bg='white', fg=self.color_text_main, font=("Segoe UI", 11), border=0, highlightthickness=0, selectbackground=self.color_sidebar)
        self.song_listbox.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)
        self.song_listbox.bind("<Double-Button-1>", lambda e: self.putar_lagu_manual())

        btn_top_f = tk.Frame(self.main_content, bg=self.color_bg)
        btn_top_f.pack(fill=tk.X, padx=40, pady=(0, 20))
        tk.Button(btn_top_f, text="+ IMPORT MP3", command=self.tambah_lagu, bg=self.color_btn, fg="white", border=0, padx=15, pady=8).pack(side=tk.RIGHT)
        tk.Button(btn_top_f, text="🗑️ HAPUS", command=self.hapus_lagu, bg="#A52A2A", fg="white", border=0, padx=15, pady=8).pack(side=tk.RIGHT, padx=10)
        tk.Button(btn_top_f, text="📥 KE PLAYLIST", command=self.tambah_ke_playlist, bg=self.color_header, fg="white", border=0, padx=15, pady=8).pack(side=tk.RIGHT)

        self.refresh_sidebar(); self.pindah_mode("Semua Lagu")
        self.update_loop()

    # --- LOGIKA SEEKING ---
    def lompat_ke_posisi(self, event):
        length = mci_send("status musik length")
        if length:
            total_ms = int(length)
            persentase = event.x / self.bar_width
            posisi_baru = int(persentase * total_ms)
            if posisi_baru < 0: posisi_baru = 0
            if posisi_baru > total_ms: posisi_baru = total_ms
            mci_send(f"seek musik to {posisi_baru}")
            mci_send("play musik")
            self.is_paused = False
            self.btn_play_pause.config(text="⏸")

    def update_loop(self):
        status = mci_send("status musik mode")
        if status == "stopped" and not self.is_paused and self.current_song_index != -1:
            self.next_lagu()
        if status in ["playing", "paused"]:
            length = mci_send("status musik length")
            pos = mci_send("status musik position")
            if length and pos:
                try:
                    t, p = int(length), int(pos)
                    self.progress_canvas.coords(self.progress_fill, 0, 0, (p/t)*self.bar_width, 8)
                    self.lbl_current_time.config(text=self.format_waktu(p))
                    self.lbl_total_time.config(text=self.format_waktu(t))
                except: pass
        self.root.after(500, self.update_loop)

    def jalankan_musik(self):
        query = self.ent_search.get().lower()
        all_s = self.all_data[self.current_user].get(self.current_playlist, [])
        filtered = [s for s in all_s if query in os.path.basename(s).lower()]
        if 0 <= self.current_song_index < len(filtered):
            path = filtered[self.current_song_index]
            self.lbl_now_playing.config(text=os.path.basename(path)[:30])
            self.btn_play_pause.config(text="⏸")
            mci_send("close musik")
            mci_send(f'open "{path}" type mpegvideo alias musik')
            mci_send("set musik time format milliseconds")
            mci_send("play musik")
            self.is_paused = False

    def putar_lagu_manual(self):
        sel = self.song_listbox.curselection()
        if sel: self.current_song_index = sel[0]; self.jalankan_musik()
        else: self.pause_resume_lagu()

    def pause_resume_lagu(self):
        status = mci_send("status musik mode")
        if status == "playing": mci_send("pause musik"); self.is_paused = True; self.btn_play_pause.config(text="▶")
        elif status == "paused": mci_send("resume musik"); self.is_paused = False; self.btn_play_pause.config(text="⏸")

    def next_lagu(self):
        query = self.ent_search.get().lower()
        all_s = self.all_data[self.current_user].get(self.current_playlist, [])
        filtered = [s for s in all_s if query in os.path.basename(s).lower()]
        if filtered:
            self.current_song_index = (self.current_song_index + 1) % len(filtered)
            self.jalankan_musik()

    def prev_lagu(self):
        query = self.ent_search.get().lower()
        all_s = self.all_data[self.current_user].get(self.current_playlist, [])
        filtered = [s for s in all_s if query in os.path.basename(s).lower()]
        if filtered:
            self.current_song_index = (self.current_song_index - 1) % len(filtered)
            self.jalankan_musik()

    def refresh_songs(self):
        self.song_listbox.delete(0, tk.END)
        songs = self.all_data[self.current_user].get(self.current_playlist, [])
        query = self.ent_search.get().lower()
        count = 1
        for s in songs:
            nama = os.path.basename(s)
            if query in nama.lower():
                self.song_listbox.insert(tk.END, f" {count}.  {nama}")
                count += 1

    def pindah_mode(self, nama):
        self.current_playlist = nama; self.lbl_title.config(text=nama); self.refresh_songs()

    def refresh_sidebar(self):
        for c in self.scroll_frame.winfo_children(): c.destroy()
        for p in self.all_data[self.current_user]:
            if p != "Semua Lagu": tk.Button(self.scroll_frame, text=f"   🎶  {p.upper()}", command=lambda x=p: self.pindah_mode(x), bg=self.color_sidebar, fg=self.color_text_main, border=0, anchor='w', padx=20, font=("Arial", 10, "bold"), pady=8).pack(fill=tk.X)

    def tambah_lagu(self):
        fs = filedialog.askopenfilenames(filetypes=[("MP3", "*.mp3")])
        for f in fs:
            if f not in self.all_data[self.current_user]["Semua Lagu"]: self.all_data[self.current_user]["Semua Lagu"].append(f)
        self.simpan_semua_data(); self.refresh_songs()

    def buat_playlist_baru(self):
        n = simpledialog.askstring("Seandfa Playlist", "Nama Playlist Baru:")
        if n: self.all_data[self.current_user][n] = []; self.simpan_semua_data(); self.refresh_sidebar()

    def hapus_lagu(self):
        sel = self.song_listbox.curselection()
        if sel:
            query = self.ent_search.get().lower()
            songs = self.all_data[self.current_user][self.current_playlist]
            filtered = [s for s in songs if query in os.path.basename(s).lower()]
            songs.remove(filtered[sel[0]])
            self.simpan_semua_data(); self.refresh_songs()

    def tambah_ke_playlist(self):
        sel = self.song_listbox.curselection()
        if not sel: return
        query = self.ent_search.get().lower()
        all_s = self.all_data[self.current_user].get(self.current_playlist, [])
        filtered = [s for s in all_s if query in os.path.basename(s).lower()]
        path = filtered[sel[0]]
        playlists = [p for p in self.all_data[self.current_user].keys() if p != "Semua Lagu"]
        win_p = tk.Toplevel(self.root); win_p.geometry("250x300"); win_p.configure(bg=self.color_bg)
        tk.Label(win_p, text="Pilih Playlist:", bg=self.color_bg, pady=10).pack()
        for p in playlists:
            tk.Button(win_p, text=p, bg=self.color_sidebar, command=lambda x=p: [self.all_data[self.current_user][x].append(path) if path not in self.all_data[self.current_user][x] else None, self.simpan_semua_data(), win_p.destroy()]).pack(fill=tk.X, pady=2)

if __name__ == "__main__":
    root = tk.Tk(); app = Seandfa(root); root.mainloop()