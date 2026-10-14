# Llave Abierta

**Agua para todos, con ingeniería abierta para acueductos pequeños.**

Este repositorio contiene el libro vivo ***Hasta la Última Llave: el caso Palmas de la Sabana***
y los datos con los que se construye.

El libro sigue a un acueducto comunitario ficticio, Palmas de la Sabana, y en cada capítulo le
resuelve una pregunta a su junta: cuánta agua se pierde, dónde buscar las fugas, por qué al
sector alto no le llega el agua o qué inversión pedirle a la alcaldía. Cada capítulo tiene dos
lecturas:

- **Para ingenieros y estudiantes:** el método completo, con código Python y datos.
- **Para operadores de acueductos pequeños:** una herramienta sencilla y una guía de qué hacer con el resultado.

## Contenido

| Carpeta | Qué hay |
|---|---|
| `libro/` | Fuentes del Jupyter Book |
| `datos/` | Datos sintéticos del caso y su diccionario ([datos/README.md](datos/README.md)) |
| `scripts/` | Generador reproducible de los datos |

## Cómo reproducirlo

```bash
pip install -r requirements.txt
python scripts/generar_datos.py      # regenera datos/ y el solucionario local
jupyter-book build libro/            # construye el libro en libro/_build/html
```

## Autor

**Rubert Ernesto Montes Correa**: ingeniero civil, MSc en Recursos Hídricos e Hidroinformática.
[rubertm.github.io](https://rubertm.github.io)

## Licencia

Código bajo MIT; texto del libro y datos bajo CC BY 4.0. Ver [LICENSE](LICENSE).
Todos los datos del caso son ficticios.
