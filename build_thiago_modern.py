from pathlib import Path
import shutil, math, html, zipfile
from PIL import Image, ImageDraw, ImageFont, ImageOps
import cairosvg

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'assets'
ASSETS.mkdir(parents=True,exist_ok=True)
source=ASSETS/'thiago-ascii-banner.gif'
assert source.exists(), 'Banner original ausente em assets/'

C={'bg':'#07101F','card':'#0B1527','line':'#234167','white':'#F5F9FF','text':'#D8E7FC','dim':'#90A8C9','blue':'#5EA9FF','cyan':'#58E4F1','green':'#5DE4B0','purple':'#AFA4FF','orange':'#F89F66'}

def tag(s):return html.escape(str(s),quote=True)
def text(x,y,s,size=26,color=None,weight=500,anchor=None,spacing=0,mono=False):
    f='ui-monospace, SFMono-Regular, Consolas, monospace' if mono else 'Inter, Arial, sans-serif'
    anch=f' text-anchor="{anchor}"' if anchor else ''
    return f'<text x="{x}" y="{y}" fill="{color or C["text"]}" font-family="{f}" font-size="{size}" font-weight="{weight}" letter-spacing="{spacing}"{anch}>{tag(s)}</text>'
def rect(x,y,w,h,fill=None,rx=18,stroke=None,sw=1):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill or "none"}"'+(f' stroke="{stroke}" stroke-width="{sw}"' if stroke else '')+'/>'
def line(x1,y1,x2,y2,color=None,sw=1,opa=1):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color or C["line"]}" stroke-width="{sw}" opacity="{opa}"/>'
def circle(cx,cy,r,fill=None,stroke=None,sw=2):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill or "none"}"'+(f' stroke="{stroke}" stroke-width="{sw}"' if stroke else '')+'/>'
def svgbody(w,h,children):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">
 <defs>
 <linearGradient id="panel" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#111E36"/><stop offset="55%" stop-color="#0B1527"/><stop offset="100%" stop-color="#071020"/></linearGradient>
 <linearGradient id="bluebar" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#297BEF"/><stop offset="1" stop-color="#56D5F1"/></linearGradient>
 <radialGradient id="aura"><stop offset="0" stop-color="#183C74" stop-opacity=".62"/><stop offset="1" stop-color="#183C74" stop-opacity="0"/></radialGradient>
 <filter id="softglow"><feGaussianBlur stdDeviation="8"/></filter>
 </defs>
 {''.join(children)}
