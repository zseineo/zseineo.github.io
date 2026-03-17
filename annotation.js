// import { initializeApp } from 'https://www.gstatic.com/firebasejs/11.0.0/firebase-app.js';
// import { getFirestore, doc, setDoc, deleteDoc, getDocs, collection, query, where } from 'https://www.gstatic.com/firebasejs/11.0.0/firebase-firestore.js';

// const firebaseConfig = {
//   apiKey: "AIzaSyBIQuQfJwU909LRqFXVXBSPdRemPvdxmmo",
//   authDomain: "aaannotationsystem.firebaseapp.com",
//   projectId: "aaannotationsystem",
//   storageBucket: "aaannotationsystem.firebasestorage.app",
//   messagingSenderId: "571657337570",
//   appId: "1:571657337570:web:7aa6df8af9cf7415727cbb"
// };

// 套用底色設定
const savedBg = localStorage.getItem('pagebgColor');
if (savedBg) document.body.style.backgroundColor = savedBg;

// const app = initializeApp(firebaseConfig);
// const db = getFirestore(app);

// const pageName = location.pathname.split('/').pop().replace('.html', '');

// const style = document.createElement('style');
// style.textContent = `
//   .anno-line {
//     display: block;
//     cursor: pointer;
//     border-left: 3px solid transparent;
//     padding-left: 4px;
//     transition: background 0.1s;
//   }
//   .anno-line:hover {
//     background: rgba(0, 100, 255, 0.06);
//   }
//   .anno-line.anno-marked {
//     background: rgba(255, 200, 0, 0.2);
//     border-left: 3px solid #f0a500;
//   }
// `;
// document.head.appendChild(style);

// function escapeHtml(text) {
//   return text
//     .replace(/&/g, '&amp;')
//     .replace(/</g, '&lt;')
//     .replace(/>/g, '&gt;');
// }

// async function init() {
//   const pre = document.querySelector('pre');
//   if (!pre) return;

//   const lines = pre.textContent.split('\n');

//   pre.innerHTML = lines.map((line, i) =>
//     `<span id="line-${i}" class="anno-line" data-index="${i}">${escapeHtml(line) || '&nbsp;'}</span>`
//   ).join('');

//   // 載入已有的標記
//   const snap = await getDocs(query(collection(db, 'marks'), where('page', '==', pageName)));
//   snap.forEach(d => {
//     const el = document.getElementById(`line-${d.data().lineIndex}`);
//     if (el) el.classList.add('anno-marked');
//   });

//   // 點擊切換標記
//   pre.addEventListener('click', async e => {
//     const span = e.target.closest('.anno-line');
//     if (!span) return;

//     const index = parseInt(span.dataset.index);
//     const docId = `${pageName}_line_${index}`;
//     const docRef = doc(db, 'marks', docId);

//     if (span.classList.contains('anno-marked')) {
//       await deleteDoc(docRef);
//       span.classList.remove('anno-marked');
//     } else {
//       await setDoc(docRef, {
//         page: pageName,
//         lineIndex: index,
//         lineContent: lines[index].trim().slice(0, 120),
//         timestamp: new Date().toISOString()
//       });
//       span.classList.add('anno-marked');
//     }
//   });

//   // 跳到 hash 指定的行
//   if (location.hash) {
//     const el = document.querySelector(location.hash);
//     if (el) setTimeout(() => el.scrollIntoView({ behavior: 'smooth', block: 'center' }), 300);
//   }
// }

// init();
