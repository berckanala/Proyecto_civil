"""
Diseño iterativo de fundaciones bajo MUROS y COLUMNAS, cerrando cada elemento
contra todas las verificaciones antes de pasar al siguiente.

MUROS (zapata corrida, verificación 1D):
  paso B,L -> presión -> corte 1D -> deslizamiento -> flexión -> actualiza

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


def disenar_muro(row):
    esp, Lmuro = row["espesor"], row["Largo"]
    perim = row["Pier"] in PERIMETRALES
    d = D_UTIL
    B_corte = esp + (d if perim else 2 * d)
    B = techo(esp + (HOLGURA_B if perim else 2 * HOLGURA_B))
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
print(out[["ID", "tipo_elem", "B", "L", "combo", "tipo", "N", "M", "e", "comp",
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