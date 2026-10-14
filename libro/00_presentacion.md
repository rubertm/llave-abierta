# 0. Presentación

## Para quién es este libro

- **Operadores y juntas de acueductos pequeños:** cada capítulo termina con una herramienta
  sencilla y una guía de qué hacer con el resultado. No hace falta leer el código.
- **Ingenieros y estudiantes:** cada capítulo desarrolla el método completo con Python y datos,
  para que puedan reproducirlo y aplicarlo a otros sistemas.

## Cómo usarlo

Cada capítulo responde una pregunta de la junta de Palmas de la Sabana:

| Capítulo | Pregunta |
|---|---|
| 1 | ¿Qué sabemos de nuestro acueducto? |
| 2 | ¿Cuánta agua se pierde? |
| 3 | ¿Por dónde empezamos a buscar las fugas? |
| 4 | ¿Por qué al Norte Alto no le llega agua? |
| 5 | ¿Cuánto nos cuesta el agua que se pierde? |
| 6 | ¿Qué pasa si cambiamos la red? |
| 7 | ¿Qué medidores instalamos primero? |
| 8 | ¿Qué le pedimos a la alcaldía? |

## Preparar el entorno

```bash
git clone https://github.com/rubertm/llave-abierta
cd llave-abierta
pip install -r requirements.txt
python scripts/generar_datos.py
```

```{warning}
Todos los datos de Palmas de la Sabana son **ficticios**. Se construyeron para que se parezcan
a los de un acueducto pequeño real, pero no corresponden a ningún sistema existente.
```
