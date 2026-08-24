"""backend/v3/tools/macd_segmentation_template.py — dashboard segmentacji na TYM SAMYM rendererze.

Nie ma tu drugiej implementacji wykresu. Strona bierze zatwierdzony szablon V3.1B i robi
trzy celowane wstrzyknięcia: przełącznik metody w górnym pasku, rysowanie markerów na
panelu MACD oraz linię metody w tooltipie. Reszta renderera (świece, wolumen, EMA, MACD,
RSI, Stochastic, A/D, siatka, crosshair, zoom) pozostaje bez zmian.

Markery segmentacji są wizualnie inne od zatwierdzonych kropek przecięć MACD/Signal
(pusty rombik w kolorze neutralnym vs pełna zielona/czerwona kropka), żeby nie dało się
ich pomylić.
"""

import json

from .chart_validation_template import _PAGE

_SELECTOR = """
    <span id="segbox" style="display:flex;align-items:center;gap:6px;margin-left:14px">
      <span class="dim" style="font-size:11px">Segmentacja:</span>
      <select id="segsel" style="background:#1a1d26;color:#d4d7e0;border:1px solid #262a35;
        border-radius:4px;padding:3px 6px;font:11px 'Segoe UI'">
        <option value="">bez markera historycznego</option>
        <option value="top">poka&#380; najwi&#281;ksze historyczne wychylenie</option>
      </select>
      <span id="segrule" style="font-size:10px;color:#5c6172">segmentacja: wariant B &middot; 0,25 &times; std(MACD)</span>
      <span id="segwarn" style="font-size:10px;color:#5c6172"></span>
    </span>
"""

_MARKER_JS = """
// ---- JEDEN marker: najwieksze historyczne wychylenie MACD (B 0,25) ----
// Lokalne doliny B 0,25 zyja w payloadzie (profil, srednia, mediana, ranking), ale
// NIE sa rysowane. Rysowany jest wylacznie punkt o najwiekszej prominencji, wybrany
// na PELNEJ historii - zoom i zmiana zakresu nie zmieniaja wyboru. Marker domyslnie
// ukryty; wlacza go selektor. Zielone i czerwone kropki przeciec MACD/Signal to
// osobny, zamkniety element kontraktu i pozostaja niezalezne.
 const SEGON=(window.__SEGKEY==='top'),TOPX=(d.top_excursion||null);
 if(SEGON&&TOPX&&TOPX.in_view){const i=TOPX.index_display;
  if(i>=i0&&i<=i1){const v=S.macd[i];
   if(v!=null&&isFinite(v)){const x=xOf(i,i0,i1,W),y=yOf(v,mlo,mhi,P.macd),r=5.0;
    ctx.save();ctx.strokeStyle='#c9a227';ctx.lineWidth=1.6;
    ctx.beginPath();ctx.moveTo(x,y-r);ctx.lineTo(x+r,y);ctx.lineTo(x,y+r);
    ctx.lineTo(x-r,y);ctx.closePath();ctx.stroke();ctx.restore()}}}
 if(SEGON&&TOPX&&!TOPX.in_view){ctx.save();ctx.fillStyle='#c9a227';
  ctx.font='10px Segoe UI';ctx.textAlign='left';
  ctx.fillText('najwieksze historyczne wychylenie poza widocznym oknem \u00b7 '
   +TOPX.date+' \u00b7 MACD '+TOPX.macd.toFixed(3)
   +' \u00b7 prominencja '+TOPX.prominence.toFixed(3),M.l+2,P.macd.y+P.macd.h-4);
  ctx.restore()}
"""

_TIP_JS = """
 const TOP2=(d.top_excursion||null);
 if(window.__SEGKEY==='top'&&TOP2&&TOP2.in_view&&TOP2.index_display===i){
  const b=document.createElement('div');
  b.style.cssText='margin-top:5px;color:#c9a227';
  b.textContent='Najwieksze historyczne wychylenie MACD'
   +'\\n'+TOP2.date
   +'\\nMACD minimum: '+TOP2.macd.toFixed(4)
   +'\\nstd(MACD): '+TOP2.macd_std.toFixed(4)
   +'\\nprog 0,25 x std: '+TOP2.threshold.toFixed(4)
   +'\\nlewe odbicie: '+TOP2.left.toFixed(4)
   +'\\nprawe odbicie: '+TOP2.right.toFixed(4)
   +'\\nprominencja = min(lewe, prawe): '+TOP2.prominence.toFixed(4)
   +'\\nprominencja >= prog: '+(TOP2.prominence>=TOP2.threshold?'TAK':'NIE')
   +'\\n1 z '+TOP2.local_count+' lokalnych dolin';
  el.appendChild(b)}
"""

