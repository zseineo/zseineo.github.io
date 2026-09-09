/* sidebar.js — AA 作品通用側邊欄
 *
 * 用法：在章節 HTML 的 </body> 前加一行（相對路徑依檔案深度）：
 *     <script src="../../sidebar.js" defer></script>
 *
 * 章節清單來源：同層或上一層的 index.html。
 * 不另建 list.json —— index.html 由 update.sh 維護，是唯一真實來源。
 *
 * ★ 本腳本只在 <body> 尾端 append 元素，
 *   絕不讀取、修改、或以任何方式觸碰 <pre> 的內容。
 */
(function () {
  'use strict';

  var NS = 'aa-sb';
  var LS_OPEN = 'aaSidebarOpen';

  // ── 路徑工具 ────────────────────────────────────────────────
  // 取得 URL 的目錄部分（含結尾斜線），decode 後才能與本頁比對
  function dirOf(pathname) {
    return decodeURIComponent(pathname.replace(/[^/]*$/, ''));
  }

  var here = new URL(location.href);
  var hereDir = dirOf(here.pathname);
  var hereFile = decodeURIComponent(here.pathname);

  // ── 從 index.html 抽出「與本頁同目錄」的章節連結 ──────────────
  // 正式作品：index.html 在同層，href = "檔名.html"
  // working ：index.html 在上一層，href = "子資料夾/檔名.html"
  // 兩者都靠「解析成絕對路徑後比對目錄」處理，順便自動濾掉別部作品。
  function collectItems(anchors, indexUrl) {
    var items = [];
    for (var i = 0; i < anchors.length; i++) {
      var a = anchors[i];
      var raw = a.getAttribute('href');
      if (!raw || !/\.html?$/i.test(raw)) continue;
      if (/^[a-z]+:/i.test(raw) || raw.charAt(0) === '#') continue;

      var abs;
      try {
        abs = new URL(raw, indexUrl);
      } catch (e) {
        continue;
      }
      if (dirOf(abs.pathname) !== hereDir) continue;

      items.push({
        anchor: a,
        href: abs.href,
        path: decodeURIComponent(abs.pathname),
        label: (a.textContent || '').trim() || raw
      });
    }
    return items;
  }

  function parseIndex(html, indexUrl) {
    var doc = new DOMParser().parseFromString(html, 'text/html');
    var items = collectItems(doc.querySelectorAll('a[href]'), indexUrl);
    if (!items.length) return null;

    // 標題：優先用包住這些連結的 <details><summary>（working 的分組），
    // 其次 index 的 <h1>，最後退回 <title>
    var title = '';
    var det = items[0].anchor.closest ? items[0].anchor.closest('details') : null;
    if (det) {
      var sum = det.querySelector('summary');
      if (sum) title = sum.textContent.trim();
    }
    if (!title) {
      var h1 = doc.querySelector('h1');
      if (h1) title = h1.textContent.trim();
    }
    if (!title && doc.title) title = doc.title.trim();

    items.forEach(function (it) { delete it.anchor; });
    return { items: items, title: title || '目錄', indexUrl: indexUrl };
  }

  // 依序試同層、上一層的 index.html，取第一個有同目錄章節的
  function loadIndex() {
    return ['index.html', '../index.html'].reduce(function (chain, rel) {
      return chain.then(function (found) {
        if (found) return found;
        var url = new URL(rel, here.href).href;
        return fetch(url)
          .then(function (r) { return r.ok ? r.text() : null; })
          .then(function (t) { return t ? parseIndex(t, url) : null; })
          .catch(function () { return null; });
      });
    }, Promise.resolve(null));
  }

  // ── 樣式 ────────────────────────────────────────────────────
  var CSS = [
    '.' + NS + '-root{position:fixed;top:0;right:0;z-index:2147483000;',
    'font-family:system-ui,-apple-system,"Segoe UI","Noto Sans TC",sans-serif;',
    'font-size:14px;line-height:1.5;color:#333;}',

    '.' + NS + '-toggle{position:fixed;top:10px;right:10px;z-index:2147483001;',
    'width:44px;height:44px;border:0;border-radius:10px;',
    'background:rgba(33,37,43,.88);color:#fff;cursor:pointer;',
    'display:flex;align-items:center;justify-content:center;padding:0;',
    'box-shadow:0 2px 10px rgba(0,0,0,.3);-webkit-tap-highlight-color:transparent;}',
    '.' + NS + '-toggle:hover{background:rgba(33,37,43,1);}',
    '.' + NS + '-toggle i{display:block;width:18px;height:2px;background:currentColor;',
    'position:relative;border-radius:2px;}',
    '.' + NS + '-toggle i::before,.' + NS + '-toggle i::after{content:"";position:absolute;',
    'left:0;width:18px;height:2px;background:currentColor;border-radius:2px;}',
    '.' + NS + '-toggle i::before{top:-6px;}',
    '.' + NS + '-toggle i::after{top:6px;}',

    '.' + NS + '-panel{position:fixed;top:0;right:0;height:100%;width:320px;max-width:85vw;',
    'background:#fff;border-left:1px solid #ddd;box-shadow:-2px 0 12px rgba(0,0,0,.12);',
    'display:flex;flex-direction:column;',
    'transform:translateX(101%);transition:transform .18s ease-out;z-index:2147483000;}',
    '.' + NS + '-root.is-open .' + NS + '-panel{transform:translateX(0);}',

    '.' + NS + '-head{padding:14px 64px 10px 14px;border-bottom:1px solid #eee;flex:0 0 auto;}',
    '.' + NS + '-title{font-weight:700;font-size:15px;margin:0 0 8px;word-break:break-word;}',
    '.' + NS + '-links{display:flex;gap:12px;flex-wrap:wrap;font-size:12px;}',
    '.' + NS + '-links a{color:#0066cc;text-decoration:none;}',
    '.' + NS + '-links a:hover{text-decoration:underline;}',

    '.' + NS + '-nav{display:flex;gap:8px;padding:10px 14px;border-bottom:1px solid #eee;flex:0 0 auto;}',
    '.' + NS + '-nav a,.' + NS + '-nav span{flex:1 1 0;min-width:0;text-align:center;',
    'padding:8px 6px;border:1px solid #ddd;border-radius:6px;font-size:13px;',
    'text-decoration:none;color:#0066cc;background:#fafafa;',
    'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}',
    '.' + NS + '-nav a:hover{background:#f0f6ff;}',
    '.' + NS + '-nav span{color:#bbb;background:#f5f5f5;}',

    '.' + NS + '-filter{padding:10px 14px 6px;flex:0 0 auto;}',
    '.' + NS + '-filter input{width:100%;box-sizing:border-box;padding:7px 10px;',
    'font-size:13px;border:1px solid #ddd;border-radius:6px;background:#fff;',
    'color:#333;font-family:inherit;}',

    '.' + NS + '-count{padding:2px 14px 6px;font-size:12px;color:#999;flex:0 0 auto;}',

    '.' + NS + '-list{flex:1 1 auto;overflow-y:auto;overscroll-behavior:contain;',
    '-webkit-overflow-scrolling:touch;padding:0 0 16px;margin:0;list-style:none;}',
    '.' + NS + '-list li{margin:0;}',
    '.' + NS + '-list a{display:block;padding:7px 14px;text-decoration:none;color:#0066cc;',
    'word-break:break-word;border-left:3px solid transparent;}',
    '.' + NS + '-list a:visited{color:#663399;}',
    '.' + NS + '-list a:hover{background:#f3f7ff;}',
    '.' + NS + '-list a.is-current{background:#fff8e1;border-left-color:#ffc107;',
    'color:#333;font-weight:700;}',

    '.' + NS + '-backdrop{position:fixed;top:0;left:0;right:0;bottom:0;',
    'background:rgba(0,0,0,.28);opacity:0;pointer-events:none;',
    'transition:opacity .18s ease-out;z-index:2147482999;}',
    '.' + NS + '-root.is-open .' + NS + '-backdrop{opacity:1;pointer-events:auto;}',
    '@media (min-width:900px){.' + NS + '-root.is-open .' + NS + '-backdrop',
    '{opacity:0;pointer-events:none;}}',

    '@media print{.' + NS + '-root,.' + NS + '-toggle{display:none !important;}}'
  ].join('');

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  function build(data) {
    var style = el('style');
    style.textContent = CSS;
    document.head.appendChild(style);

    var root = el('div', NS + '-root');
    var backdrop = el('div', NS + '-backdrop');
    var panel = el('div', NS + '-panel');

    // 目前章節在清單中的位置
    var cur = -1;
    for (var i = 0; i < data.items.length; i++) {
      if (data.items[i].path === hereFile) { cur = i; break; }
    }

    function countText() {
      return cur >= 0
        ? '第 ' + (cur + 1) + ' / ' + data.items.length + ' 話'
        : '共 ' + data.items.length + ' 話';
    }

    // 標頭
    var head = el('div', NS + '-head');
    head.appendChild(el('div', NS + '-title', data.title));
    var links = el('div', NS + '-links');
    var toIndex = el('a', null, '← 完整目錄');
    toIndex.href = data.indexUrl;
    var toHome = el('a', null, '⌂ 首頁');
    toHome.href = new URL('../../', data.indexUrl).href;
    links.appendChild(toIndex);
    links.appendChild(toHome);
    head.appendChild(links);
    panel.appendChild(head);

    // 上一話 / 下一話
    var nav = el('div', NS + '-nav');
    function navBtn(idx, label) {
      if (cur >= 0 && idx >= 0 && idx < data.items.length) {
        var a = el('a', null, label);
        a.href = data.items[idx].href;
        a.title = data.items[idx].label;
        return a;
      }
      return el('span', null, label);
    }
    nav.appendChild(navBtn(cur - 1, '← 上一話'));
    nav.appendChild(navBtn(cur + 1, '下一話 →'));
    panel.appendChild(nav);

    // 篩選
    var filterWrap = el('div', NS + '-filter');
    var input = el('input');
    input.type = 'search';
    input.placeholder = '篩選章節…';
    filterWrap.appendChild(input);
    panel.appendChild(filterWrap);

    var count = el('div', NS + '-count', countText());
    panel.appendChild(count);

    // 章節列表
    var list = el('ul', NS + '-list');
    var currentLink = null;
    data.items.forEach(function (it, idx) {
      var li = el('li');
      var a = el('a', null, it.label);
      a.href = it.href;
      if (idx === cur) {
        a.className = 'is-current';
        a.setAttribute('aria-current', 'page');
        currentLink = a;
      }
      li.appendChild(a);
      list.appendChild(li);
    });
    panel.appendChild(list);

    input.addEventListener('input', function () {
      var q = input.value.trim().toLowerCase();
      var shown = 0;
      var lis = list.children;
      for (var i = 0; i < lis.length; i++) {
        var hit = !q || data.items[i].label.toLowerCase().indexOf(q) !== -1;
        lis[i].hidden = !hit;
        if (hit) shown++;
      }
      count.textContent = q ? '符合 ' + shown + ' 話' : countText();
    });

    // 開關按鈕
    var toggle = el('button', NS + '-toggle');
    toggle.type = 'button';
    toggle.setAttribute('aria-label', '章節目錄');
    toggle.appendChild(el('i'));

    function setOpen(open, remember) {
      root.classList.toggle('is-open', open);
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      if (remember) {
        try { localStorage.setItem(LS_OPEN, open ? '1' : '0'); } catch (e) { /* 隱私模式 */ }
      }
      if (open && currentLink) currentLink.scrollIntoView({ block: 'center' });
    }

    toggle.addEventListener('click', function () {
      setOpen(!root.classList.contains('is-open'), true);
    });
    backdrop.addEventListener('click', function () { setOpen(false, true); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && root.classList.contains('is-open')) setOpen(false, true);
    });

    root.appendChild(backdrop);
    root.appendChild(panel);
    document.body.appendChild(root);
    document.body.appendChild(toggle);

    // 手機一律預設收起，避免遮住 AA；桌機沿用上次狀態
    var remembered = null;
    try { remembered = localStorage.getItem(LS_OPEN); } catch (e) { /* 隱私模式 */ }
    setOpen(remembered === '1' && window.innerWidth >= 900, false);
  }

  function start() {
    loadIndex().then(function (data) {
      if (data) build(data);   // 找不到目錄就安靜地什麼都不做
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();
