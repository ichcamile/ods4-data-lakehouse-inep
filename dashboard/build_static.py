import os
import json
import asyncio

# Configura o diretório correto antes de importar a api
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from api import (
    load_data,
    get_kpis, get_evasion_trend, get_stage_dropout, 
    get_infra_evasion_rate, get_urban_rural, 
    get_evasion_gender, get_social_demand_eja
)

async def main():
    out_dir = "api_data"
    os.makedirs(out_dir, exist_ok=True)
    
    # Carrega os dataframes globais
    print("Carregando dados Parquet...")
    load_data()
    
    endpoints = {
        "kpis": get_kpis,
        "evasion_trend": get_evasion_trend,
        "stage_dropout": get_stage_dropout,
        "infra_evasion_rate": get_infra_evasion_rate,
        "urban_rural": get_urban_rural,
        "evasion_gender": get_evasion_gender,
        "social_demand_eja": get_social_demand_eja
    }
    
    for name, func in endpoints.items():
        print(f"Gerando dados para: {name}.json")
        try:
            res = await func()
            
            # FastAPI JSONResponse tem atributo body, dicts normais não
            if hasattr(res, "body"):
                data = json.loads(res.body)
            else:
                data = res
                
            with open(f"{out_dir}/{name}.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Erro ao gerar {name}: {e}")
            
    print("Build estático concluído com sucesso! Os dados estão na pasta api_data/")

if __name__ == "__main__":
    asyncio.run(main())
