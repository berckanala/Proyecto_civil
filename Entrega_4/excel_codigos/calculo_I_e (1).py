import math

# ─────────────────────────────────────────────
#  DATOS DE ENTRADA
# ─────────────────────────────────────────────
# Geometría (m)
h   = 0.50
b   = 0.25
d   = 0.45
rec = 0.05

# Luces y cargas
L    = 5.49      # m
M_a  = 7.1124    # tonf·m  (momento de servicio máximo)

# Materiales
f_c  = 35.0      # MPa
E_s  = 200_000.0 # MPa
lam  = 1.0       # factor λ (hormigón normal)

# Acero en tracción
n_barras   = 3
diam_mm    = 18.0
A_barra    = math.pi * (diam_mm / 2) ** 2   # mm²
A_s_mm2    = n_barras * A_barra              # mm²
A_s        = A_s_mm2 * 1e-6                  # m²

# Parámetros de carga
alphas = {
    "Viga simplemente apoyada (carga dist.)": 9.6,
    "Viga empotrada - apoyo simple":         16.0,
}

# ── Flecha diferida (estimación simplificada: 100% carga permanente) ──
xi           = 2.0     # ξ según tiempo: 3m→1.0 | 6m→1.2 | 12m→1.4 | 5+años→2.0
tiempo_desc  = "5 años o más"

# Acero en compresión (zona de momento máximo) — poner 0 si no hay
n_barras_comp = 0
diam_comp_mm  = 0.0

# ─────────────────────────────────────────────
#  CÁLCULOS
# ─────────────────────────────────────────────

SEP  = "─" * 58
SEP2 = "═" * 58

def titulo(txt):
    print(f"\n{SEP2}")
    print(f"  {txt}")
    print(SEP2)

def seccion(txt):
    print(f"\n{SEP}")
    print(f"  {txt}")
    print(SEP)

# ── 1. Módulo de elasticidad del hormigón ──
E_c_MPa = 4700 * math.sqrt(f_c)             # MPa
E_c_tonf = E_c_MPa * 1e6 / 9806.65          # tonf/m²  (1 MPa = 1 MN/m² = 101.97 tonf/m²)
E_c_tonf = E_c_MPa * 101.9716               # tonf/m²

titulo("CÁLCULO DEL MOMENTO DE INERCIA EFECTIVO Ie")

seccion("1 | MÓDULO DE ELASTICIDAD DEL HORMIGÓN")
print(f"  f'c             = {f_c:.1f} MPa")
print(f"  Ec = 4700·√f'c  = 4700 × √{f_c} = {E_c_MPa:.3f} MPa")
print(f"                  = {E_c_tonf:.2f} tonf/m²")

# ── 2. Razón modular ──
n = E_s / E_c_MPa

seccion("2 | RAZÓN MODULAR n")
print(f"  Es              = {E_s:,.0f} MPa")
print(f"  Ec              = {E_c_MPa:.3f} MPa")
print(f"  n = Es/Ec       = {E_s:.0f} / {E_c_MPa:.3f} = {n:.4f}")

# ── 3. Área de acero ──
seccion("3 | ÁREA DE ACERO")
print(f"  Barras          = {n_barras} φ{diam_mm:.0f} mm")
print(f"  A_barra         = π(d/2)² = {A_barra:.4f} mm²")
print(f"  A_s total       = {A_s_mm2:.4f} mm²  =  {A_s:.6f} m²")

# ── 4. Eje neutro fisurado c ──
seccion("4 | EJE NEUTRO FISURADO c")
print("  Ecuación: (b/2)·c² + (n·As)·c - (n·As·d) = 0")
print()

nAs = n * A_s        # m²
A_coef = b / 2
B_coef = nAs
C_coef = -nAs * d

discriminante = B_coef**2 - 4 * A_coef * C_coef
c = (-B_coef + math.sqrt(discriminante)) / (2 * A_coef)

print(f"  n·As            = {n:.4f} × {A_s:.6f} = {nAs:.6f} m²")
print(f"  Coeficientes cuadrática:")
print(f"    A = b/2       = {A_coef:.4f}")
print(f"    B = n·As      = {B_coef:.6f}")
print(f"    C = -n·As·d   = {C_coef:.6f}")
print(f"  Discriminante   = {discriminante:.8f}")
print(f"  c               = {c:.6f} m  =  {c*100:.3f} cm")

# ── 5. Inercia fisurada Icr ──
seccion("5 | INERCIA FISURADA Icr")

term1 = b * c**3 / 3
term2 = nAs * (d - c)**2

I_cr = term1 + term2

print(f"  b·c³/3          = {b}×{c:.6f}³/3 = {term1:.6e} m⁴")
print(f"  (d-c)           = {d} - {c:.6f} = {(d-c):.6f} m")
print(f"  n·As·(d-c)²     = {nAs:.6f}×{(d-c):.6f}² = {term2:.6e} m⁴")
print(f"  Icr             = {term1:.6e} + {term2:.6e}")
print(f"                  = {I_cr:.6e} m⁴")

# ── 6. Inercia bruta Ig ──
seccion("6 | INERCIA BRUTA Ig (sección sin fisurar)")

