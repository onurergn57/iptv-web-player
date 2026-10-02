import os
from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>StreamPro IPTV Web Player</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-thumb { background: #4f46e5; border-radius: 4px; }
        ::-webkit-scrollbar-track { background: #0f172a; }
    </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen font-sans flex flex-col justify-between overflow-x-hidden">

    <!-- LOGIN MODAL -->
    <div id="loginModal" class="fixed inset-0 bg-slate-950/95 backdrop-blur-md z-50 flex items-center justify-center p-4">
        <div class="bg-slate-900 border border-slate-800 w-full max-w-md p-6 rounded-2xl shadow-2xl space-y-4">
            <div class="text-center space-y-1">
                <div class="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-indigo-600/20 text-indigo-400 mb-2">
                    <i class="fa-solid fa-play text-2xl"></i>
                </div>
                <h2 class="text-xl font-bold text-white">IPTV Hesabınıza Giriş Yapın</h2>
                <p class="text-xs text-slate-400">Sunucu ve üyelik bilgilerinizi giriniz</p>
            </div>

            <form onsubmit="handleLogin(event)" class="space-y-3">
                <div>
                    <label class="text-[11px] font-medium text-slate-400 block mb-1">Sunucu Adresi (URL)</label>
                    <input type="text" id="loginHost" placeholder="http://platindpltn.xyz:8080" required class="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-xs text-white focus:outline-none focus:border-indigo-500">
                </div>
                <div>
                    <label class="text-[11px] font-medium text-slate-400 block mb-1">Kullanıcı Adı</label>
                    <input type="text" id="loginUser" placeholder="Kullanıcı Adı" required class="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-xs text-white focus:outline-none focus:border-indigo-500">
                </div>
                <div>
                    <label class="text-[11px] font-medium text-slate-400 block mb-1">Şifre</label>
                    <div class="relative flex items-center">
                        <input type="password" id="loginPass" placeholder="Şifre" required class="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-xs text-white focus:outline-none focus:border-indigo-500 pr-9">
                        <button type="button" onclick="togglePassView()" class="absolute right-3 text-slate-400 hover:text-white text-xs p-1">
                            <i id="passViewIcon" class="fa-solid fa-eye"></i>
                        </button>
                    </div>
                </div>

                <div class="flex items-center justify-between pt-1">
                    <label class="flex items-center space-x-2 cursor-pointer text-xs text-slate-300">
                        <input type="checkbox" id="rememberMe" checked class="rounded border-slate-700 bg-slate-950 text-indigo-600 focus:ring-0">
                        <span>Beni Hatırla</span>
                    </label>
                </div>

                <button type="submit" id="btnLogin" class="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-2.5 rounded-lg text-xs transition shadow-lg shadow-indigo-600/30 flex items-center justify-center space-x-2">
                    <span>Giriş Yap ve Bağlan</span>
                </button>
            </form>
            <div id="loginError" class="hidden text-center text-xs text-rose-400 bg-rose-950/40 p-2.5 rounded border border-rose-800/50 leading-relaxed"></div>
        </div>
    </div>

    <!-- MAIN HEADER -->
    <header class="bg-slate-900 border-b border-slate-800 px-4 py-3 flex items-center justify-between">
        <div class="flex items-center space-x-3">
            <i class="fa-solid fa-play-circle text-indigo-500 text-2xl"></i>
            <h1 class="font-bold text-base text-white hidden sm:block">StreamPro <span class="text-xs text-indigo-400">Web</span></h1>
        </div>

        <div class="flex bg-slate-950 p-1 rounded-xl border border-slate-800 text-xs">
            <button id="tabLive" onclick="switchType('live')" class="px-3 py-1.5 rounded-lg font-medium transition bg-indigo-600 text-white"><i class="fa-solid fa-tv mr-1.5"></i>Canlı TV</button>
            <button id="tabMovies" onclick="switchType('movies')" class="px-3 py-1.5 rounded-lg font-medium transition text-slate-400 hover:text-white"><i class="fa-solid fa-film mr-1.5"></i>Filmler</button>
            <button id="tabSeries" onclick="switchType('series')" class="px-3 py-1.5 rounded-lg font-medium transition text-slate-400 hover:text-white"><i class="fa-solid fa-clapperboard mr-1.5"></i>Diziler</button>
        </div>

        <button onclick="logout()" class="text-xs bg-slate-800 hover:bg-slate-700 px-3 py-1.5 rounded-lg text-slate-300 transition">
            <i class="fa-solid fa-right-from-bracket mr-1"></i>Çıkış
        </button>
    </header>

    <!-- CONTENT -->
    <div class="flex flex-col md:flex-row flex-1 h-[calc(100vh-60px)]">
        <aside class="w-full md:w-96 bg-slate-900/90 border-r border-slate-800 flex flex-col">
            <div class="p-3 border-b border-slate-800 space-y-2">
                <div class="flex space-x-2">
                    <input type="text" id="searchInput" oninput="applyFilters()" placeholder="İçerik Ara..." class="flex-1 bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-white focus:outline-none">
                    <select id="sortSelect" onchange="applyFilters()" class="bg-slate-950 border border-slate-800 text-xs text-slate-300 rounded-lg p-2 focus:outline-none">
                        <option value="default">Varsayılan</option>
                        <option value="az">A - Z Sırala</option>
                        <option value="za">Z - A Sırala</option>
                    </select>
                </div>
            </div>

            <div class="px-3 pt-2">
                <select id="categorySelect" onchange="applyFilters()" class="w-full bg-slate-950 border border-slate-800 text-xs text-indigo-300 rounded-lg p-2 focus:outline-none font-semibold">
                    <option value="ALL">Tüm Kategoriler</option>
                    <option value="FAV">★ Favorilerim</option>
                </select>
            </div>

            <div id="contentList" class="flex-1 overflow-y-auto p-3 space-y-1">
                <div class="text-center text-xs text-slate-500 py-10">Giriş Yapılıyor...</div>
            </div>
        </aside>

        <main class="flex-1 bg-black relative flex flex-col items-center justify-center">
            <video id="videoPlayer" class="w-full h-full object-contain" controls autoplay playsinline></video>
            <div id="spinner" class="hidden absolute inset-0 bg-black/80 flex flex-col items-center justify-center z-20">
                <div class="w-10 h-10 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
                <p id="spinnerText" class="text-xs text-slate-300 mt-3">Yükleniyor...</p>
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

        async function directFetch(targetUrl) {
            // Doğrudan kullanıcının IP'sinden istek atar. İptv sunucusu CORS engeli verirse güvenli proxy devreye girer.
            try {
                const res = await fetch(targetUrl);
                if(res.ok) return await res.json();
            } catch(e) {}

            // CORS engeli için tarayıcı bazlı alternatif proxy
            const proxyUrl = 'https://corsproxy.io/?' + encodeURIComponent(targetUrl);
            const res2 = await fetch(proxyUrl);
            return await res2.json();
        }

        async function fetchData() {
            const btn = document.getElementById('btnLogin');
            const err = document.getElementById('loginError');
            err.classList.add('hidden');
            if(btn) btn.innerText = 'Bağlanılıyor...';

            let catAction = "get_live_categories";
            let streamAction = "get_live_streams";

            if(currentType === 'movies') { catAction = "get_vod_categories"; streamAction = "get_vod_streams"; }
            if(currentType === 'series') { catAction = "get_series_categories"; streamAction = "get_series"; }

            const catUrl = `${authData.host}/player_api.php?username=${authData.user}&password=${authData.pass}&action=${catAction}`;
            const streamUrl = `${authData.host}/player_api.php?username=${authData.user}&password=${authData.pass}&action=${streamAction}`;

            try {
                categories = await directFetch(catUrl);
                rawItems = await directFetch(streamUrl);

                if(!Array.isArray(rawItems) || rawItems.length === 0) {
                    throw new Error('Kullanıcı adı veya şifre hatalı!');
                }

                document.getElementById('loginModal').classList.add('hidden');
                populateCategories();
                applyFilters();

            } catch(e) {
                err.innerText = 'Giriş Başarısız! Kullanıcı adı/şifre veya sunucu adresini kontrol edin.';
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
                document.getElementById(id).className = "px-3 py-1.5 rounded-lg font-medium transition text-slate-400 hover:text-white";
            });
            if(type === 'live') document.getElementById('tabLive').className = "px-3 py-1.5 rounded-lg font-medium transition bg-indigo-600 text-white";
            if(type === 'movies') document.getElementById('tabMovies').className = "px-3 py-1.5 rounded-lg font-medium transition bg-indigo-600 text-white";
            if(type === 'series') document.getElementById('tabSeries').className = "px-3 py-1.5 rounded-lg font-medium transition bg-indigo-600 text-white";

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

                const div = document.createElement('div');
                div.className = 'flex items-center justify-between p-2.5 bg-slate-800/40 hover:bg-indigo-600/30 rounded-lg cursor-pointer text-xs font-medium transition border border-slate-800/50 group';
                
                div.innerHTML = `
                    <span class="truncate pr-2 text-slate-200 group-hover:text-white" onclick="playItem('${id}')">${name}</span>
                    <button onclick="toggleFav('${id}', event)" class="text-slate-500 hover:text-amber-400 p-1">
                        <i class="fa-solid fa-star ${isFav ? 'text-amber-400' : ''}"></i>
                    </button>
                `;
                container.appendChild(div);
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

        function playItem(id) {
            let ext = 'ts';
            if(currentType === 'movies') ext = 'mp4';
            if(currentType === 'series') ext = 'mp4';

            let typePath = 'live';
            if(currentType === 'movies') typePath = 'movie';
            if(currentType === 'series') typePath = 'series';

            const streamUrl = `${authData.host}/${typePath}/${authData.user}/${authData.pass}/${id}.${ext}`;

            const video = document.getElementById('videoPlayer');
            document.getElementById('spinner').classList.remove('hidden');

            if(hls) hls.destroy();

            if (Hls.isSupported() && currentType === 'live') {
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

        function logout() {
            localStorage.removeItem('iptv_auth');
            location.reload();
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
