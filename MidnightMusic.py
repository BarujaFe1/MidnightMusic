import os
import sys
import threading
import requests
import customtkinter as ctk
from tkinter import messagebox, filedialog
import yt_dlp
from PIL import Image
from io import BytesIO
import random
import time
import json

# =============================================================================
# ⚙️ CONFIGURAÇÕES DE DIRETÓRIO E FFMPEG
# =============================================================================

# Caminho padrão inicial
DEFAULT_DOWNLOAD_PATH = r"D:\Músicas\Spotify"

# Caminho para o arquivo de configuração
if getattr(sys, 'frozen', False):
    APPLICATION_PATH = os.path.dirname(sys.executable)
else:
    APPLICATION_PATH = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(APPLICATION_PATH, "midnight_config.json")

# Carrega configuração salva ou usa padrão
def load_config():
    default_config = {
        "download_path": DEFAULT_DOWNLOAD_PATH,
        "delay_between_songs": 5,
        "retry_attempts": 3
    }
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Atualiza com valores padrão para novas chaves
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        except:
            return default_config
    return default_config

def save_config(config):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except:
        pass

# Carrega configuração atual
config = load_config()
DOWNLOAD_PATH = config["download_path"]

# Caminho exato para o executável
FFMPEG_EXE = os.path.join(APPLICATION_PATH, "ffmpeg.exe")
FFPROBE_EXE = os.path.join(APPLICATION_PATH, "ffprobe.exe")

# Cria a pasta de músicas se não existir
if not os.path.exists(DOWNLOAD_PATH):
    try: 
        os.makedirs(DOWNLOAD_PATH)
    except: 
        # Se não conseguir criar, volta para a pasta do programa
        DOWNLOAD_PATH = APPLICATION_PATH
        config["download_path"] = DOWNLOAD_PATH
        save_config(config)

# =============================================================================
# 🎨 TEMA
# =============================================================================
THEME = {
    "bg": "#121212", "card": "#181818", "sidebar": "#000000",
    "fg": "#ffffff", "green": "#1DB954", "green_hover": "#1ed760",
    "gray": "#b3b3b3", "dark_gray": "#282828", "red": "#e91429",
    "blue": "#1E90FF", "blue_hover": "#4682B4"
}

FONT_FAMILY = "Segoe UI"
FONT_BOLD = (FONT_FAMILY, 12, "bold")
FONT_HEADER = (FONT_FAMILY, 22, "bold")
FONT_SMALL = (FONT_FAMILY, 10)

ctk.set_appearance_mode("Dark")

