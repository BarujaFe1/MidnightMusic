```markdown
# 🌙 Midnight Music Suite - MP3 Downloader

![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-ff69b4)

**Midnight Music Suite** é um aplicativo desktop moderno e elegante para baixar músicas em formato MP3 a partir do YouTube. Com uma interface intuitiva e escura (modo noturno), o programa permite buscas individuais, downloads em lote de playlists, extração de capas de álbuns e configurações personalizáveis. Tudo isso com proteções anti-bot para evitar bloqueios do YouTube.

---

## 📋 Índice

- [✨ Funcionalidades](#-funcionalidades)
- [📸 Screenshots](#-screenshots)
- [🚀 Instalação](#-instalação)
  - [Pré-requisitos](#pré-requisitos)
  - [Passo a passo](#passo-a-passo)
  - [Configurando o FFmpeg](#configurando-o-ffmpeg)
- [🎮 Como Usar](#-como-usar)
  - [Aba Música (Busca/Link)](#aba-música-buscalink)
  - [Aba Multi Playlists](#aba-multi-playlists)
  - [Aba Baixar Capa](#aba-baixar-capa)
  - [Aba Configurações](#aba-configurações)
- [⚙️ Configurações Avançadas](#️-configurações-avançadas)
- [📁 Estrutura do Projeto](#-estrutura-do-projeto)
- [🛠️ Tecnologias Utilizadas](#️-tecnologias-utilizadas)
- [🤝 Contribuição](#-contribuição)
- [📄 Licença](#-licença)
- [💖 Agradecimentos](#-agradecimentos)

---

## ✨ Funcionalidades

- **Download de MP3** com qualidade 192 kbps, já com as tags ID3 e capa embutida.
- **Busca inteligente**: digite o nome da música ou cole um link do YouTube.
- **Suporte a playlists**: analise playlists públicas do YouTube e selecione quais músicas baixar.
- **Download em lote** com delay configurável entre as músicas para evitar bloqueios.
- **Extração de capas**: baixe a capa do vídeo em alta qualidade (JPG).
- **Configurações persistentes**: escolha o local de salvamento, delay entre downloads e número de tentativas.
- **Interface moderna** com tema escuro, sidebar e cards estilizados (CustomTkinter).
- **Proteção anti-bot**: uso de delays aleatórios, cliente Android e suporte a cookies para contornar bloqueios do YouTube.
- **Verificação de integridade** do FFmpeg na inicialização.
- **Multi-threading**: downloads em segundo plano sem travar a interface.

---

## 🚀 Instalação

### Pré-requisitos

- **Python 3.7 ou superior** instalado no sistema.
- **FFmpeg** (necessário para conversão e embed de capas).
- Conexão com a internet.

### Passo a passo

1. **Clone o repositório** (ou baixe o ZIP):
   ```bash
   git clone https://github.com/seu-usuario/Midnight-Music-Suite.git
   cd Midnight-Music-Suite
   ```

2. **(Recomendado) Crie um ambiente virtual**:
   ```bash
   python -m venv venv
   # Ative no Windows:
   venv\Scripts\activate
   # No Linux/Mac:
   source venv/bin/activate
   ```

3. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure o FFmpeg** (leia a seção abaixo).

5. **Execute o programa**:
   ```bash
   python MidnightMusic.py
   ```

### Configurando o FFmpeg

O programa **não funciona** sem o FFmpeg. Siga os passos:

1. **Baixe o FFmpeg**:
   - Acesse [ffmpeg.org/download.html](https://ffmpeg.org/download.html) e baixe a versão para Windows (ou seu sistema).
   - Ou use um link direto: [FFmpeg Windows builds](https://www.gyan.dev/ffmpeg/builds/) (baixe o arquivo `ffmpeg-release-full.7z`).

2. **Extraia os arquivos**:
   - Dentro da pasta extraída, localize `bin/ffmpeg.exe` e `bin/ffprobe.exe`.

3. **Copie para a pasta do programa**:
   - Coloque `ffmpeg.exe` e `ffprobe.exe` na mesma pasta onde está `MidnightMusic.py` (ou o executável gerado).

4. **Verifique**:
   - Ao iniciar o programa, a barra lateral mostrará "FFmpeg: OK" em verde.

> **Nota para usuários de Linux/macOS**: você pode instalar o FFmpeg via gerenciador de pacotes (`sudo apt install ffmpeg` no Ubuntu) e alterar o caminho no código, mas o programa espera os executáveis na mesma pasta. Recomenda-se manter a estrutura padrão.

---

## 🎮 Como Usar

### Aba Música (Busca/Link)

1. Na sidebar, clique em **🎵 Música (Busca/Link)**.
2. Digite o nome de uma música ou cole um link do YouTube.
3. Clique em **BAIXAR MP3**.
4. O arquivo será salvo na pasta configurada com o formato `Artista - Título.mp3`.

### Aba Multi Playlists

1. Clique em **📚 Multi Playlists**.
2. **Configurações**:
   - Ajuste o **delay entre músicas** (recomendado: 5 a 10 segundos).
   - Defina o número de **tentativas por música**.
3. Cole os links das playlists (um por linha) na caixa de texto.
4. Clique em **ANALISAR LINKS**.
5. Após a análise, uma lista de músicas aparecerá. Você pode marcar/desmarcar quais deseja baixar.
6. Use os botões **SELECIONAR TODOS** ou **DESMARCAR TODOS** para facilitar.
7. Clique em **BAIXAR LISTA SELECIONADA (MP3)**.
8. O download começará com o delay configurado. O status será exibido na tela.

### Aba Baixar Capa

1. Clique em **🖼️ Baixar Capa**.
2. Digite o nome da música ou artista.
3. Clique em **SALVAR JPG**.
4. O programa buscará a capa do primeiro vídeo encontrado.
5. Escolha onde salvar o arquivo JPG.

### Aba Configurações

1. Clique em **⚙️ Configurações**.
2. **Local de salvamento**: clique em "MUDAR LOCAL" para escolher uma nova pasta.
3. **Configurações de download**: altere o delay padrão e o número de tentativas.
4. Clique em **SALVAR CONFIGURAÇÕES** para persistir as alterações.
5. Para restaurar os valores iniciais, clique em **RESTAURAR PADRÕES**.
6. Na seção **Informações do Sistema**, você pode verificar se o FFmpeg está presente e seu caminho.

---

## ⚙️ Configurações Avançadas

O arquivo de configuração `midnight_config.json` é criado automaticamente na pasta do programa. Você pode editá-lo manualmente:

```json
{
    "download_path": "D:\\Músicas\\Spotify",
    "delay_between_songs": 5,
    "retry_attempts": 3
}
```

- **download_path**: diretório onde os MP3s serão salvos.
- **delay_between_songs**: tempo de espera (em segundos) entre downloads consecutivos.
- **retry_attempts**: número de tentativas para cada música em caso de falha.

Além disso, o código possui parâmetros anti-bot embutidos, como uso de cookies (`cookies.txt`) e seleção de cliente Android. Caso enfrente bloqueios, você pode criar um arquivo `cookies.txt` exportado do seu navegador (extensão Get cookies.txt) e colocá-lo na pasta do programa.

---

## 📁 Estrutura do Projeto

```
Midnight-Music-Suite/
│
├── MidnightMusic.py          # Código principal
├── ffmpeg.exe                  # (necessário, não incluso)
├── ffprobe.exe                 # (necessário, não incluso)
├── midnight_config.json        # Configurações salvas (gerado automaticamente)
├── cookies.txt                 # (opcional) cookies para autenticação
├── requirements.txt            # Dependências Python
├── README.md                   # Este arquivo
└── .gitignore                  # Arquivos ignorados pelo Git
```

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.10+**
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) – GUI moderna com tema escuro.
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) – Download de áudio e vídeo do YouTube.
- [FFmpeg](https://ffmpeg.org/) – Conversão para MP3 e manipulação de metadados.
- [Pillow (PIL)](https://python-pillow.org/) – Processamento de imagens (capas).
- [Requests](https://docs.python-requests.org/) – Download de thumbnails.

---

## 🤝 Contribuição

Contribuições são super bem-vindas! Se você quiser melhorar o projeto:

1. Faça um fork do repositório.
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`).
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`).
4. Push para a branch (`git push origin feature/nova-funcionalidade`).
5. Abra um Pull Request.

Por favor, siga as boas práticas de código e adicione testes quando possível.

---

## 📄 Licença

Este projeto está licenciado sob a **MIT License**. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 💖 Agradecimentos

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) – Pela excelente ferramenta de download.
- [TomSchimansky](https://github.com/TomSchimansky) – Pelo CustomTkinter que deixou a GUI bonita.
- Todos os contribuidores e usuários que testarem e derem feedback.

---

**Feito com 🌙 e muito ☕ por BarujaFE (https://github.com/BarujaFe1).**  
Se gostou, deixe uma ⭐ no repositório!
