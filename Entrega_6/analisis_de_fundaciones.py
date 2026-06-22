"""
Diseño iterativo de fundaciones bajo MUROS y COLUMNAS, cerrando cada elemento
contra todas las verificaciones antes de pasar al siguiente.

MUROS INTERIORES (zapata corrida concéntrica, verificación 1D):
  paso B,L -> presión -> corte 1D -> deslizamiento -> flexión -> actualiza

MUROS PERIMETRALES sobre los ejes H/E/9 (zapata corrida EXCÉNTRICA):
  el muro no puede volar hacia afuera (línea de cierro), de modo que queda en el
  borde exterior de la zapata y el voladizo es sólo hacia adentro (Lv = B - ew).
  La excentricidad geométrica e_B = (B - ew)/2 se combina biaxialmente con la de
  carga e_L = M/N. La presión se evalúa por sección bruta admitiendo tracción
  nominal y se reporta el porcentaje de base comprimida.

COLUMNAS (zapata aislada, verificación BIAXIAL):
  paso B,L -> presión biaxial -> corte 1D (X,Y) + punzonamiento ->
  deslizamiento (Q resultante) -> flexión X/Y -> actualiza

Para columnas se consideran AMBOS sismos (SX y SY) en cada combo; el peor manda.

Unidades: fuerzas tonf, momentos tonf*m, longitudes m -> sigma tonf/m2.
"""
import numpy as np
import pandas as pd

# ===================== ENTRADAS =====================
ARCHIVO_MUROS    = "fuerzas_por_pier.xlsx"
ARCHIVO_COLUMNAS = "fuerzas_por_columna.xlsx"
SALIDA           = "diseno_fundaciones.xlsx"

SIGMA_ADM_EST = 70.0
SIGMA_ADM_DIN = 93.0
FS            = 1.0

GAMMA_SUELO_kN = 18.0
GAMMA_HORM     = 2.5
DF_SELLO       = 2.5

# Muros perimetrales sobre los ejes de cierro H, E y 9 (confirmado del plano de
# arquitectura). P12 quedó como muro INTERIOR (no cae sobre H/E/9) y por lo tanto
# NO entra al diseño excéntrico: se gobierna por la combinación estática C2.
PERIMETRALES = {"P1", "PN", "P13", "Plb"}
DIST_CERCA   = 0.5

FRAC_COMP_MIN = 0.80

H_CIM   = 1.2
RECUB   = 0.05
FC_MPA  = 35.0
PHI_V   = 0.75
FACTOR_CARGA = 1.4
PRESION_NETA = True

MU_ROCE  = 0.4
FSD_MIN  = 1.5

FY_KGF      = 4200.0
PHI_F       = 0.9
SIGMA_TRACC = 8.5
CUANTIA_MIN = 0.0018

HOLGURA_L = 0.30
HOLGURA_B = 0.60
PASO      = 0.05
MAX_IT    = 600
L_MAX_EXTRA = 12.0
B_MAX       = 8.0

# columnas
HOLGURA_COL = 0.30
B_MAX_COL   = 4.0
L_MAX_COL   = 4.0

KERN_LMURO = False
# ====================================================

GT = GAMMA_SUELO_kN / 9.80665
D_UTIL = H_CIM - RECUB
FC_KGF = FC_MPA * 10.19716
VC_STRESS    = 0.53 * np.sqrt(FC_KGF)
VC_STRESS_2D = 1.06 * np.sqrt(FC_KGF)


_trapz = getattr(np, "trapezoid", np.trapz)   # compat numpy>=2.0 / <2.0


def techo(x, paso=PASO):
    return np.ceil(x / paso - 1e-9) * paso


BARRAS = [(8, 0.5027), (10, 0.7854), (12, 1.1310), (16, 2.0106), (18, 2.5447),
          (22, 3.8013), (25, 4.9087), (28, 6.1575), (32, 8.0425), (36, 10.1788)]


def sugerir_barra(As):
    for phi, area in BARRAS:
        s = area / As * 100.0
        if s >= 10.0:
            s_r = min(np.floor(s / 2.5) * 2.5, 25.0)
            return f"phi{phi}@{s_r:.0f}"
    return "phi36@10"


def as_requerida(Mu_tonfm, b_cm, d_cm):
    Mu = Mu_tonfm * 1e5
    a = d_cm / 5.0
    for _ in range(50):
        As = Mu / (PHI_F * FY_KGF * (d_cm - a / 2.0))
        a = As * FY_KGF / (0.85 * FC_KGF * b_cm)
    return As


# ==============================  MUROS  ==============================

def combinaciones_muro(row, B, L):
    S = "SX" if str(row["orientacion"]).strip().upper().startswith("X") else "SY"
    P = lambda c: row[f"{c}Pmin"]
    M = lambda c: row[f"{c}M3max"]
    V = lambda c: row[f"{c}V2max"]
    W = (GT * DF_SELLO + GAMMA_HORM * H_CIM) * B * L
    defs = [
        ("C1",  "est", [("PP", 1.0)]),
        ("C2",  "est", [("PP", 1.0), ("SC", 1.0)]),
        ("C3+", "din", [("PP", 1.0), (S, 1.0)]),
        ("C3-", "din", [("PP", 1.0), (S, -1.0)]),
        ("C4+", "din", [("PP", 1.0), (S, 0.75), ("SC", 0.75)]),
        ("C4-", "din", [("PP", 1.0), (S, -0.75), ("SC", 0.75)]),
    ]
    out = []
    for nombre, tipo, terms in defs:
        Pc = sum(f * P(c) for c, f in terms)
        Mc = sum(f * M(c) for c, f in terms)
        Vc = sum(f * V(c) for c, f in terms)
        fPP = dict(terms).get("PP", 1.0)
        out.append((nombre, tipo, -Pc + fPP * W, Mc, Vc))
    return out