</svg>'''

def icon(name,cx,cy,sz):
    # Icons are vector shapes and text, intentionally independent from remote CDNs.
    p=[]; x=cx; y=cy; d=sz
    def t(s,fs=32,color='#FFFFFF',weight=800):return text(x,y+fs*.33,s,fs,color,weight,'middle',-1,True)
    if name=='HTML5':
        pts=f'{x-d*.38},{y-d*.40} {x+d*.38},{y-d*.40} {x+d*.31},{y+d*.37} {x},{y+d*.49} {x-d*.31},{y+d*.37}'
        p += [f'<polygon points="{pts}" fill="#EF652A"/>',t('5',35)]
    elif name=='CSS3':
        pts=f'{x-d*.38},{y-d*.40} {x+d*.38},{y-d*.40} {x+d*.31},{y+d*.37} {x},{y+d*.49} {x-d*.31},{y+d*.37}'
        p += [f'<polygon points="{pts}" fill="#2C87D8"/>',t('3',35)]
    elif name=='JavaScript':
        p += [rect(x-d*.43,y-d*.43,d*.86,d*.86,'#F7DF1E',8),t('JS',27,'#171717')]
    elif name=='React':
        p += [circle(x,y,6,'#66D9F0')]
        for deg in (0,60,120):
            p += [f'<ellipse cx="{x}" cy="{y}" rx="{d*.43}" ry="{d*.16}" transform="rotate({deg} {x} {y})" fill="none" stroke="#64D9F1" stroke-width="4"/>']
    elif name=='Next.js':
        p += [circle(x,y,d*.43,'#080E1D','#DCE6F9',3),t('N',36,'#FFFFFF')]
        p += [line(x+3,y-17,x+25,y+20,'#FFFFFF',3)]
    elif name=='Node.js':
        pts=' '.join(f'{x+math.cos(math.radians(a))*d*.43:.1f},{y+math.sin(math.radians(a))*d*.43:.1f}' for a in range(-90,270,60))
        p += [f'<polygon points="{pts}" fill="#70AF4B"/>',t('JS',27)]
    elif name=='Python':
        p += [rect(x-d*.38,y-d*.27,d*.65,d*.42,'#3573A0',12),rect(x-d*.20,y-d*.04,d*.62,d*.42,'#FFD24C',12),circle(x-d*.10,y-d*.16,3,'#FFFFFF'),circle(x+d*.17,y+d*.20,3,'#FFFFFF')]
    elif name=='Java':
        p += [f'<path d="M {x-22} {y+7} L {x+18} {y+7} C {x+28} {y+7} {x+27} {y-6} {x+18} {y-6} M {x-18} {y+7} Q {x-14} {y+28} {x+12} {y+27} Q {x+23} {y+24} {x+22} {y+7}" stroke="#E8F3FA" fill="none" stroke-width="4" stroke-linecap="round"/>',f'<path d="M {x-9} {y-12} C {x+6} {y-22} {x-2} {y-30} {x+7} {y-40} M {x+2} {y-11} C {x+18} {y-20} {x+9} {y-29} {x+19} {y-37}" stroke="#F36B59" fill="none" stroke-width="4" stroke-linecap="round"/>']
    elif name=='C#':
        pts=' '.join(f'{x+math.cos(math.radians(a))*d*.43:.1f},{y+math.sin(math.radians(a))*d*.43:.1f}' for a in range(-90,270,60))
        p += [f'<polygon points="{pts}" fill="#9953C9"/>',t('C#',27)]
    elif name=='.NET':
        p += [rect(x-d*.44,y-d*.33,d*.88,d*.67,'#5127A7',12),t('.NET',23)]
    elif name=='PostgreSQL':
        p += [f'<ellipse cx="{x}" cy="{y-15}" rx="24" ry="12" fill="#376F9B" stroke="#9AD1F3" stroke-width="3"/>',f'<path d="M {x-24} {y-15} V {y+20} Q {x} {y+44} {x+24} {y+20} V {y-15}" fill="#376F9B" stroke="#9AD1F3" stroke-width="3"/>',t('P',27)]
    elif name=='Git':
        p += [f'<rect x="{x-26}" y="{y-26}" width="52" height="52" rx="6" fill="#F05133" transform="rotate(45 {x} {y})"/>',f'<path d="M {x-10} {y-21} V {y+8} H {x+12} V {y+22}" stroke="white" fill="none" stroke-width="4"/>',circle(x-10,y-21,5,'white'),circle(x-10,y+8,5,'white'),circle(x+12,y+22,5,'white')]
    elif name=='GitHub':
        p += [circle(x,y,d*.42,'#ECF4FF'),f'<path d="M{x-21} {y+18} V{y+4} Q{x-39} {y-8} {x-22} {y-24} Q{x-16} {y-29} {x-12} {y-19} Q{x} {y-25} {x+12} {y-19} Q{x+16} {y-30} {x+22} {y-24} Q{x+39} {y-8} {x+21} {y+4} V{y+18} Z" fill="#0B1527"/>']
    elif name=='VS Code':
        p += [f'<path d="M{x-24} {y-3} L{x+6} {y-30} L{x+28} {y-25} V{y+27} L{x+6} {y+31} L{x-24} {y+4} L{x-37} {y+13} L{x-45} {y+5} L{x-45} {y-7} L{x-37} {y-15} Z" fill="#2AA4F4"/>',f'<path d="M{x+6} {y-30} V{y+31} L{x+28} {y+27} V{y-25} Z" fill="#1272BC"/>']
    return ''.join(p)

def stack_tile(x,y,w,h,name):
    # 'name' at foot and mark centered.
    s=[rect(x,y,w,h,'#0B1A30',16,'#223D61'),rect(x+3,y+3,w-6,3,'#19365E',2)]
    s.append(icon(name,x+w/2,y+(51 if h<160 else 67),78 if h<160 else 88))
    s.append(text(x+w/2,y+h-22,name,24,C['text'],600,'middle'))
    return ''.join(s)

def card_base(x,y,w,h,title,num,subtitle,count,accent):
    arr=[rect(x,y,w,h,'url(#panel)',26,'#29466C',2),rect(x+20,y+20,5,54,accent,2),text(x+42,y+45,num,20,accent,700,spacing=2,mono=True),text(x+118,y+52,title,34,C['white'],750),text(x+42,y+93,subtitle,23,C['dim'],400),line(x+42,y+116,x+w-42,y+116,'#2E4C72',1),rect(x+w-120,y+27,93,38,'#102843',19,'#2B4A6C',1),text(x+w-74,y+52,count,18,accent,650,'middle',0.8,True)]
    return arr

def board_desktop():
    w,h=1600,735
    a=[circle(310,160,260,'url(#aura)'),circle(1360,640,250,'url(#aura)')]
    # cards top
    for x,wi,title,num,subtitle,icons,accent in [
        (16,765,'Frontend','01','Interfaces, experiências e interação.',['HTML5','CSS3','JavaScript','React','Next.js'],C['cyan']),
        (801,783,'Backend','02','APIs, lógica de negócio e serviços.',['Node.js','Python','Java','C#','.NET'],C['blue'])]:
        a += card_base(x,12,wi,393,title,num,subtitle,'05 TECHS',accent)
        tilew=132; gap=10; start=x+42
        for i,tech in enumerate(icons):a.append(stack_tile(start+i*(tilew+gap),149,tilew,199,tech))
        a.append(text(x+42,379,'BUILD  /  SHIP  /  IMPROVE',17,accent,550,spacing=1.6,mono=True))
    # bottom full width, horizontal
    x,y,wi,hi=16,427,1568,275
    a += card_base(x,y,wi,hi,'Dados & Ferramentas','03','Persistência, versionamento e ambiente de desenvolvimento.','04 TECHS',C['purple'])
    for i,tech in enumerate(['PostgreSQL','Git','GitHub','VS Code']):
        a.append(stack_tile(510+i*254,568,238,105,tech) if False else '')
    # bottom compact tile with icon at center left + text right
    for i,tech in enumerate(['PostgreSQL','Git','GitHub','VS Code']):
        xx=487+i*272
        a += [rect(xx,571,250,105,'#0B1A30',18,'#244264'),icon(tech,xx+56,624,82),text(xx+106,632,tech,23,C['text'],650)]
    a.append(text(58,615,'DATABASE',19,C['purple'],650,spacing=1.3,mono=True)); a.append(text(58,647,'&amp; DEV WORKFLOW'.replace('&amp;','&'),23,C['text'],600))
    return svgbody(w,h,a)

def board_mobile():
    w,h=760,1460
    a=[]
    specs=[('Frontend','01','Interfaces, experiências e interação.',['HTML5','CSS3','JavaScript','React','Next.js'],C['cyan']),('Backend','02','APIs, lógica de negócio e serviços.',['Node.js','Python','Java','C#','.NET'],C['blue']),('Dados & Ferramentas','03','Persistência e fluxo de desenvolvimento.',['PostgreSQL','Git','GitHub','VS Code'],C['purple'])]
    yy=15
    for title,num,sub,icons,accent in specs:
        hi=465 if len(icons)==5 else 455
        a += card_base(15,yy,730,hi,title,num,sub,f'{len(icons):02d} TECHS',accent)
        tx,ty=43,yy+138
        tilew=210; gap=10; tileh=135
        for i,tech in enumerate(icons):
            xx=tx+(i%3)*(tilew+gap); cy=ty+(i//3)*164
            a.append(stack_tile(xx,cy,tilew,tileh,tech))
        yy+=hi+19
    return svgbody(w,h,a)

def focus_strip():
    w,h=1600,178
    a=[rect(0,2,1600,169,'url(#panel)',26,'#29466C',2),rect(22,22,1556,4,'url(#bluebar)',2)]
    specs=[('01','STATUS','LEARNING & BUILDING',C['green']),('02','FOCUS','FULLSTACK WEB',C['cyan']),('03','EXPLORING','GAME DEV  +  AI',C['purple'])]
    for i,(num,lab,val,col) in enumerate(specs):
        xx=47+i*520
        a += [circle(xx+17,100,8,col),circle(xx+17,100,18,'none',col,1),text(xx+53,87,lab,19,C['dim'],650,spacing=2,mono=True),text(xx+53,126,val,30,C['white'],740)]
        if i<2:a.append(line(xx+485,49,xx+485,145,'#2A496E',2))
    return svgbody(w,h,a)

for name,body in [('stack-desktop.svg',board_desktop()),('stack-mobile.svg',board_mobile()),('focus-strip.svg',focus_strip())]:
    (ASSETS/name).write_text(body,encoding='utf-8')
    cairosvg.svg2png(bytestring=body.encode(),write_to=str(ASSETS/name.replace('.svg','.png')),output_width=1600 if 'desktop' in name else (760 if 'mobile' in name else 1600))

readme='''<!-- Thiago Patriota | github.com/ThiagoPatriotaDev -->
<!-- Identidade: Terminal Neon / Bento Grid. Assets locais: pasta assets/ -->

