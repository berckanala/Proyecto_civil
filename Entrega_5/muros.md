# Diseño Sísmico de Muros de Hormigón Armado

### Guía de procedimiento, fundamentos y ejemplo resuelto

> Documento de referencia general, aplicable a muros sísmicos de sección rectangular **y, con las salvedades del §11, a secciones T / L / C**. Marco normativo: **ACI 318-19** (Cap. 18, muros especiales), **DS 60 / DS 61 (2011)** sobre la NCh 433, **NCh 433** (análisis sísmico), **NCh 430** (hormigón armado; propuesta de corte en estudio), y recomendaciones del **NIST GCR 11-917-11 Rev. 1 (Moehle, 2014)** y de Priestley-Paulay (1991).

---

## 0. Filosofía de diseño (el "porqué" de todo lo que sigue)

Los muros de hormigón armado son muy rígidos, por lo que mantienen los desplazamientos laterales pequeños y limitan el daño incluso ante sismos severos. El problema es que esa misma rigidez hace que **fluyan a desplazamientos relativamente pequeños**, así que hay que detallarlos para que fluyan en flexión **sin caer en fallas frágiles** (corte, deslizamiento en la base, pandeo de barras longitudinales).

El objetivo de diseño es entonces:

1. **Que la disipación de energía ocurra por fluencia de la armadura de flexión** en una zona controlada (la rótula plástica, normalmente en la base = sección crítica).
2. **Que el corte nunca controle.** El corte es una falla frágil; se diseña por capacidad para que el muro alcance su desplazamiento de techo de diseño *antes* de fallar al corte.
3. **Que la zona comprimida sea estable.** Por eso se confina el borde cuando la deformación de compresión es alta, evitando aplastamiento del hormigón y pandeo de las barras.

Todo el procedimiento siguiente es la traducción operativa de estos tres principios.

### Notación

| Símbolo | Significado |
|---|---|
| $l_w$ | Largo del muro (en planta) |
| $b_w$ (ó $e$) | Espesor del muro |
| $H_w$ | Altura total del muro, medida desde la sección crítica |
| $H_u$ | Altura libre de entrepiso |
| $A_g$ | Área bruta de la sección $= b_w \cdot l_w$ |
| $A_{cv}$ | Área de corte $= b_w \cdot l_w$ (ACI 318-19) |
| $A_{cw}$ | Área de un machón / segmento individual |
| $N_u, P_u$ | Carga axial última |
| $M_u$ | Momento último |
| $V_u$ | Corte último (de la combinación) |
| $V_e$ | Corte de diseño amplificado por capacidad |
| $f'_c$ | Resistencia del hormigón |
| $f_y$ | Tensión de fluencia del acero |
| $\delta_u$ | Desplazamiento lateral de techo de diseño |
| $\delta_e$ | Componente elástica del desplazamiento de techo |
| $\phi_u$ | Demanda de curvatura última |
| $\phi_y$ | Curvatura de fluencia |
| $l_p$ | Longitud de rótula plástica |
| $c$ | Profundidad del eje neutro |
| $C_c$ | Extensión en planta del núcleo a confinar |
| $\rho_t$ | Cuantía de refuerzo transversal (horizontal, corte) |
| $\rho_l$ | Cuantía de refuerzo longitudinal (vertical, flexión) |

> **Unidades.** Las normas conviven en kg/cm² y MPa. Conversiones útiles:
> $1\ \text{MPa} = 10.2\ \text{kg/cm}^2 = 100\ \text{T/m}^2$ ;  $1\ \text{kg/cm}^2 = 10\ \text{T/m}^2$ ;  $1\ \text{N} = 0.102\ \text{kg}$.

---

## 1. Geometría y clasificación del muro

**Qué se hace:** definir $l_w$, $b_w$, $H_w$ y la **sección crítica** (zona donde se espera la incursión inelástica cíclica, normalmente la base sobre la cota cero). Clasificar el muro por su esbeltez.

**Por qué:** la esbeltez decide qué mecanismo controla y, por lo tanto, qué verificaciones aplican.

$$\boxed{\text{Esbeltez} = \dfrac{H_w}{l_w}}$$

| Condición | Clasificación | Implicancia |
|---|---|---|
| $H_w/l_w > 2$ | Muro esbelto | **Controla flexión.** Diseño dúctil por flexión. |
| $H_w/l_w \le 2$ | Muro chato / bajo | **Controla corte.** Puede usarse modelo puntal-tensor. |
| $H_w/l_w \ge 3$ | Esbelto (DS60) | Obligatoria la verificación de **demanda de curvatura** $\phi_u$. |

**Chequeos geométricos que conviene anticipar:**

- **Espesor mínimo por pandeo (DS60-2011):**
$$e_{\min} \ge \dfrac{H_u}{16}$$
con $H_u$ la luz libre de entrepiso. Esto evita el pandeo fuera del plano del muro.

- **Espesores límite de detallamiento:**
  - $e = 20$ cm: límite inferior de un muro sismorresistente.
  - $e = 30$ cm: **límite inferior para poder confinar el borde** (por congestión de barras y faena de hormigonado).
  - $e = 35$ cm: muros con vigas de acoplamiento; $40$ cm si llevan armadura diagonal.

> **Por qué importa desde el paso 1:** si el muro resulta esbelto y va a requerir confinamiento (pasos 6-8), pero su espesor es menor a 30 cm, hay un conflicto que se resuelve engrosando la zona crítica o justificando con análisis más fino. Anticiparlo evita rehacer trabajo.

---

## 2. Esfuerzos del modelo

**Qué se hace:** obtener del modelo (ETABS/SAP2000) los esfuerzos de diseño en la sección crítica, **por nivel**: carga axial $N_u$, momento $M_u$ y corte $V_u$.

**Por qué:** son las solicitaciones contra las que se dimensiona. La combinación más desfavorable manda.

**Reglas prácticas (errores frecuentes que evitar):**

1. Asignar el número de **PIER** a cada muro (sin un PIER asignado no se obtienen esfuerzos integrados del muro).
2. Encender ejes locales en el **menú PIER, no en SHELL**.
3. Para muros rectangulares, los esfuerzos en la traza del muro son **$M_{3\text{-}3}$ (momento)** y **$Q_{2\text{-}2}$ (corte)**. En general $M_{2\text{-}2}$ y $Q_{3\text{-}3}$ no controlan (no están en la traza), salvo torsiones importantes.
4. La armadura de corte resulta en **cm²/m**, no en barras sueltas: con ese valor se elige la malla.

**Combinaciones (NCh 3171):** se generan ≥ 8 combinaciones y se toma la envolvente. Para el diseño a flexo-compresión, el **caso más desfavorable suele ser el de menor carga axial** (p. ej. sin sobrecarga), porque baja la capacidad y exige más ductilidad. Para el chequeo de compresión máxima, en cambio, controla la **mayor** carga axial.

---

## 3. Verificaciones previas

