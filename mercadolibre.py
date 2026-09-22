"""
Búsqueda de productos en la API pública de Mercado Libre.
No requiere autenticación para búsquedas simples.

Filtros aplicados:
- Se descartan publicaciones internacionales (compra internacional /
  cross-border), nos quedamos solo con vendedores locales.
- Se prioriza que el vendedor esté en Capital Federal (CABA); si no
  hay ninguna opción en CABA, se usan las del resto del país.
- Dentro de lo que queda, se ordena por precio de menor a mayor.
"""

import requests

ML_SEARCH_URL = "https://api.mercadolibre.com/sites/MLA/search"

# En el campo seller_address.state.name de la API, Capital Federal
# puede figurar con cualquiera de estos nombres según la publicación.
NOMBRES_CABA = {
    "capital federal",
    "ciudad autónoma de buenos aires",
    "ciudad autonoma de buenos aires",
    "caba",
}

# Cuántos resultados le pedimos a la API antes de filtrar, para tener
# margen y no quedarnos sin opciones tras descartar internacionales.
CANTIDAD_A_PEDIR = 20


def _es_internacional(item: dict) -> bool:
    """
    True si la publicación es de compra internacional (cross-border),
    y no de un vendedor local.
    """
    tags = item.get("tags") or []
    if "cross_border" in tags or "international_item" in tags:
        return True

    logistic_type = (item.get("shipping") or {}).get("logistic_type", "")
    if logistic_type == "cross_docking_international":
        return True

    return False


def _es_capital_federal(item: dict) -> bool:
    estado = (
        (item.get("seller_address") or {}).get("state", {}).get("name", "")
    )
    return estado.strip().lower() in NOMBRES_CABA


def buscar_productos(query: str, limite: int = 3) -> list:
    """
    Busca productos en Mercado Libre Argentina, descarta publicaciones
    internacionales, prioriza vendedores de Capital Federal y devuelve
    hasta `limite` productos ordenados de menor a mayor precio.
    """
    params = {"q": query, "limit": CANTIDAD_A_PEDIR}

    try:
        resp = requests.get(ML_SEARCH_URL, params=params, timeout=10)
        resp.raise_for_status()
    except requests.RequestException:
        return []

    data = resp.json()
    items = data.get("results", [])

    # 1) Sacamos las publicaciones internacionales.
    items = [item for item in items if not _es_internacional(item)]

    # 2) Si hay opciones en Capital Federal, nos quedamos solo con esas.
    #    Si no hay ninguna, seguimos con el resto de Argentina.
    de_capital = [item for item in items if _es_capital_federal(item)]
    if de_capital:
        items = de_capital

    # 3) Ordenamos por precio, de menor a mayor.
    items.sort(key=lambda item: item.get("price") or float("inf"))

    resultados = []
    for item in items[:limite]:
        estado = (
            (item.get("seller_address") or {}).get("state", {}).get("name", "")
        )
        resultados.append(
            {
                "id": item.get("id"),
                "titulo": item.get("title"),
                "precio": item.get("price"),
                "imagen": (item.get("thumbnail") or "").replace("http://", "https://"),
                "link": item.get("permalink"),
                "ubicacion": estado,
            }
        )

    return resultados