def evaluar_muro(nombre, tipo, N, M, B, L, Lmuro):
    sadm = (SIGMA_ADM_EST if tipo == "est" else SIGMA_ADM_DIN) / FS
    kern = (Lmuro if KERN_LMURO else L) / 6.0
    if N <= 0:
        return dict(combo=nombre, tipo=tipo, N=N, M=M, e=np.inf, kern=kern, tension=True,
                    Lp=0.0, Lp_ok=False, comp=0.0, sigma=np.inf, sadm=sadm, ratio=np.inf,
                    FS_real=0.0, ok=False)
    e = abs(M) / N
    if e <= kern:
        sigma = N / (B * L) * (1 + 6 * e / L)
        tension, Lp, Lp_ok = False, L, True
    else:
        u = L / 2.0 - e
        Lp = 3.0 * u
        Lp_ok = Lp >= FRAC_COMP_MIN * L
        sigma = 2.0 * N / (B * Lp) if Lp > 0 else np.inf
        tension = True
    ok = (sigma <= sadm) and Lp_ok
    return dict(combo=nombre, tipo=tipo, N=N, M=M, e=e, kern=kern, tension=tension,
                Lp=Lp, Lp_ok=Lp_ok, comp=min(Lp / L, 1.0), sigma=sigma, sadm=sadm,
                ratio=sigma / sadm, FS_real=sadm / sigma if sigma > 0 else np.inf, ok=ok)


def peor_presion_muro(row, B, L):
    evs = [evaluar_muro(c[0], c[1], c[2], c[3], B, L, row["Largo"])
           for c in combinaciones_muro(row, B, L)]
    return max(evs, key=lambda d: d["ratio"])


def eval_corte_muro(row, B, L, d, sigma, perim):
    esp = row["espesor"]
    base = (sigma - GT * DF_SELLO) if PRESION_NETA else sigma
    su = max(base, 0.0) * FACTOR_CARGA
    L1 = (B - esp) if perim else (B - esp) / 2.0
    Lc = L1 - d
    bw = L
    phiVc = PHI_V * VC_STRESS * (bw * 100) * (d * 100) / 1000.0
    Vu = su * max(Lc, 0.0) * bw
    ratio = Vu / phiVc if phiVc > 0 else np.inf
    return dict(L1=L1, Lc=max(Lc, 0.0), corta=Lc > 0, Vu=Vu, phiVc=phiVc,
                ratio=ratio, ok=(Vu <= phiVc) if Lc > 0 else True)


def eval_desliz_muro(row, B, L):
    best = (np.inf, "", 0.0, 0.0)
    for nm, tipo, N, M, V in combinaciones_muro(row, B, L):
        Q = abs(V)
        fsd = (MU_ROCE * N / Q) if (Q > 1e-6 and N > 0) else np.inf
        if fsd < best[0]:
            best = (fsd, nm, N, Q)
    return dict(FSD=best[0], combo=best[1], N=best[2], Q=best[3], ok=best[0] >= FSD_MIN)


def eval_flexion_muro(row, B, L, d, sigma, perim):
    esp = row["espesor"]
    sn = max(sigma - GT * DF_SELLO, 0.0)
    Lv = (B - esp) if perim else (B - esp) / 2.0
    M_serv = sn * Lv ** 2 / 2.0
    W = H_CIM ** 2 / 6.0
    sigma_h = (M_serv / W) / 10.0 if W > 0 else 0.0
    parrilla = sigma_h > SIGMA_TRACC
    As_min = CUANTIA_MIN * 100.0 * (H_CIM * 100.0)
    if parrilla:
        Mu = sn * FACTOR_CARGA * Lv ** 2 / 2.0
        As_flex = as_requerida(Mu, 100.0, d * 100.0)
        As = max(As_flex, As_min)
        barra_p = sugerir_barra(As)
        barra_s = "phi10@20"
    else:
        As = As_min
        barra_p = sugerir_barra(As_min)
        barra_s = sugerir_barra(As_min)
    return dict(Lv=Lv, M_serv=M_serv, sigma_h=sigma_h, parrilla=parrilla,
                As_min=As_min, As=round(As, 2), barra_ppal=barra_p, barra_sec=barra_s)


# =================  MUROS PERIMETRALES (EXCÉNTRICOS)  =================
# El muro queda en el borde exterior de la zapata (línea de cierro). En la
# dirección transversal B la resultante se desplaza una excentricidad geométrica
# e_B = (B - ew)/2 respecto del centro de la zapata, que se combina con la
# excentricidad de carga longitudinal e_L = M/N. La presión se obtiene por
# sección bruta (se admite tracción nominal y se reporta el % comprimido).

