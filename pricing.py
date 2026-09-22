"""
Cálculo de precios para Mundo Encargado.

Fórmula (según la planilla de Gabriel, hoja "credito personal"):
    costo_base = precio_mercadolibre + FLETE_FIJO

    promo_encargado (precio contado) = costo_base x 1,35
    precio_lista                     = costo_base x 1,5
    cuota_6   = (costo_base x 2,25) / 6
    cuota_9   = (costo_base x 2,875) / 9
    cuota_12  = (costo_base x 3,65) / 12
"""

FLETE_FIJO = 40000


def calcular_precios(precio_ml: float) -> dict:
    """
    Recibe el precio del producto tal como figura en Mercado Libre
    y devuelve todos los precios derivados (contado, lista, cuotas).
    """
    costo_base = precio_ml + FLETE_FIJO

    return {
        "costo_base": round(costo_base, 2),
        "promo_encargado": round(costo_base * 1.35, 2),
        "precio_lista": round(costo_base * 1.5, 2),
        "cuota_6": round((costo_base * 2.25) / 6, 2),
        "cuota_9": round((costo_base * 2.875) / 9, 2),
        "cuota_12": round((costo_base * 3.65) / 12, 2),
    }


def formatear_precio(monto: float) -> str:
    """Formatea un número como pesos argentinos: $123.456"""
    return f"${monto:,.0f}".replace(",", ".")
