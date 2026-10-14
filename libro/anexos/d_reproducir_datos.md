# Anexo D. Cómo reproducir los datos del caso

Todos los datos de Palmas de la Sabana se generan con `scripts/generar_datos.py`, con una semilla fija. Cualquier persona obtiene exactamente los mismos números:

```bash
python scripts/generar_datos.py
```

El script también crea la carpeta `datos/_solucionario/`, con la verdad con que se generaron los datos, para comprobar los métodos de cada capítulo. El diccionario de datos está en `datos/README.md` del repositorio.
