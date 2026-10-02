import os
import requests
from flask import Flask, render_template_string, request, Response

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StreamPro Web Player</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-thumb { background: #4f46e5; border-radius: 4px; }
    </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen font-sans flex flex-col overflow-hidden">

    <header class="bg-slate-900/90 border-b border-slate-800 px-4 py-3 flex items-center justify-between">
        <div class="flex items-center space-x-2">
            <i class="fa-solid fa-play-circle text-indigo-500 text-2xl"></i>
            <h1 class="font-bold text-lg text-white">StreamPro <span class="text-xs text-indigo-400">Web Player</span></h1>
        </div>
        <div id="statusLabel" class="text-xs text-slate-400 font-medium">Bağlantı Yok</div>
    </header>

    <div class="flex flex-col md:flex-row flex-1 h-[calc(100vh-57px)]">
        <!-- Sidebar / Sol Panel -->
        <aside class="w-full md:w-80 bg-slate-900/80 border-r border-slate-800 p-3 flex flex-col space-y-3">
            <div class="space-y-2 bg-slate-950/60 p-3 rounded-xl border border-slate-800">
                <input type="text" id="host" placeholder="Sunucu Adresi (http://sunucu:8080)" class="w-full bg-slate-900 border border-slate-700/80 rounded-lg p-2 text-xs text-white focus:outline-none focus:border-indigo-500">
                <input type="text" id="user" placeholder="Kullanıcı Adı" class="w-full bg-slate-900 border border-slate-700/80 rounded-lg p-2 text-xs text-white focus:outline-none focus:border-indigo-500">
                <div class="relative flex items-center">
                    <input type="password" id="pass" placeholder="Şifre" class="w-full bg-slate-900 border border-slate-700/80 rounded-lg p-2 text-xs text-white focus:outline-none focus:border-indigo-500 pr-8">
                    <button type="button" onclick="togglePass()" class="absolute right-2 text-slate-400 hover:text-white p-1 text-xs">
                        <i id="passIcon" class="fa-solid fa-eye"></i>
                    </button>
                </div>
                <button onclick="loadStreams()" class="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-2 rounded-lg text-xs transition shadow-lg shadow-indigo-600/30">
                    Giriş Yap ve Yükle
                </button>
            </div>

            <input type="text" id="searchInput" oninput="filterChannels()" placeholder="Kanal Ara..." class="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-white focus:outline-none">

            <div id="channelList" class="flex-1 overflow-y-auto space-y-1 pr-1">
                <div class="text-center text-xs text-slate-500 py-10">Lütfen IPTV bilgilerinizi girip Giriş Yap butonuna basın.</div>
            </div>
        </aside>

        <!-- Video Player / Sağ Panel -->
        <main class="flex-1 bg-black relative flex items-center justify-center">
            <video id="videoPlayer" class="w-full h-full object-contain" controls autoplay playsinline></video>
            
            <div id="spinner" class="hidden absolute inset-0 bg-black/80 flex flex-col items-center justify-center z-20">
                <div class="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
                <p id="spinnerText" class="text-xs text-slate-300 mt-3">Yükleniyor...</p>
            </div>
        </main>
    </div>

    <script>
        let rawChannels = [];
        let hls = null;

        function togglePass() {
            const input = document.getElementById('pass');
            const icon = document.getElementById('passIcon');
            if(input.type === 'password') {
                input.type = 'text';
                icon.className = 'fa-solid fa-eye-slash';
            } else {
                input.type = 'password';
                icon.className = 'fa-solid fa-eye';
            }
        }

        async function loadStreams() {
            const host = document.getElementById('host').value.trim();
            const user = document.getElementById('user').value.trim();
            const pass = document.getElementById('pass').value.trim();

            if(!host || !user || !pass) {
                alert('Lütfen tüm alanları doldurun!');
                return;
            }

            document.getElementById('spinnerText').innerText = 'Kanallar Çekiliyor...';
            document.getElementById('spinner').classList.remove('hidden');

            try {
                const res = await fetch(`/api/channels?host=${encodeURIComponent(host)}&user=${user}&pass=${pass}`);
                rawChannels = await res.json();
                
                if(rawChannels.length === 0) {
                    alert('Kanal bulunamadı veya bilgiler hatalı!');
                } else {
                    document.getElementById('statusLabel').innerText = 'Bağlandı (' + rawChannels.length + ' Kanal)';
                    renderChannels(rawChannels);
                    localStorage.setItem('saved_iptv_data', JSON.stringify({host, user, pass}));
                }
            } catch(e) {
                alert('Sunucuya bağlanılamadı!');
            } finally {
                document.getElementById('spinner').classList.add('hidden');
            }
        }

        function renderChannels(list) {
            const container = document.getElementById('channelList');
            container.innerHTML = '';
            
            list.forEach(item => {
                const div = document.createElement('div');
                div.className = 'p-2.5 bg-slate-800/40 hover:bg-indigo-600/30 rounded-lg cursor-pointer text-xs font-medium text-slate-200 hover:text-white transition truncate border border-slate-800/50';
                div.innerText = item.name;
                div.onclick = () => playChannel(item.stream_id);
                container.appendChild(div);
            });
        }

        function filterChannels() {
            const q = document.getElementById('searchInput').value.toLowerCase();
            renderChannels(rawChannels.filter(c => c.name.toLowerCase().includes(q)));
        }

        function playChannel(streamId) {
            const host = document.getElementById('host').value.trim();
            const user = document.getElementById('user').value.trim();
            const pass = document.getElementById('pass').value.trim();
            const streamUrl = `/proxy_stream?host=${encodeURIComponent(host)}&user=${user}&pass=${pass}&stream_id=${streamId}`;

            const video = document.getElementById('videoPlayer');
            document.getElementById('spinner').classList.remove('hidden');
            document.getElementById('spinnerText').innerText = 'Yayın Başlatılıyor...';

            if(hls) hls.destroy();

            if (Hls.isSupported()) {
                hls = new Hls();
                hls.loadSource(streamUrl);
                hls.attachMedia(video);
                hls.on(Hls.Events.MANIFEST_PARSED, () => {
                    video.play().catch(() => {});
                    document.getElementById('spinner').classList.add('hidden');
                });
                hls.on(Hls.Events.ERROR, () => {
                    document.getElementById('spinner').classList.add('hidden');
                });
            } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
                video.src = streamUrl;
                video.play();
                document.getElementById('spinner').classList.add('hidden');
            }
        }

        window.onload = () => {
            const saved = localStorage.getItem('saved_iptv_data');
            if(saved) {
                const {host, user, pass} = JSON.parse(saved);
                document.getElementById('host').value = host;
                document.getElementById('user').value = user;
                document.getElementById('pass').value = pass;
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/channels')
def get_channels():
    host = request.args.get('host', '').rstrip('/')
    user = request.args.get('user')
    pass_ = request.args.get('pass')
    url = f"{host}/player_api.php?username={user}&password={pass_}&action=get_live_streams"
    try:
        r = requests.get(url, timeout=12)
        return Response(r.text, mimetype='application/json')
    except Exception as e:
        return Response("[]", mimetype='application/json')

@app.route('/proxy_stream')
def proxy_stream():
    host = request.args.get('host', '').rstrip('/')
    user = request.args.get('user')
    pass_ = request.args.get('pass')
    stream_id = request.args.get('stream_id')
    stream_url = f"{host}/live/{user}/{pass_}/{stream_id}.ts"
    
    try:
        req = requests.get(stream_url, stream=True, timeout=15)
        return Response(req.iter_content(chunk_size=4096), content_type=req.headers.get('content-type', 'video/mp2t'))
    except Exception as e:
        return Response("Yayın Hatası", status=500)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
