"""
Generador de reportes profesionales en LaTeX.
Produce documentos académicos de alta calidad.
"""

import os
from datetime import datetime
from typing import Optional

from src.utils.logger import get_logger

logger = get_logger(__name__)


class LaTeXReportGenerator:
    """Genera reportes profesionales en formato LaTeX."""

    def __init__(self, config: dict):
        """
        Inicializa el generador.

        Args:
            config: Configuración del proyecto
        """
        self.config = config
        self.latex_dir = config.get("paths", {}).get("latex", "reports/latex")
        os.makedirs(self.latex_dir, exist_ok=True)

    def generate_full_report(
        self,
        results: dict,
        output_path: Optional[str] = None,
        title: str = "Análisis de Bienestar Psicológico Estudiantil",
        author: str = "Universidad Santo Tomás",
    ) -> str:
        """
        Genera un reporte completo en LaTeX.

        Args:
            results: Resultados del análisis
            output_path: Ruta de salida (None = auto)
            title: Título del documento
            author: Autor del documento

        Returns:
            Ruta del archivo .tex generado
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(
                self.latex_dir,
                f"reporte_bienestar_{timestamp}.tex"
            )

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Generar contenido
        content = self._build_document(results, title, author)

        # Escribir archivo
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"Reporte LaTeX generado: {output_path}")

        # Intentar compilar a PDF
        pdf_path = self._compile_to_pdf(output_path)

        return pdf_path if pdf_path else output_path

    def _build_document(self, results: dict, title: str, author: str) -> str:
        """Construye el documento LaTeX completo."""
        # Metadata
        date = datetime.now().strftime("%d de %B de %Y")
        total_responses = results.get("total_responses", 0)
        global_mean = results.get("global_mean", 0)
        global_std = results.get("global_std", 0)

        doc = r"""
\documentclass[12pt,a4paper]{article}

% Paquetes
\usepackage[utf8]{inputenc}
\usepackage[spanish]{babel}
\usepackage{geometry}
\geometry{margin=2.5cm}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{array}
\usepackage{hyperref}
\usepackage{xcolor}
\usepackage{fancyhdr}
\usepackage{titlesec}
\usepackage{amsmath}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\usepackage{float}
\usepackage{caption}
\usepackage{subcaption}

% Colores personalizados
\definecolor{ustblue}{RGB}{0,51,102}
\definecolor{ustgray}{RGB}{128,128,128}
\definecolor{sigreen}{RGB}{39,174,96}
\definecolor{sired}{RGB}{231,76,60}
\definecolor{siyellow}{RGB}{241,196,15}

% Configuración de hipervínculos
\hypersetup{
    colorlinks=true,
    linkcolor=ustblue,
    urlcolor=ustblue,
    citecolor=ustblue
}

% Encabezados y pies de página
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\textcolor{ustgray}{Análisis de Bienestar Psicológico}}
\fancyhead[R]{\textcolor{ustgray}{\today}}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0.4pt}
\renewcommand{\footrulewidth}{0.4pt}

% Títulos
\titleformat{\section}{\Large\bfseries\color{ustblue}}{\thesection}{1em}{}
\titleformat{\subsection}{\large\bfseries\color{ustblue!80}}{\thesubsection}{1em}{}
\titleformat{\subsubsection}{\normalsize\bfseries\color{ustblue!60}}{\thesubsubsection}{1em}{}

\begin{document}

% Portada
\begin{titlepage}
\centering
\vspace*{2cm}

{\Huge\bfseries\textcolor{ustblue}{""" + title + r"""}\par}

\vspace{1cm}

{\Large\textcolor{ustgray}{Universidad Santo Tomás}\par}

\vspace{0.5cm}

{\large\textcolor{ustgray}{""" + author + r"""}\par}

\vspace{2cm}

{\large\textcolor{ustgray}{Fecha: """ + date + r"""}\par}

\vspace{1cm}

\begin{tikzpicture}
\draw[fill=ustblue!10, draw=ustblue, rounded corners=5pt] (0,0) rectangle (12,4);
\node[align=center] at (6,3) {\textbf{\large Resumen Ejecutivo}};
\node[align=center] at (6,2) {Muestra: """ + str(total_responses) + r""" estudiantes};
\node[align=center] at (6,1.2) {Bienestar Global: """ + f"{global_mean:.2f}" + r""" $\pm$ """ + f"{global_std:.2f}" + r"""};
\end{tikzpicture}

\vfill

{\small\textcolor{ustgray}{Generado automáticamente por el Sistema de Análisis de Bienestar Estudiantil}\par}
\end{titlepage}

% Índice
\tableofcontents
\newpage

% ============================================================
% SECCIÓN 1: INTRODUCCIÓN
% ============================================================
\section{Introducción}

