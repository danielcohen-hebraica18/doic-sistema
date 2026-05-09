# ============================================================================
# api/gerar-pdf.py — DOIC-8000
# Gera o PDF profissional usando ReportLab (igual ao gerado no agente)
# Runtime: Python 3.9 (Vercel Serverless)
# ============================================================================

from http.server import BaseHTTPRequestHandler
import json, os, base64
from io import BytesIO
from datetime import datetime

# ReportLab
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import Flowable

# ── Paleta ───────────────────────────────────────────────────────────────────
AZ_ESC  = colors.HexColor("#0D1B2A")
AZ_MED  = colors.HexColor("#1B3A5C")
AZ_CLA  = colors.HexColor("#2E6DA4")
CIN_CLA = colors.HexColor("#F4F6F9")
CIN_BRD = colors.HexColor("#CDD5DF")
VERM    = colors.HexColor("#C0392B")
LAR     = colors.HexColor("#E67E22")
AMAR    = colors.HexColor("#F39C12")
BRNC    = colors.white
PRETO   = colors.black
CIN_TXT = colors.HexColor("#555555")

PAGE_W, PAGE_H = A4
MARGIN  = 2.0 * cm
CONT_W  = PAGE_W - 2 * MARGIN

def S(name, **kw):
    return ParagraphStyle(name, **kw)

ST_CAPA = S("Capa", fontName="Helvetica-Bold", fontSize=20, textColor=BRNC, alignment=TA_CENTER, leading=26)
ST_H1   = S("H1",   fontName="Helvetica-Bold", fontSize=13, textColor=AZ_ESC, spaceBefore=12, spaceAfter=3, leading=17)
ST_H2   = S("H2",   fontName="Helvetica-Bold", fontSize=10, textColor=AZ_MED, spaceBefore=7,  spaceAfter=2, leading=14)
ST_H3   = S("H3",   fontName="Helvetica-Bold", fontSize=9,  textColor=AZ_CLA, spaceBefore=4,  spaceAfter=1, leading=12)
ST_BODY = S("Body", fontName="Helvetica",       fontSize=9,  textColor=PRETO,  leading=13, spaceAfter=4, alignment=TA_JUSTIFY)
ST_SM   = S("Sm",   fontName="Helvetica",       fontSize=8,  textColor=PRETO,  leading=11, spaceAfter=2, alignment=TA_JUSTIFY)
ST_NOTE = S("Note", fontName="Helvetica-Oblique", fontSize=8, textColor=CIN_TXT, leading=11, spaceAfter=3)
ST_FONT = S("Font", fontName="Helvetica-Oblique", fontSize=7.5, textColor=CIN_TXT, leading=10, spaceAfter=2)
ST_CABH = S("CabH", fontName="Helvetica-Bold", fontSize=8,  textColor=BRNC,   alignment=TA_CENTER, leading=11)
ST_CEL  = S("Cel",  fontName="Helvetica",       fontSize=7.5, textColor=PRETO, alignment=TA_LEFT,   leading=10)
ST_CELC = S("CelC", fontName="Helvetica",       fontSize=7.5, textColor=PRETO, alignment=TA_CENTER, leading=10)
ST_ROD  = S("Rod",  fontName="Helvetica",       fontSize=7,   textColor=CIN_TXT, alignment=TA_CENTER, leading=10)

class AlertBar(Flowable):
    def __init__(self, txt, cor=VERM, w=None, h=18):
        super().__init__(); self.txt=txt; self.cor=cor; self.w=w or CONT_W; self.h=h
    def wrap(self,*a): return self.w, self.h
    def draw(self):
        c=self.canv; c.setFillColor(self.cor); c.rect(0,0,self.w,self.h,fill=1,stroke=0)
        c.setFillColor(BRNC); c.setFont("Helvetica-Bold",8.5); c.drawCentredString(self.w/2,5,self.txt)

class Rule(Flowable):
    def __init__(self, w=None, cor=AZ_MED, t=1.5):
        super().__init__(); self.w=w or CONT_W; self.cor=cor; self.t=t
    def wrap(self,*a): return self.w, self.t+4
    def draw(self):
        c=self.canv; c.setStrokeColor(self.cor); c.setLineWidth(self.t); c.line(0,2,self.w,2)