_INIT_JS = """
// Widocznosc markera: WERSJONOWANY klucz ustawien. Nowa wersja startuje z markerami
// WYLACZONYMI niezaleznie od tego, co uzytkownik mial zapisane wczesniej. Przelacznik
// steruje WYLACZNIE widocznoscia jedynego markera - nie wybiera wariantu segmentacji.
// Warianty diagnostyczne nie istnieja w tym dashboardzie, wiec nie da sie ich przywrocic
// ani przez UI, ani przez storage, ani przez query string.
(function(){const KEY='v3seg.markers.v2',sel=document.getElementById('segsel');
 if(!sel)return;
 try{['v3seg.markers','segkey','__SEGKEY'].forEach(k=>{
  try{localStorage.removeItem(k);sessionStorage.removeItem(k)}catch(e){}})}catch(e){}
 let saved='';try{saved=localStorage.getItem(KEY)||''}catch(e){}
 window.__SEGKEY=(saved==='top')?'top':'';        // domyslnie: bez markerow
 sel.value=window.__SEGKEY;
 sel.onchange=()=>{window.__SEGKEY=(sel.value==='top')?'top':'';
  try{localStorage.setItem(KEY,window.__SEGKEY)}catch(e){}
  render()};
 function sync(){const d=cur(),is1D=!!(d&&d.tf==='1D'),top=(d&&d.top_excursion)||null;
  const w=document.getElementById('segwarn'),optTop=sel.querySelector('option[value="top"]');
  // Bez punktu druga opcja w ogole nie moze byc dostepna do wyboru.
  if(optTop){optTop.disabled=!top;optTop.hidden=!top}
  // Komunikat o wylaczeniu wolno pokazac WYLACZNIE na interwalach intraday.
  if(!is1D){sel.disabled=true;window.__SEGKEY='';sel.value='';
   w.textContent='historyczne wychylenia wylaczone dla tego interwalu';return}
  sel.disabled=!top;                       // 1D z punktem => selektor aktywny
  sel.value=window.__SEGKEY||'';
  if(!top){w.textContent='brak historycznego wychylenia dla tej spolki';return}
  const n=((d.segmentation_overlap||{}).count_local_valleys||0);
  w.textContent=top.in_view
   ?('B 0,25 \u00b7 1 z '+n+' lokalnych dolin')
   :('najwieksze historyczne wychylenie poza widocznym oknem \u00b7 '+top.date);}
 document.querySelectorAll('#top .tf button[data-tf]').forEach(b=>{const prev=b.onclick;
  if(!prev)return;b.onclick=()=>{prev();sync();render()}});
 document.querySelectorAll('#nav .co').forEach(e=>{const prev=e.onclick;
  if(!prev)return;e.onclick=()=>{prev();sync();render()}});
 sync();render();})();
"""


def render_review(payloads, rows, errors, build=None):
    """Strona produkcyjna = szablon V3.1B + selektor widoczności markera.

    Renderuje wyłącznie JEDNO największe historyczne wychylenie MACD (B 0,25),
    domyślnie ukryte. Lokalne doliny zostają w payloadzie do profilu i statystyk.
    """
    build = build or {"build_id": "?", "generated": "?"}
    resolution = []
    seen = set()
    for key in payloads:
        sym = key.split("|")[0]
        if sym in seen:
            continue
        seen.add(sym)
        resolution.append({"requested_name": sym, "symbol": sym, "company_name": "",
                           "exchange": "", "status": "RESOLVED_EXACT"})
    page = _PAGE
    page = page.replace('<span id="build" class="dim">',
                        _SELECTOR + '    <span id="build" class="dim">')
    page = page.replace(" // ---- crosshair przez wszystkie panele ----",
                        _MARKER_JS + " // ---- crosshair przez wszystkie panele ----")
    page = page.replace(" el.style.display='block';\n el.style.left=",
                        _TIP_JS + " el.style.display='block';\n el.style.left=")
    page = page.replace("render();\n</script>", _INIT_JS + "\n</script>")
    page = (page
            .replace("__DATA_JSON__", json.dumps(payloads, ensure_ascii=False))
            .replace("__RES_JSON__", json.dumps(resolution, ensure_ascii=False))
            .replace("__ERR_JSON__", json.dumps(errors, ensure_ascii=False))
            .replace("__BUILD_ID__", str(build["build_id"]))
            .replace("__GENERATED__", str(build["generated"]))
            .replace("<title>V3.1B — Kontrola wykresów rzeczywistych spółek</title>",
                     "<title>V3.2A — Segmentacja dolin MACD (diagnostyka)</title>"))
    return page
