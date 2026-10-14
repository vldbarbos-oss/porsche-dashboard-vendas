"""Gera index.html a partir de uma planilha de vendas Porsche (colunas sanitizadas).

Uso:
    python scripts/build_dashboard.py caminho/para/planilha.xlsx

Saídas:
    data/vendas_sanitizadas.csv  -> base tratada, SEM nomes de clientes/vendedores
    index.html                   -> dashboard em arquivo único, com a base embutida
"""
import json, sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
COLS = {
    "sale_id": "sale_id",
    "SaleDateSanitized": "data_venda",
    "PorscheModelSanitized": "modelo",
    "ModelYearSanitized": "ano_modelo",
    "SalesPriceSanitized": "preco",
    "VehicleMileageSanitized": "quilometragem",
    "PayMethodSanitized": "pagamento",
    "CitySanitized": "cidade",
    "StateSanitized": "estado",
    "DeliveryStatusSanitized": "status_entrega",
}

def main(xlsx: str) -> None:
    df = pd.read_excel(xlsx, sheet_name="Sanitized")
    # 1) só colunas sanitizadas; customer_name e salesperson ficam de fora (dado pessoal)
    df = df[list(COLS)].rename(columns=COLS)
    # 2) tipos numéricos garantidos (preço e ano) — sem fórmulas, só valores
    df["preco"] = pd.to_numeric(df["preco"], errors="coerce")
    df["ano_modelo"] = pd.to_numeric(df["ano_modelo"], errors="coerce").astype("Int64")
    # 3) datas INVALID viram vazio (continuam nos totais, saem quando há filtro de período)
    df["data_venda"] = df["data_venda"].where(df["data_venda"] != "INVALID", "")
    df = df.dropna(subset=["preco", "ano_modelo"])
    (ROOT / "data").mkdir(exist_ok=True)
    df.to_csv(ROOT / "data" / "vendas_sanitizadas.csv", index=False)

    rows = [[r.modelo, int(r.ano_modelo), int(r.preco), r.cidade, r.estado, r.pagamento, r.data_venda]
            for r in df.itertuples()]
    tpl = (ROOT / "src" / "template.html").read_text(encoding="utf-8")
    (ROOT / "index.html").write_text(tpl.replace("__DATA__", json.dumps(rows, separators=(",", ":"))), encoding="utf-8")
    print(f"OK: {len(rows)} vendas -> index.html")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