def _dist_presion_perim(N, M, B, L, ew):
    """Presión neta lineal transversal por sección bruta.
    Devuelve (q, e_B, e_L, sigma_out, sigma_in) en tonf/m2, con x=0 en el borde
    exterior (bajo el muro) y x=B en la punta interior del voladizo."""
    eB = (B - ew) / 2.0          # geométrica, transversal
    eL = abs(M) / N              # de carga, longitudinal (plano del muro)
    q = N / (B * L)
    sigma_out = q * (1 + 6 * eB / B + 6 * eL / L)   # esquina más cargada (borde)
    sigma_in = q * (1 - 6 * eB / B - 6 * eL / L)    # esquina opuesta (punta int.)
    return q, eB, eL, sigma_out, sigma_in


def evaluar_muro_perim(nombre, tipo, N, M, B, L, ew):
    sadm = (SIGMA_ADM_EST if tipo == "est" else SIGMA_ADM_DIN) / FS
    if N <= 0:
        return dict(combo=nombre, tipo=tipo, N=N, M=M, e=np.inf, eB=np.inf, eL=np.inf,
                    tension=True, comp=0.0, sigma=np.inf, sadm=sadm, ratio=np.inf,
                    FS_real=0.0, ok=False)
    q, eB, eL, s_out, s_in = _dist_presion_perim(N, M, B, L, ew)
    sigma = s_out
    if s_in >= 0:
        comp = 1.0
    else:
        comp = sigma / (sigma - s_in)     # fracción comprimida (esquina a esquina)
    ok = sigma <= sadm
    return dict(combo=nombre, tipo=tipo, N=N, M=M, e=eB, eB=eB, eL=eL,
                tension=s_in < 0, comp=min(comp, 1.0), sigma=sigma, sadm=sadm,
                ratio=sigma / sadm, FS_real=sadm / sigma if sigma > 0 else np.inf, ok=ok)


def peor_presion_muro_perim(row, B, L):
    ew = row["espesor"]
    evs = [evaluar_muro_perim(c[0], c[1], c[2], c[3], B, L, ew)
           for c in combinaciones_muro(row, B, L)]
    return max(evs, key=lambda d: d["ratio"])


def eval_corte_muro_perim(N, M, B, L, ew, d):
    """Corte 1D en la sección crítica a d de la cara interior del muro,
    integrando la presión neta positiva real del voladizo interior."""
    q, eB, eL, s_out, s_in = _dist_presion_perim(N, M, B, L, ew)
    over = GT * DF_SELLO if PRESION_NETA else 0.0
    bw = L
    phiVc = PHI_V * VC_STRESS * (bw * 100) * (d * 100) / 1000.0
    x0 = ew + d                       # sección crítica
    L1 = B - ew                       # voladizo interior total
    Lc = max(B - x0, 0.0)
    if Lc <= 0:
        return dict(L1=L1, Lc=0.0, Vu=0.0, phiVc=phiVc, ratio=0.0, ok=True)
    xs = np.linspace(x0, B, 1000)
    sx = np.clip((s_out + (s_in - s_out) * xs / B) - over, 0.0, None)
    Vu = _trapz(sx, xs) * FACTOR_CARGA * bw
    ratio = Vu / phiVc if phiVc > 0 else np.inf
    return dict(L1=L1, Lc=Lc, Vu=Vu, phiVc=phiVc, ratio=ratio, ok=Vu <= phiVc)


def eval_flexion_muro_perim(N, M, B, L, ew, d):
    """Flexión del voladizo interior (Lv = B - ew, un solo lado) bajo la presión
    neta real (trapezoidal, sin contribución donde la base despega)."""
    q, eB, eL, s_out, s_in = _dist_presion_perim(N, M, B, L, ew)
    over = GT * DF_SELLO if PRESION_NETA else 0.0
    Lv = B - ew
    xs = np.linspace(ew, B, 2000)
    sx = np.clip((s_out + (s_in - s_out) * xs / B) - over, 0.0, None)
    arm = xs - ew                     # brazo respecto a la cara interior del muro
    M_serv = _trapz(sx * arm, xs)   # tonf*m/m (servicio)
    Mu = M_serv * FACTOR_CARGA
    W = H_CIM ** 2 / 6.0
    sigma_h = (M_serv / W) / 10.0 if W > 0 else 0.0
    parrilla = sigma_h > SIGMA_TRACC
    As_min = CUANTIA_MIN * 100.0 * (H_CIM * 100.0)
    if parrilla:
        As_flex = as_requerida(Mu, 100.0, d * 100.0)
        As = max(As_flex, As_min)
        barra_p = sugerir_barra(As)
        barra_s = "phi10@20"
    else:
        As = As_min
        barra_p = sugerir_barra(As_min)
        barra_s = sugerir_barra(As_min)
    return dict(Lv=Lv, M_serv=M_serv, sigma_h=sigma_h, parrilla=parrilla,
                As_min=As_min, As=round(As, 2), barra_ppal=barra_p, barra_sec=barra_s)


