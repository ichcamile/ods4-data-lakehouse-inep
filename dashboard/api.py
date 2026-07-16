import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd
import uvicorn

app = FastAPI(title="Inteligência em Evasão Escolar (ODS 4)")

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
GOLD_DIR = PROJECT_ROOT / "data" / "gold"

app.mount("/static", StaticFiles(directory=str(BASE_DIR)), name="static")

dim_escola_path = GOLD_DIR / "dim_escola.parquet"
fct_matriculas_path = GOLD_DIR / "fct_matriculas_por_escola_ano.parquet"

df_dim = None
df_fct = None
df_merged_full = None
df_merged_recent = None

def load_data():
    global df_dim, df_fct, df_merged_full, df_merged_recent
    try:
        df_dim = pd.read_parquet(dim_escola_path).fillna(0)
        df_fct = pd.read_parquet(fct_matriculas_path).fillna(0)
        
        # Merge para série histórica
        df_merged_full = pd.merge(df_fct, df_dim, on='cod_escola', how='inner')
        
        # Merge para o ano atual (2024 ou o último disponível)
        ano_recente = df_fct['ano_censo'].max()
        df_merged_recent = df_merged_full[df_merged_full['ano_censo'] == ano_recente]
    except Exception as e:
        print(f"Erro ao carregar dados: {e}")
        df_dim, df_fct, df_merged_full, df_merged_recent = (pd.DataFrame(),) * 4

@app.on_event("startup")
def startup_event():
    load_data()

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    with open(BASE_DIR / "index.html", "r", encoding="utf-8") as f:
        return f.read()

# ==========================================
# 1. KPIs (Ano Recente)
# ==========================================
@app.get("/api/kpis")
async def get_kpis():
    if df_merged_recent.empty: return JSONResponse({"error": "No data"}, status_code=500)
    
    total_escolas = len(df_merged_recent)
    total_matriculas = int(df_merged_recent['qt_matriculas_total'].sum())
    
    # KPIs Focados em Demanda Social e Infraestrutura Crítica
    escolas_eja = len(df_merged_recent[df_merged_recent['in_eja'] == 1])
    pct_eja = (escolas_eja / total_escolas) * 100 if total_escolas else 0
    
    # Vulnerabilidade Crítica (Escolas sem água OU sem internet)
    vulneraveis = len(df_merged_recent[(df_merged_recent['in_agua_potavel'] == 0) | (df_merged_recent['in_internet'] == 0)])
    pct_vuln = (vulneraveis / total_escolas) * 100 if total_escolas else 0
    
    return {
        "ano_referencia": int(df_merged_recent['ano_censo'].max()),
        "total_escolas": total_escolas,
        "total_matriculas": total_matriculas,
        "pct_eja": round(pct_eja, 1),
        "pct_vulneraveis": round(pct_vuln, 1)
    }

# ==========================================
# 2. Storytelling: A Fuga Nacional
# ==========================================
@app.get("/api/evasion_trend")
async def get_evasion_trend():
    """Linha do tempo: Queda livre nas matrículas totais."""
    if df_merged_full.empty: return JSONResponse({"error": "No data"}, status_code=500)
    grouped = df_merged_full.groupby('ano_censo')['qt_matriculas_total'].sum().reset_index().sort_values('ano_censo')
    return {"labels": [int(x) for x in grouped['ano_censo'].tolist()], "total": [float(x) for x in grouped['qt_matriculas_total'].tolist()]}

@app.get("/api/stage_dropout")
async def get_stage_dropout():
    """Gargalo do sistema: A queda massiva entre Fundamental e Médio."""
    if df_merged_full.empty: return JSONResponse({"error": "No data"}, status_code=500)
    grouped = df_merged_full.groupby('ano_censo')[
        ['qt_mat_infantil', 'qt_mat_fundamental', 'qt_mat_medio']
    ].sum().reset_index().sort_values('ano_censo')
    labels = [int(x) for x in grouped['ano_censo'].tolist()]
    f = grouped['qt_mat_fundamental'].tolist()
    m = grouped['qt_mat_medio'].tolist()
    
    retencao = []
    for i in range(len(labels)):
        fund_val = float(f[i])
        med_val = float(m[i])
        pct = (med_val / fund_val * 100) if fund_val > 0 else 0
        retencao.append(round(pct, 2))
        
    return {
        "labels": labels,
        "retencao_medio": retencao
    }