I_g = b * h**3 / 12
y_t = h / 2

print(f"  Ig = b·h³/12    = {b}×{h}³/12 = {I_g:.6e} m⁴")
print(f"  yt = h/2        = {h}/2 = {y_t:.4f} m")

# ── 7. Momento de fisuración Mcr ──
seccion("7 | MOMENTO DE FISURACIÓN Mcr")

f_r_MPa  = 0.62 * lam * math.sqrt(f_c)                   # MPa
f_r_tonf = f_r_MPa * 101.9716                             # tonf/m²
M_cr     = f_r_tonf * I_g / y_t                           # tonf·m

print(f"  fr = 0.62λ√f'c  = 0.62×{lam}×√{f_c} = {f_r_MPa:.4f} MPa")
print(f"                  = {f_r_tonf:.4f} tonf/m²")
print(f"  Mcr = fr·Ig/yt  = {f_r_tonf:.4f}×{I_g:.6e}/{y_t}")
print(f"                  = {M_cr:.4f} tonf·m")

# ── 8. Inercia efectiva Ie — ACI 318-19 Tabla 24.2.3.5 ──
seccion("8 | INERCIA EFECTIVA Ie — ACI 318-19 (Tabla 24.2.3.5)")

eta      = 1 - (I_cr / I_g)
umbral   = (2 / 3) * M_cr   # si Ma ≤ (2/3)Mcr → sección sin fisurar

print(f"  Norma: ACI 318-19, Tabla 24.2.3.5")
print(f"  Condición: si Ma ≤ (2/3)·Mcr  →  Ie = Ig  (sin fisurar)")
print(f"             si Ma > (2/3)·Mcr  →  Ie = Icr / [1 - η·(Mcr/Ma)²]")
print()
print(f"  η = 1 - Icr/Ig = 1 - {I_cr:.6e}/{I_g:.6e} = {eta:.6f}")
print(f"  (2/3)·Mcr      = (2/3)×{M_cr:.4f} = {umbral:.4f} tonf·m")
print(f"  Ma (servicio)  = {M_a:.4f} tonf·m")
print()

if M_a <= umbral:
    I_e = I_g
    print(f"  Ma ≤ (2/3)·Mcr  →  sección SIN FISURAR")
    print(f"  Ie = Ig = {I_e:.6e} m⁴")
else:
    ratio_2  = (M_cr / M_a) ** 2
    I_e_calc = I_cr / (1 - eta * ratio_2)
    I_e      = min(I_e_calc, I_g)

    print(f"  Ma > (2/3)·Mcr  →  sección FISURADA")
    print(f"  (Mcr/Ma)²      = ({M_cr:.4f}/{M_a:.4f})² = {ratio_2:.6f}")
    print(f"  η·(Mcr/Ma)²    = {eta:.6f} × {ratio_2:.6f} = {eta*ratio_2:.6f}")
    print(f"  1 - η·(Mcr/Ma)²= 1 - {eta*ratio_2:.6f} = {1 - eta*ratio_2:.6f}")
    print(f"  Ie = Icr / [1 - η·(Mcr/Ma)²]")
    print(f"     = {I_cr:.6e} / {1 - eta*ratio_2:.6f}")
    print(f"     = {I_e_calc:.6e} m⁴")
    if I_e_calc > I_g:
        print(f"  ⚠ Ie > Ig → se limita a Ig")

print(f"\n  {'Icr':>6} = {I_cr:.4e} m⁴")
print(f"  {'Ie':>6}  = {I_e:.4e} m⁴  ← RESULTADO")
print(f"  {'Ig':>6} = {I_g:.4e} m⁴")
print(f"\n  Verificación: Icr ≤ Ie ≤ Ig")
print(f"  {I_cr:.4e} ≤ {I_e:.4e} ≤ {I_g:.4e}  →  {'✓ OK' if I_cr <= I_e <= I_g else '✗ ERROR'}")

# ── 9. Flecha instantánea ──
titulo("9 | FLECHA INSTANTÁNEA fi")

print(f"\n  fi = (Ma·L²) / (α·Ec·Ie)\n")
print(f"  Ma  = {M_a:.4f} tonf·m")
print(f"  L   = {L:.2f} m  →  L² = {L**2:.4f} m²")
print(f"  Ec  = {E_c_tonf:.2f} tonf/m²")
print(f"  Ie  = {I_e:.6e} m⁴")

numerador = M_a * L**2
print(f"\n  Numerador  Ma·L²  = {M_a:.4f} × {L**2:.4f} = {numerador:.4f} tonf·m³")

fi_por_alpha = {}
print()
for descripcion, alpha in alphas.items():
    denominador = alpha * E_c_tonf * I_e
    fi_m  = numerador / denominador
    fi_mm = fi_m * 1000
    fi_por_alpha[descripcion] = fi_m
    print(f"  α = {alpha:4.1f}  ({descripcion})")
    print(f"         fi = {numerador:.4f} / ({alpha}×{E_c_tonf:.2f}×{I_e:.4e})")
    print(f"            = {numerador:.4f} / {denominador:.4f}")
    print(f"            = {fi_m:.6f} m  =  {fi_mm:.3f} mm")
    print()

