<!-- fixtures/iphone/MEDICIONES.md: protocolo para grabar y anotar la calibración a bordo (B11).
     Dice qué medir con cinta y qué reservar fuera del ajuste, antes de grabar.
     Se distingue de docs/verificacion.md (que guarda el número ya medido) y de
     fixtures/iphone/calibration_points.json (que guarda los píxeles): esto es el instructivo. -->

# Calibración a bordo — qué medir antes de grabar

El error del ajuste **siempre da ~0 y no prueba nada** (Lección 3). El número honesto sale de puntos
que **no** entraron en el ajuste. Por eso las marcas se deciden antes de grabar, no después.

## Para el ajuste (4 marcas)

Cuatro marcas visibles en las esquinas de un rectángulo medido con cinta metrica. Anotar:

- Ancho medido (m):
- Profundidad medida (m):

## Reservadas fuera del ajuste (mínimo 2)

Puntos de separación conocida sobre una misma línea — juntas de baldosa sirven, como en
`fixtures/home/`, donde el lado es 0,305 m. **No se anotan en `marks`.**

- Separación conocida (m):
- Cuántos puntos:

## Al grabar

1. El suelo tiene que verse en el mismo plano en el frame elegido.
2. Anotar resolución y el número de frame usado.
3. El clip **no se versiona**: solo entran píxeles y medidas a `calibration_points.json`.
4. Con todo anotado, poner `"status": "measured"` y correr `python -m pytest -q tests/test_calibration_onboard.py`.
