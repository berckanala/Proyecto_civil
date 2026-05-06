# Punto 6 - Resultados del modelo sísmico

Fecha: 06-05-2026

## 1. Objetivo

Este documento resume el procedimiento y los resultados que se deben reportar en el punto 6 del informe de la Entrega 3:

- Cortes basales en X e Y y comparación con valores máximos y mínimos.
- Deformaciones del centro de masa por dirección.
- Verificación de rigidez.
- Indicador de acoplamiento.

La redacción y los criterios se apoyan en:

- `Apuntes_marchdown.md`
- `Entrega_3/Factor R.xlsx`
- `Entrega_3/Informe/secciones/3calculo.tex`
- `Entrega_3/Informe/secciones/7coef_max.tex`

## 2. Datos ya cerrados del proyecto

Los siguientes valores ya quedaron definidos en el Excel `Factor R.xlsx` y pueden usarse directamente en el informe:

- Tipo de suelo: A
- Zona sísmica: 3
- S = 0.90
- T0 = 0.15 s
- T' = 0.20 s
- n = 1
- p = 2
- A0 = 0.40
- I = 1.00
- R0 = 11
- Peso sísmico total del edificio: P = 7660.54 tonf
- Altura total del edificio: H = 54.78 m
- Período traslacional principal en X: Tx = 1.14 s
- Período traslacional principal en Y: Ty = 0.853 s
- Período torsional principal obtenido del modelo: Ttors = 1.251 s

## 3. Fórmulas base que hay que mostrar

### 3.1 Factor de reducción espectral

R* = T* / (0.1*T0 + T*/R0)

Aplicando la expresión:

- R*x = 1.14 / (0.1*0.15 + 1.14/11) = 10.609
- R*y = 0.853 / (0.1*0.15 + 0.853/11) = 10.217

En ETABS se ingresa el inverso:

- 1/R*x = 0.0943
- 1/R*y = 0.0979

### 3.2 Coeficiente sísmico

Cmin = A0*S*I/6

Cmin = 0.40*0.90*1/6 = 0.060

Rango usado en el informe previo:

- Cmin = 0.0666 si se adopta la expresión escrita en `7coef_max.tex`
- Cmax = 0.126
- Coeficiente adoptado para el modelo: C = 0.10

Para mantener coherencia con el Excel y con el texto ya escrito en el informe, conviene reportar que se adopta C = 0.10.

### 3.3 Rango de corte basal según el apunte

Qmin = I*A0*P/6

Qmax = 0.35*S*I*A0*P

Reemplazando:

- Qmin = 1*0.40*7660.54/6 = 510.70 tonf
- Qmax = 0.35*0.90*1*0.40*7660.54 = 965.23 tonf

### 3.4 Corte basal objetivo con C adoptado

Qobjetivo = C*I*P

Qobjetivo = 0.10*1*7660.54 = 766.05 tonf

## 4. Resultados cerrados que ya puedes poner

### 4.1 Primer corrido del modelo

Con los valores iniciales de R*:

- Qx,1 = 160.34 tonf
- Qy,1 = 201.91 tonf

Estos valores quedan bajo el mínimo exigido, por lo que el apunte indica que se deben escalar fuerzas y desplazamientos cuando el corte basal queda por debajo de Qmin.

### 4.2 Corrección de R para cumplir el corte mínimo

Se usa:

R*corregido = (Qobtenido/Qnorma)*R*calculado

Resultados:

- R*x,corregido = (160.34/766.05)*10.609 = 2.2206
- R*y,corregido = (201.91/766.05)*10.217 = 2.6929

Valores a ingresar en ETABS:

- 1/R*x,corregido = 0.4503
- 1/R*y,corregido = 0.3713

### 4.3 Segundo corrido del modelo

Con los valores corregidos:

- Caso SX en ETABS: FX = 763.60 tonf y FY = 55.94 tonf
- Caso SY en ETABS: FX = 46.13 tonf y FY = 764.28 tonf
- Corte basal directo final en X: Qx,final = 763.60 tonf
- Corte basal directo final en Y: Qy,final = 764.28 tonf

Conclusión cerrada para este inciso:

Los cortes basales finales en ambas direcciones quedan prácticamente iguales al corte basal objetivo de 766.05 tonf. La diferencia es de aproximadamente 0.32% en X y 0.23% en Y respecto del valor objetivo. Además, ambos se ubican dentro del rango permitido por la norma, definido entre 510.70 tonf y 965.23 tonf. Por lo tanto, el modelo sísmico corregido cumple con la exigencia de corte basal mínimo y máximo.

