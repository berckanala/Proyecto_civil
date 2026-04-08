"""Espectro de diseno NCh433 para el Grupo 1.

Ejecutar:
    python espectro_nch433.py
"""

from __future__ import annotations

from dataclasses import dataclass

import matplotlib.pyplot as plt


@dataclass(frozen=True)
class SoilSpectrumParameters:
    soil_type: str
    S: float
    T0_s: float
    T_prime_s: float
    n: float
    p: float


@dataclass(frozen=True)
class ProjectSeismicData:
    city: str
    seismic_zone: int
    occupation_category: str
    importance_factor: float
    soil: SoilSpectrumParameters
    structural_system: str
    floors: int
    total_seismic_weight_tf: float
    dominant_period_s: float
    R: float
    R0: float


@dataclass(frozen=True)
class SpectrumPoint:
    period_s: float
    alpha: float
    sa_elastic_g: float
    sa_design_g: float


SOIL_A = SoilSpectrumParameters(
    soil_type="A",
    S=0.90,
    T0_s=0.15,
    T_prime_s=0.20,
    n=1.00,
    p=2.0,
)

PROJECT = ProjectSeismicData(
    city="Antofagasta, Chile",
    seismic_zone=3,
    occupation_category="II",
    importance_factor=1.0,
    soil=SOIL_A,
    structural_system="Muros de hormigon armado",
    floors=21,
    total_seismic_weight_tf=8766.65,
    dominant_period_s=1.05,
    R=7.0,
    R0=11.0,
)

COURSE_DESIGN_COEFFICIENT = 0.10


def a0_over_g(seismic_zone: int) -> float:
    values = {1: 0.20, 2: 0.30, 3: 0.40}
    if seismic_zone not in values:
        raise ValueError(f"Zona sismica no soportada: {seismic_zone}")
    return values[seismic_zone]


def cmax_multiplier(R: float) -> float:
    values = {2.0: 0.90, 3.0: 0.60, 4.0: 0.55, 5.5: 0.40, 6.0: 0.35, 7.0: 0.35}
    key = round(R, 2)
    if key not in values:
        raise ValueError(f"R={R} no esta tabulado en Tabla 6.4.")
    return values[key]


def alpha_nch433(period_s: float, soil: SoilSpectrumParameters) -> float:
    ratio = period_s / soil.T0_s
    numerator = 1.0 + 4.5 * ratio**soil.p
    denominator = 1.0 + ratio**3.0
    return numerator / denominator


def r_star(period_s: float, soil: SoilSpectrumParameters, R0: float) -> float:
    return 1.0 + period_s / (0.10 * soil.T0_s + period_s / R0)


def sa_elastic_over_g(period_s: float, project: ProjectSeismicData) -> float:
    return (
        project.importance_factor
        * project.soil.S
        * a0_over_g(project.seismic_zone)
        * alpha_nch433(period_s, project.soil)
    )


def sa_design_over_g(period_s: float, project: ProjectSeismicData) -> float:
    return sa_elastic_over_g(period_s, project) / r_star(
        project.dominant_period_s,
        project.soil,
        project.R0,
    )


def static_coefficients(project: ProjectSeismicData) -> dict[str, float]:
    a0_g = a0_over_g(project.seismic_zone)
    c_raw = (
        2.75
        * project.soil.S
        * a0_g
        / project.R
        * (project.soil.T_prime_s / project.dominant_period_s) ** project.soil.n
    )
    c_min = project.soil.S * a0_g / 6.0
    c_max = cmax_multiplier(project.R) * project.soil.S * a0_g
    c_used = min(max(c_raw, c_min), c_max)
    return {
        "C_raw": c_raw,
        "C_min": c_min,
        "C_max": c_max,
        "C_used": c_used,
    }


def q_limits(project: ProjectSeismicData) -> dict[str, float]:
    coeffs = static_coefficients(project)
    qmin_coeff = project.importance_factor * coeffs["C_min"]
    qmax_coeff = project.importance_factor * coeffs["C_max"]
    return {
        "Qmin_tf": qmin_coeff * project.total_seismic_weight_tf,
        "Qmax_tf": qmax_coeff * project.total_seismic_weight_tf,
    }


def course_base_shear(project: ProjectSeismicData) -> float:
    return COURSE_DESIGN_COEFFICIENT * project.importance_factor * project.total_seismic_weight_tf


def build_spectrum(
    project: ProjectSeismicData,
    period_max_s: float = 4.0,
    step_s: float = 0.01,
) -> list[SpectrumPoint]:
    point_count = int(period_max_s / step_s) + 1
    spectrum: list[SpectrumPoint] = []
    for index in range(point_count):
        period_s = round(index * step_s, 10)
        spectrum.append(
            SpectrumPoint(
                period_s=period_s,
                alpha=alpha_nch433(period_s, project.soil),
                sa_elastic_g=sa_elastic_over_g(period_s, project),
                sa_design_g=sa_design_over_g(period_s, project),
            )
        )
    return spectrum


