"""backend/v3/tools/chart_validation_template.py — HTML dashboardu V3.1B-UI.

Samowystarczalny plik (dane osadzone w <script>, zero fetch po wygenerowaniu, zero CDN,
zero nowych zależności — rendering własnym canvas). Charakter: terminal wykresowy,
ergonomicznie zbliżony do TradingView: dominujący panel ceny ze świecami, wolumenem,
EMA 20/50/100 i linią ostatniego zamknięcia, pod spodem wyraźnie oddzielone panele
MACD / RSI / Stochastic / Akumulacja-Dystrybucja na wspólnej osi czasu, wspólny
crosshair, zoom i pan.

Warstwa renderera niczego nie liczy — wszystkie wartości, w tym EMA i A/D (kontekst
wizualny), pochodzą z payloadu zbudowanego na canonical danych. Poziomy 70/50/30 (RSI)
i 80/50/20 (Stochastic) oraz wypełnienia przy wyjściu RSI poza kanał są WYŁĄCZNIE
prowadnicami wizualnymi: nie są progiem, eventem, cechą ani scoringiem. Nie ma pełnych
pasów tła 70–100 i 0–30 — kolor pojawia się tylko tam, gdzie linia RSI faktycznie
wychodzi poza kanał. Zero BUY/SELL, zero interpretacji.
"""

import json