\subsection{Contexto}
El bienestar psicológico de los estudiantes universitarios es un factor determinante 
en su rendimiento académico, retención y desarrollo integral. Este informe presenta 
un análisis completo de """ + str(total_responses) + r""" respuestas obtenidas a través 
de la Escala de Bienestar Psicológico de Ryff.

\subsection{Objetivos}
\begin{itemize}
    \item Evaluar el nivel de bienestar psicológico de los estudiantes
    \item Identificar dimensiones con mayores áreas de oportunidad
    \item Detectar patrones y perfiles de estudiantes
    \item Proponer intervenciones basadas en evidencia
\end{itemize}

\subsection{Metodología}
Se utilizó la Escala de Bienestar Psicológico de Ryff (29 ítems), adaptada al español 
por Díaz et al. (2006). Las respuestas se codificaron en una escala Likert de 1 a 6, 
donde valores más altos indican mayor bienestar.

% ============================================================
% SECCIÓN 2: RESULTADOS
% ============================================================
\section{Resultados}

\subsection{Estadísticas Descriptivas}

\begin{table}[H]
\centering
\caption{Estadísticas descriptivas por dimensión del bienestar}
\label{tab:descriptivas}
\begin{tabular}{@{}lcccccc@{}}
\toprule
\textbf{Dimensión} & \textbf{N} & \textbf{Media} & \textbf{DE} & \textbf{Mín} & \textbf{Máx} & \textbf{Interpretación} \\
\midrule
"""
        # Agregar estadísticas por dimensión
        dimensions = results.get("dimension_stats", [])
        for dim in dimensions:
            name = dim.get("dimension", "")
            n = dim.get("n", 0)
            mean = dim.get("mean", 0)
            std = dim.get("std", 0)
            min_val = dim.get("min", 0)
            max_val = dim.get("max", 0)

            # Interpretación
            if mean >= 5:
                interp = r"\textcolor{sigreen}{Alto}"
            elif mean >= 3.5:
                interp = r"\textcolor{siyellow}{Medio}"
            else:
                interp = r"\textcolor{sired}{Bajo}"

            doc += f"{name} & {n} & {mean:.2f} & {std:.2f} & {min_val:.0f} & {max_val:.0f} & {interp} \\\\\n"

        doc += r"""
\bottomrule
\end{tabular}
\end{table}

\subsection{Índice Global de Bienestar}

El bienestar global promedio es de \textbf{""" + f"{global_mean:.2f}" + r"""} sobre 6.00 
(Desviación Estándar = """ + f"{global_std:.2f}" + r""").

\begin{figure}[H]
\centering
\begin{tikzpicture}
\begin{axis}[
    ybar,
    bar width=15pt,
    width=0.8\textwidth,
    height=8cm,
    ylabel={Puntuación Promedio},
    symbolic x coords={""" + ", ".join([d.get("dimension", "")[:3] for d in dimensions]) + r"""},
    xtick=data,
    ymin=0, ymax=6,
    nodes near coords,
    nodes near coords align={vertical},
]
\addplot[fill=ustblue] coordinates {
"""
        for dim in dimensions:
            short_name = dim.get("dimension", "")[:3]
            mean = dim.get("mean", 0)
            doc += f"({short_name}, {mean:.2f})\n"

        doc += r"""
};
\end{axis}
\end{tikzpicture}
\caption{Puntuaciones promedio por dimensión del bienestar}
\label{fig:dimensiones}
\end{figure}

"""
        # Agregar sección de correlaciones si existen
        correlations = results.get("correlations", [])
        if correlations:
            doc += r"""
\subsection{Análisis de Correlaciones}

\begin{table}[H]
\centering
\caption{Correlaciones con el bienestar global}
\label{tab:correlaciones}
\begin{tabular}{@{}lcc@{}}
\toprule
\textbf{Dimensión} & \textbf{Correlación} & \textbf{p-valor} \\
\midrule
"""
            for corr in correlations[:6]:
                dim = corr.get("dimension", corr.get("var1", ""))
                r_val = corr.get("correlation", 0)
                p_val = corr.get("p_value", 1)

                sig = ""
                if p_val < 0.001:
                    sig = "***"
                elif p_val < 0.01:
                    sig = "**"
                elif p_val < 0.05:
                    sig = "*"

                doc += f"{dim} & {r_val:.4f} & {p_val:.4f} {sig} \\\\\n"

            doc += r"""
\bottomrule
\end{tabular}
\end{table}

"""

        # Agregar regresiones si existen
        regression = results.get("regression", {})
        if regression:
            r_squared = regression.get("r_squared", 0)
            doc += r"""
\subsection{Análisis de Regresión}