# ── 10. Flecha diferida y total ──
titulo("10 | FLECHA DIFERIDA Y FLECHA TOTAL  (estimación simplificada)")

# Acero de compresión
if diam_comp_mm > 0 and n_barras_comp > 0:
    A_s_comp_mm2 = n_barras_comp * math.pi * (diam_comp_mm / 2) ** 2
else:
    A_s_comp_mm2 = 0.0
A_s_comp  = A_s_comp_mm2 * 1e-6   # m²
rho_prima = A_s_comp / (b * d)
lam       = xi / (1 + 50 * rho_prima)

seccion("10.1 | FACTOR λ (deformación adicional a largo plazo)")
print(f"  ξ (tiempo: {tiempo_desc})  = {xi:.1f}")
print()
if A_s_comp_mm2 > 0:
    print(f"  Acero compresión  = {n_barras_comp} φ{diam_comp_mm:.0f} mm")
    print(f"  A's               = {A_s_comp_mm2:.4f} mm²")
else:
    print(f"  Acero compresión  = Sin acero de compresión (ρ' = 0)")
print(f"  ρ' = A's/(b·d)    = {A_s_comp:.6f} / ({b}×{d}) = {rho_prima:.6f}")
print(f"  50·ρ'             = {50*rho_prima:.6f}")
print(f"  λ = ξ/(1+50·ρ')  = {xi:.1f} / (1 + {50*rho_prima:.6f}) = {lam:.4f}")

seccion("10.2 | FLECHA POR CREEP Y TOTAL (por condición de apoyo)")
print(f"  Hipótesis simplificada: 100% de la carga es permanente")
print(f"  Δcreep = λ · Δfis")
print(f"  Δtot   = (1 + λ) · Δfis")
print(f"  λ      = {lam:.4f}")
print()

for descripcion, fi_m in fi_por_alpha.items():
    fi_mm    = fi_m * 1000
    dif_mm   = lam * fi_m * 1000
    tot_mm   = (1 + lam) * fi_m * 1000

    print(f"  ┌─ {descripcion}")
    print(f"  │  Δfis           = {fi_mm:.3f} mm")
    print(f"  │  Δcreep = {lam:.4f} × {fi_mm:.3f} = {dif_mm:.3f} mm")
    print(f"  │  Δtot   = (1 + {lam:.4f}) × {fi_mm:.3f} = {1+lam:.4f} × {fi_mm:.3f}")
    print(f"  └─ Δtot          = {tot_mm:.3f} mm")
    print()

# ── 11. Verificación límites admisibles — Tabla 24.2.2 ACI 318 ──
titulo("11 | VERIFICACIÓN DEFLEXIÓN ADMISIBLE — Tabla 24.2.2 ACI 318")
print(f"  Tipo de miembro : Entrepiso (estacionamiento)")
print(f"  Hipótesis       : 100% carga muerta  →  ΔCV = 0")
print()
print(f"  Caso 2 │ Inmediata por CV      │ Límite ℓ/360")
print(f"  Caso 4 │ Δcreep(CP) + Δinm(CV)│ Límite ℓ/240")
print()

lim_360 = L * 1000 / 360   # mm
lim_240 = L * 1000 / 240   # mm

print(f"  Luz  ℓ     = {L:.2f} m  =  {L*1000:.1f} mm")
print(f"  ℓ/360      = {lim_360:.2f} mm")
print(f"  ℓ/240      = {lim_240:.2f} mm")
print()

for descripcion, fi_m in fi_por_alpha.items():
    fi_mm    = fi_m * 1000
    dif_mm   = lam * fi_m * 1000   # Δcreep = λ·Δfis (100% CM)
    delta_cv = 0.0                  # ΔCV = 0 por hipótesis

    # Caso 2: inmediata CV
    caso2_mm  = delta_cv
    ok2       = caso2_mm <= lim_360

    # Caso 4: creep CP + inmediata CV
    caso4_mm  = dif_mm + delta_cv
    ok4       = caso4_mm <= lim_240

    print(f"  ┌─ {descripcion}")
    print(f"  │")
    print(f"  │  CASO 2  →  Δ_CV = {caso2_mm:.3f} mm  ≤  ℓ/360 = {lim_360:.2f} mm  →  {'✓ OK' if ok2 else '✗ NO CUMPLE'}")
    print(f"  │             (ΔCV = 0 porque 100% CM → siempre cumple)")
    print(f"  │")
    print(f"  │  CASO 4  →  Δcreep + ΔCV = {dif_mm:.3f} + {delta_cv:.3f} = {caso4_mm:.3f} mm")
    print(f"  │             Límite ℓ/240  = {lim_240:.2f} mm")
    print(f"  └─            {'✓ CUMPLE' if ok4 else '✗ NO CUMPLE'}  ({caso4_mm:.3f} {'≤' if ok4 else '>'} {lim_240:.2f} mm)")
    print()

print(SEP2)
print("  FIN DEL CÁLCULO")
print(SEP2 + "\n")