Tres chequeos de "viabilidad" antes de armar nada. Si alguno no se cumple, la salida natural es **modificar la sección** (engrosar) y volver al paso 2.

### 3.1 Compresión máxima

$$\boxed{\sigma_u = \dfrac{N_u}{l_w \cdot b_w} \le 0.35\, f'_c}$$
equivalente a $P_u \le 0.35\,f'_c\,A_g$.

**Por qué:** limitar la carga axial asegura una mínima capacidad de deformación plástica. Con axiales altos la zona comprimida se vuelve frágil (el hormigón aplasta antes de que fluya el acero).

> **Atención — secciones no rectangulares (T, L, C).** Este límite fue calibrado para muros rectangulares simétricos (busca dejar la sección bajo el punto de balance, ver §5.3). En secciones con alas o armadura asimétrica **el límite de $0.35\,f'_c A_g$ puede ser insuficiente**: cuando la cabeza del alma queda en compresión, poco hormigón debe equilibrar mucho acero del ala traccionada, el eje neutro se profundiza y la sección puede no fluir. Verificar siempre por momento-curvatura y, además, chequear el límite **referido solo al área del alma $A_w$**, no solo a $A_g$ (ver §11). Es un caso documentado de fallas frágiles en muros T del 27F-2010.

### 3.2 Esbeltez de entrepiso

$$e_{\min} \ge \dfrac{H_u}{16}$$

### 3.3 Corte máximo de la sección

$$\boxed{V_u \le V_{\max} = \tfrac{2}{3}\,A_{cv}\sqrt{f'_c}\ \ [\text{MPa}] = 0.66\,A_{cv}\sqrt{f'_c}}$$
$$V_{\max} = 2.12\,b_w\,l_w\,\sqrt{f'_c}\ \ [\text{kg/cm}^2]$$

Para machones / segmentos individuales el límite es $5/6\,A_{cv}\sqrt{f'_c} = 0.83\,A_{cv}\sqrt{f'_c}$ [MPa] $= 2.65\,A_{cw}\sqrt{f'_c}$ [kg/cm²].

**Por qué:** existe un tope físico de corte (aplastamiento del alma por compresión diagonal, en torno a $10\sqrt{f'_c}A_{cv}$). Si la demanda lo supera, no hay armadura que lo arregle: **hay que engrosar el muro**.

---

## 4. Diseño de la armadura de corte (por capacidad)

**Qué se hace:** amplificar el corte por capacidad y dimensionar la malla horizontal.

**Por qué la amplificación:** el análisis lineal subestima el corte real. Por sobrerresistencia a flexión y por efectos de modos superiores, el corte que efectivamente puede llegar al muro es mayor que el del análisis. Como el corte es frágil, se diseña para un corte mayor y así **forzar que el muro falle por flexión, no por corte**.

### 4.1 Corte de diseño amplificado

**Propuesta NCh 430 (en estudio, aprobada en comité Jul-2025):**
$$\boxed{V_e = \Omega_v \cdot \omega_v \cdot V_{u,\text{env}} \le 3\,V_{u,\text{env}}}$$

- $\Omega_v$: factor de sobrerresistencia (mínimo 1.25 para muros esbeltos).
- $\omega_v$: amplificación dinámica por modos superiores. En edificios chilenos típicos se usa $\omega_v = 1$.

El valor de $\Omega_v$ depende de la demanda de ductilidad $\mu_\delta = \delta_u/\delta_y$:

| Caso | $\Omega_v$ |
|---|---|
| $\mu_\delta \le 1$ | 1.25 |
| $1 < \mu_\delta < 2$ | interpolación lineal entre 1.25 y $\tfrac{2}{3}(M_{pr,sc}/M_{u,sc})$ |
| $\mu_\delta \ge 2$ | $\tfrac{2}{3}(M_{pr,sc}/M_{u,sc})$ |

> **En la práctica docente / informes** suele exigirse usar **$\Omega_v = 2.0$ como mínimo** en la sección crítica (criterio conservador equivalente al ACI 318-19, que usa $\Omega_v = M_{pr}/M_u$). Mientras no se oficialice la NCh430, este valor es un buen estándar.

> **Expresión clásica equivalente (factor de amplificación dinámica $\omega$).** En literatura previa el corte de diseño se escribe $V \approx \omega\,\phi_o\,V_u$, con el factor de sobrerresistencia $\phi_o = M_p/M_u$ y una expresión típica de amplificación dinámica $\omega = 0.75\,(1.2 + N/50) \le 1.35$ (no menor que 1; $N$ = número de pisos). Es la misma idea de "amplificar el corte a la capacidad plástica en flexión", reformulada hoy como $\Omega_v\cdot\omega_v$.

### 4.2 Resistencia nominal al corte

$$\boxed{V_n = V_c + V_s = V_c + A_{cv}\,\rho_t\,f_y} \qquad ; \qquad V_n \ge \dfrac{V_e}{\phi}, \quad \phi = 0.75$$

> **$\phi$ según origen de la demanda.** $\phi = 0.75$ cuando el corte proviene de un **diseño por capacidad**; $\phi = 0.60$ cuando proviene **directamente del análisis estructural** (sin amplificar). En esta guía se usa el enfoque por capacidad, por lo que rige $\phi = 0.75$.

**Aporte del hormigón** (menor valor; depende de la esbeltez):

$$V_c = \alpha_c\,\sqrt{f'_c}\,A_{cv}$$

| Relación $h_w/l_w$ | $\alpha_c$ [MPa] | $\alpha_c$ [kg/cm²] |
|---|---|---|
| $\le 1.5$ | 0.25 | 0.80 |
| $\ge 2.0$ (esbelto) | $0.17 = 1/6$ | 0.53 |
| intermedio | interpolar | interpolar |

> **Segmentos de muro.** Para un segmento, el valor de $h_w/l_w$ a usar es **el mayor** entre el del muro completo y el del segmento aislado (de modo que $\alpha_c$ resulte el **menor**). El criterio del ACI es que no se le asigne a ningún segmento una resistencia mayor que la del muro completo.

Para muros esbeltos: $\;V_c = 0.53\,b_w\,l_w\,\sqrt{f'_c}$ [kg/cm²].

**Aporte del acero** (con tope):
$$V_s = A_{cv}\,\rho_t\,f_y \le \tfrac{2}{3}A_{cv}\sqrt{f'_c}\ [\text{MPa}] = 2.12\,b_w\,l_w\sqrt{f'_c}\ [\text{kg/cm}^2]$$

De ahí se despeja la cuantía y se traduce a malla:
$$\rho_t = \dfrac{V_s}{A_{cv}\,f_y} \qquad ; \qquad A_h = \rho_t\,b_w\cdot 100\ \ [\text{cm}^2/\text{m total}]$$

> **Composición de la resistencia (referencia):** suele descomponerse como $\approx 1/3$ hormigón y $2/3$ acero. El profesor Bertero recomienda, conservadoramente, usar $1/2$ en vez de $2/3$ en el tope.

---

## 5. Diseño de la armadura de flexo-compresión

**Qué se hace:** determinar la armadura longitudinal (vertical) que resiste el par $(N_u, M_u)$ en la sección crítica.

**Por qué:** es la armadura que define la resistencia a flexión, que es la que *debe* controlar. La selección busca la **mayor compresión compatible con la ductilidad de curvatura requerida** (dar la mayor ductilidad posible).

### 5.1 Métodos disponibles

1. **Ábacos / diagramas de interacción** (Manual de Hormigón, Larraín-Yáñez 2006). Parámetros:
$$m = \dfrac{M_u}{f'_c\,A_g\,l_w} \qquad ; \qquad p = \dfrac{P_u}{f'_c\,A_g} \qquad ; \qquad \dfrac{e}{l_w} = \dfrac{M_u}{P_u\,l_w}$$
   Con $(m, p)$ se entra al ábaco y se lee la cuantía $\rho$.
2. **Método de Cárdenas-Magura (1973)** — armadura uniforme (ver §7).
3. **Section Design (ETABS / SAP2000)** — el más preciso; genera el diagrama de interacción y M-curvatura. Para M-curvatura se prefiere SAP2000.

> **Sección compuesta (T, L, C) — ACI/DS60 S21.9.5.2.** Al verificar secciones con alas se debe considerar la **sección completa con todas las armaduras especificadas**. Alternativamente, puede usarse el **ancho efectivo del ala**, que se extiende desde la cara del alma una distancia igual al **menor** valor entre la mitad de la distancia al alma de un muro adyacente y el **25 % de la altura total del muro**. Considerar la sección completa es importante porque captura los efectos de asimetría de armadura y geometría (cambio relevante en la práctica chilena desde el DS60).

### 5.2 Armadura de borde vs. uniforme

- Concentrar armadura en los **bordes** (puntas de muro) aumenta la resistencia a flexión **en 20-25 %** respecto de la misma cantidad distribuida uniforme. Es el método más común.
- Rango de cuantía vertical uniforme: $\rho_l = 0.005$ máximo (más no aporta a la ductilidad); $\rho_l = 0.002$ mínimo (da deformaciones de tracción excesivas, ~6 %).
- **Experiencia chilena:** cuantía de borde típica 1.5-3.5 ‰ de la sección del borde; cuantía total del muro **del orden de 1 %** de la sección, solo en la sección crítica. Para evitar fractura del refuerzo en tracción, se aconseja cuantía de borde ≥ 0.35 % de la sección completa del muro.

### 5.3 Verificación de ductilidad (diagrama de interacción)

El diseño debe quedar **bajo el punto de balance**:
$$\boxed{P_n < P_b}$$

**Por qué:** si $P_n < P_b$ la sección está controlada por la fluencia del acero (dúctil). Si $P_n > P_b$, el hormigón aplasta antes de que fluya el acero del borde opuesto → comportamiento frágil. La curvatura última disminuye al aumentar la carga axial (el eje neutro crece). Por eso un buen diseño mantiene la carga axial bajo el punto de balance.

> **Muros T tienen dos puntos de balance.** Un muro rectangular con armadura simétrica tiene un único punto de balance, independiente del sentido de carga. Un muro T tiene **dos**, según la dirección de la carga: el caso crítico es **cabeza del alma en compresión**, donde la sección puede quedar sobre el balance aun cumpliendo el límite de carga axial de $A_g$. Las asimetrías de geometría y armadura equivalen, en la práctica, a tener cargas axiales altas.

---

## 6. Demanda de desplazamiento y curvatura (DS60 / NCh433)

**Qué se hace:** estimar el desplazamiento de techo de diseño y, de ahí, la demanda de curvatura en la sección crítica. **Aplica a muros con $H_w/l_w \ge 3$.**

**Por qué:** Wallace (1994) demostró que los requerimientos de confinamiento deben derivarse de la **deformada del muro** (su desplazamiento real), no de las fuerzas reducidas por ductilidad. La curvatura es el nexo entre el desplazamiento del edificio y la deformación local del hormigón.

### 6.1 Desplazamiento de techo

$$\boxed{\delta_u = 1.3\,S_{de}(T_{ag})}$$

donde $S_{de}$ es la ordenada del **espectro elástico de desplazamientos** (5 % de amortiguamiento) para el período de mayor masa traslacional con **sección agrietada** $T_{ag}$:

$$S_{de}(T_n) = \dfrac{T_n^2}{4\pi^2}\,\alpha\,A_0\,C_d$$

$$\alpha = \dfrac{1 + 4.5\left(\tfrac{T_n}{T_0}\right)^p}{1 + \left(\tfrac{T_n}{T_0}\right)^3}$$

- $T_{ag} \approx 1.5\,T_{\text{bruto}}$ (si se modeló con secciones brutas, se aumenta 1.5 veces).
- $A_0$: aceleración efectiva (zona sísmica); $S, T_0, p, C_d$: parámetros de suelo (NCh433-2012).

### 6.2 Demanda de curvatura — los dos métodos del DS60

El DS60 permite dos formas de estimar $\phi_u$ a partir de $\delta_u$.

**Método simplificado (21-7a)** — desprecia la deformación elástica; considera solo la capacidad de deformación plástica (rótula que rota como cuerpo rígido en la base):

$$\boxed{\phi_u = \dfrac{2\,\delta_u}{H_w\,l_w} = \dfrac{\varepsilon_c}{c} \le \dfrac{0.008}{c}} \qquad \text{(ACI 21-7a)}$$

resultado de $\delta_u = \theta_p\,H_w = \phi_u\,l_p\,H_w$ con $l_p = l_w/2$.

**Método completo (21-7b)** — incluye la componente elástica $\delta_e$:

$$\boxed{\phi_u = \dfrac{\delta_u - \delta_e}{l_p\left(H_t - l_p/2\right)} + \phi_y} \qquad \text{(ACI 21-7b)}$$

$$\text{con}\quad \delta_e = \dfrac{11}{40}\,\phi_y\,H_t^2 \qquad ; \qquad \phi_y = \dfrac{2\,\varepsilon_y}{l_w}$$

La longitud de rótula plástica no se toma mayor a:
$$l_p \le \dfrac{l_w}{2} \quad (\text{DS60})$$

> **¿Cuál usar?** Se recomienda, de forma **conservadora, usar solo el método simplificado (21-7a)**: hoy no hay buenas estimaciones de la deformación elástica de los muros (depende de muchas variables), y considerarla puede marcar la diferencia entre confinar o no el borde. El DS60 **permite** usar 21-7b para materializar configuraciones especiales (muros secundarios L o T con machones pequeños) donde el confinamiento por 21-7a sería excesivo, poco práctico o muy difícil de ejecutar. En esos casos, 21-7b suele dar una $\phi_u$ menos exigente.
>
> **Ojo con la fórmula cerrada de $\delta_e$.** La expresión $\delta_e = \tfrac{11}{40}\phi_y H_t^2$ supone una distribución triangular de curvatura en toda la altura y, para edificios altos, puede dar valores de $\delta_e$ desproporcionados (incluso mayores que $\delta_u$). En la práctica $\delta_e$ se evalúa mejor con la **rigidez agrietada real del modelo** (el desplazamiento elástico que entrega el análisis), no con esa fórmula cerrada. Úsala solo como referencia gruesa.
>
> A diferencia del ACI318-08 (que fijaba $\delta_u/H_t = 1.5\%$ para edificios típicos de EE.UU.), el DS60 prefiere determinar el confinamiento en función del **drift calculado caso a caso**, por considerar ese 1.5% demasiado conservador para los edificios chilenos de muros.

> **Actualización (Massone, 2022):** en Chile, por edificios rígidos con bajas incursiones inelásticas, $l_p = 0.5\,l_w$ resulta excesivo; se propone **$l_p = 0.3\,l_w$**.

### 6.3 Demanda de ductilidad (preliminar)

$$\delta_y = 0.004\,H_w \qquad ; \qquad \mu_\delta = \dfrac{\delta_u}{\delta_y} \qquad ; \qquad \delta_p = \delta_u - \delta_y$$

(El $\delta_y$ alimenta la elección de $\Omega_v$ del paso 4.)

---

## 7. Profundidad del eje neutro $c$

**Qué se hace:** con las armaduras ya definidas (paso 5), calcular la profundidad del eje neutro $c$ en la sección crítica.

**Por qué:** $c$ es la variable que cierra el chequeo de confinamiento. La curvatura última es inversamente proporcional a $c$: a menor eje neutro, mayor ductilidad. El confinamiento se gatilla cuando $c$ es grande.

### 7.1 Método aproximado de Moehle (con armadura de borde)

$$\boxed{c = \dfrac{P + A_s f_y + \rho_l\,t_w\,l_w\,f_y - A'_s f_y}{0.85\,f'_c\,t_w\,\beta_1 + 2\,\rho_l\,t_w\,f_y}}$$

Es **conservador**: subestima la compresión del hormigón (sobre todo en zona confinada), da ejes neutros mayores. Hipótesis: fluencia de armaduras de tracción y compresión, diseño controlado por tracción ($c/l_w < 3/8 = 0.375$).

### 7.2 Método de Cárdenas-Magura (1973) — armadura uniforme

Permite obtener el $M_u$ máximo con solo armadura repartida y, de paso, $c$:

$$M_u = 0.5\,\phi\,A_s\,f_y\,l_w\left(1 + \dfrac{N_u}{A_s f_y}\right)\left(1 - \dfrac{c}{l_w}\right)$$

$$\dfrac{c}{l_w} = \dfrac{\omega + \alpha}{2\omega + 0.85\,\beta_1} \qquad ; \qquad \omega = \dfrac{\rho_v\,f_y}{f'_c} \qquad ; \qquad \alpha = \dfrac{N_u}{l_w\,b_w\,f'_c}$$

(Válido para carga axial menor a la de falla balanceada.)

**Verificación de tipo de diseño:**
$$c < \tfrac{3}{8}\,l_w \;\Rightarrow\; \text{controlado por tracción (dúctil)}$$

### 7.3 Límite teórico de $c$ para sección simétrica

Para una sección rectangular simétrica con armadura solo en los bordes, imponiendo el equilibrio con $P_u = 0.35\,f'_c A_g$ y $T_f = C_s$:
$$0.85\,f'_c\,\beta_1\,c\,e_w = 0.35\,l_w\,e_w\,f'_c \;\Rightarrow\; \dfrac{c}{l_w} = \dfrac{0.35}{0.85\,\beta_1} \approx 0.48$$

Es decir, el límite de carga axial está pensado para que **$c$ no supere ~la mitad del largo** de la sección, asegurando fluencia del acero y, con ello, ductilidad. (Este es el "porqué" numérico del $0.35\,f'_c A_g$ del §3.1, y por qué falla para secciones T donde $c$ se va a 0.8 $l_w$.)

---

## 8. Verificación de necesidad de confinamiento (elementos de borde)

**Qué se hace:** decidir si los bordes requieren confinamiento (estribos + trabas), **calcular el largo a confinar** y dimensionarlo. Hay **dos métodos para gatillar**; conviene correr ambos porque **no siempre coinciden**.

**Por qué:** el confinamiento no aumenta la capacidad de tomar carga, pero **aumenta la capacidad de deformación del hormigón de 0.003 a 0.008**, permitiendo que el borde comprimido soporte la curvatura última sin aplastarse ni pandear las barras.

### 8.1 Método 1 — por deformaciones (ACI 318-19, 18.10.6.2 / Ec. 21-8)

Se requiere elemento especial de borde cuando el eje neutro supera el umbral:

$$\boxed{c \ge \dfrac{l_w}{600\,(\delta_u/h_{wcs})}}$$

(forma DS60 con factor 1.5: $\;c \ge \dfrac{l_w}{600\cdot 1.5\,(\delta_u/H_w)}$).

- Moehle recomienda usar **1000 en vez de 600** (más exigente).
- $\delta_u/h_w$ no se toma menor a **0.005**.

### 8.2 Largo a confinar (extensión en planta del núcleo) — DS60 (21-8a)

Si se confina, el **largo $C_c$ a confinar** corresponde a la porción de la sección que supera $\varepsilon_c = 0.003$:

$$\boxed{C_c = c\left(1 - \dfrac{\varepsilon_L}{\varepsilon_{cu}}\right) \approx c - \dfrac{l_w}{600\,(\delta_u/H_w)}} \qquad \text{con}\ \varepsilon_L = 0.003,\ \ \varepsilon_{cu}=\dfrac{2\delta_u}{H_t}\cdot\dfrac{c}{l_w}$$

es decir, $C_c$ es lo que **excede** el umbral de confinamiento del §8.1. Reescrito como cuantía del largo:
$$\dfrac{C_c}{l_w} = \dfrac{c}{l_w} - \dfrac{1}{600\,(\delta_u/H_w)}$$

**Largo mínimo del elemento de borde** (ACI 18.10.6.4):
$$\boxed{l_c \ge \max\left(c - 0.1\,l_w,\ \ \dfrac{c}{2}\right) \quad ; \quad l_c \ge e_w \ (\ge 30\ \text{cm})}$$

> **$C_c$ y $l_c$ son cosas distintas — siempre rige el mayor.** $C_c$ es el largo *teórico* de la zona cuya deformación de compresión supera $\varepsilon_c = 0.003$ (lo que "pide" confinamiento por física de la sección). $l_c$ es el largo *normativo mínimo* del elemento de borde que el ACI obliga a confinar (un piso de seguridad geométrico). El elemento de borde se materializa con la **mayor** de las dos longitudes: $l_{conf} = \max(C_c,\ l_c)$. Es frecuente que $l_c$ controle, como ocurre en el ejemplo del final.

### 8.3 Extensión vertical del elemento de borde

El elemento de borde se extiende verticalmente desde la sección crítica la mayor de:
$$\max\left(l_w,\ \dfrac{M_u}{4\,V_u}\right)$$

### 8.4 Método 2 — por tensiones

$$\sigma = \dfrac{P_u}{A_g} + \dfrac{M_{ux}}{S_{gx}} + \dfrac{M_{uy}}{S_{gy}} \qquad ; \qquad S_g = \dfrac{I}{l_w/2} = \dfrac{2I}{l_w}$$

| Condición | Acción |
|---|---|
| $\sigma > 0.2\,f'_c$ | **Confinar** (elementos especiales de borde) |
| $\sigma < 0.15\,f'_c$ y $A_{s,be}/A_{g,be} > 2.8/f_y$ | Elementos ordinarios de borde |
| $\sigma < 0.15\,f'_c$ y $A_{s,be}/A_{g,be} \le 2.8/f_y$ | No requiere confinar |

Donde se dispongan elementos de borde, se continúan sobre y bajo hasta que $\sigma$ baje de $0.15\,f'_c$. **Método preferido para muros irregulares o discontinuos.**

### 8.5 Detallamiento del confinamiento (DS60 / ACI)

- **Espesor mínimo para confinar: $e_w \ge 30$ cm.**
- Las armaduras de confinamiento deben cumplir los **requerimientos de columnas**, con ganchos a **135°**.
- **Área de refuerzo transversal:**
$$A_{sh} = 0.09\,\dfrac{s\,b_c\,f'_c}{f_{yt}}$$
(equivale a $A_{sh} = 0.09\,s\,h_x\,f'_c/f_{yt}$ por rama, con $b_c$ la dimensión del núcleo confinado medida entre ejes de estribos).
- **Espaciamiento vertical $s$ de los estribos de confinamiento** (el menor de):
$$\boxed{s \le \min\left(6\,\varnothing_l,\ \ \dfrac{e_w}{2},\ \ s_o\right)} \qquad s_o = 100 + \left(\dfrac{350 - h_x}{3}\right)\ [\text{mm}]$$
- **Separación de trabas a centro entre ramas:**
$$h_x \le \min\left(20\ \text{cm},\ \dfrac{e_w}{2}\right)$$
- Diámetro transversal $\varnothing_{trans} \ge \varnothing_{long}/3$ (ACI 21.9.2.4); diámetro longitudinal $\varnothing_{long} \le e_w/9$.
- **Elementos ordinarios** (donde **no** se requiera especial pero $\rho > 2.8/f_y$):
$$s \le \min(20\ \text{cm},\ 6\,\varnothing_l) \qquad ; \qquad h_x < 20\ \text{cm}$$

---

## 9. Verificación final de deformaciones

**Qué se hace:** confirmar que, con el eje neutro y la curvatura calculados, las deformaciones quedan dentro de límites.

**Por qué:** cierra el lazo. Asegura que el hormigón comprimido no aplaste (con confinamiento, límite 0.008) y que el acero traccionado no se fracture.

$$\boxed{\varepsilon_u = \phi_u \cdot c = \dfrac{2\,\delta_u\,c}{H_w\,l_w} \le 0.008}$$

$$\boxed{\xi_s = \dfrac{2\,\delta_u\,(l_w - c)}{H_w\,l_w} \le 0.03 = 3\%} \quad (\text{tracción máxima, Norma Chilena 2022})$$

Si $\varepsilon_u > 0.003$ sin confinar → se requiere elemento especial de borde (consistente con el paso 8).

---

## 10. Detallamiento, armaduras mínimas y esquemas

**Qué se hace:** definir mallas mínimas, separaciones y dibujar el esquema de armadura en altura.

### 10.1 Cuantías mínimas (corte)

$$\rho_l,\ \rho_t \ge 0.0025 \qquad ; \qquad A_{\min} = 0.0025\,b_w \cdot 100\ [\text{cm}^2/\text{m}]$$

Puede reducirse esta armadura (según ACI 14.3) si $V_u < 0.26\,A_{cv}\sqrt{f'_c}$ [kg/cm²].

| Espesor | Doble malla mínima |
|---|---|
| $e = 20$ | DM $\varnothing 8$@20 |
| $e = 25$ | DM $\varnothing 8$@16 |
| $e = 30$ | DM $\varnothing 10$@20 |
| $e = 35$ | DM $\varnothing 10$@18 |
| $e = 40$ | DM $\varnothing 10$@15 |

### 10.2 Reglas de detallamiento

- **En Chile, siempre dos mallas** de refuerzo. (ACI las exige si $V_u > 0.17\,A_{cv}\lambda\sqrt{f'_c}$ [MPa] $= 0.53\,A_{cv}\lambda\sqrt{f'_c}$ [kg/cm²]).
- Se requieren **dos puntas de refuerzo en los bordes** si $V_u > 2\,A_{cv}\lambda\sqrt{f'_c}$.
- Diferencia entre cuantía horizontal y vertical **≤ 50 %**.
- **Reparto en dos capas:** una capa debe proveer **al menos 1/2 y no más de 2/3** de la armadura requerida en cada dirección; la otra capa cubre el resto.
- **Empalmes:** el refuerzo se empalma según los criterios de **empalme de barras en tracción**. La armadura horizontal de corte debe ser **continua** y distribuida en el plano de corte, con separación máxima de **450 mm** (ACI); **en Chile no más de 20-25 cm**.
- En pisos superiores, si $V_u \le 0.27\,A_{cv}\lambda\sqrt{f'_c}$ [kg/cm²], puede reducirse la malla de corte.

### 10.3 Entregables

Esquema en planta y elevación con geometría; armaduras mínimas; esfuerzos $(V_u, M_u, N_u, e, l_w)$ por nivel; y el resumen de armaduras de corte y flexo-compresión en la altura.

---

## 11. Secciones T, L y C (consideraciones especiales)

Las secciones con alas son muy comunes en edificios chilenos de muros y **no se diseñan exactamente igual que las rectangulares**. Los principios cambian en los siguientes puntos:

1. **Límite de carga axial (§3.1).** Verificar **dos** veces: referido a $A_g$ y referido **solo al área del alma $A_w$**. Es habitual que se cumpla con $A_g$ pero se supere con $A_w$ → señal de comportamiento frágil. (Caso real 27F-2010: $P_u/(A_w f'_c) = 0.45$ vs. $P_u/(A_g f'_c) = 0.20$.)

2. **Dos puntos de balance (§5.3).** Diseñar para el sentido crítico (cabeza del alma en compresión: poco hormigón equilibra mucho acero traccionado del ala).

3. **Sección completa (§5.1).** Considerar toda la sección con todas las armaduras, o usar el ancho efectivo del ala (menor entre ½ distancia al muro adyacente y 25 % de la altura).

4. **Verificación obligatoria por momento-curvatura.** En T/L/C el límite de carga axial puede ser insuficiente; el chequeo decisivo es la curva M-φ con la carga axial real, comparando $\phi_u$ disponible contra la demanda (21-7a y 21-7b).

5. **Estrategia de rediseño cuando no cumple** (en orden de menor a mayor costo):
   - **Aumentar espesor** del muro/alma → baja el eje neutro $c$.
   - **Subir la calidad del hormigón** → mayor capacidad de compresión, baja $c$.
   - **Incorporar la deformación elástica (21-7b)** → demanda de curvatura menos exigente.
   - **Confinar y/o reconfigurar** los cabezales como dos elementos de borde confinados.

6. **Elementos de borde en el ala (sin confinamiento, si aplica).** Verificar 21.9.2.4: $\varnothing_{long} \le e_w/9$ y $\varnothing_{trans} \ge \varnothing_{long}/3$, con $s \le \min(6\varnothing_l, 200\,\text{mm})$ cuando la cuantía vertical supera $2.8/f_y$.

---
---

# Ejemplo resuelto, paso a paso

> Muro rectangular de un edificio de muros. Recorremos las 10 etapas con sus porqués. *(Valores didácticos consistentes.)*

### Datos

| Dato | Valor |
|---|---|
| Largo $l_w$ | 6.50 m (650 cm) |
| Espesor $e = b_w$ | 30 cm |
| Altura total $H_w$ | 48.6 m (18 pisos de 2.70 m) |
| Hormigón | $f'_c = 250$ kg/cm² (G25) |
| Acero | A630-420H, $f_y = 4200$ kg/cm² |
| Zona / suelo (NCh433) | Zona 3 ($A_0 = 0.4g$), Suelo C |

**Esfuerzos en la sección crítica (base):**

| Combinación | Para qué controla | Valores |
|---|---|---|
| Flexo-compresión (axial mínimo) | armadura F-C | $N_u = 370$ T ; $M_u = 2130$ T-m |
| Compresión máxima | chequeo $\sigma_u$ | $P_{u,\max} = 1033$ T |
| Corte | armadura de corte | $V_u = 359$ T |

*(Por qué dos axiales: el menor axial es más desfavorable para la ductilidad/flexión; el mayor para la compresión. Es correcto usar distintas combinaciones en distintos chequeos.)*

---

### Paso 1 — Geometría y clasificación

$$\dfrac{H_w}{l_w} = \dfrac{48.6}{6.5} = 7.48 \;>\; 3$$

→ Muro **esbelto**. Controla flexión y **aplica la verificación de curvatura** del DS60. La sección crítica es la base.

---

### Paso 2 — Esfuerzos

Del modelo (PIER asignado, ejes locales en PIER, esfuerzos $M_{3\text{-}3}$ y $Q_{2\text{-}2}$), envolvente de combinaciones → los valores de la tabla de datos.

---

### Paso 3 — Verificaciones previas

**Compresión máxima:**
$$\sigma_u = \dfrac{P_{u,\max}}{l_w b_w} = \dfrac{1\,033\,000}{650 \times 30} = 53.0\ \text{kg/cm}^2 \;<\; 0.35\,f'_c = 87.5\ \text{kg/cm}^2 \quad\checkmark$$

**Esbeltez de entrepiso:**
$$e_{\min} = 30\ \text{cm} \;>\; \dfrac{H_u}{16} = \dfrac{270}{16} = 16.9\ \text{cm} \quad\checkmark$$

**Corte máximo:**
$$V_{\max} = 2.12\,b_w\,l_w\sqrt{f'_c} = 2.12 \times 30 \times 650 \times \sqrt{250} = 653\ \text{T} \;>\; V_u = 359\ \text{T} \quad\checkmark$$

Las tres se cumplen → seguimos.

---

### Paso 4 — Armadura de corte (capacidad)

Usamos $\Omega_v = 2.0$ (mínimo conservador):
$$V_e = \Omega_v \cdot V_u = 2.0 \times 359 = 718\ \text{T}$$

Chequeo contra el tope con **resistencia esperada** del hormigón ($1.3\,f'_c$):
$$V_{\max,\text{esp}} = 2.12 \times 30 \times 650 \times \sqrt{1.3 \times 250} = 745\ \text{T} \;>\; 718\ \text{T} \quad\checkmark$$

Resistencia requerida y aporte del hormigón:
$$V_c = 0.53\,b_w\,l_w\sqrt{f'_c} \approx 186\ \text{T (con propiedad esperada)}$$
$$V_s = V_e - V_c = 718 - 186 = 532\ \text{T}$$

Cuantía y malla ($A_{cv} = 30\times650 = 19\,500\ \text{cm}^2$):
$$\rho_t = \dfrac{V_s}{A_{cv}\,f_y} = \dfrac{532\,000}{19\,500 \times 4200} = 0.0065$$
$$A_h = \rho_t\,b_w\cdot 100 = 0.0065 \times 30 \times 100 = 19.5\ \text{cm}^2/\text{m (total)} \;\Rightarrow\; 9.75\ \text{cm}^2/\text{m por cara}$$

→ **Malla horizontal: DM $\varnothing 12$@11** ($\varnothing12$ = 1.13 cm² → $s = 1.13/9.75\times100 \approx 11.6$ cm). Cumple con holgura sobre la mínima por la amplificación de capacidad.

*(Si no se amplificara, con $V_n = V_u/\phi = 359/0.75 = 479$ T daría $V_s \approx 293$ T, $\rho_t \approx 0.0036$ y una malla bastante menor. La diferencia es el "precio" del diseño por capacidad, que protege contra la falla frágil.)*

---

### Paso 5 — Armadura de flexo-compresión

Parámetros para axial:
$$\alpha = \dfrac{N_u}{l_w b_w f'_c} = \dfrac{370\,000}{650\times30\times250} = 0.076$$

**Iteración 1**, armadura mínima $\rho_v = 0.0025$:
$$\omega = \dfrac{0.0025\times4200}{250} = 0.042 \quad;\quad \dfrac{c}{l_w} = \dfrac{0.042+0.076}{2(0.042)+0.85(0.85)} = 0.146$$
$$A_{sw} = 0.0025\times30\times650 = 48.75\ \text{cm}^2$$
$$M_u = 0.5(0.9)(48.75)(4200)(650)\left(1+\tfrac{370\,000}{48.75\times4200}\right)(1-0.146) = 1436\ \text{T-m} \;<\; 2130 \quad\text{✗}$$

→ No alcanza con la mínima. **Iteración 2**, $\rho_v = 0.007$ (DM $\varnothing 12$@10):
$$\omega = 0.118 \quad;\quad \dfrac{c}{l_w} = \dfrac{0.118+0.076}{2(0.118)+0.7225} = 0.202$$
$$A_{sw} = 0.007\times30\times650 = 136.5\ \text{cm}^2$$
$$M_u = 0.5(0.9)(136.5)(4200)(650)\left(1+\tfrac{370\,000}{136.5\times4200}\right)(1-0.202) = 2201\ \text{T-m} \;>\; 2130 \quad\checkmark$$

→ **Armadura vertical uniforme: DM $\varnothing 12$@10** (11.31 cm²/m, ~7 ‰).

Tipo de diseño:
$$c = 0.202 \times 650 = 131\ \text{cm} \;<\; \tfrac{3}{8}l_w = 244\ \text{cm} \quad\Rightarrow\quad \text{controlado por tracción (dúctil)}\ \checkmark$$

---

### Paso 6 — Demanda de desplazamiento y curvatura

Período agrietado supuesto $T_{ag} = 1.5\ T_{\text{bruto}} = 1.5\ \text{s}$. Suelo C: $T_0 = 0.40$, $p = 1.6$; $A_0 = 0.4g = 392.4$ cm/s²; $C_d = 0.57\,T_n + 0.63 = 1.49$.

$$\alpha = \dfrac{1 + 4.5(1.5/0.40)^{1.6}}{1 + (1.5/0.40)^3} = \dfrac{1 + 4.5(8.29)}{1 + 52.7} = 0.71$$

$$S_{de} = \dfrac{T_n^2}{4\pi^2}\,\alpha\,A_0\,C_d = \dfrac{1.5^2}{4\pi^2}(0.71)(392.4)(1.49) = 23.7\ \text{cm}$$

$$\boxed{\delta_u = 1.3 \times 23.7 = 30.8\ \text{cm} \approx 0.31\ \text{m}}$$

**Curvatura — método simplificado (21-7a):**
$$\phi_u = \dfrac{2\,\delta_u}{H_w\,l_w} = \dfrac{2(0.31)}{48.6\times6.5} = 0.00196\ \text{m}^{-1}$$

**Curvatura — método completo (21-7b), para comparar:**
$$\phi_y = \dfrac{2\varepsilon_y}{l_w} = \dfrac{2(0.0021)}{6.5} = 0.00065\ \text{m}^{-1} \quad;\quad \delta_e = \dfrac{11}{40}\phi_y H_t^2 = \dfrac{11}{40}(0.00065)(48.6^2) = 0.42\ \text{m}$$

Como $\delta_e > \delta_u$, en este muro la fórmula cerrada de $\delta_e$ daría una rótula prácticamente nula → "diría" que la sección está casi en rango elástico. Esto es precisamente el efecto distorsionador advertido en §6.2: la fórmula triangular sobreestima $\delta_e$ en edificios altos. Lo correcto sería tomar $\delta_e$ del **desplazamiento elástico del modelo con rigidez agrietada**; por consistencia y conservadurismo se usa **21-7a** ($\phi_u = 0.00196\ \text{m}^{-1}$). *(Este contraste ilustra por qué 21-7b se reserva para casos especiales: la incertidumbre de $\delta_e$ puede invertir la conclusión sobre confinar.)*

Ductilidad preliminar: $\delta_y = 0.004\times48.6 = 0.194$ m → $\mu_\delta = 0.31/0.194 = 1.6$.

---

### Paso 7 — Eje neutro $c$

Con la armadura final ($\rho_v = 0.007$), por **Moehle**:
$$c = \dfrac{P_u + \rho_v\,b_w\,l_w\,f_y}{0.85\,f'_c\,b_w\,\beta_1 + 2\,\rho_v\,b_w\,f_y} = \dfrac{370\,000 + 0.007(30)(650)(4200)}{0.85(250)(30)(0.85) + 2(0.007)(30)(4200)}$$
$$c = \dfrac{370\,000 + 573\,300}{5419 + 1764} = \dfrac{943\,300}{7183} = 131\ \text{cm}$$

Coincide con Cárdenas-Magura ($c = 0.202\,l_w = 131$ cm). → $\boxed{c = 1.31\ \text{m}}$

---

### Paso 8 — ¿Requiere confinamiento? ¿Cuánto largo?

**Método por deformaciones (gatillo):**
$$\dfrac{\delta_u}{H_w} = \dfrac{0.31}{48.6} = 0.0064 \;(> 0.005,\ \text{se usa } 0.0064)$$
$$c_{\lim} = \dfrac{l_w}{600 \cdot 1.5\,(\delta_u/H_w)} = \dfrac{6.5}{600(1.5)(0.0064)} = 1.13\ \text{m}$$
$$c = 1.31\ \text{m} \;>\; c_{\lim} = 1.13\ \text{m} \quad\Rightarrow\quad \textbf{Confinar}$$

**Largo a confinar (extensión teórica del núcleo, 21-8a):**
$$C_c = c - \dfrac{l_w}{600\cdot 1.5\,(\delta_u/H_w)} = 1.31 - 1.13 = 0.18\ \text{m}$$

**Largo mínimo normativo del elemento de borde:**
$$l_c \ge \max\left(c - 0.1\,l_w,\ \tfrac{c}{2}\right) = \max(1.31 - 0.65,\ 0.655) = 0.66\ \text{m} \quad;\quad l_c \ge e_w = 0.30\ \text{m}$$

**Largo a materializar** (rige el mayor entre $C_c$ y $l_c$):
$$l_{conf} = \max(C_c,\ l_c) = \max(0.18,\ 0.66) = 0.66\ \text{m}$$
→ Aquí controla el **mínimo normativo** $l_c$, no el largo teórico $C_c$.

**Método por tensiones (verificación cruzada):** $A_g = 0.30\times6.5 = 1.95$ m²; $S_g = \dfrac{e\,l_w^2}{6} = \dfrac{0.30\times6.5^2}{6} = 2.11$ m³.
$$\sigma = \dfrac{370}{1.95} + \dfrac{2130}{2.11} = 190 + 1009 = 1199\ \text{T/m}^2 = 120\ \text{kg/cm}^2 \;>\; 0.2 f'_c = 50 \quad\Rightarrow\quad \textbf{Confinar}$$

Ambos métodos coinciden → **elementos especiales de borde**, $l_{conf} = 0.66$ m a cada extremo. (El espesor de 30 cm es justo el mínimo para confinar: OK.)

**Extensión vertical** del elemento de borde desde la base:
$$\max\left(l_w,\ \dfrac{M_u}{4V_u}\right) = \max\left(6.5,\ \dfrac{2130}{4\times359}\right) = \max(6.5,\ 1.48) = 6.5\ \text{m}$$

**Detallamiento del confinamiento** (con $\varnothing_l = 12$ mm, $h_x \approx 15$ cm):
$$s \le \min\left(6\varnothing_l,\ \tfrac{e_w}{2},\ s_o\right) = \min\left(7.2,\ 15,\ 10+\tfrac{350-150}{30}\right)\ \text{cm} \approx \min(7.2,\ 15,\ 16.7) = 7.2\ \text{cm}$$
→ Estribos + trabas **$\varnothing 10$@7** en el núcleo confinado, ganchos a 135°, con $A_{sh} = 0.09\,s\,b_c\,f'_c/f_{yt}$.

---

### Paso 9 — Verificación final de deformaciones

$$\varepsilon_u = \phi_u \cdot c = 0.00196 \times 1.31 = 0.0026 \;<\; 0.008 \quad\checkmark \;(\text{con confinamiento})$$

$$\xi_s = \dfrac{2\,\delta_u\,(l_w - c)}{H_w\,l_w} = \dfrac{2(0.31)(6.5-1.31)}{48.6\times6.5} = 0.0102 \;<\; 0.03 \quad\checkmark$$

---

### Paso 10 — Detallamiento y resumen

| Concepto | Resultado |
|---|---|
| Malla horizontal (corte) | DM $\varnothing 12$@11 (zona crítica) |
| Armadura vertical (flexión) | DM $\varnothing 12$@10 uniforme, ~7 ‰ |
| Bordes | Elementos especiales de borde confinados, $l_{conf} = 0.66$ m, $\varnothing 10$@7, $A_{sh} = 0.09\,s\,b_c\,f'_c/f_{yt}$ |
| Extensión vertical del borde | 6.5 m desde la base |
| Mínimos | doble malla, $\rho \ge 0.0025$, separación ≤ 20-25 cm, reparto 1/2–2/3 por capa |
| Compresión | $\sigma_u = 53 < 87.5$ kg/cm² ✓ |
| Esbeltez | $30 > 16.9$ cm ✓ |
| Ductilidad | $c/l_w = 0.20 < 0.375$ → controlado por tracción ✓ |

**Comentario de diseño:** el muro disipa energía por flexión en la base (zona crítica), con la armadura de corte amplificada por capacidad para impedir la falla frágil, y bordes confinados que sostienen la curvatura última. En altura, sobre la zona crítica, las cuantías de corte y flexión pueden reducirse hacia los mínimos a medida que bajan las solicitaciones.

---

## Anexo — Modos de falla al corte (fundamentos)

Para entender por qué el corte se diseña por capacidad, conviene reconocer los mecanismos de falla. El comportamiento al corte tiene dos fases: rango elástico hasta el **agrietamiento diagonal** (problema de tensiones principales: dependen de la resistencia a tracción, el esfuerzo axial y la esbeltez), y el rango **post-agrietamiento** (resisten la trabazón de agregados, la garganta comprimida no fisurada, el refuerzo transversal a tracción y el efecto "tarugo" del refuerzo longitudinal).

| Modo de falla | Cuándo ocurre | Carácter |
|---|---|---|
| **Frágil por corte** | Muros bajos, baja cuantía transversal | Gran grieta diagonal, no se desarrolla mecanismo post-agrietamiento; la armadura transversal se fractura. Falla súbita. |
| **Tensión diagonal** | Muros más esbeltos, mayor cuantía transversal | El refuerzo limita el ancho de grieta y fluye; comportamiento algo más dúctil antes de fracturar. |
| **Compresión diagonal** | Mucha cuantía transversal | Aplastamiento del hormigón en la biela/cabeza de compresión ($V/(t_w l_w) \to k f'_c$). Por eso existe el tope de corte del §3.3. |
| **Corte en muros muy bajos** | $M/Vd < 0.5$ | La grieta no cruza toda el alma, solo una esquina; participa la armadura longitudinal. |

**Parámetros influyentes:**
- **Esbeltez:** define el mecanismo de falla.
- **Compresión axial:** aumenta la resistencia al agrietamiento diagonal y al corte (mejora trabazón, agranda la zona comprimida), pero **reduce la capacidad de deformación plástica** → favorece la falla frágil.
- **Refuerzo transversal:** solo efectivo tras el agrietamiento; aporta resistencia y, sobre todo, capacidad de deformación. Un exceso puede inducir falla por compresión diagonal.
- **Refuerzo longitudinal:** aporta por efecto tarugo y define la posición de la línea neutra (tamaño de la cabeza de compresión).

---

## Anexo — Deslizamiento en la base (cortante por fricción)

El deslizamiento en la junta de hormigonado de la base es otra falla frágil a evitar. Se verifica por **cortante por fricción** (ACI 318-19, 22.9):

$$V_n = \mu\,A_{vf}\,f_y$$

con los topes (ACI 318-19, Tabla 22.9.4.4, convertidos a kg/cm²):

$$V_n \le \min\Big(0.2\,f'_c\,A_c,\ \ (33.6 + 0.08\,f'_c)\,A_c,\ \ 56\ \text{kg/cm}^2\cdot A_c\Big)$$

> **Nota de unidades.** En el ACI 318-19 (SI), los topes son $0.2\,f'_c$, $(3.3 + 0.08\,f'_c)$ MPa y $11$ MPa. La conversión a kg/cm² da $0.2\,f'_c$, $(33.6 + 0.08\,f'_c)$ y $\approx 112$ kg/cm². El valor de $56$ kg/cm² ($\approx 5.5$ MPa) corresponde al **tope reducido** que aplica para hormigón colocado contra hormigón endurecido con superficie **no intencionalmente rugosa** (junta de construcción lisa). Si la junta se deja **intencionalmente rugosa** (amplitud ≈ 6 mm), rige el tope mayor de $\approx 112$ kg/cm² ($11$ MPa). Verificar siempre la condición de junta del proyecto.

donde $A_{vf}$ es la armadura vertical que cruza el plano de deslizamiento (la propia armadura de flexión suele bastar), $\mu$ el coeficiente de fricción según el tratamiento de la junta —$\mu = 1.0$ para junta intencionalmente rugosa, $0.6$ para junta lisa, $1.4$ monolítico—, y $A_c$ el área de contacto. Conviene además dejar la junta limpia y rugosa, y considerar el aporte favorable de la compresión axial permanente $N_u$ (se puede sumar $\mu\,N_u$ al lado resistente).

---

## Referencias

- **ACI 318-19**, Capítulo 18 — Muros estructurales especiales; Cap. 22.9 — Cortante por fricción.
- **DS 60 / DS 61 (2011)**, modificaciones a la NCh 433 tras el terremoto del Maule (2010).
- **NCh 433** — Diseño sísmico de edificios; **NCh 430** — Hormigón armado (propuesta de corte en estudio, comité 2025); **NCh 3171** — Combinaciones de carga.
- **NIST GCR 11-917-11 Rev. 1 (2014)**, J. Moehle — *Seismic Design of Cast-in-Place Concrete Special Structural Walls and Coupling Beams*.
- **Priestley & Paulay (1991)** — *Seismic Design of Reinforced Concrete and Masonry Buildings*.
- **Cárdenas & Magura (1973)** — armadura repartida uniforme.
- **Wallace & Orakcal (2002)** — modelo de demanda de curvatura adoptado por ACI/DS60.
- **Larraín & Yáñez (2006)** — *Manual de Cálculo de Hormigón Armado* (ábacos de interacción).
- Wallace (1994); Bonelli (ICH, 2005); Carvallo (ICH, 2012); René Lagos (2010); Massone (2022).
- **Peña, C. (CPL Ingeniería)** — *Diseño Sismorresistente, Hormigón Armado: comportamiento y diseño de muros* (apuntes de cátedra).

> *Nota: mientras la NCh 430 no se oficialice, el criterio de sobrerresistencia para corte aquí descrito es referencial; verificar la versión vigente al momento de proyectar.*