<div align="center">
  <img src="./assets/thiago-ascii-banner.gif" width="100%" alt="Banner horizontal animado de Thiago Patriota, com retrato ASCII, terminal em tons de azul e TARDIS" />
</div>

<br>

<div align="center">
  <sub>SOFTWARE ENGINEERING  ·  WEB DEVELOPMENT  ·  CREATIVE TECHNOLOGY</sub>
  <h2>FullStack Web Developer em formação</h2>
  <p>Construindo interfaces, sistemas e experiências digitais com foco em <b>Web, tecnologia e criatividade.</b></p>
  <img src="./assets/focus-strip.svg" alt="Status: Learning & Building. Foco: FullStack Web. Explorando: Game Dev e inteligência artificial." width="100%" />
</div>

<br>

### `01 / SOBRE MIM`

Sou estudante de **Engenharia de Software no IFPE** e gosto de transformar ideias em interfaces e sistemas que sejam simples de usar, agradáveis de explorar e sólidos por dentro.

Minha jornada está concentrada em **desenvolvimento FullStack**, passando por frontend, backend, banco de dados e ferramentas do ciclo de software. Também venho experimentando **inteligência artificial, Agents e Skills**, além de explorar o universo do **Game Dev**.

<br>

### `02 / MINHA STACK`