## 5. Qué tienes que hacer en ETABS para completar el punto 6

## 5.1 Cortes basales X e Y

Esto sirve para verificar lo que ya calculaste y para sacar la tabla final del informe.

Paso a paso:

1. Abre el modelo final, es decir, el que ya tiene ingresados los valores corregidos de 1/R en los espectros de X e Y.
2. Corre el análisis: `Run Analysis`.
3. Ve a `Display > Show Tables`.
4. En las tablas de resultados, busca `Analysis Results > Structure Results > Base Reactions`.
5. Filtra por los casos sísmicos espectrales finales de X e Y.
6. Para el sismo en X, anota el valor absoluto de `FX`.
7. Para el sismo en Y, anota el valor absoluto de `FY`.
8. Si tienes casos con torsión accidental positiva y negativa, toma la envolvente más desfavorable para cada dirección.

Qué debes comparar:

- Qx final con Qmin y Qmax
- Qy final con Qmin y Qmax
- Qx final y Qy final con Qobjetivo = 766.05 tonf

Tabla sugerida para el informe:

Dirección | Corte basal obtenido (tonf) | Corte mínimo (tonf) | Corte máximo (tonf) | Verificación
X | 763.60 | 510.70 | 965.23 | Cumple
Y | 764.28 | 510.70 | 965.23 | Cumple

## 5.2 Deformaciones del centro de masa por dirección

El apunte pide controlar:

- delta/Hcm <= 0.002 en el centro de masa
- (delta/Hcm - 0.001) <= delta/Hi <= (delta/Hcm + 0.001) en cualquier punto de la planta

Lo que debes sacar de ETABS:

Opción A, si la tabla aparece disponible:

1. `Display > Show Tables`
2. `Analysis Results > Displacements > Diaphragm Center of Mass Displacements`
3. Exporta la tabla a Excel

Opción B, si la tabla anterior no aparece:

1. `Display > Show Tables`
2. `Analysis Results > Displacements > Joint Displacements`
3. Filtra el nodo maestro del diafragma o el nodo ubicado en el centro de masa del piso
4. Exporta la tabla a Excel

Cómo procesarlo:

1. Ordena los pisos desde base a techo.
2. Para cada piso, toma el desplazamiento absoluto del centro de masa en X y en Y.
3. Calcula la deformación relativa de entrepiso:

delta_x,i = |Ux,i - Ux,i-1|

delta_y,i = |Uy,i - Uy,i-1|

4. Divide por la altura del entrepiso:

drift_x,i = delta_x,i / hi

drift_y,i = delta_y,i / hi

5. Repite el cálculo para todas las combinaciones sísmicas relevantes.
6. Si existen casos con torsión accidental positiva y negativa, toma la envolvente máxima por piso.

Qué debes reportar:

- Piso crítico en X
- Piso crítico en Y
- Deriva máxima del centro de masa en X
- Deriva máxima del centro de masa en Y
- Verificación contra 0.002

Resultados obtenidos desde `resul.xlsx`:

- Desplazamiento máximo de techo en X bajo `SX`: 46.43 mm
- Desplazamiento máximo de techo en Y bajo `SY`: 28.59 mm
- Deriva máxima del CM en X: 0.001015
- Deriva máxima del CM en Y: 0.000612
- Piso crítico en X: piso 15, entre los niveles 14 y 15
- Piso crítico en Y: piso 13, entre los niveles 12 y 13
- Verificación: ambas direcciones cumplen holgadamente con el límite 0.002

Plantilla de tabla:

Piso | Ux (mm) | Uy (mm) | h entrepiso (mm) | delta_x (mm) | delta_x/h | delta_y (mm) | delta_y/h | Cumple

Frase sugerida para el informe:

Las deformaciones del centro de masa se obtuvieron a partir de los desplazamientos modales espectrales del modelo final corregido. Para cada piso se calculó la deformación relativa de entrepiso como la diferencia entre desplazamientos absolutos consecutivos dividida por la altura del entrepiso, igual a 2.42 m. La máxima deriva obtenida en la dirección X fue 0.001015, localizada en el piso 15, mientras que la máxima deriva obtenida en la dirección Y fue 0.000612, localizada en el piso 13. Ambas se encuentran por debajo del límite de 0.002 indicado en el apunte y en la NCh433, por lo que el edificio cumple el control de deformaciones del centro de masa en ambas direcciones.

## 5.3 Verificación de rigidez

Aquí conviene hacer dos verificaciones: una global y otra por piso.

### 5.3.1 Rigidez global con H/T