def disenar_muro_perimetral(row, esp, Lmuro, d):
    # L = largo del muro (se mantiene); B crece sólo hacia adentro para cumplir
    # deslizamiento y presión.
    L = techo(Lmuro + HOLGURA_L)
    B = techo(esp + HOLGURA_B)

    it = 0
    while it < MAX_IT:
        pres = peor_presion_muro_perim(row, B, L)
        cor = eval_corte_muro_perim(pres["N"], pres["M"], B, L, esp, d)
        des = eval_desliz_muro(row, B, L)
        if pres["ok"] and cor["ok"] and des["ok"]:
            break
        B += PASO                     # ensanche hacia adentro
        if B > B_MAX:
            break
        it += 1

    pres = peor_presion_muro_perim(row, B, L)
    cor = eval_corte_muro_perim(pres["N"], pres["M"], B, L, esp, d)
    des = eval_desliz_muro(row, B, L)
    fle = eval_flexion_muro_perim(pres["N"], pres["M"], B, L, esp, d)

    cx, cy = (row["xi"] + row["xf"]) / 2.0, (row["yi"] + row["yf"]) / 2.0
    return dict(
        ID=row["Pier"], tipo_elem="muro", perimetral=True, bx=esp, by=esp,
        Largo=Lmuro, B=round(B, 3), L=round(L, 3), area=round(B * L, 3), H=H_CIM,
        combo=pres["combo"], tipo=pres["tipo"], N=round(pres["N"], 1), M=round(pres["M"], 1),
        e=round(pres["eB"], 3), comp=round(pres["comp"] * 100, 1),
        sigma=round(pres["sigma"], 2), sigma_adm=round(pres["sadm"], 1),
        FS_real=round(pres["FS_real"], 3), OK_pres=pres["ok"],
        L1=round(cor["L1"], 3), Lc=round(cor["Lc"], 3),
        Vu=round(cor["Vu"], 1), phiVc=round(cor["phiVc"], 1),
        ratio_V=round(cor["ratio"], 3), OK_corte=cor["ok"],
        OK_punz=True, ratio_pz=0.0,
        Q=round(des["Q"], 1), FSD=round(des["FSD"], 3), OK_desl=des["ok"],
        combo_desl=des["combo"],
        Lv=round(fle["Lv"], 3), sigma_h=round(fle["sigma_h"], 2), parrilla=fle["parrilla"],
        As=fle["As"], barra_ppal=fle["barra_ppal"], barra_sec=fle["barra_sec"],
        iters=it,
        orientacion=row["orientacion"], cx=cx, cy=cy,
        xi=row["xi"], yi=row["yi"], xf=row["xf"], yf=row["yf"],
    )


def disenar_muro(row):
    esp, Lmuro = row["espesor"], row["Largo"]
    perim = row["Pier"] in PERIMETRALES
    d = D_UTIL
    if perim:
        return disenar_muro_perimetral(row, esp, Lmuro, d)

    B_corte = esp + 2 * d
    B = techo(esp + 2 * HOLGURA_B)
    L = techo(Lmuro + HOLGURA_L)

    it = 0
    while it < MAX_IT:
        pres = peor_presion_muro(row, B, L)
        cor = eval_corte_muro(row, B, L, d, pres["sigma"], perim)
        des = eval_desliz_muro(row, B, L)
        if pres["ok"] and cor["ok"] and des["ok"]:
            break
        if pres["tension"] or not pres["Lp_ok"]:
            L += PASO
        elif not cor["ok"]:
            L += PASO
        elif not pres["ok"]:
            if B < B_corte - 1e-9:
                B += PASO
            else:
                L += PASO
        elif not des["ok"]:
            B += PASO
        if (L - Lmuro) > L_MAX_EXTRA or B > B_MAX:
            break
        it += 1

    pres = peor_presion_muro(row, B, L)
    cor = eval_corte_muro(row, B, L, d, pres["sigma"], perim)
    des = eval_desliz_muro(row, B, L)
    fle = eval_flexion_muro(row, B, L, d, pres["sigma"], perim)

    cx, cy = (row["xi"] + row["xf"]) / 2.0, (row["yi"] + row["yf"]) / 2.0
    return dict(
        ID=row["Pier"], tipo_elem="muro", perimetral=perim, bx=esp, by=esp,
        Largo=Lmuro, B=round(B, 3), L=round(L, 3), area=round(B * L, 3), H=H_CIM,
        combo=pres["combo"], tipo=pres["tipo"], N=round(pres["N"], 1), M=round(pres["M"], 1),
        e=round(pres["e"], 3), comp=round(pres["comp"] * 100, 1),
        sigma=round(pres["sigma"], 2), sigma_adm=round(pres["sadm"], 1),
        FS_real=round(pres["FS_real"], 3), OK_pres=pres["ok"],
        L1=round(cor["L1"], 3), Lc=round(cor["Lc"], 3),
        Vu=round(cor["Vu"], 1), phiVc=round(cor["phiVc"], 1),
        ratio_V=round(cor["ratio"], 3), OK_corte=cor["ok"],
        OK_punz=True, ratio_pz=0.0,
        Q=round(des["Q"], 1), FSD=round(des["FSD"], 3), OK_desl=des["ok"],
        combo_desl=des["combo"],
        Lv=round(fle["Lv"], 3), sigma_h=round(fle["sigma_h"], 2), parrilla=fle["parrilla"],
        As=fle["As"], barra_ppal=fle["barra_ppal"], barra_sec=fle["barra_sec"],
        iters=it,
        orientacion=row["orientacion"], cx=cx, cy=cy,
        xi=row["xi"], yi=row["yi"], xf=row["xf"], yf=row["yf"],
    )


# ============================  COLUMNAS  =============================

