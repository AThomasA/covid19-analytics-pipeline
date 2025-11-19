import pandas as pd
import os

def run_etl():
    """
    Função principal de ETL (Extract, Transform, Load).
    Lê dados raw, aplica limpeza e regras de negócios, salva na amada processed.
    """
    print(">> Iniciando processo de ETL...")
    
    # 1 EXTRACT (Extração)
    # File Path
    input_file = 'data/raw/Base_Covid.xlsx'
    
    try:
        print(f">> Lendo arquivo Excel: {input_file}")
        # Ler aba de casos
        df_casos = pd.read_excel(input_file, sheet_name='BASE_COVID_CASOS', engine='openpyxl')
        # Ler aba de população
        df_pop = pd.read_excel(input_file, sheet_name='BASE_COVID_POPULACAO', engine='openpyxl')
        
        print(">> Abas carregadas com sucesso.")
        
    except FileNotFoundError:
        print(f">> Erro: Arquivo {input_file} não encontrado.")
        return
    except ValueError as e:
        print(f">> Erro de Leitura: Verifique se os nomes das abas (sheet_name) estão corretos no código.\nErro: {e}")
        return
    
    # 2 TRANSFORM (Transformação)
    # Padronizar nomes das colunas
    df_casos.columns = [c.strip() for c in df_casos.columns]
    df_pop.columns = [c.strip() for c in df_pop.columns]
    
    # Converter datas
    if 'Data' in df_casos.columns:
        df_casos['Data'] = pd.to_datetime(df_casos['Data'])
        
    # Limpeza de strings para o JOIN
    df_casos['País'] = df_casos['País'].astype(str).str.strip()
    df_pop['País'] = df_pop['País'].astype(str).str.strip()
    
    # JOIN (Procv)
    df_final = pd.merge(df_casos, df_pop, on='País', how='left')
    
    # Tratar nulos
    df_final['População'] = df_final['População'].fillna(0)
    
    # Calculos (Feature Engineering)
    df_final['Taxa_Letalidade'] = df_final.apply(
        lambda row: (row['Mortes_Acumulado_dia'] / row['Casos_Acumulado_dia'] * 100)
        if row['Casos_Acumulado_dia'] > 0 else 0, axis=1
    )
    
    df_final['Casos_por_100k'] = df_final.apply(
        lambda row: (row['Casos_Acumulado_dia'] / row['População'] * 100000)
        if row['População'] > 0 else 0, axis=1
    )
    
    # Seleção de colunas 
    cols_interesse = [
        'Continente', 
        'País', 
        'Data', 
        'População', 
        'Casos_Acumulado_dia', 
        'Novos_Casos_dia', 
        'Mortes_Acumulado_dia', 
        'Novas_Mortes_dia', 
        'Taxa_Letalidade', 
        'Casos_por_100k'
    ]
    
    # Filtrar apenas as que existem pra evitar erro
    cols_existentes = [c for c in cols_interesse if c in df_final.columns]
    df_final = df_final[cols_existentes]
    
    # 3 LOAD
    output_path = 'data/processed/covid_consolidado.csv'
    df_final.to_csv(output_path, index=False)
    
    print("-" * 30)
    print(f">> ETL Concluído! Arquivo gerado: {output_path}")
    print(f">> Total de registros: {len(df_final)}")
    print("-" * 30)
    
if __name__ == "__main__":
    run_etl()