\subsubsection{Regresión Lineal Múltiple}
El modelo de regresión lineal múltiple explicó el \textbf{""" + f"{r_squared*100:.1f}" + r"""\%} 
de la varianza en el bienestar global (R² = """ + f"{r_squared:.4f}" + r""").

\begin{table}[H]
\centering
\caption{Coeficientes de regresión estandarizados}
\label{tab:regresion}
\begin{tabular}{@{}lccc@{}}
\toprule
\textbf{Variable} & \textbf{β} & \textbf{p-valor} & \textbf{Significativo} \\
\midrule
"""
            for factor in regression.get("factors", []):
                name = factor.get("factor", "")
                beta = factor.get("std_coefficient", 0)
                p_val = factor.get("p_value", 1)
                sig = "Sí" if factor.get("significant", False) else "No"

                doc += f"{name} & {beta:.4f} & {p_val:.4f} & {sig} \\\\\n"

            doc += r"""
\bottomrule
\end{tabular}
\end{table}

"""

        # Agregar clustering si existe
        clusters = results.get("clusters", [])
        if clusters:
            doc += r"""
\subsection{Análisis de Clustering}

Se identificaron \textbf{""" + str(len(clusters)) + r"""} perfiles diferenciados de estudiantes:

\begin{table}[H]
\centering
\caption{Perfiles de estudiantes identificados}
\label{tab:clusters}
\begin{tabular}{@{}lccc@{}}
\toprule
\textbf{Perfil} & \textbf{Cantidad} & \textbf{Porcentaje} & \textbf{Descripción} \\
\midrule
"""
            for cluster in clusters:
                cid = cluster.get("id", 0)
                size = cluster.get("size", 0)
                pct = cluster.get("percentage", 0)
                label = cluster.get("label", "Sin descripción")

                doc += f"Perfil {cid} & {size} & {pct:.1f}\\% & {label} \\\\\n"

            doc += r"""
\bottomrule
\end{tabular}
\end{table}

"""

        # Regresión logística si existe
        logistic = results.get("logistic_regression", {})
        if logistic:
            doc += r"""
\subsubsection{Regresión Logística}

El modelo logístico clasificó a los estudiantes con \textbf{""" + f"{logistic.get('accuracy', 0)*100:.1f}" + r"""\%} 
de precisión (AUC = """ + f"{logistic.get('auc_roc', 0):.4f}" + r""").

\textbf{Odds Ratios:}

\begin{itemize}
"""
            for factor, or_val in logistic.get("odds_ratios", {}).items():
                interpretation = "aumenta" if or_val > 1 else "reduce"
                doc += f"    \\item {factor}: OR = {or_val:.4f} ({interpretation} la probabilidad)\n"

            doc += r"""
\end{itemize}

"""

        # Regresión stepwise si existe
        stepwise = results.get("stepwise_regression", {})
        if stepwise:
            doc += r"""
\subsubsection{Selección de Variables (Stepwise)}

El análisis stepwise seleccionó \textbf{""" + str(stepwise.get("n_selected", 0)) + r"""} 
variables como predictoras significativas:

\begin{itemize}
"""
            for var in stepwise.get("selected_variables", []):
                doc += f"    \\item {var}\n"

            doc += r"""
\end{itemize}

"""

        # ANOVA si existe
        anova = results.get("anova_gender", {})
        if anova:
            doc += r"""
\subsection{Comparación por Género (ANOVA)}

\begin{table}[H]
\centering
\caption{Resultados ANOVA por género}
\label{tab:anova}
\begin{tabular}{@{}lccccc@{}}
\toprule
\textbf{Dimensión} & \textbf{F} & \textbf{p-valor} & \textbf{η²} & \textbf{Significativo} \\
\midrule
"""
            for dim in anova.get("dimensions", []):
                name = dim.get("dimension", "")
                f_stat = dim.get("f_statistic", 0)
                p_val = dim.get("p_value", 1)
                eta = dim.get("eta_squared", 0)
                sig = "Sí" if dim.get("significant", False) else "No"

                doc += f"{name} & {f_stat:.4f} & {p_val:.4f} & {eta:.4f} & {sig} \\\\\n"

            doc += r"""
\bottomrule
\end{tabular}
\end{table}

"""

        # Conclusiones
        doc += r"""
% ============================================================
% SECCIÓN 3: CONCLUSIONES
% ============================================================
\section{Conclusiones y Recomendaciones}

\subsection{Principales Hallazgos}
"""
        # Generar conclusiones basadas en resultados
        if global_mean >= 5:
            doc += r"""
\begin{itemize}
    \item El bienestar global de los estudiantes es \textcolor{sigreen}{\textbf{ALTO}}, 
    lo que indica un ambiente propicio para el desarrollo integral.
    \item Se recomienda mantener las estrategias actuales y documentar las buenas prácticas.