def combinaciones_columna(row, B, L):
    P  = lambda c: row[f"{c}Pmin"]
    M2 = lambda c: row[f"{c}M2max"]
    M3 = lambda c: row[f"{c}M3max"]
    V2 = lambda c: row[f"{c}V2max"]
    V3 = lambda c: row[f"{c}V3max"]
    W = (GT * DF_SELLO + GAMMA_HORM * H_CIM) * B * L
    defs = [("C1",  "est", [("PP", 1.0)]),
            ("C2",  "est", [("PP", 1.0), ("SC", 1.0)])]
    for S in ["SX", "SY"]:
        defs.append((f"C3+{S}", "din", [("PP", 1.0), (S,  1.0)]))
        defs.append((f"C3-{S}", "din", [("PP", 1.0), (S, -1.0)]))
        defs.append((f"C4+{S}", "din", [("PP", 1.0), (S,  0.75), ("SC", 0.75)]))
        defs.append((f"C4-{S}", "din", [("PP", 1.0), (S, -0.75), ("SC", 0.75)]))
    out = []
    for nombre, tipo, terms in defs:
        Pc  = sum(f * P(c)  for c, f in terms)
        Mc3 = sum(f * M3(c) for c, f in terms)
        Mc2 = sum(f * M2(c) for c, f in terms)
        Vc2 = sum(f * V2(c) for c, f in terms)
        Vc3 = sum(f * V3(c) for c, f in terms)
        fPP = dict(terms).get("PP", 1.0)
        out.append((nombre, tipo, -Pc + fPP * W, Mc3, Mc2, Vc2, Vc3))
    return out


def presion_biaxial(N, Mx, My, B, L):
    if N <= 0:
        return np.inf, np.inf, np.inf, 0.0
    ex = abs(Mx) / N
    ey = abs(My) / N
    if ex / B + ey / L <= 1.0 / 6.0:
        sigma = N / (B * L) * (1 + 6 * ex / B + 6 * ey / L)
        return sigma, ex, ey, 100.0
    if ex > B / 6:
        u = B / 2 - ex; Bp = 3 * u
        sx = 2 * N / (Bp * L) if Bp > 0 else np.inf
        compx = Bp / B
    else:
        sx = N / (B * L) * (1 + 6 * ex / B); compx = 1.0
    if ey > L / 6:
        u = L / 2 - ey; Lp = 3 * u
        sy = 2 * N / (B * Lp) if Lp > 0 else np.inf
        compy = Lp / L
    else:
        sy = N / (B * L) * (1 + 6 * ey / L); compy = 1.0
    return max(sx, sy), ex, ey, min(compx, compy) * 100.0


def peor_presion_columna(row, B, L):
    worst = None
    for nm, tipo, N, M3, M2, V2, V3 in combinaciones_columna(row, B, L):
        sadm = (SIGMA_ADM_EST if tipo == "est" else SIGMA_ADM_DIN) / FS
        sigma, ex, ey, comp = presion_biaxial(N, M3, M2, B, L)
        ratio = sigma / sadm
        ok = (sigma <= sadm) and (comp >= FRAC_COMP_MIN * 100.0)
        d = dict(combo=nm, tipo=tipo, N=N, Mx=M3, My=M2, Vx=V2, Vy=V3,
                 sigma=sigma, sadm=sadm, ex=ex, ey=ey, comp=comp,
                 ratio=ratio, ok=ok)
        if worst is None or ratio > worst["ratio"]:
            worst = d
    return worst


def eval_corte_1d_col(B, L, esp_x, esp_y, d, sigma):
    base = (sigma - GT * DF_SELLO) if PRESION_NETA else sigma
    su = max(base, 0.0) * FACTOR_CARGA
    L1x = (B - esp_x) / 2.0;  Lcx = max(L1x - d, 0.0)
    Vux = su * Lcx * L
    phiVcx = PHI_V * VC_STRESS * (L * 100) * (d * 100) / 1000.0
    rx = Vux / phiVcx if phiVcx > 0 else np.inf
    L1y = (L - esp_y) / 2.0;  Lcy = max(L1y - d, 0.0)
    Vuy = su * Lcy * B
    phiVcy = PHI_V * VC_STRESS * (B * 100) * (d * 100) / 1000.0
    ry = Vuy / phiVcy if phiVcy > 0 else np.inf
    if rx >= ry:
        return dict(eje="X", L1=L1x, Lc=Lcx, Vu=Vux, phiVc=phiVcx, ratio=rx, ok=rx <= 1)
    return dict(eje="Y", L1=L1y, Lc=Lcy, Vu=Vuy, phiVc=phiVcy, ratio=ry, ok=ry <= 1)


def eval_punzonamiento(B, L, esp_x, esp_y, d, N, sigma):
    base = (sigma - GT * DF_SELLO) if PRESION_NETA else sigma
    qu_neta = max(base, 0.0) * FACTOR_CARGA
    Pu = N * FACTOR_CARGA
    bx = esp_x + d
    by = esp_y + d
    bo = 2.0 * (bx + by)
    A_crit = bx * by
    Vu = max(Pu - qu_neta * A_crit, 0.0)
    phiVc = PHI_V * VC_STRESS_2D * (bo * 100) * (d * 100) / 1000.0
    ratio = Vu / phiVc if phiVc > 0 else np.inf
    return dict(bo=bo, Vu=Vu, phiVc=phiVc, ratio=ratio, ok=Vu <= phiVc)


def eval_desliz_columna(row, B, L):
    best = (np.inf, "", 0.0, 0.0)
    for nm, tipo, N, M3, M2, V2, V3 in combinaciones_columna(row, B, L):
        Q = np.sqrt(V2 ** 2 + V3 ** 2)
        fsd = (MU_ROCE * N / Q) if (Q > 1e-6 and N > 0) else np.inf
        if fsd < best[0]:
            best = (fsd, nm, N, Q)
    return dict(FSD=best[0], combo=best[1], N=best[2], Q=best[3], ok=best[0] >= FSD_MIN)


