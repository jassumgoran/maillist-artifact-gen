#!/usr/bin/env python3
# Build the Tournament Mail List artifact HTML from a query-output CSV.
# Usage: build_artifact.py <csv_path> <out_html_path> [snapshot_label]
import json, csv, io, sys

CSV_PATH = sys.argv[1]
OUT      = sys.argv[2]
SNAPSHOT = sys.argv[3] if len(sys.argv) > 3 else "snapshot"

raw = open(CSV_PATH, newline="").read().rstrip("\n") + "\n"  # exact bytes for download
rows = list(csv.reader(io.StringIO(raw)))
header, data = rows[0], rows[1:]

dates = sorted([r[4] for r in data if len(r) > 4 and r[4]])
newest = dates[-1][:10] if dates else "—"
oldest = dates[0][:10] if dates else "—"
count = len(data)

html = r"""<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tournament Mail List</title>
<style>
  :root{
    --bg:#F4F6F7; --surface:#FFFFFF; --surface-2:#FAFBFB; --border:#DEE4E5;
    --text:#16201F; --muted:#5A6765; --faint:#8A9794;
    --accent:#0F766E; --accent-ink:#0B544E; --accent-weak:#DCEEEC;
    --shadow:0 1px 2px rgba(16,32,30,.04),0 8px 24px rgba(16,32,30,.05);
    --mono:ui-monospace,"SF Mono",SFMono-Regular,"JetBrains Mono","Cascadia Code",Menlo,Consolas,monospace;
    --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",system-ui,Roboto,Helvetica,Arial,sans-serif;
  }
  @media (prefers-color-scheme:dark){
    :root{
      --bg:#0E1413; --surface:#161E1D; --surface-2:#131A19; --border:#29312F;
      --text:#E8EDEC; --muted:#94A3A0; --faint:#6B7A77;
      --accent:#2DD4BF; --accent-ink:#5EEAD9; --accent-weak:#10302D;
      --shadow:0 1px 2px rgba(0,0,0,.3),0 8px 28px rgba(0,0,0,.35);
    }
  }
  :root[data-theme="light"]{
    --bg:#F4F6F7; --surface:#FFFFFF; --surface-2:#FAFBFB; --border:#DEE4E5;
    --text:#16201F; --muted:#5A6765; --faint:#8A9794;
    --accent:#0F766E; --accent-ink:#0B544E; --accent-weak:#DCEEEC;
    --shadow:0 1px 2px rgba(16,32,30,.04),0 8px 24px rgba(16,32,30,.05);
  }
  :root[data-theme="dark"]{
    --bg:#0E1413; --surface:#161E1D; --surface-2:#131A19; --border:#29312F;
    --text:#E8EDEC; --muted:#94A3A0; --faint:#6B7A77;
    --accent:#2DD4BF; --accent-ink:#5EEAD9; --accent-weak:#10302D;
    --shadow:0 1px 2px rgba(0,0,0,.3),0 8px 28px rgba(0,0,0,.35);
  }
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--text);font-family:var(--sans);
    line-height:1.5;-webkit-font-smoothing:antialiased;padding:32px 20px 56px}
  .wrap{max-width:1120px;margin:0 auto}

  header.page{display:flex;flex-wrap:wrap;align-items:flex-end;justify-content:space-between;
    gap:16px;margin-bottom:24px}
  .title-block h1{font-size:clamp(22px,3.4vw,30px);font-weight:650;letter-spacing:-.02em;
    margin:0;text-wrap:balance}
  .title-block p{margin:6px 0 0;color:var(--muted);font-size:14px;max-width:62ch}
  .snap{display:inline-flex;align-items:center;gap:8px;font-family:var(--mono);font-size:12.5px;
    color:var(--accent-ink);background:var(--accent-weak);border:1px solid color-mix(in srgb,var(--accent) 24%,transparent);
    padding:7px 12px;border-radius:999px;white-space:nowrap}
  .snap b{font-weight:600}
  .dot{width:7px;height:7px;border-radius:50%;background:var(--accent);box-shadow:0 0 0 3px color-mix(in srgb,var(--accent) 22%,transparent)}

  .stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px}
  @media(max-width:620px){.stats{grid-template-columns:repeat(2,1fr)}}
  .stat{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:14px 16px;box-shadow:var(--shadow)}
  .stat .k{font-size:11px;text-transform:uppercase;letter-spacing:.07em;color:var(--faint);font-weight:600}
  .stat .v{font-family:var(--mono);font-size:24px;font-weight:600;margin-top:5px;font-variant-numeric:tabular-nums;letter-spacing:-.01em}
  .stat .v.small{font-size:16px}

  .toolbar{display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin-bottom:12px}
  .search{position:relative;flex:1 1 280px;min-width:220px}
  .search input{width:100%;font-family:var(--sans);font-size:14px;color:var(--text);
    background:var(--surface);border:1px solid var(--border);border-radius:10px;
    padding:10px 12px 10px 36px;outline:none;transition:border-color .15s,box-shadow .15s}
  .search input:focus{border-color:var(--accent);box-shadow:0 0 0 3px color-mix(in srgb,var(--accent) 20%,transparent)}
  .search svg{position:absolute;left:11px;top:50%;transform:translateY(-50%);color:var(--faint)}
  .actions{display:flex;gap:8px;flex-wrap:wrap}
  button.btn{font-family:var(--sans);font-size:13.5px;font-weight:550;cursor:pointer;
    border-radius:10px;padding:10px 14px;border:1px solid var(--border);background:var(--surface);
    color:var(--text);transition:background .15s,border-color .15s,transform .05s;display:inline-flex;align-items:center;gap:7px}
  button.btn:hover{border-color:var(--faint)}
  button.btn:active{transform:translateY(1px)}
  button.btn.primary{background:var(--accent);border-color:var(--accent);color:#fff}
  :root[data-theme="dark"] button.btn.primary,@media(prefers-color-scheme:dark){}
  button.btn.primary{color:#04100E}
  button.btn:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
  .count{font-family:var(--mono);font-size:12.5px;color:var(--muted);white-space:nowrap}
  .count b{color:var(--text);font-weight:600}

  .tablecard{background:var(--surface);border:1px solid var(--border);border-radius:14px;
    box-shadow:var(--shadow);overflow:hidden}
  .scroll{overflow:auto;max-height:min(66vh,640px)}
  table{border-collapse:collapse;width:100%;font-size:13px}
  thead th{position:sticky;top:0;z-index:2;background:var(--surface-2);text-align:left;
    font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);font-weight:650;
    padding:11px 14px;border-bottom:1px solid var(--border);white-space:nowrap;cursor:pointer;user-select:none}
  thead th .ar{opacity:.0;margin-left:5px;font-size:10px;transition:opacity .12s}
  thead th.sorted .ar{opacity:.85;color:var(--accent-ink)}
  thead th:hover{color:var(--text)}
  tbody td{padding:9px 14px;border-bottom:1px solid var(--border);vertical-align:top}
  tbody tr:last-child td{border-bottom:none}
  tbody tr:hover{background:color-mix(in srgb,var(--accent) 6%,transparent)}
  td.mono,.email{font-family:var(--mono);font-size:12.5px}
  td.email{color:var(--accent-ink);word-break:break-all}
  td.date{font-family:var(--mono);font-size:12px;color:var(--muted);white-space:nowrap;font-variant-numeric:tabular-nums}
  td.dim{color:var(--faint)}
  .idx{font-family:var(--mono);font-size:11.5px;color:var(--faint);text-align:right;font-variant-numeric:tabular-nums;width:1%}
  .empty{padding:40px;text-align:center;color:var(--muted);font-size:14px}

  footer.page{margin-top:18px;color:var(--faint);font-size:12px;display:flex;flex-wrap:wrap;gap:6px 14px;align-items:center}
  footer.page .mono{font-family:var(--mono)}
  .toast{position:fixed;bottom:22px;left:50%;transform:translateX(-50%) translateY(20px);
    background:var(--text);color:var(--bg);font-size:13px;font-weight:550;padding:10px 16px;border-radius:10px;
    opacity:0;pointer-events:none;transition:opacity .2s,transform .2s;z-index:50}
  .toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
  @media(prefers-reduced-motion:reduce){*{transition:none!important}}
</style>

<div class="wrap">
  <header class="page">
    <div class="title-block">
      <h1>Tournament Mail List</h1>
      <p>Registered members, newest first. Shared snapshot &mdash; refreshed in place from the production tournament database.</p>
    </div>
    <span class="snap"><span class="dot"></span>Snapshot&nbsp;<b>__SNAPSHOT__</b></span>
  </header>

  <section class="stats">
    <div class="stat"><div class="k">Total members</div><div class="v" id="s-total">__COUNT__</div></div>
    <div class="stat"><div class="k">Newest signup</div><div class="v small">__NEWEST__</div></div>
    <div class="stat"><div class="k">Earliest in list</div><div class="v small">__OLDEST__</div></div>
    <div class="stat"><div class="k">Columns</div><div class="v small">5 fields</div></div>
  </section>

  <div class="toolbar">
    <div class="search">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="11" cy="11" r="7"></circle><path d="M21 21l-4.3-4.3"></path></svg>
      <input id="q" type="search" placeholder="Filter by email, name or username&hellip;" autocomplete="off" spellcheck="false">
    </div>
    <span class="count">Showing <b id="shown">__COUNT__</b> / __COUNT__</span>
    <div class="actions">
      <button class="btn" id="copy"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="12" height="12" rx="2"></rect><path d="M5 15V5a2 2 0 0 1 2-2h10"></path></svg>Copy emails</button>
      <button class="btn primary" id="dl"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v12"></path><path d="M7 11l5 4 5-4"></path><path d="M5 21h14"></path></svg>Download CSV</button>
    </div>
  </div>

  <div class="tablecard">
    <div class="scroll">
      <table>
        <thead><tr>
          <th class="idx">#</th>
          <th data-key="0">Email<span class="ar"></span></th>
          <th data-key="1">Username<span class="ar"></span></th>
          <th data-key="2">Full name<span class="ar"></span></th>
          <th data-key="3">Display name<span class="ar"></span></th>
          <th data-key="4" class="sorted">Registered<span class="ar">&darr;</span></th>
        </tr></thead>
        <tbody id="tb"></tbody>
      </table>
      <div class="empty" id="empty" hidden>No members match that filter.</div>
    </div>
  </div>

  <footer class="page">
    <span>Source: production <span class="mono">api-tournament</span> &middot; <span class="mono">users</span></span>
    <span>&bull;</span>
    <span>Full overwrite each refresh &mdash; no duplicates, same link</span>
  </footer>
</div>
<div class="toast" id="toast"></div>

<script>
const CSV = __CSV_JSON__;
const HEADERS = __HEADER_JSON__;
// parse embedded CSV (robust enough for quoted fields)
function parseCSV(text){
  const out=[];let row=[],f="",q=false;
  for(let i=0;i<text.length;i++){const c=text[i];
    if(q){ if(c=='"'){ if(text[i+1]=='"'){f+='"';i++;} else q=false;} else f+=c; }
    else{ if(c=='"')q=true; else if(c==','){row.push(f);f="";}
      else if(c=='\n'){row.push(f);out.push(row);row=[];f="";}
      else if(c=='\r'){} else f+=c; } }
  if(f.length||row.length){row.push(f);out.push(row);}
  return out;
}
const all = parseCSV(CSV).slice(1).filter(r=>r.length>1 && r.some(x=>x!==""));
let view = all.slice();
let sortKey = 4, sortDir = -1; // registered desc

const tb=document.getElementById('tb'), empty=document.getElementById('empty'),
      shown=document.getElementById('shown'), qEl=document.getElementById('q');

function esc(s){return (s||"").replace(/[&<>]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[m]));}
function render(){
  const q=qEl.value.trim().toLowerCase();
  view = all.filter(r=> !q || r.join(" ").toLowerCase().includes(q));
  view.sort((a,b)=>{
    const x=(a[sortKey]||""), y=(b[sortKey]||"");
    return x<y?-1*sortDir : x>y?1*sortDir : 0;
  });
  shown.textContent = view.length;
  empty.hidden = view.length>0;
  tb.innerHTML = view.map((r,i)=>{
    const full = r[2] && r[2].trim() ? esc(r[2]) : '<span class="dim">&mdash;</span>';
    const disp = r[3] && r[3].trim() ? esc(r[3]) : '<span class="dim">&mdash;</span>';
    const user = r[1] && r[1].trim() ? esc(r[1]) : '<span class="dim">&mdash;</span>';
    const reg  = r[4] ? esc(r[4].slice(0,19)) : "";
    return `<tr><td class="idx">${i+1}</td><td class="email">${esc(r[0])}</td>`+
           `<td class="mono">${user}</td><td>${full}</td><td>${disp}</td>`+
           `<td class="date">${reg}</td></tr>`;
  }).join("");
}
qEl.addEventListener('input', render);

document.querySelectorAll('thead th[data-key]').forEach(th=>{
  th.addEventListener('click',()=>{
    const k=+th.dataset.key;
    if(k===sortKey) sortDir*=-1; else {sortKey=k; sortDir=1;}
    document.querySelectorAll('thead th').forEach(h=>{h.classList.remove('sorted');const a=h.querySelector('.ar');if(a)a.textContent="";});
    th.classList.add('sorted');
    th.querySelector('.ar').innerHTML = sortDir>0?'&uarr;':'&darr;';
    render();
  });
});

function toast(msg){const t=document.getElementById('toast');t.textContent=msg;t.classList.add('show');
  clearTimeout(t._t);t._t=setTimeout(()=>t.classList.remove('show'),1800);}

document.getElementById('dl').addEventListener('click',()=>{
  const blob=new Blob([CSV],{type:'text/csv'});
  const a=document.createElement('a');a.href=URL.createObjectURL(blob);
  a.download='latest_mail_list.csv';document.body.appendChild(a);a.click();
  a.remove();setTimeout(()=>URL.revokeObjectURL(a.href),1000);
  toast('Downloaded latest_mail_list.csv');
});
document.getElementById('copy').addEventListener('click',async()=>{
  const emails=view.map(r=>r[0]).filter(Boolean).join('\n');
  try{await navigator.clipboard.writeText(emails);toast(`Copied ${view.length} email${view.length===1?'':'s'}`);}
  catch(e){toast('Copy blocked by browser');}
});
render();
</script>
"""

html = (html
    .replace("__CSV_JSON__", json.dumps(raw))
    .replace("__HEADER_JSON__", json.dumps(header))
    .replace("__SNAPSHOT__", SNAPSHOT)
    .replace("__COUNT__", str(count))
    .replace("__NEWEST__", newest)
    .replace("__OLDEST__", oldest))

open(OUT, "w").write(html)
print("wrote", OUT, "| bytes:", len(html), "| members:", count, "| range:", oldest, "->", newest)
