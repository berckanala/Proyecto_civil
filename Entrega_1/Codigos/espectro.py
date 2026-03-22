import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

G = 9.81  # m/s^2

# ============================================================
# DATOS DEL PROYECTO
# ============================================================

# Datos normativos del caso
Ao_over_g = 0.40     # Zona sísmica 3
I = 1.0              # Categoría II
S = 0.90             # Suelo A
To = 0.15            # s
Tprime = 0.20        # s
n = 1.0
p = 2.0

# Factores de respuesta
R = 7.0
Ro = 11.0

# Geometría básica
N_pisos = 21

# Peso sísmico total sobre el nivel basal
# Si P está en kN, Qo saldrá en kN
P_total = 250000.0   # <-- CAMBIA ESTE VALOR por tu peso real

# ============================================================
# OPCIÓN DE PERÍODO
# ============================================================
# Si ya tienes el período modal del modelo, usa:
usar_periodo_modal = False
T_modal = 1.20       # s  <-- si usar_periodo_modal = True, este valor se usa

# Si NO tienes el período modal, el script usa:
# T_aprox = N_pisos / 20
# ============================================================


# ============================================================
# FUNCIONES
# ============================================================

def periodo_aproximado(N):
    """
    Período aproximado asumido por criterio del usuario:
    T = N_pisos / 20
    """
    return N / 20.0


def alpha(T, To, p):
    """
    Factor de amplificación espectral alpha(T)
    """
    return (1.0 + 4.5 * (T / To)**p) / (1.0 + (T / To)**3)


def rstar_general(Tstar, To, Ro):
    """
    R* según fórmula general:
    R* = 1 + T* / (0.10*To + T*/Ro)
    """
    return 1.0 + Tstar / (0.10 * To + Tstar / Ro)


def rstar_muros_alternativo(N, To, Ro):
    """
    R* alternativo para edificios estructurados con muros:
    R* = 1 + (N*Ro) / (4*To*Ro + N)
    """
    return 1.0 + (N * Ro) / (4.0 * To * Ro + N)


def coeficiente_sismico_estatico(Tstar, S, Ao_over_g, R, Tprime, n):
    """
    C = (2.75*S*Ao/g / R) * (T'/T*)^n
    Como Ao_over_g = Ao/g, no hace falta usar g explícitamente.
    """
    return (2.75 * S * Ao_over_g / R) * (Tprime / Tstar)**n


def coeficiente_minimo(Ao_over_g, S):
    """
    Cmin = Ao*S / (6g)
    """
    return Ao_over_g * S / 6.0


def coeficiente_maximo(Ao_over_g, S, R):
    """
    Tabla 6.4 para Cmax
    """
    factores = {
        2.0: 0.90,
        3.0: 0.60,
        4.0: 0.55,
        5.5: 0.40,
        6.0: 0.35,
        7.0: 0.35
    }

    if R not in factores:
        raise ValueError(f"No hay factor de Cmax definido para R = {R}")

    return factores[R] * Ao_over_g * S


def espectro_diseno(T_array, S, Ao_over_g, I, Rstar, To, p):
    """
    Sa = (S * Ao/g * alpha(T) * I / R*) * g
    """
    a = alpha(T_array, To, p)
    Sa = ((S * Ao_over_g * a * I) / Rstar) * G
    return Sa


# ============================================================
# CÁLCULO DEL PERÍODO T*
# ============================================================

if usar_periodo_modal:
    Tstar = T_modal
    origen_periodo = "Período modal ingresado por el usuario"
else:
    Tstar = periodo_aproximado(N_pisos)
    origen_periodo = "Período aproximado T = N_pisos / 20"

# ============================================================
# CÁLCULO DE R*
# ============================================================

Rstar_formula_general = rstar_general(Tstar, To, Ro)
Rstar_formula_muros = rstar_muros_alternativo(N_pisos, To, Ro)