def eval_flexion_columna(B, L, esp_x, esp_y, d, sigma):
    sn = max(sigma - GT * DF_SELLO, 0.0)
    Lvx = (B - esp_x) / 2.0
    Lvy = (L - esp_y) / 2.0
    W = H_CIM ** 2 / 6.0
    As_min = CUANTIA_MIN * 100.0 * (H_CIM * 100.0)

    def ramo(Lv):
        M_serv = sn * Lv ** 2 / 2.0
        sigma_h = (M_serv / W) / 10.0 if W > 0 else 0.0
        parrilla = sigma_h > SIGMA_TRACC
        if parrilla:
            Mu = sn * FACTOR_CARGA * Lv ** 2 / 2.0
            As_flex = as_requerida(Mu, 100.0, d * 100.0)
            As = max(As_flex, As_min)
        else:
            As = As_min
        return dict(Lv=Lv, sigma_h=sigma_h, parrilla=parrilla, As=As, barra=sugerir_barra(As))

    rx, ry = ramo(Lvx), ramo(Lvy)
    return dict(Lv_x=rx["Lv"], sigma_h_x=rx["sigma_h"], parr_x=rx["parrilla"],
                As_x=rx["As"], barra_x=rx["barra"],
                Lv_y=ry["Lv"], sigma_h_y=ry["sigma_h"], parr_y=ry["parrilla"],
                As_y=ry["As"], barra_y=ry["barra"])


def disenar_columna(row):
    esp_x, esp_y = row["bx"], row["by"]
    d = D_UTIL
    B = techo(esp_x + 2 * HOLGURA_COL)
    L = techo(esp_y + 2 * HOLGURA_COL)
    Bx_corte = esp_x + 2 * d
    Ly_corte = esp_y + 2 * d

    it = 0
    while it < MAX_IT:
        pres = peor_presion_columna(row, B, L)
        cor  = eval_corte_1d_col(B, L, esp_x, esp_y, d, pres["sigma"])
        pun  = eval_punzonamiento(B, L, esp_x, esp_y, d, pres["N"], pres["sigma"])
        des  = eval_desliz_columna(row, B, L)
        if pres["ok"] and cor["ok"] and pun["ok"] and des["ok"]:
            break
        if pres["comp"] < FRAC_COMP_MIN * 100.0:
            if pres["ex"] >= pres["ey"]:
                B += PASO
            else:
                L += PASO
        elif not pres["ok"]:
            if B <= L:
                B += PASO
            else:
                L += PASO
        elif not cor["ok"]:
            if cor["eje"] == "X" and B < Bx_corte - 1e-9:
                B += PASO
            elif cor["eje"] == "Y" and L < Ly_corte - 1e-9:
                L += PASO
            else:
                if B <= L: L += PASO
                else:      B += PASO
        elif not pun["ok"]:
            B += PASO; L += PASO
        elif not des["ok"]:
            if B <= L: B += PASO
            else:      L += PASO
        if B > B_MAX_COL or L > L_MAX_COL:
            break
        it += 1

    pres = peor_presion_columna(row, B, L)
    cor  = eval_corte_1d_col(B, L, esp_x, esp_y, d, pres["sigma"])
    pun  = eval_punzonamiento(B, L, esp_x, esp_y, d, pres["N"], pres["sigma"])
    des  = eval_desliz_columna(row, B, L)
    fle  = eval_flexion_columna(B, L, esp_x, esp_y, d, pres["sigma"])

    # ramo más cargado va como principal, el otro como secundaria
    if fle["As_x"] >= fle["As_y"]:
        As_main, barra_p, barra_s = fle["As_x"], fle["barra_x"], fle["barra_y"]
    else:
        As_main, barra_p, barra_s = fle["As_y"], fle["barra_y"], fle["barra_x"]

    return dict(
        ID=row["Column"], tipo_elem="columna", perimetral=False,
        bx=esp_x, by=esp_y, Largo=np.nan,
        B=round(B, 3), L=round(L, 3), area=round(B * L, 3), H=H_CIM,
        combo=pres["combo"], tipo=pres["tipo"], N=round(pres["N"], 1),
        M=round(pres["Mx"], 2),
        e=round(max(pres["ex"], pres["ey"]), 3),
        comp=round(pres["comp"], 1),
        sigma=round(pres["sigma"], 2), sigma_adm=round(pres["sadm"], 1),
        FS_real=round(pres["sadm"] / pres["sigma"], 3) if pres["sigma"] > 0 else np.inf,
        OK_pres=pres["ok"],
        L1=round(cor["L1"], 3), Lc=round(cor["Lc"], 3),
        Vu=round(cor["Vu"], 2), phiVc=round(cor["phiVc"], 2),
        ratio_V=round(cor["ratio"], 3), OK_corte=cor["ok"],
        OK_punz=pun["ok"], ratio_pz=round(pun["ratio"], 3),
        Q=round(des["Q"], 2), FSD=round(des["FSD"], 3), OK_desl=des["ok"],
        combo_desl=des["combo"],
        Lv=round(max(fle["Lv_x"], fle["Lv_y"]), 3),
        sigma_h=round(max(fle["sigma_h_x"], fle["sigma_h_y"]), 2),
        parrilla=fle["parr_x"] or fle["parr_y"],
        As=round(As_main, 2), barra_ppal=barra_p, barra_sec=barra_s,
        iters=it,
        orientacion="--", cx=row["x"], cy=row["y"],
        xi=row["x"] - esp_x / 2, yi=row["y"] - esp_y / 2,
        xf=row["x"] + esp_x / 2, yf=row["y"] + esp_y / 2,
    )