<div align="center">
  <p><sub>TECNOLOGIAS & FERRAMENTAS COM QUE ESTUDO E CONSTRUO</sub></p>
  <picture>
    <source media="(max-width: 650px)" srcset="./assets/stack-mobile.svg">
    <img src="./assets/stack-desktop.svg" alt="Painel de tecnologias. Frontend: HTML5, CSS3, JavaScript, React e Next.js. Backend: Node.js, Python, Java, C# e .NET. Dados e Ferramentas: PostgreSQL, Git, GitHub e VS Code." width="100%">
  </picture>
</div>

<details>
<summary><b>Ver lista completa de tecnologias em texto</b></summary>

- **Frontend:** HTML5 · CSS3 · JavaScript · React · Next.js
- **Backend:** Node.js · Python · Java · C# · .NET
- **Dados & Ferramentas:** PostgreSQL · Git · GitHub · VS Code

</details>

<br>

### `03 / ATIVIDADE NO GITHUB`

<div align="center">
  <p><sub>COMMITS • COLABORAÇÃO • EVOLUÇÃO CONTÍNUA</sub></p>
  <img src="https://github-readme-activity-graph.vercel.app/graph?username=ThiagoPatriotaDev&amp;bg_color=0B1527&amp;color=D8E7FC&amp;line=5EA9FF&amp;point=58E4F1&amp;area=true&amp;hide_border=true&amp;area_color=12376D" alt="Gráfico de atividade de ThiagoPatriotaDev no GitHub" width="100%" />
</div>

<br>

### `04 / VAMOS CONVERSAR?`

<div align="center">
  <p>Uma ideia, uma colaboração ou só uma boa conversa sobre tecnologia? Me encontra por aqui.</p>
  <a href="mailto:thiagosilvapatriota@gmail.com"><img src="https://img.shields.io/badge/EMAIL-0B1527?style=for-the-badge&amp;logo=gmail&amp;logoColor=58E4F1" alt="Enviar e-mail" /></a>
  <a href="https://www.linkedin.com/in/thiago-patriota-a6841b271"><img src="https://img.shields.io/badge/LINKEDIN-0B1527?style=for-the-badge&amp;logo=linkedin&amp;logoColor=5EA9FF" alt="LinkedIn de Thiago Patriota" /></a>
  <a href="https://github.com/ThiagoPatriotaDev"><img src="https://img.shields.io/badge/GITHUB-0B1527?style=for-the-badge&amp;logo=github&amp;logoColor=D8E7FC" alt="Perfil do GitHub" /></a>
  <br><br>
  <samp>Code. Build. Learn. Repeat.</samp>
