import os
import requests
from flask import Flask, render_template_string, request, Response, jsonify

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr" class="h-full bg-slate-950">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StreamPro Cinema & TV Player</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-thumb { background: #6366f1; border-radius: 4px; }
        ::-webkit-scrollbar-track { background: #090d16; }
        .glass-card { background: rgba(15, 23, 42, 0.75); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); }
        .active-tab { background: #4f46e5; color: #ffffff; font-weight: 600; box-shadow: 0 4px 14px rgba(79, 70, 229, 0.4); }
    </style>
</head>
<body class="h-full text-slate-100 font-sans flex flex-col overflow-hidden bg-slate-950">

    <!-- LOGIN MODAL -->
    <div id="loginModal" class="fixed inset-0 bg-slate-950/90 backdrop-blur-xl z-50 flex items-center justify-center p-4">
        <div class="glass-card w-full max-w-md p-8 rounded-3xl shadow-2xl space-y-5 border border-slate-800/80">
            <div class="text-center space-y-2">
                <div class="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-indigo-600/20 text-indigo-400 mb-1 border border-indigo-500/30">
                    <i class="fa-solid fa-play text-2xl"></i>
                </div>
                <h2 class="text-2xl font-extrabold text-white tracking-wide">StreamPro IPTV</h2>
                <p class="text-xs text-slate-400">Üyelik ve sunucu bilgilerinizi girerek bağlanın</p>
            </div>

            <form onsubmit="handleLogin(event)" class="space-y-4">
                <div>
                    <label class="text-[11px] font-semibold text-slate-400 block mb-1 uppercase tracking-wider">Sunucu Adresi</label>
                    <input type="text" id="loginHost" placeholder="http://platindpltn.xyz:8080" required class="w-full bg-slate-900/90 border border-slate-700/60 rounded-xl p-3 text-xs text-white focus:outline-none focus:border-indigo-500 transition">
                </div>
                <div>
                    <label class="text-[11px] font-semibold text-slate-400 block mb-1 uppercase tracking-wider">Kullanıcı Adı</label>
                    <input type="text" id="loginUser" placeholder="Kullanıcı Adı" required class="w-full bg-slate-900/90 border border-slate-700/60 rounded-xl p-3 text-xs text-white focus:outline-none focus:border-indigo-500 transition">
                </div>
                <div>
                    <label class="text-[11px] font-semibold text-slate-400 block mb-1 uppercase tracking-wider">Şifre</label>
                    <div class="relative flex items-center">
                        <input type="password" id="loginPass" placeholder="Şifre" required class="w-full bg-slate-900/90 border border-slate-700/60 rounded-xl p-3 text-xs text-white focus:outline-none focus:border-indigo-500 transition pr-10">
                        <button type="button" onclick="togglePassView()" class="absolute right-3 text-slate-400 hover:text-white text-xs p-1">
                            <i id="passViewIcon" class="fa-solid fa-eye"></i>
                        </button>
                    </div>
                </div>

                <div class="flex items-center justify-between pt-1">
                    <label class="flex items-center space-x-2 cursor-pointer text-xs text-slate-300">
                        <input type="checkbox" id="rememberMe" checked class="rounded border-slate-700 bg-slate-900 text-indigo-600 focus:ring-0">
                        <span>Beni Hatırla</span>
                    </label>
                </div>

                <button type="submit" id="btnLogin" class="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-3 rounded-xl text-xs transition-all shadow-lg shadow-indigo-600/30 flex items-center justify-center space-x-2">
                    <span>Giriş Yap ve Bağlan</span>
                </button>
            </form>
            <div id="loginError" class="hidden text-center text-xs text-rose-400 bg-rose-950/50 p-3 rounded-xl border border-rose-800/50 leading-relaxed"></div>
        </div>
    </div>

    <!-- NAVBAR -->
    <header class="bg-slate-900/90 border-b border-slate-800/80 px-6 py-3.5 flex items-center justify-between z-10 backdrop-blur-md">
        <div class="flex items-center space-x-3">
            <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center text-white shadow-lg shadow-indigo-500/30">
                <i class="fa-solid fa-play text-sm"></i>
            </div>
            <h1 class="font-extrabold text-lg text-white tracking-wider">StreamPro <span class="text-xs font-semibold px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">WEB</span></h1>
        </div>

        <!-- TAB NAVIGATION -->
        <div class="flex bg-slate-950/80 p-1.5 rounded-2xl border border-slate-800 text-xs">
            <button id="tabLive" onclick="switchType('live')" class="px-5 py-2 rounded-xl font-medium transition-all active-tab flex items-center space-x-2">
                <i class="fa-solid fa-tv"></i><span>Canlı TV</span>
            </button>
            <button id="tabMovies" onclick="switchType('movies')" class="px-5 py-2 rounded-xl font-medium transition-all text-slate-400 hover:text-white flex items-center space-x-2">
                <i class="fa-solid fa-film"></i><span>Filmler</span>
            </button>
            <button id="tabSeries" onclick="switchType('series')" class="px-5 py-2 rounded-xl font-medium transition-all text-slate-400 hover:text-white flex items-center space-x-2">
                <i class="fa-solid fa-clapperboard"></i><span>Diziler</span>
            </button>
        </div>

        <button onclick="logout()" class="text-xs bg-slate-800/80 hover:bg-rose-600/20 hover:text-rose-400 border border-slate-700/50 px-4 py-2 rounded-xl text-slate-300 transition flex items-center space-x-2">
            <i class="fa-solid fa-right-from-bracket"></i><span class="hidden sm:inline">Çıkış</span>
        </button>
    </header>

    <!-- MAIN LAYOUT -->
    <div class="flex flex-1 h-[calc(100vh-65px)] overflow-hidden">
        
        <!-- SIDEBAR & CONTENT LIST -->
        <aside class="w-full md:w-96 bg-slate-900/60 border-r border-slate-800/80 flex flex-col h-full z-10">
            <!-- SEARCH & FILTER -->
            <div class="p-4 border-b border-slate-800/80 space-y-3 bg-slate-900/40">
                <div class="relative">
                    <i class="fa-solid fa-magnifying-glass absolute left-3.5 top-3 text-slate-500 text-xs"></i>
                    <input type="text" id="searchInput" oninput="applyFilters()" placeholder="İçerik ara..." class="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500">
                </div>
                <div class="flex space-x-2">
                    <select id="categorySelect" onchange="applyFilters()" class="flex-1 bg-slate-950 border border-slate-800 text-xs text-indigo-300 rounded-xl p-2 focus:outline-none font-semibold truncate">
                        <option value="ALL">Tüm Kategoriler</option>
                        <option value="FAV">★ Favorilerim</option>
                    </select>
                    <select id="sortSelect" onchange="applyFilters()" class="bg-slate-950 border border-slate-800 text-xs text-slate-300 rounded-xl p-2 focus:outline-none">
                        <option value="default">Sırala</option>
                        <option value="az">A-Z</option>
                        <option value="za">Z-A</option>
                    </select>
                </div>
            </div>

            <!-- STREAM LIST CONTAINER -->
            <div id="contentList" class="flex-1 overflow-y-auto p-3 space-y-2">
                <div class="text-center text-xs text-slate-500 py-12 flex flex-col items-center">
                    <i class="fa-solid fa-spinner animate-spin text-2xl text-indigo-500 mb-2"></i>
                    <span>Veriler Yükleniyor...</span>
                </div>
            </div>
        </aside>

        <!-- PLAYER & MAIN DISPLAY -->
        <main class="flex-1 bg-slate-950 flex flex-col relative overflow-hidden">
            <!-- CURRENT PLAYING BAR -->
            <div class="bg-slate-900/80 border-b border-slate-800/80 px-6 py-3 flex items-center justify-between">
                <div class="flex items-center space-x-3 truncate">
                    <div id="currentLogo" class="w-8 h-8 rounded-lg bg-slate-800 flex items-center justify-center overflow-hidden border border-slate-700/50">
                        <i class="fa-solid fa-tv text-slate-500 text-xs"></i>
                    </div>
                    <div class="truncate">
                        <h3 id="currentTitle" class="text-xs font-bold text-white truncate">Yayın Seçilmedi</h3>
                        <p id="currentCategory" class="text-[10px] text-slate-400 truncate">Lütfen listeden bir içerik seçin</p>
                    </div>
                </div>
                <button onclick="toggleFullscreen()" class="text-slate-400 hover:text-white p-2 rounded-lg bg-slate-800/50 border border-slate-700/40 text-xs">
                    <i class="fa-solid fa-expand"></i>
                </button>
            </div>

            <!-- VIDEO CONTAINER -->
            <div class="flex-1 bg-black relative flex items-center justify-center group">
                <video id="videoPlayer" class="w-full h-full object-contain" controls autoplay playsinline></video>
                
                <!-- SPINNER / OVERLAY -->
                <div id="spinner" class="hidden absolute inset-0 bg-slate-950/80 backdrop-blur-sm flex flex-col items-center justify-center z-20">
                    <div class="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
                    <p id="spinnerText" class="text-xs text-slate-300 mt-4 font-medium">Yayın Bağı Kuruluyor...</p>
                </div>
            </div>
        </main>
    </div>

    <script>
        let authData = { host: '', user: '', pass: '' };
        let currentType = 'live';
        let rawItems = [];
        let categories = [];
        let favorites = JSON.parse(localStorage.getItem('iptv_favs') || '[]');
        let hls = null;

        window.onload = () => {
            const saved = localStorage.getItem('iptv_auth');
            if(saved) {
                authData = JSON.parse(saved);
                document.getElementById('loginHost').value = authData.host;
                document.getElementById('loginUser').value = authData.user;
                document.getElementById('loginPass').value = authData.pass;
                fetchData();
            }
        };

        function togglePassView() {
            const passInput = document.getElementById('loginPass');
            const icon = document.getElementById('passViewIcon');
            if(passInput.type === 'password') {
                passInput.type = 'text';
                icon.className = 'fa-solid fa-eye-slash';
            } else {
                passInput.type = 'password';
                icon.className = 'fa-solid fa-eye';
            }
        }

        async function handleLogin(e) {
            e.preventDefault();
            let host = document.getElementById('loginHost').value.trim();
            if(!host.startsWith('http://') && !host.startsWith('https://')) {
                host = 'http://' + host;
            }
            host = host.replace(/\/+$/, "");

            authData = {
                host: host,
                user: document.getElementById('loginUser').value.trim(),
                pass: document.getElementById('loginPass').value.trim()
            };

            if(document.getElementById('rememberMe').checked) {
                localStorage.setItem('iptv_auth', JSON.stringify(authData));
            } else {
                localStorage.removeItem('iptv_auth');
            }

            fetchData();
        }

        async function fetchData() {
            const btn = document.getElementById('btnLogin');
            const err = document.getElementById('loginError');
            err.classList.add('hidden');
            if(btn) btn.innerText = 'Bağlanılıyor...';

            try {
                const catRes = await fetch(`/api/categories?host=${encodeURIComponent(authData.host)}&user=${encodeURIComponent(authData.user)}&pass=${encodeURIComponent(authData.pass)}&type=${currentType}`);
                categories = await catRes.json();

                const streamRes = await fetch(`/api/streams?host=${encodeURIComponent(authData.host)}&user=${encodeURIComponent(authData.user)}&pass=${encodeURIComponent(authData.pass)}&type=${currentType}`);
                const streamData = await streamRes.json();

                if(streamData.error) {
                    throw new Error(streamData.error);
                }

                if(!Array.isArray(streamData) || streamData.length === 0) {
                    throw new Error('Kullanıcı adı, şifre veya sunucu adresi hatalı!');
                }

                rawItems = streamData;

                document.getElementById('loginModal').classList.add('hidden');
                populateCategories();
                applyFilters();

            } catch(e) {
                err.innerText = e.message || 'Giriş Başarısız! Lütfen bilgilerinizi kontrol edin.';
                err.classList.remove('hidden');
            } finally {
                if(btn) btn.innerText = 'Giriş Yap ve Bağlan';
            }
        }

        function populateCategories() {
            const select = document.getElementById('categorySelect');
            select.innerHTML = '<option value="ALL">Tüm Kategoriler</option><option value="FAV">★ Favorilerim</option>';
            if(Array.isArray(categories)) {
                categories.forEach(c => {
                    const opt = document.createElement('option');
                    opt.value = c.category_id;
                    opt.innerText = c.category_name;
                    select.appendChild(opt);
                });
            }
        }

        function switchType(type) {
            currentType = type;
            ['tabLive', 'tabMovies', 'tabSeries'].forEach(id => {
                const el = document.getElementById(id);
                el.className = "px-5 py-2 rounded-xl font-medium transition-all text-slate-400 hover:text-white flex items-center space-x-2";
            });
            
            if(type === 'live') document.getElementById('tabLive').className = "px-5 py-2 rounded-xl font-medium transition-all active-tab flex items-center space-x-2";
            if(type === 'movies') document.getElementById('tabMovies').className = "px-5 py-2 rounded-xl font-medium transition-all active-tab flex items-center space-x-2";
            if(type === 'series') document.getElementById('tabSeries').className = "px-5 py-2 rounded-xl font-medium transition-all active-tab flex items-center space-x-2";

            fetchData();
        }

        function applyFilters() {
            const search = document.getElementById('searchInput').value.toLowerCase();
            const sort = document.getElementById('sortSelect').value;
            const catId = document.getElementById('categorySelect').value;

            let filtered = rawItems.filter(item => {
                const name = (item.name || item.title || '').toLowerCase();
                const matchesSearch = name.includes(search);
                
                let matchesCat = true;
                if(catId === 'FAV') {
                    matchesCat = favorites.includes(getStreamId(item));
                } else if(catId !== 'ALL') {
                    matchesCat = String(item.category_id) === String(catId);
                }
                return matchesSearch && matchesCat;
            });

            if(sort === 'az') {
                filtered.sort((a,b) => (a.name || a.title || '').localeCompare(b.name || b.title || ''));
            } else if(sort === 'za') {
                filtered.sort((a,b) => (b.name || b.title || '').localeCompare(a.name || a.title || ''));
            }

            renderContent(filtered);
        }

        function renderContent(list) {
            const container = document.getElementById('contentList');
            container.innerHTML = '';

            if(list.length === 0) {
                container.innerHTML = '<div class="text-center text-xs text-slate-500 py-10">Hiç içerik bulunamadı.</div>';
                return;
            }

            list.forEach(item => {
                const id = getStreamId(item);
                const isFav = favorites.includes(id);
                const name = item.name || item.title;
                const iconUrl = item.stream_icon || item.cover || '';

                const card = document.createElement('div');
                card.className = 'flex items-center justify-between p-2.5 bg-slate-900/80 hover:bg-indigo-600/20 border border-slate-800/80 hover:border-indigo-500/40 rounded-xl cursor-pointer transition group';
                
                let imgTag = `<div class="w-10 h-10 rounded-lg bg-slate-800/80 border border-slate-700/50 flex items-center justify-center overflow-hidden flex-shrink-0 mr-3">
                                <i class="fa-solid ${currentType === 'live' ? 'fa-tv' : 'fa-film'} text-slate-500 text-xs"></i>
                             </div>`;

                if(iconUrl) {
                    imgTag = `<div class="w-10 h-10 rounded-lg bg-slate-800/80 border border-slate-700/50 overflow-hidden flex-shrink-0 mr-3">
                                <img src="${iconUrl}" onerror="this.onerror=null; this.src='https://via.placeholder.com/40?text=TV';" class="w-full h-full object-cover">
                              </div>`;
                }

                card.innerHTML = `
                    <div class="flex items-center flex-1 min-w-0" onclick="playItem('${id}', '${name.replace(/'/g, "\\'")}', '${iconUrl}')">
                        ${imgTag}
                        <div class="truncate pr-2">
                            <h4 class="text-xs font-medium text-slate-200 group-hover:text-indigo-300 truncate">${name}</h4>
                            <p class="text-[10px] text-slate-500">${currentType.toUpperCase()}</p>
                        </div>
                    </div>
                    <button onclick="toggleFav('${id}', event)" class="text-slate-600 hover:text-amber-400 p-2">
                        <i class="fa-solid fa-star ${isFav ? 'text-amber-400' : ''}"></i>
                    </button>
                `;
                container.appendChild(card);
            });
        }

        function getStreamId(item) {
            return String(item.stream_id || item.series_id || item.vod_id);
        }

        function toggleFav(id, event) {
            event.stopPropagation();
            if(favorites.includes(id)) {
                favorites = favorites.filter(f => f !== id);
            } else {
                favorites.push(id);
            }
            localStorage.setItem('iptv_favs', JSON.stringify(favorites));
            applyFilters();
        }

        function playItem(id, name, logo) {
            document.getElementById('currentTitle').innerText = name;
            document.getElementById('currentCategory').innerText = currentType.toUpperCase();
            
            const logoBox = document.getElementById('currentLogo');
            if(logo) {
                logoBox.innerHTML = `<img src="${logo}" class="w-full h-full object-cover">`;
            } else {
                logoBox.innerHTML = `<i class="fa-solid fa-tv text-slate-500 text-xs"></i>`;
            }

            let ext = 'ts';
            if(currentType === 'movies' || currentType === 'series') ext = 'mp4';

            const streamUrl = `/proxy_stream?host=${encodeURIComponent(authData.host)}&user=${encodeURIComponent(authData.user)}&pass=${encodeURIComponent(authData.pass)}&stream_id=${id}&type=${currentType}&ext=${ext}`;

            const video = document.getElementById('videoPlayer');
            document.getElementById('spinner').classList.remove('hidden');

            if(hls) hls.destroy();

            if (Hls.isSupported() && (currentType === 'live' || ext === 'm3u8')) {
                hls = new Hls();
                hls.loadSource(streamUrl);
                hls.attachMedia(video);
                hls.on(Hls.Events.MANIFEST_PARSED, () => {
                    video.play().catch(()=>{});
                    document.getElementById('spinner').classList.add('hidden');
                });
                hls.on(Hls.Events.ERROR, () => {
                    document.getElementById('spinner').classList.add('hidden');
                });
            } else {
                video.src = streamUrl;
                video.play().catch(()=>{});
                document.getElementById('spinner').classList.add('hidden');
            }
        }

        function toggleFullscreen() {
            const video = document.getElementById('videoPlayer');
            if (video.requestFullscreen) {
                video.requestFullscreen();
            } else if (video.webkitRequestFullscreen) {
                video.webkitRequestFullscreen();
            }
        }

        function logout() {
            localStorage.removeItem('iptv_auth');
            location.reload();
        }
    </script>
</body>
</html>
"""

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Connection': 'keep-alive'
}

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/categories')
def get_categories():
    host = request.args.get('host', '').rstrip('/')
    user = request.args.get('user')
    pass_ = request.args.get('pass')
    type_ = request.args.get('type', 'live')

    action = "get_live_categories"
    if type_ == "movies": action = "get_vod_categories"
    if type_ == "series": action = "get_series_categories"

    url = f"{host}/player_api.php?username={user}&password={pass_}&action={action}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
        return Response(r.content, mimetype='application/json')
    except Exception:
        return jsonify([])

@app.route('/api/streams')
def get_streams():
    host = request.args.get('host', '').rstrip('/')
    user = request.args.get('user')
    pass_ = request.args.get('pass')
    type_ = request.args.get('type', 'live')

    action = "get_live_streams"
    if type_ == "movies": action = "get_vod_streams"
    if type_ == "series": action = "get_series"

    url = f"{host}/player_api.php?username={user}&password={pass_}&action={action}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=20, allow_redirects=True)
        return Response(r.content, mimetype='application/json')
    except Exception as e:
        return jsonify({"error": f"Sunucu hatası: {str(e)}"})

@app.route('/proxy_stream')
def proxy_stream():
    host = request.args.get('host', '').rstrip('/')
    user = request.args.get('user')
    pass_ = request.args.get('pass')
    stream_id = request.args.get('stream_id')
    type_ = request.args.get('type', 'live')
    ext = request.args.get('ext', 'ts')

    if type_ == 'live':
        stream_url = f"{host}/live/{user}/{pass_}/{stream_id}.{ext}"
    elif type_ == 'movies':
        stream_url = f"{host}/movie/{user}/{pass_}/{stream_id}.{ext}"
    else:
        stream_url = f"{host}/series/{user}/{pass_}/{stream_id}.{ext}"

    try:
        req = requests.get(stream_url, headers=HEADERS, stream=True, timeout=20, allow_redirects=True)
        return Response(req.iter_content(chunk_size=16384), content_type=req.headers.get('content-type', 'video/mp2t'))
    except Exception:
        return Response("Yayın Akışı Başarısız", status=500)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