class MidnightMusicSuite(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Midnight Suite - MP3 PRO")
        self.geometry("1100x800")
        self.configure(fg_color=THEME["bg"])
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=220, fg_color=THEME["sidebar"], corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="MIDNIGHT\nMP3 ONLY", font=FONT_HEADER, text_color=THEME["green"]).pack(pady=40)

        self.create_nav_btn("🎵 Música (Busca/Link)", "single")
        self.create_nav_btn("📚 Multi Playlists", "playlist")
        self.create_nav_btn("🖼️ Baixar Capa", "cover")
        self.create_nav_btn("⚙️ Configurações", "settings")
        
        # Mostra status do FFmpeg na barra lateral
        status_color = THEME["green"] if os.path.exists(FFMPEG_EXE) else THEME["red"]
        status_text = "FFmpeg: OK" if os.path.exists(FFMPEG_EXE) else "FFmpeg: FALTANDO"
        self.lbl_ffmpeg = ctk.CTkLabel(self.sidebar, text=status_text, font=("Arial", 12, "bold"), text_color=status_color)
        self.lbl_ffmpeg.pack(side="bottom", pady=20)

        # --- MAIN ---
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.frames = {}
        self.setup_single_frame()
        self.setup_playlist_frame()
        self.setup_cover_frame()
        self.setup_settings_frame()  # Nova aba de configurações
        self.show_frame("single")
        
        # Validação forçada ao iniciar
        self.check_system_integrity()

    def check_system_integrity(self):
        if not os.path.exists(FFMPEG_EXE):
            messagebox.showerror("ERRO FATAL: FFmpeg não encontrado", 
                "O programa NÃO vai funcionar sem o FFmpeg.\n\n"
                f"O arquivo 'ffmpeg.exe' precisa estar aqui:\n{FFMPEG_EXE}\n\n"
                "Copie o ffmpeg.exe e o ffprobe.exe da pasta bin para a pasta deste programa.")

    def create_nav_btn(self, text, name):
        ctk.CTkButton(self.sidebar, text=text, fg_color="transparent", text_color=THEME["gray"], 
                      hover_color=THEME["card"], anchor="w", font=FONT_BOLD, height=45,
                      command=lambda: self.show_frame(name)).pack(fill="x", padx=10, pady=5)

    def show_frame(self, name):
        for f in self.frames.values(): f.pack_forget()
        self.frames[name].pack(fill="both", expand=True)
        
        # Atualiza o caminho atual quando muda para aba de configurações
        if name == "settings":
            self.update_current_path_display()

    # =========================================================================
    # ⚙️ CONFIGURAÇÃO DE DOWNLOAD (COM PROTEÇÃO ANTI-BOT)
    # =========================================================================
    def get_opts(self):
        """Configuração corrigida para evitar bloqueios do YouTube"""
        # Atualiza o caminho de download da configuração
        global DOWNLOAD_PATH
        config = load_config()
        DOWNLOAD_PATH = config["download_path"]
        
        # Configuração para contornar bloqueios do YouTube
        return {
            'format': 'bestaudio/best',
            'ffmpeg_location': FFMPEG_EXE,
            'paths': {'home': DOWNLOAD_PATH},
            'outtmpl': '%(artist)s - %(title)s.%(ext)s',
            'quiet': False,  # Mantém False para ver erros
            'no_warnings': False,
            'ignoreerrors': True,
            'writethumbnail': True,
            'noplaylist': True,
            'extract_audio': True,
            'audio_format': 'mp3',
            'keepvideo': False,
            
            # CONFIGURAÇÕES ANTI-BOT CRÍTICAS
            'cookiefile': os.path.join(APPLICATION_PATH, 'cookies.txt'),  # Adiciona suporte a cookies
            'sleep_interval': random.randint(5, 10),  # Pausa aleatória entre downloads
            'max_sleep_interval': 15,
            'extractor_args': {
                'youtube': {
                    'skip': ['hls', 'dash'],  # Evita formatos problemáticos
                    'player_client': ['android'],  # Usa cliente Android
                }
            },
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                },
                {
                    'key': 'EmbedThumbnail',
                },
                {
                    'key': 'FFmpegMetadata',
                },
            ],
        }

    # =========================================================================
    # 🎵 ABA 1: SINGLE
    # =========================================================================
    def setup_single_frame(self):
        frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.frames["single"] = frame
        
        # Cabeçalho com caminho atual
        header_frame = ctk.CTkFrame(frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(header_frame, text="BAIXAR MÚSICA (MP3)", font=FONT_HEADER, text_color=THEME["green"]).pack(side="left")
        
        # Mostra o caminho atual de forma compacta
        self.single_path_label = ctk.CTkLabel(
            header_frame, 
            text=f"Salvando em: {self.get_compact_path(DOWNLOAD_PATH)}",
            text_color=THEME["gray"],
            font=FONT_SMALL
        )
        self.single_path_label.pack(side="right", padx=10)
        
        self.single_entry = ctk.CTkEntry(frame, placeholder_text="Nome ou Link...", width=500, height=45, fg_color=THEME["dark_gray"], border_width=0)
        self.single_entry.pack(pady=20)
        self.btn_dl_single = ctk.CTkButton(frame, text="BAIXAR MP3", font=FONT_BOLD, height=50, fg_color=THEME["green"], 
                                           text_color=THEME["bg"], hover_color=THEME["green_hover"], command=self.start_single_download)
        self.btn_dl_single.pack(pady=10)
        self.single_status = ctk.CTkLabel(frame, text="", text_color=THEME["gray"])
        self.single_status.pack(pady=10)
        
        # Frame para informações
        info_frame = ctk.CTkFrame(frame, fg_color=THEME["card"], corner_radius=10)
        info_frame.pack(fill="x", pady=20, padx=50)
        
        info_text = "• Digite o nome da música ou cole um link do YouTube\n• O arquivo será salvo como MP3 com capa embutida\n• Para mudar o local de salvamento, vá em Configurações"
        ctk.CTkLabel(info_frame, text=info_text, text_color=THEME["gray"], justify="left", wraplength=500).pack(padx=15, pady=15)

    def get_compact_path(self, path):
        """Retorna um caminho compactado para exibição"""
        if len(path) > 50:
            # Mostra apenas o início e o final do caminho
            return f"{path[:30]}...{path[-20:]}"
        return path

    def start_single_download(self):
        if not os.path.exists(FFMPEG_EXE):
            messagebox.showerror("Erro", "FFmpeg.exe não encontrado! O download falharia.")
            return
        
        q = self.single_entry.get()
        if not q: 
            messagebox.showwarning("Aviso", "Digite o nome da música ou cole um link!")
            return
        
        # Atualiza o caminho exibido
        config = load_config()
        compact_path = self.get_compact_path(config["download_path"])
        self.single_path_label.configure(text=f"Salvando em: {compact_path}")
        
        self.btn_dl_single.configure(state="disabled")
        threading.Thread(target=self._single_thread, args=(q,), daemon=True).start()

    def _single_thread(self, query):
        try:
            self.single_status.configure(text="Baixando e Convertendo...", text_color=THEME["green"])
            # Adiciona estratégia anti-bot
            opts = self.get_opts()
            opts['sleep_interval'] = 2  # Pausa menor para single
            
            q = query if query.startswith("http") else f"ytsearch1:{query} audio"
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([q])
            self.single_status.configure(text="Sucesso! Salvo em MP3.", text_color=THEME["green"])
            messagebox.showinfo("Sucesso", f"Download MP3 concluído!\n\nSalvo em:\n{DOWNLOAD_PATH}")
        except Exception as e:
            self.single_status.configure(text="Erro no Download", text_color=THEME["red"])
            print(f"Erro: {e}")
        finally:
            self.btn_dl_single.configure(state="normal")

    # =========================================================================
    # 📚 ABA 2: MULTI PLAYLISTS - COM SELECÇÃO DE PASTA
    # =========================================================================
    def setup_playlist_frame(self):
        frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.frames["playlist"] = frame
        
        # Cabeçalho com caminho atual
        header_frame = ctk.CTkFrame(frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(header_frame, text="MULTI PLAYLIST (MP3)", font=FONT_HEADER, text_color=THEME["green"]).pack(side="left")
        
        self.playlist_path_label = ctk.CTkLabel(
            header_frame, 
            text=f"Salvando em: {self.get_compact_path(DOWNLOAD_PATH)}",
            text_color=THEME["gray"],
            font=FONT_SMALL
        )
        self.playlist_path_label.pack(side="right", padx=10)
        
        # Frame para configurações avançadas
        settings_frame = ctk.CTkFrame(frame, fg_color="transparent")
        settings_frame.pack(pady=10)
        
        # Coluna 1
        col1 = ctk.CTkFrame(settings_frame, fg_color="transparent")
        col1.pack(side="left", padx=20)
        
        ctk.CTkLabel(col1, text="Delay entre músicas:", text_color=THEME["gray"]).pack(anchor="w", pady=2)
        self.delay_var = ctk.StringVar(value=str(config.get("delay_between_songs", 5)))
        self.delay_entry = ctk.CTkEntry(col1, width=80, textvariable=self.delay_var)
        self.delay_entry.pack(anchor="w", pady=(0, 10))
        
        # Coluna 2
        col2 = ctk.CTkFrame(settings_frame, fg_color="transparent")
        col2.pack(side="left", padx=20)
        
        ctk.CTkLabel(col2, text="Tentativas por música:", text_color=THEME["gray"]).pack(anchor="w", pady=2)
        self.retry_var = ctk.StringVar(value=str(config.get("retry_attempts", 3)))
        self.retry_entry = ctk.CTkEntry(col2, width=80, textvariable=self.retry_var)
        self.retry_entry.pack(anchor="w", pady=(0, 10))
        
        # Área para links
        links_frame = ctk.CTkFrame(frame, fg_color="transparent")
        links_frame.pack(fill="x", pady=15, padx=20)
        
        ctk.CTkLabel(links_frame, text="Links das Playlists (um por linha):", text_color=THEME["gray"]).pack(anchor="w")
        self.playlist_txt = ctk.CTkTextbox(frame, width=600, height=100, fg_color=THEME["dark_gray"], border_width=0, text_color=THEME["fg"])
        self.playlist_txt.pack(pady=(0, 15))
        
        # Botões de ação
        buttons_frame = ctk.CTkFrame(frame, fg_color="transparent")
        buttons_frame.pack(pady=5)
        
        self.btn_analyze = ctk.CTkButton(buttons_frame, text="ANALISAR LINKS", fg_color=THEME["card"], 
                                         hover_color=THEME["gray"], command=self.analyze_playlists,
                                         width=150)
        self.btn_analyze.pack(side="left", padx=5)
        
        self.btn_select_all = ctk.CTkButton(buttons_frame, text="SELECIONAR TODOS", fg_color=THEME["dark_gray"],
                                            hover_color=THEME["gray"], command=self.select_all_items,
                                            width=150, state="disabled")
        self.btn_select_all.pack(side="left", padx=5)
        
        self.btn_deselect_all = ctk.CTkButton(buttons_frame, text="DESMARCAR TODOS", fg_color=THEME["dark_gray"],
                                              hover_color=THEME["gray"], command=self.deselect_all_items,
                                              width=150, state="disabled")
        self.btn_deselect_all.pack(side="left", padx=5)
        
        # Frame rolável para lista de músicas
        list_frame = ctk.CTkFrame(frame, fg_color="transparent")
        list_frame.pack(fill="both", expand=True, pady=10)
        
        ctk.CTkLabel(list_frame, text="Músicas encontradas:", text_color=THEME["gray"]).pack(anchor="w", padx=20)
        self.scroll = ctk.CTkScrollableFrame(list_frame, fg_color=THEME["card"], height=250)
        self.scroll.pack(fill="both", expand=True, padx=20, pady=5)
        
        # Botão de download principal
        self.btn_dl_playlist = ctk.CTkButton(frame, text="BAIXAR LISTA SELECIONADA (MP3)", font=FONT_BOLD, height=45, 
                                             fg_color=THEME["green"], text_color=THEME["bg"], 
                                             hover_color=THEME["green_hover"], state="disabled", 
                                             command=self.start_playlist_download)
        self.btn_dl_playlist.pack(pady=20)
        
        self.playlist_items = []
        self.playlist_status = ctk.CTkLabel(frame, text="", text_color=THEME["gray"])
        self.playlist_status.pack(pady=(0, 10))

    def select_all_items(self):
        """Seleciona todas as músicas da lista"""
        for chk, _ in self.playlist_items:
            chk.select()

    def deselect_all_items(self):
        """Deseleciona todas as músicas da lista"""
        for chk, _ in self.playlist_items:
            chk.deselect()

    def analyze_playlists(self):
        links = [l.strip() for l in self.playlist_txt.get("0.0", "end").split('\n') if l.strip()]
        if not links: 
            messagebox.showwarning("Aviso", "Digite pelo menos um link de playlist!")
            return
        
        # Atualiza o caminho exibido
        config = load_config()
        compact_path = self.get_compact_path(config["download_path"])
        self.playlist_path_label.configure(text=f"Salvando em: {compact_path}")
        
        self.btn_analyze.configure(state="disabled")
        self.playlist_status.configure(text="Analisando... (Isso pode levar alguns minutos)", text_color=THEME["green"])
        threading.Thread(target=self._analyze_thread, args=(links,), daemon=True).start()

    def _analyze_thread(self, links):
        all_entries = []
        try:
            # Configuração específica para análise (com delay entre requisições)
            analyze_opts = {
                'extract_flat': True, 
                'quiet': True, 
                'ignoreerrors': True,
                'sleep_interval': 3,  # Delay entre vídeos
                'extractor_args': {
                    'youtube': {
                        'skip': ['hls', 'dash'],
                        'player_client': ['android'],
                    }
                }
            }
            
            with yt_dlp.YoutubeDL(analyze_opts) as ydl:
                for idx, url in enumerate(links):
                    try:
                        self.after(0, lambda idx=idx: self.playlist_status.configure(
                            text=f"Analisando link {idx+1}/{len(links)}...", 
                            text_color=THEME["green"]
                        ))
                        
                        info = ydl.extract_info(url, download=False)
                        if 'entries' in info: 
                            all_entries.extend([e for e in info['entries'] if e])
                        else: 
                            all_entries.append(info)
                        
                        # Delay aleatório para evitar bloqueios
                        time.sleep(random.uniform(2, 5))
                        
                    except Exception as e:
                        print(f"Erro ao analisar {url}: {e}")
                        continue
        except Exception as e:
            print(f"Erro geral na análise: {e}")
        
        self.after(0, lambda: self._populate_list(all_entries))

    def _populate_list(self, entries):
        for w in self.scroll.winfo_children(): w.destroy()
        self.playlist_items.clear()
        self.btn_analyze.configure(state="normal")
        
        if entries:
            self.btn_dl_playlist.configure(state="normal")
            self.btn_select_all.configure(state="normal")
            self.btn_deselect_all.configure(state="normal")
            self.playlist_status.configure(text=f"{len(entries)} músicas encontradas.", text_color=THEME["green"])
        else:
            self.btn_dl_playlist.configure(state="disabled")
            self.btn_select_all.configure(state="disabled")
            self.btn_deselect_all.configure(state="disabled")
            self.playlist_status.configure(text="Nenhuma música encontrada.", text_color=THEME["red"])
            return
        
        for entry in entries:
            url = entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
            title = entry.get('title', 'Música desconhecida')
            
            # Frame para cada item
            item_frame = ctk.CTkFrame(self.scroll, fg_color=THEME["dark_gray"])
            item_frame.pack(fill="x", pady=2, padx=5)
            
            chk = ctk.CTkCheckBox(item_frame, text="", fg_color=THEME["green"], hover_color=THEME["green_hover"], width=20)
            chk.pack(side="left", padx=5)
            chk.select()
            
            # Limita o tamanho do título para não quebrar o layout
            display_title = title[:70] + "..." if len(title) > 70 else title
            ctk.CTkLabel(item_frame, text=display_title, text_color=THEME["fg"], wraplength=450).pack(side="left", padx=10)
            self.playlist_items.append((chk, url))

    def start_playlist_download(self):
        if not os.path.exists(FFMPEG_EXE):
            messagebox.showerror("Erro", "FFmpeg não encontrado! Não é possível converter para MP3.")
            return

        urls = [url for chk, url in self.playlist_items if chk.get()]
        if not urls: 
            messagebox.showwarning("Aviso", "Selecione pelo menos uma música para baixar!")
            return
        
        # Atualiza o caminho exibido
        config = load_config()
        compact_path = self.get_compact_path(config["download_path"])
        self.playlist_path_label.configure(text=f"Salvando em: {compact_path}")
        
        # Pega configurações do usuário
        try:
            delay = max(2, int(self.delay_var.get()))  # Mínimo 2 segundos
            max_retries = min(5, max(1, int(self.retry_var.get())))  # Entre 1 e 5
        except:
            delay = 5
            max_retries = 3
        
        # Salva as configurações
        config["delay_between_songs"] = delay
        config["retry_attempts"] = max_retries
        save_config(config)
        
        # Confirmação antes de começar
        confirm = messagebox.askyesno(
            "Confirmar Download",
            f"Você está prestes a baixar {len(urls)} músicas.\n\n"
            f"Configurações:\n"
            f"• Delay entre músicas: {delay} segundos\n"
            f"• Tentativas por música: {max_retries}\n"
            f"• Local de salvamento: {DOWNLOAD_PATH}\n\n"
            f"Deseja continuar?"
        )
        
        if not confirm:
            return
        
        self.btn_dl_playlist.configure(state="disabled")
        self.btn_select_all.configure(state="disabled")
        self.btn_deselect_all.configure(state="disabled")
        threading.Thread(target=self._playlist_dl_thread, args=(urls, delay, max_retries), daemon=True).start()

    def _playlist_dl_thread(self, urls, delay, max_retries):
        total = len(urls)
        success = 0
        failed = []
        
        for i, url in enumerate(urls):
            try:
                self.after(0, lambda i=i: self.playlist_status.configure(
                    text=f"Baixando {i+1}/{total}... Aguarde {delay}s entre músicas", 
                    text_color=THEME["green"]
                ))
                
                # Configuração específica para este download
                opts = self.get_opts()
                opts['sleep_interval'] = delay
                
                # Tentativa com retry
                for attempt in range(max_retries):
                    try:
                        with yt_dlp.YoutubeDL(opts) as ydl: 
                            ydl.download([url])
                        success += 1
                        break  # Sucesso, sai do loop de tentativas
                    except Exception as e:
                        if attempt < max_retries - 1:
                            wait_time = delay * (attempt + 1)
                            self.after(0, lambda attempt=attempt: self.playlist_status.configure(
                                text=f"Tentativa {attempt+2}/{max_retries} em {wait_time}s...", 
                                text_color=THEME["gray"]
                            ))
                            time.sleep(wait_time)
                        else:
                            failed.append(f"Item {i+1}: {str(e)[:100]}")
                            print(f"Falha após {max_retries} tentativas: {url}")
                
                # Delay entre músicas (se não for a última)
                if i < total - 1:
                    time.sleep(delay)
                    
            except Exception as e:
                failed.append(f"Item {i+1}: {str(e)[:100]}")
                continue
        
        # Resultado final
        self.after(0, lambda: self._show_download_result(total, success, failed))
    
    def _show_download_result(self, total, success, failed):
        self.btn_dl_playlist.configure(state="normal")
        self.btn_select_all.configure(state="normal")
        self.btn_deselect_all.configure(state="normal")
        
        if failed:
            result_text = f"Fim! {success}/{total} baixados. {len(failed)} falhas."
            self.playlist_status.configure(text=result_text, text_color=THEME["red"])
            
            # Mostra erros em uma janela separada se houver muitos
            if len(failed) > 0:
                error_msg = "\n".join(failed[:10])  # Mostra apenas 10 primeiros erros
                if len(failed) > 10:
                    error_msg += f"\n... e mais {len(failed) - 10} erros"
                messagebox.showwarning("Alguns downloads falharam", 
                                     f"Sucesso: {success}/{total}\n\nErros:\n{error_msg}")
        else:
            self.playlist_status.configure(text=f"Sucesso total! {success}/{total} baixados.", 
                                      text_color=THEME["green"])
            messagebox.showinfo("Concluído", f"Todos os MP3s foram salvos em:\n{DOWNLOAD_PATH}")

    # =========================================================================
    # 🖼️ ABA 3: CAPA
    # =========================================================================
    def setup_cover_frame(self):
        f = ctk.CTkFrame(self.container, fg_color="transparent")
        self.frames["cover"] = f
        ctk.CTkLabel(f, text="BUSCAR CAPA (JPG)", font=FONT_HEADER).pack(pady=20)
        self.cover_ent = ctk.CTkEntry(f, width=400, placeholder_text="Digite o nome da música ou artista...")
        self.cover_ent.pack(pady=10)
        ctk.CTkButton(f, text="SALVAR JPG", fg_color=THEME["green"], command=self.save_cover).pack(pady=10)
        self.cover_status = ctk.CTkLabel(f, text="", text_color=THEME["gray"])
        self.cover_status.pack()

    def save_cover(self):
        query = self.cover_ent.get()
        if not query:
            messagebox.showwarning("Aviso", "Digite algo para buscar!")
            return
        self.cover_status.configure(text="Buscando capa...", text_color=THEME["green"])
        threading.Thread(target=self._cover_thread, args=(query,), daemon=True).start()

    def _cover_thread(self, q):
        try:
            opts = {
                'quiet': True,
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android'],
                    }
                }
            }
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(f"ytsearch1:{q}", download=False)['entries'][0]
                thumbnail_url = info.get('thumbnail', '')
                
                if not thumbnail_url:
                    self.after(0, lambda: self.cover_status.configure(
                        text="Nenhuma capa encontrada!", 
                        text_color=THEME["red"]
                    ))
                    return
                
                resp = requests.get(thumbnail_url, timeout=10)
                
                # Converte para JPG
                img = Image.open(BytesIO(resp.content)).convert("RGB")
                
                # Sugere nome baseado na consulta
                safe_name = "".join(c if c.isalnum() else "_" for c in q)[:50]
                initial_file = f"{safe_name}_capa.jpg"
                
                path = filedialog.asksaveasfilename(
                    defaultextension=".jpg",
                    initialfile=initial_file,
                    filetypes=[("JPEG files", "*.jpg"), ("All files", "*.*")]
                )
                
                if path:
                    img.save(path, "JPEG", quality=95)
                    self.after(0, lambda: messagebox.showinfo("Sucesso", f"Capa salva em:\n{path}"))
                    self.after(0, lambda: self.cover_status.configure(
                        text="Capa salva com sucesso!", 
                        text_color=THEME["green"]
                    ))
                else:
                    self.after(0, lambda: self.cover_status.configure(
                        text="Operação cancelada", 
                        text_color=THEME["gray"]
                    ))
                    
        except Exception as e:
            print(f"Erro ao baixar capa: {e}")
            self.after(0, lambda: self.cover_status.configure(
                text=f"Erro: {str(e)[:50]}", 
                text_color=THEME["red"]
            ))
            self.after(0, lambda: messagebox.showerror("Erro", f"Não foi possível baixar a capa:\n{str(e)[:100]}"))

    # =========================================================================
    # ⚙️ ABA 4: CONFIGURAÇÕES (NOVA ABA)
    # =========================================================================
    def setup_settings_frame(self):
        frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.frames["settings"] = frame
        
        ctk.CTkLabel(frame, text="CONFIGURAÇÕES", font=FONT_HEADER, text_color=THEME["green"]).pack(pady=(0, 30))
        
        # Card de configurações
        settings_card = ctk.CTkFrame(frame, fg_color=THEME["card"], corner_radius=15)
        settings_card.pack(fill="x", padx=50, pady=20)
        
        ctk.CTkLabel(settings_card, text="Configurações do Programa", font=FONT_BOLD, text_color=THEME["green"]).pack(pady=(20, 10))
        
        # Seção 1: Local de salvamento
        section1 = ctk.CTkFrame(settings_card, fg_color="transparent")
        section1.pack(fill="x", padx=30, pady=15)
        
        ctk.CTkLabel(section1, text="Local de Salvamento das Músicas", font=FONT_BOLD, text_color=THEME["fg"]).pack(anchor="w")
        
        # Frame para mostrar o caminho atual
        path_frame = ctk.CTkFrame(section1, fg_color=THEME["dark_gray"], height=40)
        path_frame.pack(fill="x", pady=10)
        
        self.current_path_label = ctk.CTkLabel(
            path_frame, 
            text=DOWNLOAD_PATH,
            text_color=THEME["gray"],
            wraplength=400
        )
        self.current_path_label.pack(side="left", padx=15, pady=10)
        
        # Botão para mudar o caminho
        self.btn_change_path = ctk.CTkButton(
            section1, 
            text="MUDAR LOCAL",
            fg_color=THEME["blue"],
            hover_color=THEME["blue_hover"],
            command=self.change_download_path
        )
        self.btn_change_path.pack(pady=(0, 10))
        
        # Seção 2: Configurações de download
        section2 = ctk.CTkFrame(settings_card, fg_color="transparent")
        section2.pack(fill="x", padx=30, pady=15)
        
        ctk.CTkLabel(section2, text="Configurações de Download", font=FONT_BOLD, text_color=THEME["fg"]).pack(anchor="w", pady=(0, 10))
        
        # Delay entre músicas
        delay_frame = ctk.CTkFrame(section2, fg_color="transparent")
        delay_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(delay_frame, text="Delay entre músicas (segundos):", text_color=THEME["gray"], width=200).pack(side="left")
        self.settings_delay_var = ctk.StringVar(value=str(config.get("delay_between_songs", 5)))
        self.settings_delay_entry = ctk.CTkEntry(delay_frame, width=80, textvariable=self.settings_delay_var)
        self.settings_delay_entry.pack(side="right")
        
        # Tentativas
        retry_frame = ctk.CTkFrame(section2, fg_color="transparent")
        retry_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(retry_frame, text="Tentativas por música:", text_color=THEME["gray"], width=200).pack(side="left")
        self.settings_retry_var = ctk.StringVar(value=str(config.get("retry_attempts", 3)))
        self.settings_retry_entry = ctk.CTkEntry(retry_frame, width=80, textvariable=self.settings_retry_var)
        self.settings_retry_entry.pack(side="right")
        
        # Botões de ação
        buttons_frame = ctk.CTkFrame(settings_card, fg_color="transparent")
        buttons_frame.pack(pady=20)
        
        ctk.CTkButton(buttons_frame, text="SALVAR CONFIGURAÇÕES", fg_color=THEME["green"], 
                      hover_color=THEME["green_hover"], command=self.save_settings).pack(side="left", padx=10)
        
        ctk.CTkButton(buttons_frame, text="RESTAURAR PADRÕES", fg_color=THEME["dark_gray"], 
                      hover_color=THEME["gray"], command=self.restore_defaults).pack(side="left", padx=10)
        
        # Seção 3: Informações do sistema
        section3 = ctk.CTkFrame(settings_card, fg_color="transparent")
        section3.pack(fill="x", padx=30, pady=15)
        
        ctk.CTkLabel(section3, text="Informações do Sistema", font=FONT_BOLD, text_color=THEME["fg"]).pack(anchor="w", pady=(0, 10))
        
        # Status do FFmpeg
        ffmpeg_frame = ctk.CTkFrame(section3, fg_color="transparent")
        ffmpeg_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(ffmpeg_frame, text="Status do FFmpeg:", text_color=THEME["gray"], width=150).pack(side="left")
        ffmpeg_status = "✅ OK" if os.path.exists(FFMPEG_EXE) else "❌ NÃO ENCONTRADO"
        ffmpeg_color = THEME["green"] if os.path.exists(FFMPEG_EXE) else THEME["red"]
        ctk.CTkLabel(ffmpeg_frame, text=ffmpeg_status, text_color=ffmpeg_color).pack(side="right")
        
        # Caminho do FFmpeg
        ffmpeg_path_frame = ctk.CTkFrame(section3, fg_color="transparent")
        ffmpeg_path_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(ffmpeg_path_frame, text="Caminho do FFmpeg:", text_color=THEME["gray"], width=150).pack(side="left")
        ffmpeg_path = FFMPEG_EXE if os.path.exists(FFMPEG_EXE) else "Não encontrado"
        ctk.CTkLabel(ffmpeg_path_frame, text=ffmpeg_path, text_color=THEME["gray"], wraplength=300).pack(side="right")

    def update_current_path_display(self):
        """Atualiza a exibição do caminho atual na aba de configurações"""
        config = load_config()
        self.current_path_label.configure(text=config["download_path"])
        
        # Atualiza também as outras abas
        compact_path = self.get_compact_path(config["download_path"])
        if hasattr(self, 'single_path_label'):
            self.single_path_label.configure(text=f"Salvando em: {compact_path}")
        if hasattr(self, 'playlist_path_label'):
            self.playlist_path_label.configure(text=f"Salvando em: {compact_path}")

    def change_download_path(self):
        global DOWNLOAD_PATH
        """Abre uma caixa de diálogo para selecionar nova pasta de downloads"""
        new_path = filedialog.askdirectory(
            title="Selecione onde salvar as músicas",
            initialdir=DOWNLOAD_PATH
        )
        
        if new_path:
            # Salva a nova configuração
            config["download_path"] = new_path
            save_config(config)
            
            # Atualiza a variável global
            DOWNLOAD_PATH = new_path
            
            # Cria a pasta se não existir
            if not os.path.exists(DOWNLOAD_PATH):
                try:
                    os.makedirs(DOWNLOAD_PATH)
                except:
                    messagebox.showerror("Erro", f"Não foi possível criar a pasta:\n{DOWNLOAD_PATH}")
                    return
            
            # Atualiza a exibição
            self.update_current_path_display()
            
            messagebox.showinfo("Sucesso", f"Local de salvamento alterado para:\n{DOWNLOAD_PATH}")

    def save_settings(self):
        """Salva as configurações da aba de configurações"""
        try:
            # Valida e salva as configurações
            delay = max(2, int(self.settings_delay_var.get()))
            retry = min(5, max(1, int(self.settings_retry_var.get())))
            
            config["delay_between_songs"] = delay
            config["retry_attempts"] = retry
            save_config(config)
            
            # Atualiza também os valores nas outras abas
            self.delay_var.set(str(delay))
            self.retry_var.set(str(retry))
            
            messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!")
            
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira valores numéricos válidos!")

    def restore_defaults(self):
        global DOWNLOAD_PATH
        """Restaura as configurações padrão"""
        confirm = messagebox.askyesno(
            "Restaurar Padrões",
            "Tem certeza que deseja restaurar todas as configurações para os valores padrão?"
        )
        
        if confirm:
            default_config = {
                "download_path": DEFAULT_DOWNLOAD_PATH,
                "delay_between_songs": 5,
                "retry_attempts": 3
            }
            
            save_config(default_config)
            
            # Atualiza a interface
            DOWNLOAD_PATH = DEFAULT_DOWNLOAD_PATH
            
            # Cria a pasta padrão se não existir
            if not os.path.exists(DOWNLOAD_PATH):
                try:
                    os.makedirs(DOWNLOAD_PATH)
                except:
                    pass
            
            # Atualiza todos os campos
            self.settings_delay_var.set("5")
            self.settings_retry_var.set("3")
            self.delay_var.set("5")
            self.retry_var.set("3")
            
            self.update_current_path_display()
            
            messagebox.showinfo("Sucesso", "Configurações restauradas para os valores padrão!")

if __name__ == "__main__":
    app = MidnightMusicSuite()
    app.mainloop()