# ==========================================
# 3. O Porquê: A Causa (Infraestrutura) 
# ==========================================
@app.get("/api/infra_evasion_rate")
async def get_infra_evasion_rate():
    """Calcula a variação de matrículas em 10 anos (2014 vs 2024) por Nota de Infraestrutura. Prova de causa e efeito."""
    if df_merged_full.empty: return JSONResponse({"error": "No data"}, status_code=500)
    
    anos_disp = sorted(df_merged_full['ano_censo'].unique())
    if len(anos_disp) < 2: return JSONResponse({"error": "Histórico insuficiente"}, status_code=500)
    
    # Pega o ano recente e o ano 10 anos atrás (ou o mais antigo)
    ano_recente = int(anos_disp[-1])
    ano_base = int(2014 if 2014 in anos_disp else anos_disp[0])
    
    df = df_merged_full[df_merged_full['ano_censo'].isin([ano_base, ano_recente])].copy()
    
    cols_infra = ['in_agua_potavel', 'in_internet', 'in_biblioteca', 'in_laboratorio_info', 'in_quadra_esportes']
    for c in cols_infra:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0).clip(0, 1)
    df['infra_score'] = df[cols_infra].sum(axis=1)
    
    # Agrupa por score e ano
    grouped = df.groupby(['infra_score', 'ano_censo'])['qt_matriculas_total'].sum().reset_index()
    
    labels = []
    variacao = []
    
    for score in range(6):
        val_base = grouped[(grouped['infra_score'] == score) & (grouped['ano_censo'] == ano_base)]['qt_matriculas_total']
        val_rec = grouped[(grouped['infra_score'] == score) & (grouped['ano_censo'] == ano_recente)]['qt_matriculas_total']
        
        b = float(val_base.iloc[0]) if not val_base.empty else 0
        r = float(val_rec.iloc[0]) if not val_rec.empty else 0
        
        pct_change = ((r - b) / b) * 100 if b > 0 else 0
        labels.append(f"Nota {score}")
        variacao.append(round(pct_change, 2))
        
    return {"labels": labels, "variacao": variacao, "ano_base": ano_base, "ano_recente": ano_recente}

@app.get("/api/urban_rural")
async def get_urban_rural():
    if df_merged_full.empty: return JSONResponse({"error": "No data"}, status_code=500)
    df = df_merged_full[df_merged_full['desc_localizacao'] != 'Não informado']
    grouped = df.groupby(['ano_censo', 'desc_localizacao'])['qt_matriculas_total'].sum().reset_index()
    anos = [int(x) for x in sorted(df['ano_censo'].unique())]
    
    # Base 100 Index (Crescimento/Queda Relativa)
    urbana_vals = [float(grouped[(grouped['ano_censo'] == a) & (grouped['desc_localizacao'] == 'Urbana')]['qt_matriculas_total'].sum()) for a in anos]
    rural_vals = [float(grouped[(grouped['ano_censo'] == a) & (grouped['desc_localizacao'] == 'Rural')]['qt_matriculas_total'].sum()) for a in anos]
    
    u_base = urbana_vals[0] if urbana_vals else 1
    r_base = rural_vals[0] if rural_vals else 1
    
    urbana_idx = [round((v / u_base) * 100, 1) if u_base > 0 else 0 for v in urbana_vals]
    rural_idx = [round((v / r_base) * 100, 1) if r_base > 0 else 0 for v in rural_vals]
    
    return {"labels": anos, "urbana": urbana_idx, "rural": rural_idx}