_PAGE = """<!DOCTYPE html>
<html lang="pl"><head><meta charset="utf-8">
<title>Wykresy walidacyjne — V3.1B</title>
<style>
:root{--bg:#0f1218;--bg2:#141822;--border:#232838;--text:#c9cdd8;--dim:#6b7183;
--up:#26a69a;--dn:#ef5350;--macd:#4a8fff;--sig:#ff9330;--rsi:#b39ddb;--rsih:#c9a227;
--k:#4dd0e1;--d:#ff8a65;--cool:rgba(74,143,255,.055);--warm:rgba(239,83,80,.055);
--price:#e3e6ee}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--text);font:12px/1.4 'Segoe UI',Arial,sans-serif;
display:flex;height:100vh;overflow:hidden}
#nav{width:172px;min-width:172px;background:var(--bg2);border-right:1px solid var(--border);
display:flex;flex-direction:column;overflow-y:auto}
#nav h1{font-size:10px;letter-spacing:.09em;padding:9px 11px 5px;color:var(--dim);font-weight:700}
#nav .co{padding:4px 11px;cursor:pointer;display:flex;justify-content:space-between;gap:6px;
line-height:1.35}
#nav .co:hover{background:#1d2231}
#nav .co.active{background:#1b2a4a;box-shadow:inset 2px 0 0 var(--macd)}
#nav .co small{color:var(--dim)}
#nav .co.active small{color:var(--price)}
#nav .bad{color:#8a5a5a;cursor:default}
#main{flex:1;display:flex;flex-direction:column;min-width:0}
#top{display:flex;align-items:center;gap:12px;padding:6px 12px;background:var(--bg2);
border-bottom:1px solid var(--border)}
#top b{font-size:14px;color:var(--price);letter-spacing:.02em;flex:0 0 auto}
#tName{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
#top .dim{color:var(--dim)}
#build{margin-left:auto;font-size:11px;letter-spacing:.02em;flex:0 1 auto;min-width:0;
overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
#top .sp{flex:1}
/* Pasek interwalow NIE moze sie kurczyc: flex:0 0 auto + overflow:visible.
   Wczesniej overflow:hidden (dla zaokraglonych naroznikow) wycinal ostatnie przyciski,
   gdy #top brakowalo miejsca - 4H i 1D znikaly bez sladu. Zaokraglenie robia teraz
   skrajne przyciski, wiec zadny interwal nie moze zostac obciety ani ukryty. */
.tf{display:flex;flex:0 0 auto;border:1px solid var(--border);border-radius:3px;
overflow:visible}
.tf button{background:none;border:0;color:var(--dim);padding:3px 10px;cursor:pointer;
flex:0 0 auto;white-space:nowrap;font-weight:700;font-size:11px}
.tf button:first-child{border-radius:2px 0 0 2px}
.tf button:last-child{border-radius:0 2px 2px 0}
.tf button.on{background:var(--macd);color:#fff}
#reset{background:none;border:1px solid var(--border);color:var(--dim);border-radius:3px;
flex:0 0 auto;white-space:nowrap;
padding:3px 9px;cursor:pointer;font-size:11px}
#reset:hover{color:var(--text)}
#charts{flex:1;position:relative;min-height:0;cursor:crosshair}
canvas{position:absolute;inset:0;width:100%;height:100%}
#tip{position:absolute;pointer-events:none;background:#0b0e14ee;border:1px solid var(--border);
border-radius:3px;padding:5px 7px;font-size:11px;line-height:1.5;white-space:pre;z-index:5;
display:none;color:var(--text)}
#side{width:236px;min-width:236px;background:var(--bg2);border-left:1px solid var(--border);
overflow-y:auto;padding:8px 11px;font-size:11px}
#side h2{font-size:9.5px;letter-spacing:.09em;color:var(--dim);margin:9px 0 3px;font-weight:700}
#side table{width:100%;border-collapse:collapse}
#side td{padding:1.5px 0}
#side td:first-child{color:var(--dim)}
#side td:last-child{text-align:right;font-variant-numeric:tabular-nums;color:var(--text)}
#side .big{font-size:12px}
#resbox{margin-top:12px;padding-top:8px;border-top:1px solid var(--border);color:var(--dim);
font-size:10px}
#resbox table td{padding:1px 0}
.err{color:var(--dn)} .ok{color:var(--up)}
</style></head><body>
<div id="nav"><h1>SPÓŁKI</h1><div id="colist"></div></div>
<div id="main">
  <div id="top"><b id="tSym">—</b><span id="tName" class="dim"></span>
    <span id="tExch" class="dim"></span>
    <div class="tf"><button id="b30m" data-tf="30m">30m</button><button id="b1h" data-tf="1H">1H</button><button id="b2h" data-tf="2H">2H</button><button id="b4h" data-tf="4H">4H</button><button id="b1d" data-tf="1D" class="on">1D</button></div>
    <button id="reset">Reset widoku</button>
    <span id="build" class="dim">BUILD __BUILD_ID__ · __GENERATED__</span>
    <span class="sp"></span><span id="tStatus" class="dim"></span></div>
  <div id="charts"><canvas id="cv"></canvas><div id="tip"></div></div>
</div>
<div id="side">
  <h2>PODSTAWOWE CECHY</h2><table id="feat"></table>
  <h2>DANE</h2><table id="qual"></table>
  <div id="resbox"><b>ROZPOZNANIE SPÓŁEK</b><table id="restab"></table></div>
</div>
<script>window.__DATA=__DATA_JSON__;window.__RES=__RES_JSON__;window.__ERR=__ERR_JSON__;</script>
<script>
const D=window.__DATA,RES=window.__RES;
const PL={POSITIVE_ACCELERATING:'dodatni, rośnie',POSITIVE_DECELERATING:'dodatni, słabnie',
NEGATIVE_ACCELERATING:'ujemny, pogłębia się',NEGATIVE_DECELERATING:'ujemny, cofa się',
UNCHANGED:'bez zmiany',UNKNOWN:'brak danych',OVERSOLD_FALLING:'wyprzedanie, spada',
OVERSOLD_RISING:'wyprzedanie, rośnie',NORMAL_FALLING:'normalny, spada',
NORMAL_RISING:'normalny, rośnie',AVAILABLE:'dostępne',WARMUP:'rozgrzewka',
MISSING_CANONICAL_HL:'brak pełnych H/L',ZERO_RANGE:'zakres zerowy',
INSUFFICIENT_PROVENANCE:'niepewne pochodzenie',STANDARD_500:'standard 500',
FULL_HISTORY_FROM_LISTING:'pełna historia od debiutu'};
const pl=s=>PL[s]||s||'—';
const TFS=['30m','1H','2H','4H','1D'];      // kolejnosc kontraktu = kolejnosc przyciskow
const TF_KEY='v3chart.tf.v3';               // wersjonowany klucz ustawienia interwalu
let sym=null,tf='1D',hover=-1,view=null;   // view = [i0,i1] zakres indeksów
// Stare albo nieznane ustawienie NIE moze zablokowac startu - wracamy do 1D z r591.
(function(){let s='';try{s=localStorage.getItem(TF_KEY)||''}catch(e){}
 if(TFS.indexOf(s)>=0)tf=s})();
function cur(){return D[sym+'|'+tf]}
function fmt(v,d){return v==null?'—':(+v).toFixed(d==null?2:d)}
// EMA: trzy rozne, natychmiast rozpoznawalne kolory, ale nadal slabsze niz swiece
const EMA_C={20:'rgba(224,102,102,.55)',50:'rgba(214,163,72,.55)',
             100:'rgba(90,178,178,.55)'};
const EMA_L={20:'rgba(224,102,102,.95)',50:'rgba(214,163,72,.95)',
             100:'rgba(90,178,178,.95)'};
// formatowanie K/M/B WYLACZNIE w warstwie UI (dane zrodlowe nie sa zaokraglane)
function big(v){if(v==null||!isFinite(v))return'—';const a=Math.abs(v);
 if(a>=1e9)return(v/1e9).toFixed(2)+' B';if(a>=1e6)return(v/1e6).toFixed(1)+' M';
 if(a>=1e3)return(v/1e3).toFixed(1)+' K';return(+v).toFixed(0)}
function pct(v){return v==null?'—':((v>=0?'+':'')+(100*v).toFixed(2)+'%')}
function firstSym(){const r=RES.find(r=>TFS.some(t=>D[r.symbol+'|'+t]));return r?r.symbol:null}
// ---------- nawigacja ----------
const colist=document.getElementById('colist');
RES.forEach(r=>{const el=document.createElement('div');
 if(r.status==='RESOLVED_EXACT'||r.status==='RESOLVED_UNIQUE'){
  el.className='co';el.innerHTML='<span>'+r.requested_name+'</span><small>'+r.symbol+'</small>';
  el.onclick=()=>{sym=r.symbol;view=null;hover=-1;render()};el.dataset.sym=r.symbol;}
 else{el.className='co bad';el.innerHTML='<span>'+r.requested_name+'</span><small>'+
  (r.status==='AMBIGUOUS'?'?':'—')+'</small>';}
 colist.appendChild(el);});
const restab=document.getElementById('restab');
RES.forEach(r=>{const bad=(r.status==='NOT_FOUND'||r.status==='AMBIGUOUS');
 const tr=document.createElement('tr');
 tr.innerHTML='<td>'+r.requested_name+'</td><td class="'+(bad?'err':'ok')+'">'
  +(r.symbol||r.status)+'</td>';restab.appendChild(tr);});
function tfButtons(){return document.querySelectorAll('#top .tf button[data-tf]')}
function hidetip(){const t=document.getElementById('tip');if(t)t.style.display='none'}
// Zmiana TF czyta GOTOWY payload: zero pobierania, zero liczenia wskaznikow w UI.
// Kasujemy zoom, hover i tooltip, zeby nie zostala zadna wartosc z poprzedniego TF.
function setTf(t){if(!D[sym+'|'+t])return;tf=t;
 try{localStorage.setItem(TF_KEY,t)}catch(e){}
 view=null;hover=-1;hidetip();render()}
tfButtons().forEach(b=>{b.onclick=()=>setTf(b.dataset.tf)});
document.getElementById('reset').onclick=()=>{view=null;hover=-1;render()};
// ---------- geometria ----------
const cv=document.getElementById('cv'),ctx=cv.getContext('2d');
const M={l:6,r:58,top:2,bot:17,gap:9};
function panels(H){const inner=H-M.top-M.bot-4*M.gap;
 // Wysokosc paneli oscylatorow wynika z KANALU, nie z rownej wysokosci pudelek.
 // Przy skali 0-100 kanal RSI 30-70 to 40% panelu, a Stochastic 20-80 to 60%,
 // wiec panel RSI musi byc 1.5x wyzszy, zeby oba kanaly mialy tyle samo pikseli
 // (0.40 * 1.5 = 0.60). Nadwyzka daje RSI miejsce nad 70 i pod 30 na wychylenia.
 const stoch=Math.round(inner*0.115),rsi=Math.round(stoch*1.5),
  macd=Math.round(inner*0.165),ad=Math.round(inner*0.085),
  price=inner-macd-ad-rsi-stoch;
 let y=M.top;const P={};
 P.price={y:y,h:price};y+=price+M.gap;P.macd={y:y,h:macd};y+=macd+M.gap;
 P.rsi={y:y,h:rsi};y+=rsi+M.gap;P.stoch={y:y,h:stoch};y+=stoch+M.gap;
 P.ad={y:y,h:ad};return P}
// RSI i STOCHASTIC rysuja sie w tej samej skali 0-100 na pelnej wysokosci panelu.
// Rowna sie NIE wysokosc pudelek, a wysokosc uzytecznego kanalu: patrz panels().
const OSC_LO=0,OSC_HI=100;
// Histogram momentum: czterostanowa klasyfikacja jak w TradingView.
// Kolor kazdego slupka wyliczany NIEZALEZNIE i zapisywany - pojawienie sie nowego
// slupka nie przemalowuje historii. Pelne krycie, zero przezroczystosci, zero
// mieszania i zero dziedziczenia z wolumenu (wolumen ma wlasne, osobne tokeny).
const MOMENTUM_POSITIVE_RISING='#00BCD4',MOMENTUM_POSITIVE_FALLING='#2962FF',
      MOMENTUM_NEGATIVE_FALLING='#F23645',MOMENTUM_NEGATIVE_RISING='#880E4F';
function momentumColors(hist,n){const out=new Array(n);let prev=null;
 for(let i=0;i<n;i++){const v=hist[i];
  if(v==null||!isFinite(v)){out[i]=null;continue}
  const p=(i>0?hist[i-1]:null),hasPrev=(p!=null&&isFinite(p));
  let c;
  if(!hasPrev)              c=(v>=0?MOMENTUM_POSITIVE_FALLING:MOMENTUM_NEGATIVE_RISING);
  else if(v===p)            c=(prev!=null?prev
                               :(v>=0?MOMENTUM_POSITIVE_FALLING:MOMENTUM_NEGATIVE_RISING));
  else if(v>=0&&v>p)        c=MOMENTUM_POSITIVE_RISING;
  else if(v>=0&&v<p)        c=MOMENTUM_POSITIVE_FALLING;
  else if(v<0&&v<p)         c=MOMENTUM_NEGATIVE_FALLING;
  else                      c=MOMENTUM_NEGATIVE_RISING;
  out[i]=c;prev=c}
 return out}
function range(n){if(!view)return[0,n-1];
 return[Math.max(0,view[0]),Math.min(n-1,view[1])]}
function xOf(i,i0,i1,W){const c=i1-i0+1,w=(W-M.l-M.r)/c;return M.l+w*(i-i0)+w/2}
function idxAt(px,i0,i1,W){const c=i1-i0+1,w=(W-M.l-M.r)/c;
 const i=i0+Math.floor((px-M.l)/w);return(i<i0||i>i1)?-1:i}
function scale(arrs,i0,i1,pad){let lo=Infinity,hi=-Infinity;
 arrs.forEach(a=>{for(let i=i0;i<=i1;i++){const v=a[i];
  if(v!=null&&isFinite(v)){if(v<lo)lo=v;if(v>hi)hi=v}}});
 if(!isFinite(lo)){lo=0;hi=1}if(lo===hi){lo-=1;hi+=1}
 const p=(hi-lo)*(pad==null?0.07:pad);return[lo-p,hi+p]}
function yOf(v,lo,hi,p){return p.y+p.h-(v-lo)/(hi-lo)*p.h}
// ---------- prymitywy ----------
function hgrid(p,lo,hi,W,dec){const n=Math.max(2,Math.round(p.h/48));
 ctx.font='10px Segoe UI';ctx.textAlign='left';
 for(let i=0;i<=n;i++){const v=lo+(hi-lo)*i/n,y=Math.round(yOf(v,lo,hi,p))+.5;
  ctx.strokeStyle='rgba(255,255,255,.045)';ctx.lineWidth=1;
  ctx.beginPath();ctx.moveTo(M.l,y);ctx.lineTo(W-M.r,y);ctx.stroke();
  ctx.fillStyle='#5c6172';ctx.fillText((+v).toFixed(dec==null?2:dec),W-M.r+5,y+3)}}
// delikatny grid o zadanej liczbie poziomow, etykiety w formacie K/M/B
function hgridN(p,lo,hi,W,n){ctx.font='10px Segoe UI';ctx.textAlign='left';
 for(let i=1;i<n;i++){const v=lo+(hi-lo)*i/n,y=Math.round(yOf(v,lo,hi,p))+.5;
  ctx.strokeStyle='rgba(255,255,255,.04)';ctx.lineWidth=1;
  ctx.beginPath();ctx.moveTo(M.l,y);ctx.lineTo(W-M.r,y);ctx.stroke();
  ctx.fillStyle='#5c6172';ctx.fillText(big(v),W-M.r+5,y+3)}}
// Skala panelu MACD: autoscale po WIDOCZNYCH barach, ale zero zawsze z oddechem
// po obu stronach. Bez wymuszania symetrii 50/50 - asymetria danych zostaje,
// dopoki zadna strona nie schodzi ponizej MIN_SIDE_SHARE panelu. Renderer-only:
// wartosci MACD, Signal, histogramu i eventow bez zmian.
const MIN_SIDE_SHARE=0.28,MACD_PAD=0.10;
function macdScale(S,i0,i1){let mn=0,mx=0;
 [S.macd,S.macd_signal,S.macd_hist].forEach(a=>{for(let i=i0;i<=i1;i++){
  const v=a[i];if(v==null||!isFinite(v))continue;
  if(v<mn)mn=v;if(v>mx)mx=v}});
 let neg=Math.abs(Math.min(mn,0)),pos=Math.max(mx,0);
 if(neg===0&&pos===0){neg=1;pos=1}
 neg*=1+MACD_PAD;pos*=1+MACD_PAD;                 // zapas od ekstremow
 const total=neg+pos,k=MIN_SIDE_SHARE/(1-MIN_SIDE_SHARE);
 if(pos/total<MIN_SIDE_SHARE)pos=neg*k;           // dodatnia strona ma kanal
 else if(neg/total<MIN_SIDE_SHARE)neg=pos*k;      // ujemna strona ma kanal
 return[-neg,pos]}
function guide(p,lv,lo,hi,W,alpha,label){const y=Math.round(yOf(lv,lo,hi,p))+.5;
 ctx.strokeStyle='rgba(255,255,255,'+alpha+')';ctx.lineWidth=1;ctx.setLineDash([4,4]);
 ctx.beginPath();ctx.moveTo(M.l,y);ctx.lineTo(W-M.r,y);ctx.stroke();ctx.setLineDash([]);
 if(label){ctx.fillStyle='#5c6172';ctx.textAlign='left';ctx.font='10px Segoe UI';
  ctx.fillText(String(lv),W-M.r+5,y+3)}}
// etykieta biezacej wartosci serii na prawej osi (jak w terminalu wykresowym)
function vlabel(p,val,lo,hi,W,bg,dec){if(val==null||!isFinite(val))return;
 vlabelTxt(p,val,lo,hi,W,bg,(+val).toFixed(dec==null?1:dec))}
function vlabelTxt(p,val,lo,hi,W,bg,text){if(val==null||!isFinite(val))return;
 const y=Math.max(p.y+7,Math.min(p.y+p.h-7,yOf(val,lo,hi,p)));
 ctx.fillStyle=bg;ctx.fillRect(W-M.r+2,y-7,M.r-4,14);
 ctx.fillStyle='#0e1117';ctx.textAlign='left';ctx.font='600 10px Segoe UI';
 ctx.fillText(text,W-M.r+5,y+3.5)}
// maly marker potwierdzajacy ISTNIEJACE zdarzenie (nie tworzy sygnalu)
function dot(x,y,color,r){ctx.beginPath();ctx.arc(x,y,r||3,0,6.2832);
 ctx.fillStyle=color;ctx.fill();
 ctx.strokeStyle='rgba(14,17,23,.9)';ctx.lineWidth=1;ctx.stroke()}
// wypelnienie WYLACZNIE tam, gdzie seria faktycznie wychodzi poza poziom
function excursion(vals,i0,i1,level,above,lo,hi,p,W,color){ctx.fillStyle=color;
 let run=null;
 const flush=()=>{if(!run||!run.length){run=null;return}const ly=yOf(level,lo,hi,p);
  ctx.beginPath();ctx.moveTo(run[0][0],ly);
  run.forEach(q=>ctx.lineTo(q[0],q[1]));
  ctx.lineTo(run[run.length-1][0],ly);ctx.closePath();ctx.fill();run=null};
 for(let i=i0;i<=i1;i++){const v=vals[i];
  const out=(v!=null&&isFinite(v))&&(above?v>level:v<level);
  if(out){if(!run)run=[];run.push([xOf(i,i0,i1,W),yOf(v,lo,hi,p)])}else flush()}
 flush()}
function line(vals,i0,i1,lo,hi,p,color,W,width){ctx.strokeStyle=color;
 ctx.lineWidth=width||1.35;ctx.beginPath();let on=false;
 for(let i=i0;i<=i1;i++){const v=vals[i];
  if(v==null||!isFinite(v)){on=false;continue}
  const x=xOf(i,i0,i1,W),y=yOf(v,lo,hi,p);
  if(!on){ctx.moveTo(x,y);on=true}else ctx.lineTo(x,y)}ctx.stroke()}
function head(p,parts){let x=M.l+3;ctx.textAlign='left';ctx.font='11px Segoe UI';
 parts.forEach(([txt,col])=>{ctx.fillStyle=col||'#8b91a3';ctx.fillText(txt,x,p.y+11);
  x+=ctx.measureText(txt).width+9})}
// ---------- render ----------
function render(){if(!sym)sym=firstSym();if(!sym)return;
 document.querySelectorAll('#nav .co').forEach(e=>e.classList.toggle('active',e.dataset.sym===sym));
 tfButtons().forEach(b=>{const t=b.dataset.tf,ok=!!D[sym+'|'+t];
  b.classList.toggle('on',tf===t);b.disabled=!ok;
  b.style.opacity=ok?'':'.35';b.title=ok?'':('brak payloadu '+sym+' '+t)});
 const r=RES.find(x=>x.symbol===sym)||{};
 document.getElementById('tSym').textContent=sym;
 document.getElementById('tName').textContent=r.company_name||'';
 document.getElementById('tExch').textContent=r.exchange||'';
 const d=cur(),st=document.getElementById('tStatus');
 if(!d){st.innerHTML='<span class="err">BRAK PAYLOADU '+sym+' '+tf+'</span>';
  hidetip();hover=-1;ctx.clearRect(0,0,cv.width,cv.height);side(null);return}
 const Q=d.quality;
 st.innerHTML='Dane: '+(Q.data_status==='DANE PEŁNE'
  ?'<span class="ok">pełne</span>':'<span class="err">'+Q.data_status.toLowerCase()+'</span>')
  +' <span style="font-size:10px">· '+Q.display_bars+' barów · '
  +(Q.latest_bar_time||'—').replace('T',' ').slice(0,16)+'</span>';
 draw(d);side(d)}
function draw(d){const box=document.getElementById('charts');
 const W=box.clientWidth,H=box.clientHeight;
 if(cv.width!==W||cv.height!==H){cv.width=W;cv.height=H}
 ctx.clearRect(0,0,W,H);const n=d.candles.length;if(!n)return;
 const[i0,i1]=range(n),P=panels(H),S=d.series,C=d.candles;
 const hi_=C.map(c=>c.h!=null?c.h:c.c),lo_=C.map(c=>c.l!=null?c.l:c.c);
 const[plo,phi]=scale([hi_,lo_,S.ema20,S.ema50,S.ema100],i0,i1);
 // pionowa siatka wspólna dla wszystkich paneli
 const cnt=i1-i0+1,step=Math.max(1,Math.round(cnt/9)),bot=P.ad.y+P.ad.h;
 ctx.font='10px Segoe UI';ctx.textAlign='center';
 for(let i=i0;i<=i1;i+=step){const x=Math.round(xOf(i,i0,i1,W))+.5;
  ctx.strokeStyle='rgba(255,255,255,.035)';ctx.lineWidth=1;
  ctx.beginPath();ctx.moveTo(x,M.top);ctx.lineTo(x,bot);ctx.stroke();
  const t=C[i].t;ctx.fillStyle='#5c6172';
  ctx.fillText(tf==='1D'?t.slice(0,10):t.slice(5,10)+' '+t.slice(11,16),x,bot+12)}
 // ---- panel ceny ----
 hgrid(P.price,plo,phi,W);
 const bw=Math.max(1.5,Math.min(11,(W-M.l-M.r)/cnt*0.66));
 for(let i=i0;i<=i1;i++){const c=C[i],x=xOf(i,i0,i1,W);
  if(c.hl_ok&&c.o!=null){const up=c.c>=c.o,col=up?'#26a69a':'#ef5350';
   ctx.strokeStyle=col;ctx.fillStyle=col;ctx.lineWidth=1;
   const xw=Math.round(x)+.5;
   ctx.beginPath();ctx.moveTo(xw,yOf(c.h,plo,phi,P.price));
   ctx.lineTo(xw,yOf(c.l,plo,phi,P.price));ctx.stroke();
   const y1=yOf(Math.max(c.o,c.c),plo,phi,P.price),y2=yOf(Math.min(c.o,c.c),plo,phi,P.price);
   ctx.fillRect(x-bw/2,y1,bw,Math.max(1,y2-y1))}
  else{ctx.fillStyle='#c9a227';ctx.fillRect(x-bw/2,yOf(c.c,plo,phi,P.price)-1,bw,2)}}
 // wolumen w dolnej części panelu ceny
 let vmax=0;for(let i=i0;i<=i1;i++){const v=C[i].v;if(v!=null&&v>vmax)vmax=v}
 if(vmax>0){const vh=P.price.h*0.16,vb=P.price.y+P.price.h;
  for(let i=i0;i<=i1;i++){const c=C[i];if(c.v==null)continue;
   const x=xOf(i,i0,i1,W),h=c.v/vmax*vh;
   ctx.fillStyle=(c.o!=null&&c.c>=c.o)?'rgba(38,166,154,.26)':'rgba(239,83,80,.26)';
   ctx.fillRect(x-bw/2,vb-h,bw,h)}}
 // EMA — trzy rozne kolory, cienkie i spokojne (slabsze niz swiece)
 line(S.ema100,i0,i1,plo,phi,P.price,EMA_C[100],W,1);
 line(S.ema50,i0,i1,plo,phi,P.price,EMA_C[50],W,1);
 line(S.ema20,i0,i1,plo,phi,P.price,EMA_C[20],W,1);
 // linia ostatniego FINAL zamknięcia
 const lc=d.last_final_close;
 if(lc!=null&&lc>=plo&&lc<=phi){const y=Math.round(yOf(lc,plo,phi,P.price))+.5;
  ctx.strokeStyle='rgba(227,230,238,.42)';ctx.lineWidth=1;ctx.setLineDash([2,3]);
  ctx.beginPath();ctx.moveTo(M.l,y);ctx.lineTo(W-M.r,y);ctx.stroke();ctx.setLineDash([]);
  ctx.fillStyle='#3a4152';ctx.fillRect(W-M.r+2,y-7,M.r-4,14);
  ctx.fillStyle='#e3e6ee';ctx.textAlign='left';ctx.font='10px Segoe UI';
  ctx.fillText(lc.toFixed(2),W-M.r+5,y+3.5)}
 const h=(hover>=i0&&hover<=i1)?hover:i1,B=C[h],S_=S;
 head(P.price,[[sym+' · '+tf,'#e3e6ee'],
  ['O '+fmt(B.o),'#8b91a3'],['H '+(B.hl_ok?fmt(B.h):'—'),'#8b91a3'],
  ['L '+(B.hl_ok?fmt(B.l):'—'),'#8b91a3'],['C '+fmt(B.c),B.o!=null&&B.c>=B.o?'#26a69a':'#ef5350'],
  ['EMA20 '+fmt(S_.ema20[h]),EMA_L[20]],
  ['EMA50 '+fmt(S_.ema50[h]),EMA_L[50]],
  ['EMA100 '+fmt(S_.ema100[h]),EMA_L[100]]]);
 // ---- MACD ----
 const[mlo,mhi]=macdScale(S,i0,i1);
 hgrid(P.macd,mlo,mhi,W,2);
 const zy=Math.round(yOf(0,mlo,mhi,P.macd))+.5;
 ctx.strokeStyle='rgba(255,255,255,.16)';ctx.lineWidth=1;
 ctx.beginPath();ctx.moveTo(M.l,zy);ctx.lineTo(W-M.r,zy);ctx.stroke();
 const HC=momentumColors(S.macd_hist,S.macd_hist.length);
 for(let i=i0;i<=i1;i++){const v=S.macd_hist[i];if(v==null||!isFinite(v))continue;
  const x=xOf(i,i0,i1,W),y=yOf(v,mlo,mhi,P.macd);
  ctx.fillStyle=HC[i]||MOMENTUM_POSITIVE_FALLING;
  ctx.fillRect(x-bw/2,Math.min(y,zy),bw,Math.max(1,Math.abs(y-zy)))}
 line(S.macd,i0,i1,mlo,mhi,P.macd,'#4a8fff',W);
 line(S.macd_signal,i0,i1,mlo,mhi,P.macd,'#ff9330',W);
 // Markery przeciec MACD/Signal - WYLACZNIE z locked eventow w payloadzie.
 // Kropka siedzi DOKLADNIE na barze i, tym samym co crosshair, OHLC i tooltip.
 // r590: usunieta interpolacja do geometrycznego punktu przeciecia (r557). Przy
 // plytkim przeciecie (PLTR: d0=-0.004, d1=+0.456 => t=0.0087) kropka ladowala
 // wizualnie na barze i-1, mimo ze zdarzenie nalezy do i. Jedna kanoniczna tablica
 // zdarzen zasila marker i tooltip, bez zadnego przesuniecia.
 for(let i=i0;i<=i1;i++){
  const up=S.macd_cross_signal_up&&S.macd_cross_signal_up[i];
  const dn=S.macd_cross_signal_down&&S.macd_cross_signal_down[i];
  if(!up&&!dn)continue;                      // bez locked eventu nie ma kropki
  const v=S.macd[i];
  if(v==null||!isFinite(v))continue;
  dot(xOf(i,i0,i1,W),yOf(v,mlo,mhi,P.macd),up?'#00c853':'#ff1744',3.6)}
 head(P.macd,[['MACD','#8b91a3'],[fmt(S.macd[h],3),'#4a8fff'],
  ['Signal','#8b91a3'],[fmt(S.macd_signal[h],3),'#ff9330'],
  ['Hist','#8b91a3'],[fmt(S.macd_hist[h],3),
   (S.macd_hist[h]||0)>=0?'#26a69a':'#ef5350']]);
 // ---- RSI: kanal 30/50/70, wypelnienie TYLKO przy wyjsciu poza kanal ----
 // Poziomy i wypelnienia to WYLACZNIE prowadnice wizualne (renderer-only).
 excursion(S.rsi,i0,i1,70,true,OSC_LO,OSC_HI,P.rsi,W,'rgba(74,143,255,.28)');
 excursion(S.rsi,i0,i1,30,false,OSC_LO,OSC_HI,P.rsi,W,'rgba(239,83,80,.28)');
 guide(P.rsi,70,OSC_LO,OSC_HI,W,.15,70);guide(P.rsi,30,OSC_LO,OSC_HI,W,.15,30);
 guide(P.rsi,50,OSC_LO,OSC_HI,W,.07,50);
 line(S.rsi_helper,i0,i1,OSC_LO,OSC_HI,P.rsi,'#ff8a65',W,1.1);
 line(S.rsi,i0,i1,OSC_LO,OSC_HI,P.rsi,'#4dd0e1',W,1.5);
 vlabel(P.rsi,S.rsi[h],OSC_LO,OSC_HI,W,'#4dd0e1',2);
 head(P.rsi,[['RSI','#8b91a3'],[fmt(S.rsi[h],1),'#4dd0e1'],
  ['Średnia','#8b91a3'],[fmt(S.rsi_helper[h],1),'rgba(201,162,39,.9)']]);
 // ---- Stochastic: 20/50/80 = tylko prowadnice wizualne ----
 guide(P.stoch,80,OSC_LO,OSC_HI,W,.15,80);guide(P.stoch,20,OSC_LO,OSC_HI,W,.15,20);
 guide(P.stoch,50,OSC_LO,OSC_HI,W,.07,50);
 line(S.stoch_d,i0,i1,OSC_LO,OSC_HI,P.stoch,'rgba(201,162,39,.7)',W,1.2);
 line(S.stoch_k,i0,i1,OSC_LO,OSC_HI,P.stoch,'#b39ddb',W,1.5);
 vlabel(P.stoch,S.stoch_d[h],OSC_LO,OSC_HI,W,'rgba(201,162,39,.7)',1);
 vlabel(P.stoch,S.stoch_k[h],OSC_LO,OSC_HI,W,'#b39ddb',1);
 head(P.stoch,[['Stochastic','#8b91a3'],['K '+fmt(S.stoch_k[h],1),'#b39ddb'],
  ['D '+fmt(S.stoch_d[h],1),'rgba(201,162,39,.7)']]);
 // ---- Akumulacja/Dystrybucja: seria diagnostyczna (renderer-only) ----
 const AD=scale([S.ad],i0,i1);
 ctx.fillStyle='rgba(255,255,255,.012)';
 ctx.fillRect(M.l,P.ad.y,W-M.r-M.l,P.ad.h);
 hgridN(P.ad,AD[0],AD[1],W,3);
 line(S.ad,i0,i1,AD[0],AD[1],P.ad,'#7fb3a0',W,1.2);
 vlabelTxt(P.ad,S.ad[h],AD[0],AD[1],W,'#7fb3a0',big(S.ad[h]));
 head(P.ad,[['Akumulacja/Dystrybucja','#8b91a3'],[big(S.ad[h]),'#7fb3a0']]);
 // ---- markery waznych informacji (tylko zaznaczaja fakt zdarzenia) ----
 const EV=d.events||[];
 if(EV.length){const ey=P.price.y+P.price.h-3;
  EV.forEach(e=>{if(e.i<i0||e.i>i1)return;
   dot(xOf(e.i,i0,i1,W),ey,'#4a8fff',3.5)})}
 // ---- crosshair przez wszystkie panele ----
 if(hover>=i0&&hover<=i1){const x=Math.round(xOf(hover,i0,i1,W))+.5;
  ctx.strokeStyle='rgba(255,255,255,.22)';ctx.lineWidth=1;ctx.setLineDash([3,3]);
  ctx.beginPath();ctx.moveTo(x,M.top);ctx.lineTo(x,bot);ctx.stroke();ctx.setLineDash([]);
  tip(d,hover,x,W)}
 else document.getElementById('tip').style.display='none'}
function tip(d,i,x,W){const C=d.candles[i],S=d.series,el=document.getElementById('tip');
 el.textContent=C.t.replace('T',' ').slice(0,16)
  +'\\nO '+fmt(C.o)+'   H '+(C.hl_ok?fmt(C.h):'—')+'   L '+(C.hl_ok?fmt(C.l):'—')
  +'   C '+fmt(C.c)+'\\nWol '+(C.v==null?'—':Math.round(C.v).toLocaleString('pl-PL'))
  +'\\nMACD '+fmt(S.macd[i],3)+'  Sig '+fmt(S.macd_signal[i],3)+'  H '+fmt(S.macd_hist[i],3)
  +'\\nRSI '+fmt(S.rsi[i],1)+'  Śr '+fmt(S.rsi_helper[i],1)
  +'\\nK '+fmt(S.stoch_k[i],1)+'  D '+fmt(S.stoch_d[i],1)
  +'\\nA/D '+big(S.ad[i]);
 const cu=S.macd_cross_signal_up&&S.macd_cross_signal_up[i];
 const cd=S.macd_cross_signal_down&&S.macd_cross_signal_down[i];
 // informacja o przecieciu w kolorze markera; reszta tooltipa neutralna
 if(cu||cd){const b=document.createElement('div');
  b.style.cssText='margin-top:5px;font-weight:600;color:'+(cu?'#00c853':'#ff1744');
  b.textContent='PRZECIECIE MACD / SIGNAL: '+(cu?'W GORE':'W DOL');
  el.appendChild(b)}
 (d.events||[]).forEach(e=>{if(e.i!==i)return;
  const b=document.createElement('div');b.style.cssText='margin-top:5px';
  b.textContent='Wazna informacja: '+e.title
   +(e.description?'\\n'+e.description:'');el.appendChild(b)});
 el.style.display='block';
 el.style.left=(x>W-200?x-el.offsetWidth-12:x+12)+'px';el.style.top='26px'}
// ---------- interakcja ----------
const box=document.getElementById('charts');
box.addEventListener('mousemove',e=>{const d=cur();if(!d)return;
 const rect=cv.getBoundingClientRect(),n=d.candles.length,[i0,i1]=range(n);
 if(drag!==null){const w=(cv.width-M.l-M.r)/(i1-i0+1);
  const shift=Math.round((drag-(e.clientX-rect.left))/w);
  if(shift!==0){let a=i0+shift,b=i1+shift;
   if(a>=0&&b<=n-1){view=[a,b];drag=e.clientX-rect.left;hover=-1;draw(cur())}}
  return}
 hover=idxAt(e.clientX-rect.left,i0,i1,cv.width);draw(d)});
box.addEventListener('mouseleave',()=>{hover=-1;drag=null;const d=cur();if(d)draw(d)});
let drag=null;
box.addEventListener('mousedown',e=>{const rect=cv.getBoundingClientRect();
 drag=e.clientX-rect.left;box.style.cursor='grabbing'});
window.addEventListener('mouseup',()=>{drag=null;box.style.cursor='crosshair'});
box.addEventListener('wheel',e=>{const d=cur();if(!d)return;e.preventDefault();
 const n=d.candles.length,[i0,i1]=range(n),cnt=i1-i0+1;
 const rect=cv.getBoundingClientRect(),anchor=idxAt(e.clientX-rect.left,i0,i1,cv.width);
 const a=anchor<0?Math.round((i0+i1)/2):anchor;
 const f=e.deltaY>0?1.18:0.85,ncnt=Math.max(20,Math.min(n,Math.round(cnt*f)));
 const left=Math.round((a-i0)/cnt*ncnt);
 let x0=Math.max(0,a-left),x1=x0+ncnt-1;
 if(x1>n-1){x1=n-1;x0=Math.max(0,x1-ncnt+1)}
 view=(ncnt>=n)?null:[x0,x1];draw(d)},{passive:false});
window.addEventListener('resize',()=>{const d=cur();if(d)draw(d)});
// ---------- panel boczny ----------
function row(t,v,cls){return '<tr><td>'+t+'</td><td class="'+(cls||'')+'">'+v+'</td></tr>'}
function side(d){const f=document.getElementById('feat'),q=document.getElementById('qual');
 if(!d){f.innerHTML=row('Dane','brak');q.innerHTML='';return}
 const L=d.last_bar,Q=d.quality;
 f.innerHTML=row('Zamknięcie',fmt(L.close),'big')+row('Zmiana',pct(L.return_1))
  +row('Luka',pct(L.gap_from_prev_close))+row('Zakres',pct(L.range_pct))
  +row('Korpus',pct(L.body_pct))
  +row('Zamk. w zakresie',L.close_location_in_range==null?'—':(100*L.close_location_in_range).toFixed(0)+'%')
  +row('MACD / Signal',fmt(L.macd,3)+' / '+fmt(L.macd_signal,3))
  +row('Histogram',fmt(L.macd_hist,3)+' (Δ '+fmt(L.macd_hist_delta,3)+')')
  +row('Stan MACD',pl(L.macd_state))
  +row('RSI',fmt(L.rsi,1)+' (Δ '+fmt(L.rsi_delta,1)+')')+row('Stan RSI',pl(L.rsi_state))
  +row('Stoch K / D',fmt(L.stoch_k,1)+' / '+fmt(L.stoch_d,1))
  +row('K − D',fmt(L.stoch_k_minus_d,1));
 const okAll=Q.data_status==='DANE PEŁNE';
 q.innerHTML=row('Status',Q.data_status,okAll?'ok':'err')
  +row('Bary (FINAL)',Q.final_bars)+row('Okno',Q.display_bars)
  +(okAll?'':row('W oknie brak H/L',Q.display_missing_hl,'err'))
  +(Q.no_lower_tf_coverage?row('Historia bez 30m',Q.no_lower_tf_coverage):'')
  +(Q.incomplete_lower_tf?row('Sesje niepełne',Q.incomplete_lower_tf):'')
  +row('Rozgrzewka',pl(Q.warmup_mode))
  +row('H/L',pl(L.price_hl_status))+row('Stochastic',pl(L.stochastic_status))}
render();
</script></body></html>
"""


def render_index(resolution, payloads, errors, build=None):
    build = build or {"build_id": "?", "generated": "?"}
    return (_PAGE
            .replace("__DATA_JSON__", json.dumps(payloads, ensure_ascii=False))
            .replace("__RES_JSON__", json.dumps(resolution, ensure_ascii=False))
            .replace("__ERR_JSON__", json.dumps(errors, ensure_ascii=False))
            .replace("__BUILD_ID__", str(build["build_id"]))
            .replace("__GENERATED__", str(build["generated"])))