En la hoja `Estimacion_periodo` del Excel aparece como referencia del ramo que H/T debe quedar aproximadamente entre 50 y 70.

Cálculo:

- H/Tx = 54.78/1.14 = 48.05 m/s
- H/Ty = 54.78/0.853 = 64.22 m/s

Interpretación:

- Dirección X: el valor queda levemente por debajo del rango de referencia, por lo que la estructura se comporta como la dirección más flexible del sistema.
- Dirección Y: el valor queda dentro del rango de referencia del curso, por lo que presenta una rigidez global adecuada.

### 5.3.2 Rigidez por piso en ETABS

Paso a paso:

1. `Display > Show Tables`
2. `Analysis Results > Structure Results > Story Stiffness`
3. Si la tabla sale vacía, como ocurrió en este exportado, calcula la rigidez por piso combinando `Story Forces` y `Diaphragm CM Displacements`
4. Para X usa: Kx,i = VX,bottom,i / delta_x,i
5. Para Y usa: Ky,i = VY,bottom,i / delta_y,i
6. Revisa la rigidez en X y en Y piso a piso
7. Identifica caídas bruscas de rigidez, especialmente:

- sobre subterráneo
- en primer nivel sobre la placa
- donde desaparecen muros perimetrales
- en pisos donde cambia fuertemente la densidad de muros

Qué debes mirar:

- Si existe un salto importante de rigidez entre dos pisos consecutivos
- Si el primer piso es mucho más flexible que los pisos superiores
- Si hay pisos con cambio abrupto por interrupción de muros o reducción fuerte de espesores

Resultados obtenidos al calcular la rigidez con las tablas de ETABS:

- En X, la rigidez calculada disminuye de forma gradual desde aproximadamente 1035.88 tonf/mm en el piso 1 hasta 35.65 tonf/mm en techo
- En Y, la rigidez calculada disminuye de forma gradual desde aproximadamente 1542.59 tonf/mm en el piso 1 hasta 56.01 tonf/mm en techo
- La reducción más marcada se observa entre los pisos 1 y 2, con razones K2/K1 cercanas a 0.66 en X y 0.69 en Y
- Desde el piso 2 hacia arriba la disminución de rigidez es progresiva y no se observa un piso blando aislado en la torre

Frase sugerida para el informe:

La verificación global de rigidez mediante la razón H/T muestra que la dirección X es la más flexible del edificio, con H/Tx = 48.05 m/s, mientras que la dirección Y presenta H/Ty = 64.22 m/s, valor consistente con el rango de referencia del curso. Como la tabla `Story Stiffness` salió vacía en el exportado, la rigidez por piso se estimó usando el corte de piso y la deriva correspondiente, obteniendo una disminución progresiva de la rigidez hacia los niveles superiores. La mayor variación se concentra en la transición entre los primeros niveles, mientras que en la torre no se identifica un piso blando aislado ni una caída abrupta singular de rigidez.

## 5.4 Indicador de acoplamiento

Como en el apunte no aparece una fórmula única desarrollada dentro de esta entrega, te conviene revisar el acoplamiento de dos maneras y usar la que el profesor o ayudante esté pidiendo.

### 5.4.1 Opción 1: Acoplamiento modal por cercanía entre período torsional y traslacional

Con los valores del modelo:

- Ttors/Tx = 1.259/1.141 = 1.10
- Ttors/Ty = 1.259/0.854 = 1.47

Interpretación:

El modo torsional está más cercano al período traslacional en X que al de Y, por lo que la dirección X presenta una interacción torsión-traslación más cercana y debe observarse con mayor cuidado.

### 5.4.2 Opción 2: Acoplamiento por respuesta ortogonal

Si el ayudante te pide un indicador basado en esfuerzos acoplados, haz lo siguiente:

1. Ve a `Display > Show Tables`
2. Abre `Analysis Results > Structure Results > Base Reactions`
3. Para el caso sísmico en X, registra:

- FX directo
- FY acoplado

4. Para el caso sísmico en Y, registra:

- FY directo
- FX acoplado

5. Calcula:

Iacop,X = |FY bajo sismo X| / |FX bajo sismo X|

Iacop,Y = |FX bajo sismo Y| / |FY bajo sismo Y|

Si tienes casos con torsión accidental positiva y negativa, toma la envolvente más desfavorable.

Resultados obtenidos desde `Base Reactions`:

- Iacop,X = 55.9448 / 763.6004 = 0.073
- Iacop,Y = 46.1267 / 764.2768 = 0.060

Interpretación:

- El acoplamiento global por respuesta ortogonal es bajo en ambas direcciones
- La dirección X presenta un acoplamiento levemente mayor que Y
- Esto es coherente con la cercanía entre el modo torsional y el modo traslacional principal en X

Frase sugerida para el informe:

El acoplamiento del sistema puede estimarse comparando la respuesta ortogonal inducida por cada sismo principal. Para el sismo en X se calcula la razón entre el corte basal ortogonal en Y y el corte basal directo en X, mientras que para el sismo en Y se calcula la razón entre el corte basal ortogonal en X y el corte basal directo en Y. Este indicador permite cuantificar la tendencia del edificio a desarrollar respuesta traslacional acoplada entre ambas direcciones.

## 6. Texto casi listo para pegar en cada subsección del informe

## 6.1 Cortes basales X e Y

Los cortes basales finales del modelo sísmico se obtuvieron a partir del análisis modal espectral del modelo corregido. Inicialmente, al ingresar los factores 1/R*x = 0.0943 y 1/R*y = 0.0979, se obtuvieron cortes basales de 160.34 tonf en X y 201.91 tonf en Y, ambos inferiores al mínimo requerido. Por esta razón, se corrigieron los factores de reducción espectral, obteniéndose R*x,corregido = 2.2206 y R*y,corregido = 2.6929, equivalentes a 1/R*x = 0.4503 y 1/R*y = 0.3713 para su ingreso en ETABS. Con estos valores, la tabla `Base Reactions` del modelo final entregó FX = 763.60 tonf para `SX` y FY = 764.28 tonf para `SY`, valores prácticamente iguales al corte basal objetivo de 766.05 tonf y dentro del rango normativo de 510.70 a 965.23 tonf. En consecuencia, el modelo final cumple con la exigencia de corte basal.

## 6.2 Deformaciones del centro de masa

Las deformaciones del centro de masa se obtuvieron a partir de la tabla `Diaphragm CM Displacements` del modelo final corregido. Para cada dirección, la deriva de entrepiso se calculó como la diferencia absoluta entre desplazamientos consecutivos dividida por la altura del entrepiso, igual a 2.42 m. El desplazamiento máximo de techo fue 46.43 mm en X y 28.59 mm en Y. La deriva máxima del centro de masa resultó igual a 0.001015 en la dirección X, localizada en el piso 15, y 0.000612 en la dirección Y, localizada en el piso 13. Ambas derivas son menores que el límite normativo de 0.002, por lo que la estructura cumple satisfactoriamente el control de deformaciones.

## 6.3 Verificación de rigidez

La verificación global de rigidez se realizó mediante la razón H/T. Para el edificio analizado, con una altura total de 54.78 m, se obtuvo H/Tx = 48.05 m/s y H/Ty = 64.22 m/s. De acuerdo con la referencia usada en el curso, la dirección Y presenta una rigidez global adecuada, mientras que la dirección X corresponde a la dirección más flexible del edificio. Además, se debe complementar esta revisión con la tabla de rigidez de pisos de ETABS, con el objetivo de identificar posibles cambios bruscos de rigidez en altura, especialmente en el primer nivel resistente y en sectores donde se interrumpen muros o disminuyen considerablemente sus espesores.

## 6.4 Indicador de acoplamiento

El acoplamiento del edificio puede evaluarse inicialmente comparando el período torsional con los períodos traslacionales principales. Con Ttors = 1.259 s, Tx = 1.141 s y Ty = 0.854 s, se obtiene Ttors/Tx = 1.10 y Ttors/Ty = 1.47, lo que indica una mayor cercanía entre torsión y traslación en la dirección X. Complementariamente, a partir de la tabla `Base Reactions` se obtiene Iacop,X = 0.073 e Iacop,Y = 0.060, calculados como la razón entre la respuesta ortogonal y la respuesta directa de cada sismo principal. Estos valores muestran un acoplamiento global bajo, aunque ligeramente mayor en la dirección X.

## 7. Checklist final antes de cerrar el informe

- Verificar que el modelo que vas a revisar en ETABS sea el modelo final con 1/R corregido.
- Exportar `Base Reactions`.
- Exportar desplazamientos del centro de masa o desplazamientos del nodo maestro de diafragma.
- Exportar `Story Stiffness`.
- Revisar si hay casos con torsión accidental positiva y negativa y usar envolvente.
- Completar las derivas máximas en X e Y.
- Completar el indicador de acoplamiento según el criterio pedido por el profesor.
- Pegar la redacción final en `10cortes_x_y.tex`, `11control_def.tex`, `12verificacion_rig.tex` y `13acoplamiento.tex`.
