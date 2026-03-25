import math
from dataclasses import dataclass, asdict
import matplotlib.pyplot as plt


# ============================================================
# UTILIDADES
# ============================================================

def kgcm2_to_kpa(value_kgcm2: float) -> float:
    return value_kgcm2 * 98.0665


def kpa_to_tfm2(value_kpa: float) -> float:
    return value_kpa / 9.80665


# ============================================================
# DATOS DEL PROYECTO
# ============================================================

@dataclass
class ProjectData:
    ciudad: str
    uso: str
    niveles: int
    subterranos: int
    categoria_ocupacion: str
    zona_sismica: int
    tipo_suelo: str
    qadm_min_kgcm2: float
    qadm_max_kgcm2: float


@dataclass
class SoilParameters:
    gamma_soil_kN_m3: float
    phi_deg: float
    cohesion_kPa: float = 0.0
    gamma_water_kN_m3: float = 9.81
    water_table_depth_m: float | None = None


@dataclass
class BasementWall:
    height_m: float
    surcharge_kPa: float = 0.0


# ============================================================
# PRESIÓN ADMISIBLE
# ============================================================

def admissible_bearing_summary(qmin_kgcm2: float, qmax_kgcm2: float) -> dict:
    qmin_kpa = kgcm2_to_kpa(qmin_kgcm2)
    qmax_kpa = kgcm2_to_kpa(qmax_kgcm2)

    return {
        "qadm_min_kgcm2": qmin_kgcm2,
        "qadm_max_kgcm2": qmax_kgcm2,
        "qadm_min_kPa": qmin_kpa,
        "qadm_max_kPa": qmax_kpa,
        "qadm_min_tfm2": kpa_to_tfm2(qmin_kpa),
        "qadm_max_tfm2": kpa_to_tfm2(qmax_kpa),
        "qadm_design_preliminar_kgcm2": qmin_kgcm2,
        "qadm_design_preliminar_kPa": qmin_kpa
    }


# ============================================================
# COEFICIENTES DE EMPUJE
# ============================================================

def earth_pressure_coefficients(phi_deg: float) -> dict:
    phi_rad = math.radians(phi_deg)

    ka = math.tan(math.radians(45.0) - phi_rad / 2.0) ** 2
    kp = math.tan(math.radians(45.0) + phi_rad / 2.0) ** 2
    k0 = 1.0 - math.sin(phi_rad)

    return {"Ka": ka, "K0": k0, "Kp": kp}


# ============================================================
# NOTA SOBRE BALASTO
# ============================================================

def estimate_subgrade_modulus_note() -> str:
    return (
        "La constante de balasto depende de la geometría de fundación, "
        "profundidad de desplante, tamaño del elemento y deformabilidad del terreno. "
        "Debe obtenerse del Informe de Mecánica de Suelos."
    )


# ============================================================
# PRESIONES LATERALES
# ============================================================

def lateral_pressure_at_depth(
    z: float,
    K: float,
    gamma_soil_kN_m3: float,
    surcharge_kPa: float = 0.0,
    water_table_depth_m: float | None = None,
    gamma_water_kN_m3: float = 9.81
) -> dict:
    sigma_h_soil = K * gamma_soil_kN_m3 * z
    sigma_h_q = K * surcharge_kPa

    sigma_h_water = 0.0
    if water_table_depth_m is not None and z > water_table_depth_m:
        hw = z - water_table_depth_m
        sigma_h_water = gamma_water_kN_m3 * hw

    sigma_total = sigma_h_soil + sigma_h_q + sigma_h_water

    return {
        "z_m": z,
        "soil_kPa": sigma_h_soil,
        "surcharge_kPa": sigma_h_q,
        "water_kPa": sigma_h_water,
        "total_kPa": sigma_total
    }


def pressure_diagram(
    wall_height_m: float,
    K: float,
    gamma_soil_kN_m3: float,
    surcharge_kPa: float = 0.0,
    water_table_depth_m: float | None = None,
    gamma_water_kN_m3: float = 9.81,
    n_points: int = 41
) -> list[dict]:
    if n_points < 2:
        raise ValueError("n_points debe ser al menos 2")

    dz = wall_height_m / (n_points - 1)
    diagram = []

    for i in range(n_points):
        z = i * dz
        diagram.append(
            lateral_pressure_at_depth(
                z=z,
                K=K,
                gamma_soil_kN_m3=gamma_soil_kN_m3,
                surcharge_kPa=surcharge_kPa,
                water_table_depth_m=water_table_depth_m,
                gamma_water_kN_m3=gamma_water_kN_m3
            )
        )

    return diagram


# ============================================================
# RESULTANTE DEL EMPUJE
# ============================================================

def resultant_force_from_diagram(diagram: list[dict]) -> dict:
    if len(diagram) < 2:
        raise ValueError("El diagrama debe tener al menos 2 puntos")

    total_force = 0.0
    total_moment_about_base = 0.0
    H = diagram[-1]["z_m"]

    for i in range(len(diagram) - 1):
        z1 = diagram[i]["z_m"]
        z2 = diagram[i + 1]["z_m"]
        p1 = diagram[i]["total_kPa"]
        p2 = diagram[i + 1]["total_kPa"]

        dz = z2 - z1
        dF = 0.5 * (p1 + p2) * dz
        z_bar = (z1 + z2) / 2.0
        lever_arm = H - z_bar
        dM = dF * lever_arm

        total_force += dF
        total_moment_about_base += dM

    resultant_arm_from_base = total_moment_about_base / total_force if total_force > 0 else 0.0

    return {
        "force_kN_per_m": total_force,
        "arm_from_base_m": resultant_arm_from_base
    }


