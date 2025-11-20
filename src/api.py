from fastapi import FastAPI, HTTPException
import pandas as pd

# Criação da aplicação
app = FastAPI(
    title="API de Dados COVID-19",
    description="API para consulta de  dados consolidados de COVID-19.",
    version="1.0.0"
)

# Carregamento de dados
# Para ser mais rápido, carregamos os dados de uma só vez na memória
try:
    DF = pd.read_csv('data/processed/covid_consolidado.csv')
    # Garantir que data é data
    DF['Data'] = pd.to_datetime(DF['Data'])
    print("Base de dadps carregada na API comsucesso!")
except FileNotFoundError:
    print("ERRO: Arquivo não encontrado. Rode o ETL primeiro.")
    DF = pd.DataFrame() # DataFrame vazio pra não quebrar o app, mas vai dar erro na rota
    
# ROTAS (ENDPOINTS)

@app.get("/")
def home():
    """
    Rota raiz para verificar se a API está online.
    """
    return {"status": "online", "message": "Bem-vindo à API COVID-19. Acesse /docs para doumentação."}

@app.get("/paises")
def listar_paises():
    """
    Retorna a lista de todos os países disponíveis na base.
    """
    paises = sorted(DF["País"].unique().tolist())
    return {"total": len(paises), "paises": paises}

@app.get("/dados/{pais}")
def get_dados_pais(pais: str):
    """
    Retorna o ULTIMO registro disponível para um país específico.
    """
    # Filtra ignorando maiusculas/minusculas
    pais_df= DF[DF['País'].str.lower() == pais.lower()]
    
    if pais_df.empty:
        raise HTTPException(status_code=404, detail="País não encontrado")
    
    # Pega o  ultimo dado (data mais recente)
    ultimo_dado = pais_df.sort_values('Data').iloc[-1]
    
    return {
        "pais": ultimo_dado['País'],
        "continente": ultimo_dado['Continente'],
        "data_referencia": ultimo_dado['Data'].strftime('%Y-%m-%d'),
        "casos_acumulados": int(ultimo_dado['Casos_Acumulado_dia']),
        "mortes_acumuladas": int(ultimo_dado['Mortes_Acumulado_dia']),
        "taxa_letalidade": round(ultimo_dado['Taxa_Letalidade'], 2),
    }
    
@app.get("/ranking/letalidade")
def ranking_letalidade(top: int = 5):
    """
    Retorna oTOP N países com maior taxa de letalidade (na data mais recente).
    """
    # Pega apenas a data mais recente de cada país
    # 1° Ordena por data, 2° Remove duplicata
    df_recente = DF.sort_values('Data').drop_duplicates(subset=['País'], keep='last')
    
    # Filtra países com poucos casos para evitar distorção
    df_recente = df_recente[df_recente['Casos_Acumulado_dia'] > 1000]
    
    top_df = df_recente.nlargest(top, 'Taxa_Letalidade')
    
    resultado = []
    for _, row in top_df.iterrows():
        resultado.append({
            "pais": row['País'],
            "letalidade": round(row['Taxa_Letalidade'], 2),
            "total_casos": int(row['Casos_Acumulado_dia'])
        })
        
    return resultado