# Elegir cuál usar en el espectro
usar_Rstar_muros = False

if usar_Rstar_muros:
    Rstar = Rstar_formula_muros
    origen_rstar = "R* alternativo para edificio con muros"
else:
    Rstar = Rstar_formula_general
    origen_rstar = "R* calculado con la fórmula general usando T*"

# ============================================================
# CÁLCULO DE C, Cmin, Cmax Y CORTE BASAL
# ============================================================

C_calculado = coeficiente_sismico_estatico(Tstar, S, Ao_over_g, R, Tprime, n)
Cmin = coeficiente_minimo(Ao_over_g, S)
Cmax = coeficiente_maximo(Ao_over_g, S, R)

# Aplicación de límites normativos
C_final = max(C_calculado, Cmin)
C_final = min(C_final, Cmax)

Qo = C_final * I * P_total
Qo_min = Cmin * I * P_total
Qo_max = Cmax * I * P_total

# ============================================================
# ESPECTRO DE DISEÑO
# ============================================================

T = np.linspace(0.01, 4.0, 1000)
Sa_m_s2 = espectro_diseno(T, S, Ao_over_g, I, Rstar, To, p)
# Conversión explícita a aceleración espectral en unidades de g
# (numéricamente equivale a Sa/g).
Sa_g = Sa_m_s2 / G

# ============================================================
# RESULTADOS EN PANTALLA
# ============================================================

print("=" * 60)
print("ANTECEDENTES ANÁLISIS SÍSMICO - NCh433")
print("=" * 60)
print(f"Ao/g                = {Ao_over_g:.3f}")
print(f"I                   = {I:.3f}")
print(f"S                   = {S:.3f}")
print(f"To                  = {To:.3f} s")
print(f"T'                  = {Tprime:.3f} s")
print(f"n                   = {n:.3f}")
print(f"p                   = {p:.3f}")
print(f"R                   = {R:.3f}")
print(f"Ro                  = {Ro:.3f}")
print(f"N° pisos            = {N_pisos}")
print(f"Peso sísmico P      = {P_total:,.2f}")
print()

print("-" * 60)
print("PERÍODO")
print("-" * 60)
print(f"Origen de T*        = {origen_periodo}")
print(f"T*                  = {Tstar:.4f} s")
print()

print("-" * 60)
print("FACTOR R*")
print("-" * 60)
print(f"R* (general)        = {Rstar_formula_general:.4f}")
print(f"R* (muros)          = {Rstar_formula_muros:.4f}")
print(f"R* usado            = {Rstar:.4f}")
print(f"Origen R*           = {origen_rstar}")
print()

print("-" * 60)
print("COEFICIENTE SÍSMICO")
print("-" * 60)
print(f"C calculado         = {C_calculado:.4f}")
print(f"Cmin                = {Cmin:.4f}")
print(f"Cmax                = {Cmax:.4f}")
print(f"C final             = {C_final:.4f}")
print()

print("-" * 60)
print("CORTE BASAL")
print("-" * 60)
print(f"Qo mínimo           = {Qo_min:,.2f}")
print(f"Qo máximo           = {Qo_max:,.2f}")
print(f"Qo final            = {Qo:,.2f}")
print("=" * 60)

# ============================================================
# GRÁFICO DEL ESPECTRO DE DISEÑO
# ============================================================

plt.figure(figsize=(10, 6))
plt.plot(T, Sa_g, label='Sa (g)', linewidth=2)
plt.axvline(Tstar, linestyle='--', linewidth=1.5, label=f'T* = {Tstar:.3f} s')
plt.xlabel("Período T (s)")
plt.ylabel("Sa (g)")
plt.title("Espectro de Diseño NCh433")
plt.gca().yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"{y:.2f}"))
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

#guardar figura en misma carpeta del script
plt.savefig("Entrega_1/Codigos/Espectro_diseno.png", dpi=300)