# ============================================================
# GRÁFICA DEL DIAGRAMA DE EMPUJE
# ============================================================

def plot_pressure_diagram(diagram: list[dict], title: str = "Diagrama de empuje lateral") -> None:
    z = [row["z_m"] for row in diagram]
    soil = [row["soil_kPa"] for row in diagram]
    surcharge = [row["surcharge_kPa"] for row in diagram]
    water = [row["water_kPa"] for row in diagram]
    total = [row["total_kPa"] for row in diagram]

    plt.figure(figsize=(8, 6))

    plt.plot(soil, z, label="Presión por suelo")
    plt.plot(surcharge, z, label="Presión por sobrecarga")
    plt.plot(water, z, label="Presión hidrostática")
    plt.plot(total, z, linewidth=2.0, label="Presión total")

    plt.fill_betweenx(z, total, 0, alpha=0.2)

    plt.gca().invert_yaxis()
    plt.xlabel("Presión lateral [kPa]")
    plt.ylabel("Profundidad z [m]")
    plt.title(title)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


# ============================================================
# REPORTE
# ============================================================

def print_project_report(project: ProjectData, soil: SoilParameters, wall: BasementWall) -> None:
    print("=" * 70)
    print("REPORTE PRELIMINAR - SUELO Y PARAMETROS DE MECANICA DE SUELOS")
    print("=" * 70)

    print("\n1) INFORMACION DEL PROYECTO")
    for key, value in asdict(project).items():
        print(f"   - {key}: {value}")

    print("\n2) PRESION ADMISIBLE")
    q_summary = admissible_bearing_summary(project.qadm_min_kgcm2, project.qadm_max_kgcm2)
    for key, value in q_summary.items():
        if isinstance(value, float):
            print(f"   - {key}: {value:.3f}")
        else:
            print(f"   - {key}: {value}")

    print("\n3) PARAMETROS GEOTECNICOS ADOPTADOS")
    for key, value in asdict(soil).items():
        print(f"   - {key}: {value}")

    coeffs = earth_pressure_coefficients(soil.phi_deg)
    print("\n4) COEFICIENTES DE EMPUJE")
    for key, value in coeffs.items():
        print(f"   - {key}: {value:.4f}")

    print("\n5) CONSTANTE DE BALASTO")
    print("   -", estimate_subgrade_modulus_note())

    diagram_k0 = pressure_diagram(
        wall_height_m=wall.height_m,
        K=coeffs["K0"],
        gamma_soil_kN_m3=soil.gamma_soil_kN_m3,
        surcharge_kPa=wall.surcharge_kPa,
        water_table_depth_m=soil.water_table_depth_m,
        gamma_water_kN_m3=soil.gamma_water_kN_m3,
        n_points=41
    )

    result_k0 = resultant_force_from_diagram(diagram_k0)

    print("\n6) EMPUJE EN REPOSO (K0)")
    print(f"   - Fuerza resultante: {result_k0['force_kN_per_m']:.2f} kN/m")
    print(f"   - Brazo desde la base: {result_k0['arm_from_base_m']:.2f} m")

    print("\n7) VALORES DE PRESION EN EL MURO")
    print("   z [m] | suelo [kPa] | sobrecarga [kPa] | agua [kPa] | total [kPa]")
    print("   " + "-" * 62)

    for row in diagram_k0:
        print(
            f"   {row['z_m']:5.2f} | "
            f"{row['soil_kPa']:11.2f} | "
            f"{row['surcharge_kPa']:16.2f} | "
            f"{row['water_kPa']:10.2f} | "
            f"{row['total_kPa']:10.2f}"
        )

    print("\n8) OBSERVACIONES")
    print("   - El valor definitivo de empujes debe ajustarse con parámetros del Informe de Mecánica de Suelos.")
    print("   - Si existe napa dentro de la excavación, debe verificarse presión hidrostática y subpresión.")
    print("   - La constante de balasto queda pendiente de definición específica.")
    print("=" * 70)

    plot_pressure_diagram(diagram_k0, title="Diagrama de empuje lateral - condición en reposo (K0)")


# ============================================================
# EJEMPLO DE USO
# ============================================================

if __name__ == "__main__":
    project = ProjectData(
        ciudad="Antofagasta, Chile",
        uso="Habitacional",
        niveles=21,
        subterranos=1,
        categoria_ocupacion="II",
        zona_sismica=3,
        tipo_suelo="A",
        qadm_min_kgcm2=7.0,
        qadm_max_kgcm2=9.3
    )

    soil = SoilParameters(
        gamma_soil_kN_m3=20.0,
        phi_deg=45.0,
        cohesion_kPa=0.0,
        gamma_water_kN_m3=9.81,
        water_table_depth_m=None
        # ejemplo con napa: water_table_depth_m=1.5
    )

    wall = BasementWall(
        height_m=2.6,
        surcharge_kPa=10.0
    )

    print_project_report(project, soil, wall)