# Datos del caso: Acueducto Comunitario de Palmas de la Sabana

> **Todos los datos son ficticios.** Se generan con `scripts/generar_datos.py` (semilla fija 2026),
> así que cualquier persona puede reproducirlos. Periodo: 1 de octubre de 2025 a 30 de septiembre de 2026.

## Lo que la junta sabe (archivos públicos del libro)

| Archivo | Qué contiene | Capítulos |
|---|---|---|
| `sistema.json` | Ficha técnica: pozo, tanque, red, acometidas, sectores y operación | Todos |
| `suscriptores.csv` | Catastro de 620 suscriptores: sector, uso, personas, cota, si tiene medidor y año del medidor | 1, 4, 5 |
| `facturacion_mensual.csv` | 12 meses por suscriptor: lectura del medidor (vacía si no tiene) y volumen facturado | 1, 4 |
| `bombeo_horario.csv` | 8.760 horas: bomba encendida o no, horómetro y energía consumida | 1, 2, 4 |
| `aforos_pozo.csv` | 3 aforos con caudalímetro ultrasónico portátil (el macromedidor está dañado) | 1, 4 |
| `energia_mensual.csv` | Factura de energía mensual: kWh, horas de bombeo, tarifa y valor | 2, 5 |
| `red_tuberias.csv` | 108 tramos (14 km): material, diámetro, longitud y año de instalación por sector | 1, 3, 5 |
| `registro_fugas.csv` | 86 fugas reparadas en el año: fecha, sector, tipo, material y días hasta reparar | 1, 5 |
| `presiones_campana_marzo2026.csv` | 2 semanas de presión cada 15 min en 4 puntos (uno por sector) | 2, 3 |
| `turnos_distribucion.csv` | Horario de servicio de cada sector | 2, 3 |

### Campos principales

**suscriptores.csv**: `id_suscriptor`, `sector` (Centro, Sur, Oriente, Norte Alto), `uso` (Residencial, Comercial, Oficial),
`personas`, `cota_m`, `medido` (True/False), `descripcion`, `anio_medidor`.

**facturacion_mensual.csv**: `id_suscriptor`, `mes` (AAAA-MM), `lectura_m3` (vacía si no hay medidor),
`volumen_facturado_m3` (a los no medidos se les asignan 12 m³/mes; los oficiales están exentos).

**bombeo_horario.csv**: `fecha_hora`, `bomba_encendida`, `horometro_h`, `energia_kWh`.

## Lo que la junta no sabe (`_solucionario/`)

Esta carpeta guarda la "verdad" con la que se generaron los datos. Sirve para comprobar que los
métodos de cada capítulo llegan a la respuesta correcta. **No se sube al repositorio:** se genera
localmente al ejecutar `python scripts/generar_datos.py`.

| Componente (año completo) | m³ | % de lo producido |
|---|---:|---:|
| Volumen producido | 240.403 | 100,0 |
| Consumo facturado medido | 34.537 | 14,4 |
| Consumo facturado no medido (asignado) | 52.704 | 21,9 |
| Consumo autorizado no facturado (escuela y puesto de salud) | 1.091 | 0,5 |
| Pérdidas aparentes | 31.860 | 13,3 |
| — conexiones fraudulentas (25 viviendas) | 5.224 | 2,2 |
| — submedición de medidores | 5.118 | 2,1 |
| — consumo de no medidos por encima de lo asignado | 21.518 | 9,0 |
| Pérdidas reales (fugas) | 120.211 | 50,0 |

El agua no facturada es del 64 %. El reto del capítulo 1 es estimar estos componentes usando solo
los archivos públicos, como lo haría la junta.

## Rasgos del caso que los datos reproducen

- Producción de unos 660 m³/día, con caudal más bajo en la temporada seca (dic-mar) por abatimiento del pozo.
- Bombeo de unas 16 h/día, que sube a casi 18 h en temporada seca, con cortes de energía ocasionales.
- Solo el 41 % de los suscriptores tiene medidor, con submedición creciente según la edad.
- El sector Norte Alto (cotas de 60 a 70 m) tiene presión menos de 2 horas de su turno de 8, casi siempre por debajo de 3 mca.
- De las 86 fugas reparadas, 67 fueron en acometidas; de las 19 en red, 12 fueron en asbesto-cemento (1998-2004).