def print_summary(project: ProjectSeismicData) -> None:
    coeffs = static_coefficients(project)
    limits = q_limits(project)
    r_star_value = r_star(project.dominant_period_s, project.soil, project.R0)
    alpha_value = alpha_nch433(project.dominant_period_s, project.soil)
    sa_elastic = sa_elastic_over_g(project.dominant_period_s, project)
    sa_design = sa_design_over_g(project.dominant_period_s, project)
    qo_modal = sa_design * project.total_seismic_weight_tf
    q_course = course_base_shear(project)

    print("=" * 72)
    print("ESPECTRO DE DISENO NCh433 - GRUPO 1")
    print("=" * 72)
    print(f"Proyecto                : {project.city}")
    print(f"Sistema estructural     : {project.structural_system}")
    print(f"Zona sismica            : {project.seismic_zone}")
    print(f"Categoria ocupacion     : {project.occupation_category}")
    print(f"Factor importancia I    : {project.importance_factor:.2f}")
    print(f"Tipo de suelo           : {project.soil.soil_type}")
    print(
        f"S, T0, T', n, p         : {project.soil.S:.2f}, {project.soil.T0_s:.2f}, "
        f"{project.soil.T_prime_s:.2f}, {project.soil.n:.2f}, {project.soil.p:.2f}"
    )
    print(f"A0/g                    : {a0_over_g(project.seismic_zone):.2f}")
    print(f"R (estatico)            : {project.R:.2f}")
    print(f"R0 (modal)              : {project.R0:.2f}")
    print(f"Numero de pisos         : {project.floors}")
    print(f"Peso sismico P          : {project.total_seismic_weight_tf:.2f} tf")
    print(f"Periodo dominante T*    : {project.dominant_period_s:.2f} s")
    print("=" * 72)
    print("RESULTADOS PRINCIPALES")
    print(f"R*                      : {r_star_value:.4f}")
    print(f"alpha(T*)               : {alpha_value:.4f}")
    print(f"Sa elastico(T*)         : {sa_elastic:.4f} g")
    print(f"Sa reducido(T*)         : {sa_design:.4f} g")
    print(f"Qo/P modo dominante     : {sa_design:.4f}")
    print(f"Qo modo dominante       : {qo_modal:.2f} tf")
    print(f"C curso profesor        : {COURSE_DESIGN_COEFFICIENT:.4f}")
    print(f"Q curso profesor        : {q_course:.2f} tf")
    print(f"C estatico crudo        : {coeffs['C_raw']:.4f}")
    print(f"Cmin                    : {coeffs['C_min']:.4f}")
    print(f"Cmax                    : {coeffs['C_max']:.4f}")
    print(f"C estatico usado        : {coeffs['C_used']:.4f}")
    print(f"Qmin                    : {limits['Qmin_tf']:.2f} tf")
    print(f"Qmax                    : {limits['Qmax_tf']:.2f} tf")
    if qo_modal < limits["Qmin_tf"]:
        print(f"Escala minima aprox.    : x{limits['Qmin_tf'] / qo_modal:.3f}")
    print("=" * 72)


def plot_spectrum(spectrum: list[SpectrumPoint], project: ProjectSeismicData) -> None:
    periods = [point.period_s for point in spectrum]
    elastic = [point.sa_elastic_g for point in spectrum]
    design = [point.sa_design_g for point in spectrum]
    dominant_sa = sa_design_over_g(project.dominant_period_s, project)

    plt.figure(figsize=(9, 6))
    plt.plot(periods, elastic, label="Espectro elastico (R*=1)", linewidth=2.0)
    plt.plot(periods, design, label="Espectro reducido modal", linewidth=2.0)
    plt.axhline(
        COURSE_DESIGN_COEFFICIENT,
        color="firebrick",
        linestyle="--",
        linewidth=1.8,
        label="C = 0.10 (curso)",
    )
    plt.scatter(
        [project.dominant_period_s],
        [dominant_sa],
        color="black",
        zorder=3,
        label=f"T*={project.dominant_period_s:.2f} s",
    )
    plt.xlabel("Periodo T [s]")
    plt.ylabel("Sa / g")
    plt.title("Espectro de diseno NCh433 - Zona III, Suelo A")
    plt.grid(True, alpha=0.3)
    plt.xlim(0.0, max(periods))
    plt.ylim(bottom=0.0)
    plt.legend()
    plt.tight_layout()
    plt.show()


def main() -> None:
    print_summary(PROJECT)
    spectrum = build_spectrum(PROJECT, period_max_s=4.0, step_s=0.01)
    print("Mostrando grafico con matplotlib...")
    print("=" * 72)
    plot_spectrum(spectrum, PROJECT)


if __name__ == "__main__":
    main()
