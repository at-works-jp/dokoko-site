import json, os, re, sys, html
sys.path.insert(0, os.path.dirname(__file__))
from content import S, PREF

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME = json.load(open('/home/claude/koukou/game_data.json'))['schools']
SITE = 'https://dokoko.mendomilab.com'
API = 'https://script.google.com/macros/s/AKfycbwvDe4IB8MTCbk8fFIwR8zSEFPdmAZ8S2rEXPCSkZ0zkuhaToa9XshZN86Qet4Wco77/exec'
GAMEURL = 'https://at-works-jp.github.io/dokoko/'
e = html.escape

# ---- 機械チェック：ひとことに数字や「有名」「強い」などの評価語が入っていないか
BAD = re.compile(r'[0-9０-９]|有名|常連|強豪|名門|一番|日本一|全国|伝統|人気|最高')
for sid, d in S.items():
    for h, c in d['items']:
        if BAD.search(c):
            sys.exit(f'NG ひとこと {sid} {h}: {c}')

CSS = open(os.path.join(os.path.dirname(__file__), 'style.css')).read()

def head(title, desc, path, extra=''):
    return f'''<!DOCTYPE html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}">
<link rel="canonical" href="{SITE}{path}">
<meta name="google-site-verification" content="zX-gX4xm_eI0b0Iq_cPIstdALPUz2ahmtHjU9jHyhtk">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:type" content="website"><meta property="og:url" content="{SITE}{path}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Zen+Kaku+Gothic+New:wght@400;700;900&display=swap" rel="stylesheet">
<style>{CSS}</style>{extra}</head><body><div class="wrap">
<header><a class="logo" href="/">どこ高？</a><span class="tag">学校あるある</span></header>'''

FOOT = '''<footer>ここにのっているあるあるは どこ高？のために集めた情報と 卒業生の声をもとにしています。ちがっていたら「ちがう」を押してください。<br>運営：<a href="https://at-works.mendomilab.com/">A&amp;T Works</a></footer></div></body></html>'''

def school_page(sid, d):
    g = GAME[sid]; name = g['name']; pref = PREF[g['region']]
    n = len(d['items'])
    others = [(k, GAME[k]['name']) for k in S if k != sid and PREF[GAME[k]['region']] == pref]
    title = f'{name}あるある｜卒業生ならわかる{n}つのこと'
    words = '・'.join(h for h, _ in d['items'][:3])
    desc = f'{name}（{pref}）の卒業生ならわかるあるあるを{n}つ。{words}…あなたはいくつわかる？'
    lis = ''.join(f'<li data-t="{e(h)}"><b>{e(h)}</b><span>{e(c)}</span>'
                  f'<div class="vote"><button class="y">わかる</button><button class="n">ちがう</button></div></li>' for h, c in d['items'])
    voices = ''
    if d['voices']:
        voices = '<h2>卒業生の声</h2><ul class="voice">' + ''.join(f'<li>{e(v)}</li>' for v in d['voices']) + '</ul>'
    nick = f'<p class="nick">呼び名：{e(d["nick"])}</p>' if d['nick'] else ''
    oth = ''
    if others:
        oth = f'<h2>{e(pref)}のほかの高校のあるある</h2><div class="others">' + ''.join(f'<a href="/aruaru/{k}/">{e(nm)}</a>' for k, nm in others) + '</div>'
    js = f'''<script>
const API='{API}', SID='{sid}', SCHOOL={json.dumps(name, ensure_ascii=False)};
let CID=''; try{{ CID=localStorage.getItem('aru-cid')||''; if(!CID){{ CID=Math.random().toString(36).slice(2,12); localStorage.setItem('aru-cid',CID); }} }}catch(e){{}}
function call(fn,arg){{ try{{ return fetch(API,{{method:'POST',body:JSON.stringify({{fn,args:[arg]}})}}).then(r=>r.json()).catch(()=>null); }}catch(e){{ return Promise.resolve(null); }} }}
let voted={{}}; try{{ voted=JSON.parse(localStorage.getItem('aru-v-'+SID)||'{{}}'); }}catch(e){{}}
document.querySelectorAll('.aru li').forEach(li=>{{ const t=li.dataset.t, box=li.querySelector('.vote');
  const mark=a=>{{ box.innerHTML='<em>'+(a==='yes'?'わかる！ありがとう':'教えてくれてありがとう')+'</em>'; }};
  if(voted[t]) mark(voted[t]);
  box.addEventListener('click',ev=>{{ const b=ev.target.closest('button'); if(!b) return; const a=b.classList.contains('y')?'yes':'no';
    call('voteAruaru',{{sid:SID,school:SCHOOL,text:t,ans:a}}); voted[t]=a; try{{ localStorage.setItem('aru-v-'+SID,JSON.stringify(voted)); }}catch(e){{}} mark(a); }}); }});
const f=document.getElementById('post');
f.addEventListener('submit',async ev=>{{ ev.preventDefault(); const t=f.text.value.trim(), m=document.getElementById('msg');
  if(t.length<3){{ m.textContent='3文字以上で書いてください'; return; }}
  if(/先生|せんせい|さん$|くん$|ちゃん$/.test(t)){{ m.textContent='人の名前が入るものは送れません'; return; }}
  f.querySelector('button').disabled=true; m.textContent='送っています…';
  const r=await call('postAruaru',{{sid:SID,school:SCHOOL,text:t,grad:'',client:CID}});
  if(r&&r.ok&&r.r&&r.r.ok===false){{ m.textContent=r.r.msg||'送れませんでした'; f.querySelector('button').disabled=false; return; }}
  m.textContent='ありがとう！ほかの人からも同じ声が届いたら ここにのります'; f.text.value=''; f.querySelector('button').disabled=false; }});
</script>'''
    body = f'''<div class="crumb"><a href="/">どこ高？</a> ＞ <a href="/aruaru/">学校あるある</a> ＞ {e(pref)} ＞ {e(name)}</div>
<h1><em>{e(name)}</em>あるある<br>卒業生ならわかる{n}つのこと</h1>
<p class="lead">{e(name)}（{e(pref)}）を出た人なら きっとわかる。いくつ当てはまるか数えてみてください。</p>{nick}
<ol class="aru">{lis}</ol>
{voices}
<div class="cta"><p>ここからが本番</p><div class="big">質問に答えていくと<br>AIが<em>あなたの母校</em>を当てます</div>
<p class="small">全国の高校から20問くらいでしぼりこみ。<br>当てられなかったら自慢してください。</p>
<a class="btn" href="{GAMEURL}?ref=aru-{sid}">当てられるか試す</a><small>無料・登録なし・1〜2分</small></div>
<h2>ほかにもある？</h2>
<form id="post" class="post"><input name="text" maxlength="25" placeholder="例：購買のパンが…（25文字まで）"><button>送る</button><p id="msg" class="sub">人の名前や悪口は送れません。ほかの人からも同じ声が届いたら このページにのります。</p></form>
{oth}'''
    path = f'/aruaru/{sid}/'
    out = head(title, desc, path) + body + FOOT.replace('</div></body>', js + '</div></body>')
    os.makedirs(ROOT + path, exist_ok=True)
    open(ROOT + path + 'index.html', 'w').write(out)
    return path