\end{itemize}
"""
        elif global_mean >= 3.5:
            doc += r"""
\begin{itemize}
    \item El bienestar global es \textcolor{siyellow}{\textbf{MEDIO}}, existiendo 
    oportunidades de mejora en varias dimensiones.
    \item Se recomienda implementar programas focalizados en las dimensiones más débiles.
\end{itemize}
"""
        else:
            doc += r"""
\begin{itemize}
    \item El bienestar global es \textcolor{sired}{\textbf{BAJO}}, lo que requiere 
    intervenciones urgentes y comprehensivas.
    \item Se recomienda un plan de acción inmediato con seguimiento periódico.
\end{itemize}
"""

        # Recomendaciones específicas por dimensión más débil
        if dimensions:
            weakest = min(dimensions, key=lambda x: x.get("mean", 6))
            weakest_name = weakest.get('dimension', '')
            weakest_mean = weakest.get('mean', 0)
            doc += f"""
\\subsection{{Recomendaciones Específicas}}

Basado en el análisis, la dimensión con mayor área de oportunidad es 
\\textbf{{{weakest_name}}} (Media = {weakest_mean:.2f}).

\\begin{{enumerate}}
    \\item \\textbf{{Diagnóstico profundo}}: Realizar grupos focales para entender las 
    causas raíz de esta dimensión.
    \\item \\textbf{{Intervención diseñada}}: Crear programas específicos para mejorar 
    esta dimensión.
    \\item \\textbf{{Seguimiento}}: Implementar mediciones periódicas para evaluar el impacto.
    \\item \\textbf{{Capacitación}}: Entrenar al personal docente en estrategias de apoyo.
\\end{{enumerate}}
"""

        # Cierre
        doc += r"""
% ============================================================
% ANEXOS
% ============================================================
\newpage
\appendix
\section{Anexos}

\subsection{Metodología Detallada}
La Escala de Bienestar Psicológico de Ryff (1989) evalúa seis dimensiones:
\begin{enumerate}
    \item \textbf{Autoaceptación}: Actitud positiva hacia uno mismo
    \item \textbf{Relaciones Positivas}: Conexiones cálidas con otros
    \item \textbf{Autonomía}: Independencia y auto-regulación
    \item \textbf{Dominio del Entorno}: Gestión efectiva del entorno
    \item \textbf{Propósito de Vida}: Sentido y dirección en la vida
    \item \textbf{Crecimiento Personal}: Desarrollo continuo
\end{enumerate}

\subsection{Ítems Invertidos}
Los siguientes ítems fueron recodificados: 2, 4, 5, 8, 9, 13, 19, 22, 23, 26.

\vfill

\begin{center}
\textcolor{ustgray}{\small Documento generado automáticamente el """ + datetime.now().strftime("%d/%m/%Y %H:%M") + r"""}
\end{center}

\end{document}
"""
        return doc

    def _compile_to_pdf(self, tex_path: str) -> Optional[str]:
        """
        Intenta compilar el archivo .tex a PDF.

        Args:
            tex_path: Ruta del archivo .tex

        Returns:
            Ruta del PDF generado o None
        """
        try:
            import subprocess

            # Verificar si pdflatex está disponible
            result = pdflatex = subprocess.run(
                ["where", "pdflatex"],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                logger.warning("pdflatex no encontrado. Solo se generó el archivo .tex")
                return None

            # Compilar (dos veces para índices)
            tex_dir = os.path.dirname(tex_path)
            tex_name = os.path.basename(tex_path)

            for _ in range(2):
                subprocess.run(
                    ["pdflatex", "-interaction=nonstopmode", "-output-directory", tex_dir, tex_name],
                    capture_output=True,
                    cwd=tex_dir
                )

            # Verificar si se generó el PDF
            pdf_path = tex_path.replace(".tex", ".pdf")
            if os.path.exists(pdf_path):
                logger.info(f"PDF generado: {pdf_path}")
                return pdf_path

        except Exception as e:
            logger.error(f"Error al compilar LaTeX: {e}")

        return None

    def generate_summary_latex(self, results: dict) -> str:
        """
        Genera un resumen rápido en LaTeX.

        Args:
            results: Resultados del análisis

        Returns:
            Código LaTeX del resumen
        """
        total = results.get("total_responses", 0)
        global_mean = results.get("global_mean", 0)

        latex = f"""
\\begin{{center}}
\\textbf{{Resumen Ejecutivo}}\\\\[0.5cm]
Total de participantes: {total}\\\\
Bienestar Global: {global_mean:.2f}/6.00
\\end{{center}}
"""
        return latex