def bloco_dois(titulo, texto, cor):
    d = [[
        Paragraph(titulo, S("_bt", fontName="Helvetica-Bold", fontSize=9, textColor=BRNC, leading=12)),
        Paragraph(texto,  S("_bb", fontName="Helvetica", fontSize=8.5, textColor=PRETO, leading=12, alignment=TA_JUSTIFY)),
    ]]
    t = Table(d, colWidths=[3.5*cm, CONT_W-3.5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(0,-1),cor),("BACKGROUND",(1,0),(1,-1),CIN_CLA),
        ("VALIGN",(0,0),(-1,-1),"TOP"),("TOPPADDING",(0,0),(-1,-1),6),
        ("BOTTOMPADDING",(0,0),(-1,-1),6),("LEFTPADDING",(0,0),(-1,-1),6),
        ("RIGHTPADDING",(0,0),(-1,-1),6),("BOX",(0,0),(-1,-1),0.5,CIN_BRD),
    ]))
    return t

def gerar_pdf_bytes(dados):
    buf = BytesIO()
    agora = datetime.now()
    data_str   = dados.get("data_emissao", agora.strftime("%d/%m/%Y"))
    corte_str  = dados.get("corte_coleta", agora.strftime("%d de %B de %Y — %H:%M (horario de Brasilia)"))
    nivel_ameaca  = dados.get("nivel_ameaca_global", "ALTO")
    nivel_hebraica= dados.get("nivel_alerta_hebraica", "MODERADO-ELEVADO")
    resumo        = dados.get("resumo_executivo", {})
    ocorrencias   = dados.get("tabela_ocorrencias", [])
    sinais        = dados.get("sinais_emergentes", [])
    grade         = dados.get("grade_riscos", [])
    avaliacao     = dados.get("avaliacao_impacto", {})
    recs          = dados.get("recomendacoes", {})
    consolidado   = dados.get("relatorio_consolidado", {})

    doc = SimpleDocTemplate(buf, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=1.8*cm, bottomMargin=1.8*cm,
        title="Relatorio DOIC-8000", author="Sistema DOIC-8000")

    story = []

    # ── CAPA ─────────────────────────────────────────────────────────────────
    blk = [[Paragraph("PROTOCOLO DOIC-8000<br/>INTELIGENCIA CONTRATERRORISMO<br/>CLUBE A HEBRAICA DE SAO PAULO", ST_CAPA)]]
    t = Table(blk, colWidths=[CONT_W])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),AZ_ESC),
        ("TOPPADDING",(0,0),(-1,-1),20),("BOTTOMPADDING",(0,0),(-1,-1),20),
        ("LEFTPADDING",(0,0),(-1,-1),12),("RIGHTPADDING",(0,0),(-1,-1),12)]))
    story.append(t); story.append(Spacer(1,10))
    story.append(Paragraph("RELATORIO EXECUTIVO DE INTELIGENCIA", ST_H1))
    story.append(Rule()); story.append(Spacer(1,5))

    meta = [
        ["Data de emissao:", data_str],
        ["Corte da coleta:", corte_str],
        ["Classificacao:", "USO INTERNO - RESTRITO"],
        ["Destinatario:", "Diretoria / Seguranca Institucional - Clube A Hebraica de SP"],
        ["Analista:", "Sistema DOIC-8000 - Agente de Inteligencia Senior"],
        ["Fontes:", "OSINT - Exclusivamente fontes publicas abertas"],
    ]
    mt = Table(meta, colWidths=[4.5*cm, CONT_W-4.5*cm])
    mt.setStyle(TableStyle([
        ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),("FONTNAME",(1,0),(1,-1),"Helvetica"),
        ("FONTSIZE",(0,0),(-1,-1),9),("TEXTCOLOR",(0,2),(1,2),VERM),
        ("FONTNAME",(0,2),(1,2),"Helvetica-Bold"),("VALIGN",(0,0),(-1,-1),"TOP"),
        ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
    ]))
    story.append(mt); story.append(Spacer(1,10))
    story.append(AlertBar(f"NIVEL GERAL DE AMEACA GLOBAL CONTRA ALVOS JUDAICOS: {nivel_ameaca}", VERM))
    story.append(Spacer(1,4))
    story.append(AlertBar(f"NIVEL DE ALERTA - CLUBE A HEBRAICA DE SAO PAULO: {nivel_hebraica}", LAR))
    story.append(Spacer(1,8))
    story.append(Paragraph(
        "<b>AVISO LEGAL:</b> Documento produzido exclusivamente para fins defensivos, preventivos e protetivos. "
        "Todas as informacoes provem de fontes publicas (OSINT). Proibida reproducao sem autorizacao.",
        ST_NOTE))
    story.append(PageBreak())

    # ── RESUMO EXECUTIVO ─────────────────────────────────────────────────────
    story.append(Paragraph(f"1. RESUMO EXECUTIVO DIARIO — {data_str}", ST_H1))
    story.append(Rule()); story.append(Spacer(1,4))
    story.append(Paragraph(f"Periodo: {resumo.get('periodo','Ultimas 24-72 horas')} | Corte: {corte_str}", ST_NOTE))
    story.append(Spacer(1,5))

    blocos_resumo = [
        ("CENARIO GEOPOLITICO GLOBAL", resumo.get("contexto_geopolitico",""), AZ_MED),
        ("PADRAO EUROPEU DE ANTISSEMITISMO", resumo.get("padrao_europeu",""), VERM),
        ("REFLEXO NO BRASIL E HEBRAICA SP", resumo.get("reflexo_brasil",""), LAR),
    ]
    for titulo, texto, cor in blocos_resumo:
        if texto:
            story.append(KeepTogether([bloco_dois(titulo, texto, cor), Spacer(1,5)]))
    story.append(PageBreak())

    # ── TABELA DE OCORRÊNCIAS ─────────────────────────────────────────────────
    story.append(Paragraph("2. TABELA DE OCORRENCIAS MONITORADAS", ST_H1))
    story.append(Rule()); story.append(Spacer(1,5))

    if ocorrencias:
        cab = [Paragraph(h, ST_CABH) for h in
               ["Data","Local","Classificacao","Resumo","Gravidade","Validacao","Fonte Principal"]]
        rows = [cab]
        cor_grav = {"CRITICO": VERM, "ALTO": LAR, "MEDIO": AMAR, "BAIXO": colors.HexColor("#27AE60")}
        for oc in ocorrencias:
            grav = oc.get("gravidade","MEDIO").upper()
            cg = cor_grav.get(grav, PRETO)
            rows.append([
                Paragraph(oc.get("data",""), ST_CELC),
                Paragraph(oc.get("local",""), ST_CEL),
                Paragraph(oc.get("classificacao",""), ST_CEL),
                Paragraph(oc.get("resumo",""), ST_CEL),
                Paragraph(grav, S(f"_g{grav}", fontName="Helvetica-Bold", fontSize=7.5, textColor=cg, alignment=TA_CENTER, leading=10)),
                Paragraph(oc.get("validacao",""), ST_CELC),
                Paragraph(oc.get("fonte_principal",""), ST_CEL),
            ])
        cw = [1.9*cm, 2.0*cm, 2.2*cm, 4.5*cm, 1.5*cm, 2.2*cm, 2.5*cm]
        tbl = Table(rows, colWidths=cw, repeatRows=1)
        tbl.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),AZ_ESC),("GRID",(0,0),(-1,-1),0.4,CIN_BRD),
            ("VALIGN",(0,0),(-1,-1),"TOP"),("TOPPADDING",(0,0),(-1,-1),3),
            ("BOTTOMPADDING",(0,0),(-1,-1),3),("LEFTPADDING",(0,0),(-1,-1),3),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[BRNC,CIN_CLA]),
        ]))
        story.append(tbl)
        story.append(Spacer(1,5))
        story.append(Paragraph(
            "<b>Legenda:</b> A = completamente confiavel | 1 = confirmado | 2 = provavel | "
            "A1 = fonte muito confiavel, fato confirmado | A2 = fato provavel", ST_NOTE))
    else:
        story.append(Paragraph("Nenhuma ocorrencia registrada neste ciclo.", ST_BODY))
    story.append(PageBreak())

    # ── SINAIS EMERGENTES ─────────────────────────────────────────────────────
    story.append(Paragraph("3. SINAIS EMERGENTES / EM APURACAO", ST_H1))
    story.append(Rule()); story.append(Spacer(1,5))
    cor_sinal = {"Confirmado": VERM, "Parcialmente Corroborado": LAR,
                 "Hipotese Analitica": AZ_MED, "Avaliacao Prospectiva": AZ_CLA}
    for sinal in sinais:
        sit = sinal.get("situacao_analitica","Avaliacao Prospectiva")
        cor = cor_sinal.get(sit, AZ_CLA)
        ht = Table([[
            Paragraph(sinal.get("titulo",""), S("_ht",fontName="Helvetica-Bold",fontSize=9,textColor=BRNC,leading=12)),
            Paragraph(f"[{sit}]", S("_hs",fontName="Helvetica-Bold",fontSize=8,textColor=BRNC,leading=12,alignment=TA_CENTER)),
        ]], colWidths=[CONT_W*0.62, CONT_W*0.38])
        ht.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),cor),
            ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),("LEFTPADDING",(0,0),(-1,-1),6)]))
        texto_sinal = sinal.get("descricao","")
        if sinal.get("reflexo_brasil"): texto_sinal += f" | Reflexo Brasil: {sinal['reflexo_brasil']}"
        if sinal.get("recomendacao"):   texto_sinal += f" | Recomendacao: {sinal['recomendacao']}"
        bt = Table([[Paragraph(texto_sinal, ST_SM)]], colWidths=[CONT_W])
        bt.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),CIN_CLA),("GRID",(0,0),(-1,-1),0.4,CIN_BRD),
            ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),("LEFTPADDING",(0,0),(-1,-1),6)]))
        story.append(KeepTogether([ht, bt, Spacer(1,5)]))
    story.append(PageBreak())

    # ── GRADE DE RISCOS ───────────────────────────────────────────────────────
    story.append(Paragraph("4. GRADE DE RISCOS / MATRIZ DE RISCO", ST_H1))
    story.append(Rule()); story.append(Spacer(1,4))
    story.append(Paragraph(
        "<b>Formula:</b> Risco = Probabilidade (1-5) x Impacto (1-5) | "
        "1-4=Baixo | 5-9=Moderado | 10-14=Relevante | 15-19=Alto | 20-25=Critico", ST_NOTE))
    story.append(Spacer(1,5))

    if grade:
        cor_cls = {"CRITICO":VERM,"ALTO":LAR,"RELEVANTE":AMAR,"MODERADO":colors.HexColor("#27AE60")}
        cab_r = [Paragraph(h,ST_CABH) for h in ["Risco","Prob.","Impacto","Score","Class.","Justificativa","Mitigacao"]]
        rows_r = [cab_r]
        for r in grade:
            cls = r.get("classificacao","MODERADO").upper()
            clr = cor_cls.get(cls, PRETO)
            rows_r.append([
                Paragraph(r.get("risco",""), ST_CEL),
                Paragraph(str(r.get("probabilidade","")), ST_CELC),
                Paragraph(str(r.get("impacto","")), ST_CELC),
                Paragraph(str(r.get("score","")), ST_CELC),
                Paragraph(cls, S(f"_rc{cls}",fontName="Helvetica-Bold",fontSize=8,textColor=clr,alignment=TA_CENTER,leading=11)),
                Paragraph(r.get("justificativa",""), ST_CEL),
                Paragraph(r.get("mitigacao",""), ST_CEL),
            ])
        rt = Table(rows_r, colWidths=[3.2*cm,1.0*cm,1.2*cm,1.1*cm,1.6*cm,2.8*cm,2.9*cm], repeatRows=1)
        rt.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),AZ_ESC),("GRID",(0,0),(-1,-1),0.4,CIN_BRD),
            ("VALIGN",(0,0),(-1,-1),"TOP"),("TOPPADDING",(0,0),(-1,-1),4),
            ("BOTTOMPADDING",(0,0),(-1,-1),4),("LEFTPADDING",(0,0),(-1,-1),3),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[BRNC,CIN_CLA]),
        ]))
        story.append(rt)
    story.append(PageBreak())

    # ── AVALIAÇÃO HEBRAICA ────────────────────────────────────────────────────
    story.append(Paragraph("5. AVALIACAO DE IMPACTO — CLUBE A HEBRAICA DE SAO PAULO", ST_H1))
    story.append(Rule()); story.append(Spacer(1,5))
    story.append(AlertBar(
        f"NIVEL DE ALERTA: {avaliacao.get('nivel_alerta_recomendado','MODERADO-ELEVADO')} | EXPOSICAO ATUAL: ELEVADA",
        LAR, h=18))
    story.append(Spacer(1,6))
    if avaliacao.get("justificativa_nivel"):
        story.append(Paragraph("<b>Justificativa:</b>", ST_H3))
        story.append(Paragraph(avaliacao["justificativa_nivel"], ST_BODY))
        story.append(Spacer(1,5))

    vetores = [
        ("RISCO FISICO",        avaliacao.get("risco_fisico",""),        LAR),
        ("RISCO DIGITAL",       avaliacao.get("risco_digital",""),       VERM),
        ("RISCO REPUTACIONAL",  avaliacao.get("risco_reputacional",""),  AZ_CLA),
        ("RISCO SIMBOLICO",     avaliacao.get("risco_simbolico",""),     VERM),
    ]
    for nome, texto, cor in vetores:
        if texto:
            ht = Table([[Paragraph(nome,S("_vn",fontName="Helvetica-Bold",fontSize=9,textColor=BRNC,leading=12))]],
                       colWidths=[CONT_W])
            ht.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),cor),
                ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),("LEFTPADDING",(0,0),(-1,-1),6)]))
            bt = Table([[Paragraph(texto,ST_SM)]], colWidths=[CONT_W])
            bt.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),CIN_CLA),("GRID",(0,0),(-1,-1),0.4,CIN_BRD),
                ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),("LEFTPADDING",(0,0),(-1,-1),6)]))
            story.append(KeepTogether([ht, bt, Spacer(1,4)]))
    story.append(PageBreak())

    # ── RECOMENDAÇÕES ─────────────────────────────────────────────────────────
    story.append(Paragraph("6. RECOMENDACOES OPERACIONAIS E PREVENTIVAS", ST_H1))
    story.append(Rule()); story.append(Spacer(1,5))

    blocos_rec = [
        ("IMEDIATO — 0 a 72 HORAS", VERM,   recs.get("imediatas_24h",[])),
        ("CURTO PRAZO — 3 a 15 DIAS", LAR,  recs.get("curto_prazo_3_15_dias",[])),
        ("MEDIO PRAZO — 15 a 30 DIAS", AMAR, recs.get("medio_prazo_15_30_dias",[])),
    ]
    for titulo, cor, itens in blocos_rec:
        if itens:
            ht = Table([[Paragraph(titulo,S("_rt",fontName="Helvetica-Bold",fontSize=10,textColor=BRNC,leading=14))]],
                       colWidths=[CONT_W])
            ht.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),cor),
                ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),("LEFTPADDING",(0,0),(-1,-1),8)]))
            story.append(ht)
            for it in itens:
                texto_it = it.get("acao","") if isinstance(it, dict) else str(it)
                prio = it.get("prioridade","") if isinstance(it, dict) else ""
                label = f"[{prio}] " if prio else ""
                story.append(Paragraph(f">> {label}{texto_it}",
                    S("_ri",fontName="Helvetica",fontSize=8.5,textColor=PRETO,leading=12,leftIndent=10,spaceAfter=3)))
            story.append(Spacer(1,8))
    story.append(PageBreak())

    # ── RELATÓRIO CONSOLIDADO + AUDITORIA ─────────────────────────────────────
    story.append(Paragraph("7. RELATORIO CONSOLIDADO E TRILHA DE AUDITORIA", ST_H1))
    story.append(Rule()); story.append(Spacer(1,5))

    if consolidado.get("sintese_ciclo"):
        story.append(Paragraph("<b>Sintese do Ciclo:</b>", ST_H3))
        story.append(Paragraph(consolidado["sintese_ciclo"], ST_BODY))
    if consolidado.get("implicacoes_hebraica"):
        story.append(Paragraph("<b>Implicacoes para a Hebraica SP:</b>", ST_H3))
        story.append(Paragraph(consolidado["implicacoes_hebraica"], ST_BODY))
    if consolidado.get("risco_agregado"):
        story.append(AlertBar(
            f"RISCO AGREGADO: {consolidado['risco_agregado']} — {consolidado.get('justificativa_agregado','')}",
            AZ_MED, h=20))
        story.append(Spacer(1,6))

    lims = consolidado.get("limitacoes_analiticas", [
        "Relatorio produzido exclusivamente com OSINT.",
        "Cenario pode evoluir apos o corte da coleta.",
        "Distincao mantida: fato confirmado / fato provavel / hipotese analitica.",
    ])
    story.append(Paragraph("<b>Limitacoes Analiticas:</b>", ST_H3))
    for l in lims:
        story.append(Paragraph(f">> {l}",
            S("_lim",fontName="Helvetica-Oblique",fontSize=8,textColor=CIN_TXT,leading=11,spaceAfter=3,leftIndent=6)))

    story.append(Spacer(1,10))
    story.append(Rule(cor=AZ_ESC, t=2)); story.append(Spacer(1,6))
    story.append(Paragraph(
        f"PROTOCOLO DOIC-8000 | DATA: {data_str} | {corte_str} | "
        "FINALIDADE EXCLUSIVAMENTE DEFENSIVA, PREVENTIVA E PROTETIVA | "
        "FONTES PUBLICAS (OSINT) | USO INTERNO RESTRITO — CLUBE A HEBRAICA DE SAO PAULO",
        ST_ROD))

    doc.build(story)
    return buf.getvalue()


# ── Handler Vercel ────────────────────────────────────────────────────────────
class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors()
        self.end_headers()

    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            body   = json.loads(self.rfile.read(length)) if length else {}
            dados  = body.get("dados", {})

            pdf_bytes = gerar_pdf_bytes(dados)
            pdf_b64   = base64.b64encode(pdf_bytes).decode('utf-8')

            self.send_response(200)
            self._cors()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"success": True, "pdf_base64": pdf_b64}).encode())

        except Exception as e:
            self.send_response(500)
            self._cors()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def log_message(self, format, *args):
        pass
