"""
Módulo de generación de reportes PDF ejecutivos.
"""

import os
from datetime import datetime
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

from src.utils.logger import get_logger

logger = get_logger(__name__)


class ReportGenerator:
    """Generador de reportes PDF ejecutivos."""

    def __init__(self, config: dict):
        """
        Inicializa el generador.

        Args:
            config: Configuración del proyecto
        """
        self.config = config
        self.project_name = config.get("project", {}).get("name", "")
        self.institution = config.get("project", {}).get("institution", "")

    def generate_executive_report(
        self,
        output_path: str,
        summary_stats: dict,
        dimension_stats: list,
        correlations: list,
        regression_results: dict,
        cluster_profiles: list,
        total_responses: int,
    ) -> str:
        """
        Genera el reporte PDF ejecutivo.

        Args:
            output_path: Ruta de salida del PDF
            summary_stats: Estadísticas resumen
            dimension_stats: Estadísticas por dimensión
            correlations: Correlaciones significativas
            regression_results: Resultados de regresión
            cluster_profiles: Perfiles de clustering
            total_responses: Total de respuestas

        Returns:
            Ruta del archivo generado
        """
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Crear documento
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2.5 * cm,
            bottomMargin=2.5 * cm,
        )

        # Estilos
        styles = getSampleStyleSheet()
        styles.add(
            ParagraphStyle(
                name="TitleCustom",
                parent=styles["Title"],
                fontSize=20,
                spaceAfter=30,
            )
        )
        styles.add(
            ParagraphStyle(
                name="Heading1Custom",
                parent=styles["Heading1"],
                fontSize=16,
                spaceBefore=20,
                spaceAfter=10,
            )
        )
        styles.add(
            ParagraphStyle(
                name="Heading2Custom",
                parent=styles["Heading2"],
                fontSize=14,
                spaceBefore=15,
                spaceAfter=8,
            )
        )
        styles.add(
            ParagraphStyle(
                name="BodyCustom",
                parent=styles["BodyText"],
                fontSize=11,
                alignment=TA_JUSTIFY,
                spaceAfter=10,
            )
        )
        styles.add(
            ParagraphStyle(
                name="SmallText",
                parent=styles["Normal"],
                fontSize=9,
                textColor=colors.grey,
            )
        )

        # Contenido
        story = []

        # Portada
        story.append(Spacer(1, 2 * inch))
        story.append(Paragraph(self.institution, styles["TitleCustom"]))
        story.append(Spacer(1, 0.5 * inch))
        story.append(Paragraph("Reporte Ejecutivo", styles["TitleCustom"]))
        story.append(Paragraph("Análisis de Bienestar Psicológico Estudiantil", styles["TitleCustom"]))
        story.append(Spacer(1, 1 * inch))
        story.append(
            Paragraph(
                f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                styles["SmallText"],
            )
        )
        story.append(Paragraph(f"Total de respuestas: {total_responses}", styles["SmallText"]))
        story.append(PageBreak())

        # Resumen Ejecutivo
        story.append(Paragraph("1. Resumen Ejecutivo", styles["Heading1Custom"]))
        story.append(
            Paragraph(
                "Este reporte presenta los resultados del análisis de bienestar psicológico "
                "evaluado mediante la Escala de Ryff (adaptación española de Díaz et al., 2006). "
                "El instrumento mide seis dimensiones del bienestar: Autoaceptación, Relaciones "
                "Positivas, Autonomía, Dominio del Entorno, Propósito de Vida y Crecimiento Personal.",
                styles["BodyCustom"],
            )
        )
        story.append(
            Paragraph(
                f"Se analizaron {total_responses} respuestas válidas. A continuación se "
                "presentan los hallazgos principales del estudio.",
                styles["BodyCustom"],
            )
        )

        # Estadísticas por Dimensión
        story.append(Paragraph("2. Resultados por Dimensión", styles["Heading1Custom"]))

        if dimension_stats:
            # Crear tabla
            table_data = [["Dimensión", "Media", "DE", "Mín", "Máx", "N"]]

            for stat in dimension_stats:
                table_data.append(
                    [
                        stat.get("dimension", ""),
                        f"{stat.get('mean', 0):.3f}",
                        f"{stat.get('std', 0):.3f}",
                        f"{stat.get('min', 0):.2f}",
                        f"{stat.get('max', 0):.2f}",
                        str(stat.get("n", 0)),
                    ]
                )

            table = Table(table_data, colWidths=[3 * cm, 2 * cm, 2 * cm, 1.5 * cm, 1.5 * cm, 1.5 * cm])
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#ECF0F1")),
                        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                    ]
                )
            )

            story.append(table)
            story.append(Spacer(1, 0.5 * inch))

        # Correlaciones
        story.append(Paragraph("3. Correlaciones Significativas", styles["Heading1Custom"]))

        if correlations:
            story.append(
                Paragraph(
                    "Las siguientes correlaciones fueron estadísticamente significativas (p < 0.05):",
                    styles["BodyCustom"],
                )
            )

            corr_table_data = [["Dimensión 1", "Dimensión 2", "Correlación", "Interpretación"]]

            for corr in correlations[:10]:  # Top 10
                r = corr.get("correlation", 0)
                if abs(r) >= 0.7:
                    interp = "Muy fuerte"
                elif abs(r) >= 0.5:
                    interp = "Fuerte"
                elif abs(r) >= 0.3:
                    interp = "Moderada"
                else:
                    interp = "Débil"

                corr_table_data.append(
                    [
                        corr.get("var1", corr.get("dimension", "")),
                        corr.get("var2", "Bienestar Global"),
                        f"{r:.3f}",
                        interp,
                    ]
                )

            corr_table = Table(corr_table_data)
            corr_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#34495E")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                    ]
                )
            )

            story.append(corr_table)

        # Factores Predictores
        story.append(Paragraph("4. Factores Predictores del Bienestar", styles["Heading1Custom"]))

        if regression_results and "factors" in regression_results:
            r_squared = regression_results.get("r_squared", 0)
            story.append(
                Paragraph(
                    f"El modelo de regresión explica el {r_squared*100:.1f}% de la varianza "
                    "del bienestar global.",
                    styles["BodyCustom"],
                )
            )

            factors = regression_results.get("factors", [])
            if factors:
                factors_table_data = [["Factor", "Coef. Estand.", "p-valor", "Significativo"]]

                for f in factors[:6]:
                    factors_table_data.append(
                        [
                            f.get("factor", ""),
                            f"{f.get('std_coefficient', 0):.3f}",
                            f"{f.get('p_value', 1):.4f}",
                            "Sí" if f.get("significant", False) else "No",
                        ]
                    )

                factors_table = Table(factors_table_data)
                factors_table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#27AE60")),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("FONTSIZE", (0, 0), (-1, -1), 9),
                            ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                        ]
                    )
                )

                story.append(factors_table)

        # Perfiles de Estudiantes
        story.append(Paragraph("5. Perfiles de Estudiantes", styles["Heading1Custom"]))

        if cluster_profiles:
            story.append(
                Paragraph(
                    f"Se identificaron {len(cluster_profiles)} perfiles de estudiantes "
                    "mediante análisis de clustering:",
                    styles["BodyCustom"],
                )
            )

            profiles_table_data = [["Perfil", "Cantidad", "%", "Descripción"]]

            for profile in cluster_profiles:
                profiles_table_data.append(
                    [
                        f"Perfil {profile.cluster_id}",
                        str(profile.size),
                        f"{profile.percentage}%",
                        profile.label,
                    ]
                )

            profiles_table = Table(profiles_table_data)
            profiles_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#8E44AD")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
                    ]
                )
            )

            story.append(profiles_table)

        # Conclusiones
        story.append(Paragraph("6. Conclusiones y Recomendaciones", styles["Heading1Custom"]))
        story.append(
            Paragraph(
                "Basado en el análisis realizado, se presentan las siguientes observaciones:",
                styles["BodyCustom"],
            )
        )

        # Generar conclusiones automáticas
        conclusions = self._generate_conclusions(
            dimension_stats, correlations, regression_results, cluster_profiles
        )

        for conclusion in conclusions:
            story.append(Paragraph(f"• {conclusion}", styles["BodyCustom"]))

        # Construir PDF
        doc.build(story)

        logger.info(f"Reporte generado: {output_path}")
        return output_path

    def _generate_conclusions(
        self, dimension_stats, correlations, regression_results, cluster_profiles
    ) -> list:
        """Genera conclusiones automáticas basadas en los datos."""
        conclusions = []

        if dimension_stats:
            # Encontrar dimensión más alta y más baja
            sorted_stats = sorted(dimension_stats, key=lambda x: x.get("mean", 0), reverse=True)

            if sorted_stats:
                highest = sorted_stats[0]
                lowest = sorted_stats[-1]

                conclusions.append(
                    f"La dimensión con mayor puntuación promedio es '{highest.get('dimension')}' "
                    f"({highest.get('mean', 0):.3f}), lo que sugiere que los estudiantes reportan "
                    f"mayores niveles en este aspecto de su bienestar."
                )

                conclusions.append(
                    f"La dimensión con menor puntuación es '{lowest.get('dimension')}' "
                    f"({lowest.get('mean', 0):.3f}), lo cual podría ser un área de oportunidad "
                    f"para intervenciones institucionales."
                )

        if regression_results and "factors" in regression_results:
            factors = regression_results.get("factors", [])
            significant_factors = [f for f in factors if f.get("significant")]

            if significant_factors:
                top_factor = significant_factors[0]
                conclusions.append(
                    f"El factor '{top_factor.get('factor')}' es el predictor más importante "
                    f"del bienestar global (β estandarizado = {top_factor.get('std_coefficient', 0):.3f})."
                )

        if cluster_profiles:
            conclusions.append(
                f"Se identificaron {len(cluster_profiles)} perfiles diferenciados de estudiantes, "
                f"lo que sugiere que el bienestar psicológico no es uniforme y puede requerir "
                f"estrategias de intervención personalizadas."
            )

        conclusions.append(
            "Se recomienda fortalecer las dimensiones con menor puntuación mediante "
            "programas institucionales de bienestar."
        )

        return conclusions

    def generate_notification_summary(self, stats: dict) -> str:
        """
        Genera un resumen para notificación por correo.

        Args:
            stats: Estadísticas resumen

        Returns:
            Texto del resumen
        """
        summary = f"""
Resumen del Análisis de Bienestar Estudiantil
==============================================
Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}

Total de respuestas: {stats.get('total_responses', 0)}

Bienestar Global:
- Promedio: {stats.get('global_mean', 0):.2f}
- Desviación Estándar: {stats.get('global_std', 0):.2f}

Dimensiones:
"""
        for dim in stats.get("dimensions", []):
            summary += f"- {dim['name']}: {dim['mean']:.2f}\n"

        if stats.get("new_responses"):
            summary += f"\nNuevas respuestas desde última ejecución: {stats['new_responses']}\n"

        return summary