</div>
'''
(ROOT/'README.md').write_text(readme,encoding='utf-8')

# Preview of the actual locally generated assets (the graph itself requires live external data).
W=1150; pad=46
banner_gif=Image.open(ASSETS/'thiago-ascii-banner.gif');banner_gif.seek(7);banner=banner_gif.convert('RGB')
focus=Image.open(ASSETS/'focus-strip.png').convert('RGB')
stacks=Image.open(ASSETS/'stack-desktop.png').convert('RGBA')
scale=(W-2*pad)/1600
banner=banner.resize((W-2*pad,int(banner.height*scale)),Image.Resampling.LANCZOS)
focus=focus.resize((W-2*pad,int(focus.height*scale)),Image.Resampling.LANCZOS)
stacks=stacks.resize((W-2*pad,int(stacks.height*scale)),Image.Resampling.LANCZOS)
canvas=Image.new('RGB',(W,1820),'#0D1117')
d=ImageDraw.Draw(canvas)
regular='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'; bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'; mono='/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
F=lambda path,n:ImageFont.truetype(path,n)
y=36
canvas.paste(banner,(pad,y));y+=banner.height+30
d.text((pad+4,y),'FULLSTACK WEB DEVELOPER EM FORMAÇÃO',font=F(bold,30),fill='#EDF5FF');y+=48
d.text((pad+4,y),'Construindo interfaces, sistemas e experiências digitais com foco em Web, tecnologia e criatividade.',font=F(regular,17),fill='#ACBFDA');y+=42
canvas.paste(focus,(pad,y));y+=focus.height+42
d.text((pad+4,y),'01 / SOBRE MIM',font=F(mono,25),fill='#61B6F9');y+=40
for linev in ['Estudante de Engenharia de Software no IFPE. Construo experiências digitais','e evoluo como FullStack, explorando IA, Agents, Skills e Game Dev.']:
    d.text((pad+4,y),linev,font=F(regular,19),fill='#DEE8F4');y+=29
y+=42
d.text((pad+4,y),'02 / MINHA STACK',font=F(mono,25),fill='#61B6F9');y+=48
canvas.paste(stacks,(pad,y),mask=stacks.getchannel('A'));y+=stacks.height+38
d.text((pad+4,y),'03 / ATIVIDADE NO GITHUB',font=F(mono,25),fill='#61B6F9');y+=45
# graph preview placeholder, not invented contributions
box=(pad,y,W-pad,y+150)
d.rounded_rectangle(box,radius=18,fill='#0B1527',outline='#234167',width=2)
d.text((pad+40,y+55),'Gráfico dinâmico de atividades do GitHub',font=F(regular,22),fill='#D9E8FF');d.text((pad+40,y+91),'(carregado no README diretamente do serviço externo)',font=F(regular,16),fill='#90A8C9')
y+=205
d.text((pad+4,y),'04 / VAMOS CONVERSAR?',font=F(mono,25),fill='#61B6F9');y+=47
d.text((pad+4,y),'EMAIL     •     LINKEDIN     •     GITHUB',font=F(bold,23),fill='#E4F1FC');y+=78
d.text((W//2,y),'Code. Build. Learn. Repeat.',font=F(mono,20),anchor='mm',fill='#9CB5D4')
canvas=canvas.crop((0,0,W,max(100,y+65)))
canvas.save(ROOT/'PREVIEW.png')
# Full-resolution mobile card preview for checking legibility and spacing.
Image.open(ASSETS/'stack-mobile.png').save(ROOT/'STACK-MOBILE-PREVIEW.png')

(root_note:=ROOT/'INSTRUCOES.md').write_text('''# Instalação

1. Abra o repositório `ThiagoPatriotaDev/ThiagoPatriotaDev`.
2. Substitua `README.md` pelo arquivo deste pacote.
3. Envie a pasta `assets/` inteira (principalmente `thiago-ascii-banner.gif`, `focus-strip.svg`, `stack-desktop.svg` e `stack-mobile.svg`).
4. Confirme a exibição em `Preview` no GitHub.

## Personalização

- Alterar a descrição, títulos e links de contato: editar `README.md`.
- Alterar as listas de tecnologias: editar a seção de texto no `README.md` e, para atualizar os cards visuais, o script `build_thiago_modern.py` (incluso).
- Banner animado: arquivo `assets/thiago-ascii-banner.gif`, preservado da versão anterior.
- As variantes desktop/mobile são imagens SVG estáticas, sem scripts externos.
- O gráfico de atividade e os badges de contato dependem dos serviços externos mencionados no README.
- Se o tema visual não se ajustar, arquivos PNG equivalentes também estão disponíveis em `assets/`.

**Importante:** o GitHub sanitiza CSS e JavaScript dentro de READMEs. A aparência é feita com HTML básico, Markdown e SVGs próprios.
''',encoding='utf-8')
# Este arquivo já está no diretório do projeto.
zip_path=ROOT.parent/'ThiagoPatriotaDev-Modern-README.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
    for file in ROOT.rglob('*'):
        if file.is_file():z.write(file,arcname='ThiagoPatriotaDev/'+str(file.relative_to(ROOT)))
print('OUTPUT',str(zip_path))
for f in [ROOT/'README.md', ROOT/'PREVIEW.png',ASSETS/'stack-desktop.svg',ASSETS/'stack-mobile.svg',ASSETS/'focus-strip.svg',ASSETS/'thiago-ascii-banner.gif']:
    print(f, f.stat().st_size)