paths = [school_page(k, d) for k, d in S.items()]

# 一覧ページ
by = {}
for k in S:
    by.setdefault(PREF[GAME[k]['region']], []).append(k)
lst = ''.join(f'<h2>{e(p)}</h2><div class="others">' + ''.join(f'<a href="/aruaru/{k}/">{e(GAME[k]["name"])}</a>' for k in ks) + '</div>' for p, ks in by.items())
idx = head('学校あるある｜卒業生ならわかる 高校ごとのあるある｜どこ高？', '高校ごとの「卒業生ならわかる」あるあるを集めています。あなたの母校はある？', '/aruaru/') + \
  f'<h1>学校あるある</h1><p class="lead">卒業生ならわかる 高校ごとのあるある。いまは{len(S)}校。少しずつ増やしていきます。</p>{lst}' + \
  f'<div class="cta"><div class="big">あなたの母校は<br>AIが<em>当てます</em></div><a class="btn" href="{GAMEURL}?ref=aru-list">当てられるか試す</a></div>' + FOOT
os.makedirs(ROOT + '/aruaru', exist_ok=True); open(ROOT + '/aruaru/index.html', 'w').write(idx)

# トップ
top = head('どこ高？学校あるある｜母校当てゲームと卒業生のあるある', '質問に答えるとAIが出身高校を当てるゲーム「どこ高？」と 高校ごとのあるある。', '/') + \
  f'''<h1>どこ高？</h1><p class="lead">質問に答えていくと AIがあなたの母校を当てます。卒業生ならわかる 高校ごとのあるあるも集めています。</p>
<div class="cta"><div class="big">AIが<em>あなたの母校</em>を当てます</div><a class="btn" href="{GAMEURL}?ref=aru-top">当てられるか試す</a><small>無料・登録なし・1〜2分</small></div>
<h2><a href="/aruaru/">学校あるある →</a></h2>{lst}''' + FOOT
open(ROOT + '/index.html', 'w').write(top)

# サイトマップとrobots
urls = ['/', '/aruaru/'] + paths
open(ROOT + '/sitemap.xml', 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{SITE}{u}</loc></url>' for u in urls) + '</urlset>\n')
open(ROOT + '/robots.txt', 'w').write(f'User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n')
print('ok', len(paths))
