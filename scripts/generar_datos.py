"""
Generador de datos sintéticos — Acueducto Comunitario de Palmas de la Sabana
Proyecto: Llave Abierta — libro "Hasta la Última Llave"

TODOS LOS DATOS SON FICTICIOS. Se generan con una semilla fija para que el libro
sea reproducible. Periodo: 1 de octubre de 2025 a 30 de septiembre de 2026.

Uso:
    python scripts/generar_datos.py            # escribe en ./datos
    python scripts/generar_datos.py --salida X # escribe en X
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

SEMILLA = 2026
rng = np.random.default_rng(SEMILLA)

INICIO = pd.Timestamp("2025-10-01")
FIN = pd.Timestamp("2026-09-30 23:00")
MESES = pd.period_range("2025-10", "2026-09", freq="M")

# Temporada seca de la sabana (dic-mar): más consumo, pozo más bajo
FACTOR_SECO = {12: 1.15, 1: 1.18, 2: 1.20, 3: 1.15, 4: 1.05}


def factor_mes(mes: int) -> float:
    return FACTOR_SECO.get(mes, 1.0)


# ---------------------------------------------------------------------------
# 1. Sistema: parámetros generales
# ---------------------------------------------------------------------------
SECTORES = {
    # nombre: (suscriptores, cota_min, cota_max, % medidos)
    "Centro":      (220, 45.0, 55.0, 0.55),
    "Sur":         (160, 40.0, 48.0, 0.40),
    "Oriente":     (130, 48.0, 56.0, 0.35),
    "Norte Alto":  (110, 60.0, 70.0, 0.15),
}
COTA_BASE_TANQUE = 58.0      # m s.n.m. (terreno)
ALTURA_TORRE = 14.0          # m hasta el fondo del tanque
ALTURA_UTIL_TANQUE = 4.0     # m de lámina útil
VOL_TANQUE = 150.0           # m3

sistema = {
    "nombre": "Acueducto Comunitario de Palmas de la Sabana",
    "advertencia": "Datos ficticios con fines educativos",
    "prestador": "Asociación de usuarios (junta de 5 personas, 1 fontanero, 1 tesorera)",
    "habitantes_aprox": 2500,
    "periodo": {"inicio": "2025-10-01", "fin": "2026-09-30"},
    "fuente": {
        "tipo": "Pozo profundo",
        "profundidad_m": 120,
        "nivel_estatico_m": 32,
        "bomba": "Sumergible, 25 HP",
        "caudal_nominal_Ls": 12.0,
        "macromedidor": "Dañado desde 2024; la producción se estima con horómetro y aforos",
    },
    "tanque": {
        "tipo": "Elevado",
        "volumen_m3": VOL_TANQUE,
        "cota_terreno_m": COTA_BASE_TANQUE,
        "cota_fondo_m": COTA_BASE_TANQUE + ALTURA_TORRE,
        "cota_rebose_m": COTA_BASE_TANQUE + ALTURA_TORRE + ALTURA_UTIL_TANQUE,
    },
    "red": {"longitud_aprox_km": 14, "materiales": ["PVC", "Asbesto-cemento"]},
    "acometidas": {"longitud_media_m": 6.0, "material": "PEAD / PVC 1/2 pulg"},
    "operacion": {
        "bombeo": "Aprox. 16 h/día (04:00-20:00), más en temporada seca",
        "distribucion": "Turnos por sector, aprox. 8 h/día cada uno",
    },
    "sectores": {k: {"suscriptores": v[0], "cota_min_m": v[1], "cota_max_m": v[2],
                     "fraccion_medida": v[3]} for k, v in SECTORES.items()},
}

# ---------------------------------------------------------------------------
# 2. Suscriptores (catastro de usuarios)
# ---------------------------------------------------------------------------
filas = []
n = 0
for sector, (cant, cmin, cmax, fmed) in SECTORES.items():
    for _ in range(cant):
        n += 1
        filas.append({
            "id_suscriptor": f"PS-{n:04d}",
            "sector": sector,
            "uso": "Residencial",
            "personas": int(rng.choice([2, 3, 3, 4, 4, 4, 5, 6])),
            "cota_m": round(float(rng.uniform(cmin, cmax)), 1),
            "medido": bool(rng.random() < fmed),
        })
sus = pd.DataFrame(filas)

# Usos no residenciales (reemplazan 4 residenciales del Centro)
especiales = [
    ("Oficial", "Escuela rural", True),
    ("Oficial", "Puesto de salud", True),
    ("Comercial", "Tienda", True),
    ("Comercial", "Restaurante", False),
]
idx_centro = sus.index[sus.sector == "Centro"][:4]
for i, (uso, desc, med) in zip(idx_centro, especiales):
    sus.loc[i, ["uso", "medido"]] = [uso, med]
    sus.loc[i, "personas"] = 0
sus["descripcion"] = ""
for i, (_, desc, _) in zip(idx_centro, especiales):
    sus.loc[i, "descripcion"] = desc

# Medidores: año de instalación y factor de submedición (verdad, no publicado en catastro)
sus["anio_medidor"] = np.where(sus.medido, rng.integers(2008, 2024, len(sus)), pd.NA)
edad = 2026 - sus["anio_medidor"].fillna(2026).astype(int)
sus["_factor_submedicion"] = np.where(
    sus.medido, np.clip(1 - 0.012 * edad - rng.normal(0, 0.02, len(sus)), 0.70, 1.0), 1.0)

# Consumo real base (m3/mes): por persona ~ 3.2 m3/mes (≈ 105 L/hab/d)
base = sus.personas * rng.lognormal(np.log(3.2), 0.18, len(sus))
# Los no medidos consumen más (sin incentivo)
base = np.where(sus.medido, base, base * 1.25)
base = np.where(sus.descripcion == "Escuela rural", 55.0, base)
base = np.where(sus.descripcion == "Puesto de salud", 30.0, base)
base = np.where(sus.descripcion == "Tienda", 12.0, base)
base = np.where(sus.descripcion == "Restaurante", 35.0, base)
sus["_consumo_base_m3mes"] = np.round(base, 2)

# Conexiones fraudulentas: 25 viviendas no catastradas (verdad oculta)
N_FRAUDE = 25
fraude = pd.DataFrame({
    "sector": rng.choice(["Norte Alto", "Oriente", "Sur"], N_FRAUDE, p=[0.5, 0.3, 0.2]),
    "personas": rng.choice([3, 4, 5, 6], N_FRAUDE),
})
fraude["_consumo_base_m3mes"] = fraude.personas * 3.6

# ---------------------------------------------------------------------------
# 3. Facturación mensual
# ---------------------------------------------------------------------------
CARGO_NO_MEDIDO_M3 = 12.0   # volumen asignado a no medidos
reg = []
for p in MESES:
    f = factor_mes(p.month)
    ruido = rng.normal(1.0, 0.08, len(sus))
    real = np.clip(sus._consumo_base_m3mes * f * ruido, 0, None)
    leido = np.where(sus.medido, np.round(real * sus._factor_submedicion), np.nan)
    exento = sus.uso.eq("Oficial")
    facturado = np.where(sus.medido, leido, CARGO_NO_MEDIDO_M3)
    facturado = np.where(exento, 0.0, facturado)
    for i in range(len(sus)):
        reg.append((sus.id_suscriptor.iat[i], str(p), leido[i], facturado[i], real[i]))
fact = pd.DataFrame(reg, columns=["id_suscriptor", "mes", "lectura_m3",
                                  "volumen_facturado_m3", "_consumo_real_m3"])

# ---------------------------------------------------------------------------
# 4. Red de tuberías
# ---------------------------------------------------------------------------
tramos = []
def agregar(sector, material, diam, total_m, anio_rango):
    restante = total_m
    while restante > 0:
        L = float(min(restante, rng.uniform(60, 220)))
        tramos.append({
            "sector": sector, "material": material, "diametro_mm": diam,
            "longitud_m": round(L, 1),
            "anio_instalacion": int(rng.integers(*anio_rango)),
        })
        restante -= L

agregar("Conducción", "PVC", 150, 420, (2005, 2006))
for sector, (cant, *_r) in SECTORES.items():
    frac = cant / 620
    agregar(sector, "Asbesto-cemento", 100, 2400 * frac, (1998, 2004))
    agregar(sector, "Asbesto-cemento", 75, 2600 * frac, (1998, 2004))
    agregar(sector, "PVC", 75, 2600 * frac, (2005, 2021))
    agregar(sector, "PVC", 50, 6000 * frac, (2005, 2021))
red = pd.DataFrame(tramos)
red.insert(0, "id_tramo", [f"T-{i:03d}" for i in range(1, len(red) + 1)])

# ---------------------------------------------------------------------------
# 5. Registro de fugas reparadas
# ---------------------------------------------------------------------------
N_FUGAS = 86
fechas = INICIO + pd.to_timedelta(rng.integers(0, 365, N_FUGAS), unit="D")
tipo = rng.choice(["Acometida", "Red"], N_FUGAS, p=[0.7, 0.3])
fugas = pd.DataFrame({
    "fecha_reporte": fechas.normalize(),
    "sector": rng.choice(list(SECTORES), N_FUGAS, p=[0.30, 0.22, 0.20, 0.28]),
    "tipo": tipo,
    "material": np.where(tipo == "Red",
                         rng.choice(["Asbesto-cemento", "PVC"], N_FUGAS, p=[0.7, 0.3]),
                         "PEAD"),
    "dias_hasta_reparar": rng.integers(1, 15, N_FUGAS),
    "visible": rng.random(N_FUGAS) < 0.9,
}).sort_values("fecha_reporte").reset_index(drop=True)
fugas["fecha_reparacion"] = fugas.fecha_reporte + pd.to_timedelta(fugas.dias_hasta_reparar, unit="D")

# ---------------------------------------------------------------------------
# 6. Bombeo horario (horómetro + estado) y energía
# ---------------------------------------------------------------------------
horas = pd.date_range(INICIO, FIN, freq="h")
bomb = pd.DataFrame({"fecha_hora": horas})
m = bomb.fecha_hora.dt.month
h = bomb.fecha_hora.dt.hour
seco = m.isin([12, 1, 2, 3])
fin_bombeo = np.where(seco, 22, 20)               # en seca se bombea hasta las 22 h
encendida = (h >= 4) & (h < fin_bombeo)
corte = rng.random(len(bomb)) < 0.025             # cortes de energía
bomb["bomba_encendida"] = encendida & ~corte
# Caudal real: baja en temporada seca (abatimiento del pozo) y con desgaste
q_base = 11.6 - 0.6 * seco.astype(float) - 0.25 * (bomb.index / len(bomb))
bomb["_caudal_real_Ls"] = np.where(bomb.bomba_encendida,
                                   np.round(q_base + rng.normal(0, 0.15, len(bomb)), 2), 0.0)
# Potencia: P = rho g Q H / eta ; H ~ 74 m (más en seca)
H = 74 + 4 * seco.astype(float)
eta = 0.55
bomb["energia_kWh"] = np.round(9.81 * bomb._caudal_real_Ls / 1000 * 1000 * H / eta / 1000, 2)
bomb["horometro_h"] = bomb.bomba_encendida.cumsum().astype(float) + 18250.0

# Aforos puntuales (lo único "medido" de caudal)
fechas_aforo = pd.to_datetime(["2025-11-12 09:00", "2026-02-18 10:00", "2026-07-22 09:00"])
aforos = bomb.set_index("fecha_hora").loc[fechas_aforo, ["_caudal_real_Ls"]].rename_axis("fecha_hora").reset_index()
aforos["caudal_aforado_Ls"] = np.round(aforos._caudal_real_Ls * rng.normal(1.0, 0.02, 3), 2)
aforos["metodo"] = "Caudalímetro ultrasónico portátil"
aforos = aforos.drop(columns="_caudal_real_Ls")

# Energía mensual (factura)
TARIFA = 905  # COP/kWh, ficticia
energia = (bomb.groupby(bomb.fecha_hora.dt.to_period("M"))
           .agg(energia_kWh=("energia_kWh", "sum"), horas_bombeo=("bomba_encendida", "sum"))
           .reset_index().rename(columns={"fecha_hora": "mes"}))
energia["energia_kWh"] = energia.energia_kWh.round(0)
energia["tarifa_COP_kWh"] = TARIFA
energia["valor_factura_COP"] = (energia.energia_kWh * TARIFA).round(-3)
energia["mes"] = energia.mes.astype(str)

# ---------------------------------------------------------------------------
# 7. Campaña de presiones (2 semanas, cada 15 min) en 4 puntos
# ---------------------------------------------------------------------------
PUNTOS = {"P1-Centro": ("Centro", 50.0), "P2-Sur": ("Sur", 44.0),
          "P3-Oriente": ("Oriente", 53.0), "P4-Norte Alto": ("Norte Alto", 67.0)}
TURNOS = {  # horas de servicio por sector
    "Centro": (5, 13), "Sur": (5, 13), "Oriente": (13, 21), "Norte Alto": (13, 21)}
t = pd.date_range("2026-03-02", "2026-03-15 23:45", freq="15min")
pres = []
for punto, (sector, cota) in PUNTOS.items():
    ini, fin = TURNOS[sector]
    hh = t.hour + t.minute / 60
    servicio = (hh >= ini) & (hh < fin)
    # nivel del tanque baja durante el turno
    avance = np.clip((hh - ini) / (fin - ini), 0, 1)
    nivel = COTA_BASE_TANQUE + ALTURA_TORRE + ALTURA_UTIL_TANQUE * (1 - 0.8 * avance)
    perdida = 6 + 4 * np.sin(np.pi * avance)  # pérdidas de carga en la red (mca)
    p = np.where(servicio, nivel - cota - perdida + rng.normal(0, 0.4, len(t)), 0.0)
    p = np.clip(p, 0, None).round(1)
    pres.append(pd.DataFrame({"fecha_hora": t, "punto": punto, "sector": sector,
                              "cota_m": cota, "presion_mca": p}))
pres = pd.concat(pres, ignore_index=True)
turnos = pd.DataFrame([{"sector": s, "hora_inicio": a, "hora_fin": b} for s, (a, b) in TURNOS.items()])

# ---------------------------------------------------------------------------
# 8. Solucionario: balance hídrico "verdadero" (solo para el autor)
# ---------------------------------------------------------------------------
produccion_m3 = (bomb._caudal_real_Ls * 3.6).sum()
consumo_real_catastro = fact._consumo_real_m3.sum()
facturado_medido = fact.loc[fact.lectura_m3.notna(), "volumen_facturado_m3"].sum()
facturado_no_medido = fact.loc[fact.lectura_m3.isna(), "volumen_facturado_m3"].sum()
oficiales = sus.loc[sus.uso == "Oficial", "id_suscriptor"]
no_facturado_autorizado = fact.loc[fact.id_suscriptor.isin(oficiales), "_consumo_real_m3"].sum()
fraude_m3 = sum(fraude._consumo_base_m3mes.sum() * factor_mes(p.month) for p in MESES)
lect = fact.merge(sus[["id_suscriptor", "medido"]], on="id_suscriptor")
submedicion = (lect.loc[lect.medido & ~lect.id_suscriptor.isin(oficiales), "_consumo_real_m3"].sum()
               - facturado_medido)
consumo_no_medido_real = lect.loc[~lect.medido, "_consumo_real_m3"].sum()
error_estimacion_no_medidos = consumo_no_medido_real - facturado_no_medido
perdidas_aparentes = fraude_m3 + submedicion + error_estimacion_no_medidos
perdidas_reales = produccion_m3 - consumo_real_catastro - fraude_m3
verdad = pd.DataFrame([
    ("Volumen producido (real)", produccion_m3),
    ("Consumo facturado medido", facturado_medido),
    ("Consumo facturado no medido (asignado)", facturado_no_medido),
    ("Consumo autorizado no facturado (oficiales)", no_facturado_autorizado),
    ("Consumo no autorizado (conexiones fraudulentas)", fraude_m3),
    ("Submedición de medidores", submedicion),
    ("Consumo no medido por encima de lo asignado", error_estimacion_no_medidos),
    ("Pérdidas aparentes (total)", perdidas_aparentes),
    ("Pérdidas reales (fugas)", perdidas_reales),
], columns=["componente", "volumen_anual_m3"])
verdad["volumen_anual_m3"] = verdad.volumen_anual_m3.round(0)
verdad["porcentaje_produccion"] = (verdad.volumen_anual_m3 / produccion_m3 * 100).round(1)


# ---------------------------------------------------------------------------
# Escritura
# ---------------------------------------------------------------------------
def escribir(salida: Path) -> None:
    salida.mkdir(parents=True, exist_ok=True)
    sol = salida / "_solucionario"
    sol.mkdir(exist_ok=True)
    (salida / "sistema.json").write_text(json.dumps(sistema, ensure_ascii=False, indent=2), encoding="utf-8")
    pub = [c for c in sus.columns if not c.startswith("_")]
    sus[pub].to_csv(salida / "suscriptores.csv", index=False)
    fact[[c for c in fact.columns if not c.startswith("_")]].to_csv(salida / "facturacion_mensual.csv", index=False)
    red.to_csv(salida / "red_tuberias.csv", index=False)
    fugas.to_csv(salida / "registro_fugas.csv", index=False)
    bomb[["fecha_hora", "bomba_encendida", "horometro_h", "energia_kWh"]].to_csv(
        salida / "bombeo_horario.csv", index=False)
    aforos.to_csv(salida / "aforos_pozo.csv", index=False)
    energia.to_csv(salida / "energia_mensual.csv", index=False)
    pres.to_csv(salida / "presiones_campana_marzo2026.csv", index=False)
    turnos.to_csv(salida / "turnos_distribucion.csv", index=False)
    # Solucionario (verdad oculta para validar los capítulos)
    verdad.to_csv(sol / "balance_hidrico_verdadero.csv", index=False)
    sus.to_csv(sol / "suscriptores_completo.csv", index=False)
    fraude.to_csv(sol / "conexiones_fraudulentas.csv", index=False)
    bomb.to_csv(sol / "bombeo_horario_completo.csv", index=False)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--salida", default=str(Path(__file__).resolve().parents[1] / "datos"))
    escribir(Path(ap.parse_args().salida))
    print(verdad.to_string(index=False))