# ======================  GEOMETRÍA EN PLANTA  =======================

def footprint(r):
    cx, cy = r["cx"], r["cy"]
    B, L = r["B"], r["L"]
    if r["tipo_elem"] == "muro":
        if str(r["orientacion"]).strip().upper().startswith("X"):
            return cx - L / 2, cx + L / 2, cy - B / 2, cy + B / 2
        return cx - B / 2, cx + B / 2, cy - L / 2, cy + L / 2
    return cx - B / 2, cx + B / 2, cy - L / 2, cy + L / 2


def luz(a, b):
    dx = max(0.0, a[0] - b[1], b[0] - a[1])
    dy = max(0.0, a[2] - b[3], b[2] - a[3])
    return (dx ** 2 + dy ** 2) ** 0.5


# ====================  FOSO DEL ASCENSOR (TAREA C)  ==================
# Losa de fondo de foso de ascensor a profundidad H_FOSO, modelada como placa
# rectangular apoyada en sus cuatro bordes (los muros de la caja). Se diseña por
# los momentos de placa bajo: empuje de suelo sobre los muros del foso, peso
# propio y reacción del ascensor. El espesor se verifica por corte sin armadura
# de corte, con el mismo criterio (vc = 0,53*sqrt(f'c)) que las zapatas.
#
# ---------------------------------------------------------------------------
# TODO (PEDRO): DATOS DEL PLANO / CATÁLOGO — NO INVENTAR
#   FOSO_B  = <ancho menor de la caja, m>          # p.ej. dos cajas de ascensor
#   FOSO_L  = <ancho mayor de la caja, m>
#   R_ASC   = <reacción de impacto del ascensor, tonf  (valor de catálogo)>
# Mientras falten, el cálculo queda parametrizado y se reporta como TODO.
# ---------------------------------------------------------------------------
FOSO_B   = None     # TODO PEDRO: ancho menor de la losa de foso [m]
FOSO_L   = None     # TODO PEDRO: ancho mayor de la losa de foso [m]
H_FOSO   = 1.5      # profundidad del foso [m] (dato del enunciado)
ESP_FOSO = 0.30     # espesor de prueba de la losa de fondo [m]
R_ASC    = None     # TODO PEDRO: reacción del ascensor [tonf] (catálogo)


def coef_placa_4bordes(rel):
    """Coeficiente de momento alpha para placa rectangular simplemente apoyada en
    4 bordes con carga uniforme, M = alpha * q * lx^2 (lx = luz menor).
    Tabla clásica (Timoshenko, nu=0,2) interpolada por relación ly/lx."""
    tabla = {1.0: 0.0479, 1.1: 0.0554, 1.2: 0.0627, 1.3: 0.0694, 1.4: 0.0755,
             1.5: 0.0812, 1.6: 0.0862, 1.7: 0.0908, 1.8: 0.0948, 1.9: 0.0985,
             2.0: 0.1017, 3.0: 0.1189, 1e9: 0.1250}
    ks = sorted(tabla)
    rel = max(1.0, rel)
    for i in range(len(ks) - 1):
        if rel <= ks[i + 1]:
            x0, x1 = ks[i], ks[i + 1]
            return tabla[x0] + (tabla[x1] - tabla[x0]) * (rel - x0) / (x1 - x0)
    return 0.125


def disenar_foso(b=FOSO_B, l=FOSO_L, h_foso=H_FOSO, esp=ESP_FOSO, r_asc=R_ASC):
    d = esp - RECUB
    # Carga de diseño sobre la losa de fondo (hacia arriba domina la subpresión/
    # empuje de suelo; hacia abajo, peso propio + reacción del ascensor).
    faltan = [n for n, v in [("FOSO_B", b), ("FOSO_L", l), ("R_ASC", r_asc)] if v is None]
    if faltan:
        print("\n=== FOSO DE ASCENSOR (TAREA C) ===")
        print("  TODO PEDRO: faltan datos del plano/catálogo -> " + ", ".join(faltan))
        print("  Cálculo parametrizado listo; al cargar los datos se obtiene la losa.")
        return None
    lx, ly = min(b, l), max(b, l)
    rel = ly / lx
    q_pp = GAMMA_HORM * esp                       # peso propio losa [tonf/m2]
    q_suelo = GT * h_foso                          # empuje vertical de suelo [tonf/m2]
    q_asc = r_asc / (b * l)                        # reacción ascensor repartida
    qu = FACTOR_CARGA * (q_pp + q_suelo + q_asc)
    alpha = coef_placa_4bordes(rel)
    Mu = alpha * qu * lx ** 2                       # tonf*m/m
    As = max(as_requerida(Mu, 100.0, d * 100.0),
             CUANTIA_MIN * 100.0 * (esp * 100.0))
    # Corte 1D sin armadura de corte (sección a d del borde)
    Vu = qu * (lx / 2.0 - d)
    phiVc = PHI_V * VC_STRESS * (100.0) * (d * 100.0) / 1000.0
    ok_corte = Vu <= phiVc
    print("\n=== FOSO DE ASCENSOR (TAREA C) ===")
    print(f"  lx={lx:.2f} ly={ly:.2f} rel={rel:.2f} esp={esp:.2f} d={d:.2f}")
    print(f"  qu={qu:.2f} tonf/m2 | alpha={alpha:.4f} | Mu={Mu:.2f} tonf*m/m | As={As:.2f} cm2/m -> {sugerir_barra(As)}")
    print(f"  Corte: Vu={Vu:.2f} phiVc={phiVc:.2f} -> {'OK' if ok_corte else 'AUMENTAR ESPESOR'}")
    return dict(lx=lx, ly=ly, rel=rel, esp=esp, d=d, qu=qu, alpha=alpha,
                Mu=Mu, As=As, barra=sugerir_barra(As), Vu=Vu, phiVc=phiVc, ok_corte=ok_corte)


