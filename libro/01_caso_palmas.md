---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# 1. El caso Palmas de la Sabana

**Pregunta de la junta:** ¿qué sabemos de nuestro acueducto?

## La historia

Palmas de la Sabana es un corregimiento ficticio de la sabana del Caribe colombiano, a 25 minutos
de la cabecera municipal. Tiene unos 2.500 habitantes y 620 suscriptores, casi todos residenciales,
más una escuela, un puesto de salud y dos comercios pequeños.

El servicio lo presta una asociación de usuarios: una junta de cinco personas, un fontanero y una
tesorera, ninguno con formación en ingeniería.

El agua sale de un pozo profundo de 120 m y sube a un tanque elevado de 150 m³. De ahí baja a unos
14 km de red en PVC y asbesto-cemento, construida por etapas durante más de 25 años, casi sin planos.

**Sus problemas:**

- **Servicio por turnos:** el agua llega unas 8 horas al día, y los barrios altos del sector Norte
  Alto casi nunca tienen presión.
- **Más bombeo que consumo:** la bomba trabaja unas 16 horas diarias y nadie sabe cuánta agua se pierde.
- **Energía:** la factura del bombeo es el mayor gasto de la asociación.
- **Fugas:** se reparan cuando afloran en la calle.
- **Proyectos sin sustento:** la alcaldía ofrece recursos, pero la junta no sabe qué pedir.

## La ficha técnica

```{code-cell} ipython3
import json
from pathlib import Path

import pandas as pd

DATOS = Path("..") / "datos"
sistema = json.loads((DATOS / "sistema.json").read_text(encoding="utf-8"))

pd.DataFrame(sistema["sectores"]).T.rename(columns={
    "suscriptores": "Suscriptores",
    "cota_min_m": "Cota mínima (m)",
    "cota_max_m": "Cota máxima (m)",
    "fraccion_medida": "Fracción con medidor",
}).astype({"Suscriptores": int})
```

```{code-cell} ipython3
t = sistema["tanque"]
print(f"Nivel del agua en el tanque: entre {t['cota_fondo_m']:.0f} y {t['cota_rebose_m']:.0f} m s.n.m.")
```

Los sectores más altos quedan muy cerca de esa cota: ahí está la primera pista de por qué al Norte
Alto no le llega el agua.

## Primer recorrido por los datos

La junta tiene diez archivos. Veamos qué contiene cada uno y qué tan completo está.

```{code-cell} ipython3
archivos = sorted(p for p in DATOS.glob("*.csv"))
resumen = []
for p in archivos:
    df = pd.read_csv(p)
    resumen.append({
        "archivo": p.name,
        "filas": len(df),
        "columnas": len(df.columns),
        "celdas vacías (%)": round(100 * df.isna().mean().mean(), 1),
    })
pd.DataFrame(resumen)
```

### Los suscriptores

```{code-cell} ipython3
sus = pd.read_csv(DATOS / "suscriptores.csv")
tabla = (sus.groupby("sector")
            .agg(suscriptores=("id_suscriptor", "count"),
                 personas=("personas", "sum"),
                 con_medidor=("medido", "mean"))
            .assign(con_medidor=lambda d: (100 * d.con_medidor).round(0).astype(int).astype(str) + " %"))
tabla
```

### La facturación

```{code-cell} ipython3
fact = pd.read_csv(DATOS / "facturacion_mensual.csv")
facturado = fact.groupby("mes").volumen_facturado_m3.sum()
ax = facturado.plot(kind="bar", figsize=(9, 3.5), color="#2a6f97",
                    title="Volumen facturado por mes (m³)")
ax.set_xlabel("")
ax.set_ylabel("m³/mes");
```

## Lo que no sabemos

Este primer recorrido muestra tres vacíos que marcarán el resto del libro:

1. **No hay macromedidor funcionando.** La producción del pozo tendrá que estimarse con el horómetro
   de la bomba y tres aforos puntuales (capítulo 2).
2. **La mayoría de los usuarios no tiene medidor.** A ellos se les factura un volumen asignado, que
   puede estar lejos de lo que realmente consumen (capítulos 2 y 7).
3. **Los planos de la red están incompletos.** Solo hay una tabla de tramos por sector, sin
   coordenadas (capítulo 6).

```{admonition} Para el operador
:class: tip
Antes de cualquier cálculo, haga un inventario como el de este capítulo: qué datos tiene, desde
cuándo y qué tan completos están. Saber lo que falta es el primer diagnóstico.
```
