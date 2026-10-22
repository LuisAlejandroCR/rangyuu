<!-- README.md (docs/brand/tilo): ficha de Tilo, la mascota decorativa de Rangyuu — concepto,
     paleta, poses y reglas de uso. Se distingue de web/styles.css, que define los colores de
     estado de la app: aquí no se define ningún estado ni se decide nada sobre la ruta.
     La bitácora de la sesión que lo creó va en docs/memoria.md, no aquí. -->

# Tilo — mascota decorativa

Criatura cartógrafa pequeña, curiosa y serena. Su cuerpo es una ficha de mapa plegada: silueta
horizontal, tres capas redondeadas, aletas laterales, brazos cortos y dos ojos del mismo tamaño.
Acabado mate, como arcilla o silicona: degradados suaves y un brillo tenue, sin filtros.

| Archivo | Pose | Uso |
|---|---|---|
| `tilo-front.svg` | Vista frontal, despierto, ojos abiertos | **Principal**: la imagen habitual de Tilo |
| `tilo-rest.svg` | Descanso: inclinado −6°, ojos cerrados, brazos recogidos | Solo estados inactivos o una página sobre la mascota; nunca la imagen por defecto de una app que informa |

Sin patas ni lóbulos redondos bajo el cuerpo: se quitaron el 2026-10-22 porque se leían como
ruedas, y Tilo no debe parecer vehículo ni robot. Las aletas son ahusadas, con nervios.

Ambos: `viewBox 0 0 240 190`, sin scripts, sin filtros, sin recursos externos.

## Paleta

| Uso | Color |
|---|---|
| Lavanda (capa superior, brazos) | `#b6a9d2` → `#9c8dbd` |
| Lavanda profunda (capa inferior, aletas) | `#a090c0` → `#87789f` |
| Marfil (capa media) | `#faf3e5` → `#eadfca` |
| Contorno y rasgos | `#4b3f60` |
| Detalle cian (dos curvas de nivel, solo trazo) | `#3fb0c6` |

Contraste medido el 2026-10-22: contorno 9,02:1 sobre `--ground` (#f4f8fa); lavanda 6,27:1 sobre
el fondo móvil (#0e1116) y 5,30:1 sobre `surface` (#1b222c).

## Por qué no se confunde con un estado

- **Tono propio.** La lavanda (tono 260°, luz 0,68) se aleja de `--incierto` #4a6fa5 (216°, 0,47):
  más violeta, más clara y menos saturada. El cian son dos curvas de nivel de 2 px, solo trazo,
  apagadas frente a `--route` #0aa7e8. Nada de puntos ni círculos rellenos: un punto de color se
  lee como luz de estado.
- **Forma, no señal.** Es un personaje con cara, nunca un disco, riel o halo de color plano como
  los que usa la tarjeta de estado.
- **Sin gestos de tráfico.** No señala, no levanta la mano, no tiene flecha ni bandera.

## Reglas de uso

- Decorativo: no detecta peligros, no indica que se pueda avanzar y no decide por la persona.
- Nunca junto a AVANZA, CUIDADO, PARA o SIN CERTEZA, ni dentro de la tarjeta `.verdict` o del mapa.
- Lugares aptos: estados vacíos, onboarding, Sistema, créditos.
- Las curvas de nivel cian no van cerca de estados operativos ni del indicador "Conectado": de
  cerca pueden leerse como señal de conexión. Si Tilo tiene que aparecer en una pantalla con
  estados, va lejos de ellos.
- Que la silueta recuerde a una tortuguita está aceptado: se lee como criatura, no como vehículo.
- Nunca con atuendo médico ni manejando una silla, un vehículo o cualquier control.
- Si se usa en línea, lleva `aria-hidden="true"` o un `alt` que diga que es la mascota, nunca un
  texto que suene a estado.