# ===========================  EJECUCIÓN  =============================

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)
pd.set_option("display.float_format", lambda x: f"{x:.3f}")

df_m = pd.read_excel(ARCHIVO_MUROS)
res_muros = [disenar_muro(r) for _, r in df_m.iterrows()]

df_c = pd.read_excel(ARCHIVO_COLUMNAS)
res_cols = [disenar_columna(r) for _, r in df_c.iterrows()]

out = pd.DataFrame(res_muros + res_cols)
out.to_excel(SALIDA, index=False)

print(f"H={H_CIM} m | f'c={FC_MPA} MPa | sigma_adm {SIGMA_ADM_EST}/{SIGMA_ADM_DIN} | "
      f"FS_pres={FS} | FSD>={FSD_MIN} (mu={MU_ROCE}) | d={D_UTIL:.2f} m")
print(f"vc 1D = {VC_STRESS:.2f} kgf/cm2 | vc punz = {VC_STRESS_2D:.2f} kgf/cm2")
print(f"Muros: {len(res_muros)} | Columnas: {len(res_cols)}\n")

print("=== PRESIÓN ===")
print(out[["ID", "tipo_elem", "perimetral", "B", "L", "combo", "tipo", "N", "M", "e", "comp",
           "sigma", "sigma_adm", "FS_real", "OK_pres", "iters"]].to_string(index=False))

print("\n=== CORTE 1D ===")
print(out[["ID", "tipo_elem", "B", "L", "L1", "Lc",
           "Vu", "phiVc", "ratio_V", "OK_corte"]].to_string(index=False))

col_mask = out["tipo_elem"] == "columna"
if col_mask.any():
    print("\n=== PUNZONAMIENTO (sólo columnas) ===")
    print(out.loc[col_mask, ["ID", "ratio_pz", "OK_punz"]].to_string(index=False))

print("\n=== DESLIZAMIENTO ===")
print(out[["ID", "tipo_elem", "combo_desl", "N", "Q", "FSD", "OK_desl"]].to_string(index=False))

print(f"\n=== FLEXIÓN / PARRILLAS  (As_min = 0.0018*b*H = {CUANTIA_MIN*100*H_CIM*100:.1f} cm2/m) ===")
print(out[["ID", "tipo_elem", "Lv", "sigma_h", "parrilla", "As",
           "barra_ppal", "barra_sec"]].to_string(index=False))

print("\n=== MUROS PERIMETRALES EXCÉNTRICOS (ejes H/E/9) ===")
mp = out[out["perimetral"] == True]
print(mp[["ID", "B", "L", "e", "comp", "sigma", "sigma_adm", "FS_real",
          "Vu", "ratio_V", "Lv", "sigma_h", "parrilla", "As", "FSD"]].to_string(index=False))

print("\n=== CHEQUEO FINAL ===")
out["TODO_OK"] = out["OK_pres"] & out["OK_corte"] & out["OK_punz"] & out["OK_desl"]
print(f"  Presión:        {out['OK_pres'].sum()}/{len(out)}")
print(f"  Corte 1D:       {out['OK_corte'].sum()}/{len(out)}")
print(f"  Punzonamiento:  {out['OK_punz'].sum()}/{len(out)}  (sólo aplica a columnas)")
print(f"  Deslizamiento:  {out['OK_desl'].sum()}/{len(out)}")
print(f"  TODO OK:        {out['TODO_OK'].sum()}/{len(out)}")
for _, r in out[~out["TODO_OK"]].iterrows():
    falla = []
    if not r["OK_pres"]:  falla.append("presión")
    if not r["OK_corte"]: falla.append("corte")
    if not r["OK_punz"]:  falla.append("punzonamiento")
    if not r["OK_desl"]:  falla.append("deslizamiento")
    print(f"    {r['ID']:8} ({r['tipo_elem']}) -> {', '.join(falla)}")
out.to_excel(SALIDA, index=False)

rects = {r["ID"]: footprint(r) for _, r in out.iterrows()}
ids = list(rects)
print(f"\n=== FUNDACIONES CERCANAS A CADA UNA (luz < {DIST_CERCA} m) ===")
for p in ids:
    vec = []
    for q in ids:
        if q == p:
            continue
        dd = luz(rects[p], rects[q])
        if dd < DIST_CERCA:
            vec.append(f"{q}({dd:.2f})")
    print(f"  {p:8}: {', '.join(vec) if vec else 'sin vecinas'}")

# Foso del ascensor (Tarea C) — parametrizado; corre con TODO hasta cargar datos.
disenar_foso()