# ==========================================
# 4. Quem Evasão Atinge e a Demanda Social
# ==========================================
@app.get("/api/evasion_gender")
async def get_evasion_gender():
    """Prova matemática de que os homens abandonam mais a escola na transição para o Ensino Médio."""
    if df_merged_recent.empty: return JSONResponse({"error": "No data"}, status_code=500)
    
    f = df_merged_recent
    # Escolas que só têm Fundamental
    so_fund = f[(f["qt_mat_fundamental"] > 0) & (f["qt_mat_medio"] == 0)]
    # Escolas que só têm Médio
    so_medio = f[(f["qt_mat_fundamental"] == 0) & (f["qt_mat_medio"] > 0)]
    
    t_fund = float(so_fund["qt_mat_masculino"].sum() + so_fund["qt_mat_feminino"].sum())
    t_med = float(so_medio["qt_mat_masculino"].sum() + so_medio["qt_mat_feminino"].sum())
    
    pct_masc_fund = (float(so_fund["qt_mat_masculino"].sum()) / t_fund * 100) if t_fund else 0
    pct_fem_fund = (float(so_fund["qt_mat_feminino"].sum()) / t_fund * 100) if t_fund else 0
    
    pct_masc_med = (float(so_medio["qt_mat_masculino"].sum()) / t_med * 100) if t_med else 0
    pct_fem_med = (float(so_medio["qt_mat_feminino"].sum()) / t_med * 100) if t_med else 0
    
    return {
        "labels": ["Fundamental", "Ensino Médio"],
        "masculino": [round(pct_masc_fund, 1), round(pct_masc_med, 1)],
        "feminino": [round(pct_fem_fund, 1), round(pct_fem_med, 1)]
    }

@app.get("/api/social_demand_eja")
async def get_social_demand_eja():
    """A Demanda por Atendimento Social (EJA) e seu Perfil."""
    if df_merged_recent.empty: return JSONResponse({"error": "No data"}, status_code=500)
    
    # 1. Perfil Racial da Demanda por EJA (Vulnerabilidade)
    # Filtramos escolas EXCLUSIVAMENTE de EJA para não sujar o dado racial com alunos regulares
    escolas_eja_puras = df_merged_recent[(df_merged_recent['qt_mat_eja'] > 0) & 
                                         (df_merged_recent['qt_mat_fundamental'] == 0) & 
                                         (df_merged_recent['qt_mat_medio'] == 0)]
    
    branca = float(escolas_eja_puras['qt_mat_branca'].sum())
    preta = float(escolas_eja_puras['qt_mat_preta'].sum())
    parda = float(escolas_eja_puras['qt_mat_parda'].sum())
    
    # 2. Curva Histórica de Demanda EJA vs Médio
    grouped = df_merged_full.groupby('ano_censo')[['qt_mat_eja', 'qt_mat_medio']].sum().reset_index().sort_values('ano_censo')
    
    eja_vals = [float(x) for x in grouped['qt_mat_eja'].tolist()]
    med_vals = [float(x) for x in grouped['qt_mat_medio'].tolist()]
    
    eja_base = eja_vals[0] if eja_vals else 1
    med_base = med_vals[0] if med_vals else 1
    
    eja_idx = [round((v / eja_base) * 100, 1) if eja_base > 0 else 0 for v in eja_vals]
    med_idx = [round((v / med_base) * 100, 1) if med_base > 0 else 0 for v in med_vals]

    return {
        "raca_eja": {
            "Preta e Parda": float(preta + parda),
            "Branca": float(branca)
        },
        "historico": {
            "labels": [int(x) for x in grouped['ano_censo'].tolist()],
            "eja_index": eja_idx,
            "medio_index": med_idx
        }
    }

if __name__ == "__main__":
    print("Iniciando API de Inteligência Analítica em Evasão na porta 8000")
    uvicorn.run("api:app", host="127.0.0.4", port=8000, reload=True)
