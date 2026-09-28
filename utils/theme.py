"""
utils/theme.py
==============
Charte graphique et système de couleurs sémantiques institutionnel pour Togo Digital Insight.
Gère les thèmes Clair et Sombre (Dark Mode).
"""

# Palette principale sémantique
COLORS = {
    # Statuts / Niveaux
    "vert": "#0B6623",        # Vert institutionnel profond (favorable / progression)
    "vert_light": "#EBFBEE",
    "vert_border": "#B2F2BB",
    
    "jaune": "#D97706",       # Ambre / Jaune (intermédiaire / vigilance)
    "jaune_light": "#FFFBEB",
    "jaune_border": "#FDE68A",
    
    "rouge": "#DC2626",       # Rouge alerte (déficit / faible couverture)
    "rouge_light": "#FEF2F2",
    "rouge_border": "#FECACA",
    
    # Domaines thématiques
    "bleu": "#1D4ED8",        # Bleu télécom & connectivité
    "bleu_light": "#EFF6FF",
    "bleu_border": "#BFDBFE",
    
    "violet": "#6D28D9",      # Violet finance numérique & mobile money
    "violet_light": "#F5F3FF",
    "violet_border": "#DDD6FE",
    
    # Neutres & Structure (Mode Clair)
    "bg_main": "#F8F9FA",
    "surface": "#FFFFFF",
    "border": "#E5E7EB",
    "border_subtle": "#F3F4F6",
    
    "text_primary": "#111827",
    "text_secondary": "#4B5563",
    "text_muted": "#6B7280",
    
    # National Togo subtil
    "togo_green": "#006A4E",
    "togo_yellow": "#FFCE00",
    "togo_red": "#D21034",
}

FONT_FAMILY = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"

def apply_plotly_theme(fig, title=None, subtitle=None, height=380, show_legend=True, is_dark=False):
    """
    Applique le design system unifié à une figure Plotly :
    - Gestion propre des marges pour éviter TOUT chevauchement
    - Couleurs adaptées au mode Clair ou Sombre
    - Masquage automatique des légendes parasites pour graphiques mono-trace
    """
    # Détection automatique : si 1 seule trace et pas de nom significatif, masquer la légende
    if len(fig.data) <= 1:
        show_legend = False
    for trace in fig.data:
        if getattr(trace, "name", None) in [None, "", "trace 0", "trace0"]:
            trace.showlegend = False

    # Couleurs contextuelles selon mode clair / sombre
    text_color = "#F3F4F6" if is_dark else COLORS["text_primary"]
    text_sec_color = "#9CA3AF" if is_dark else COLORS["text_secondary"]
    grid_color = "#334155" if is_dark else "#E5E7EB"
    line_color = "#475569" if is_dark else "#D1D5DB"
    legend_bg = "rgba(30, 41, 59, 0.9)" if is_dark else "rgba(255, 255, 255, 0.9)"
    legend_border = "#475569" if is_dark else COLORS["border"]

    # Marge supérieure calculée pour éviter tout chevauchement
    top_margin = 15
    if title:
        top_margin = 65 if not show_legend else 85
    elif show_legend:
        top_margin = 40

    fig.update_layout(
        font_family=FONT_FAMILY,
        font_color=text_color,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        margin=dict(l=45, r=25, t=top_margin, b=45),
        showlegend=show_legend,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.03 if not title else 1.15,
            xanchor="left",
            x=0,
            font=dict(size=11, color=text_sec_color),
            bgcolor=legend_bg,
            bordercolor=legend_border,
            borderwidth=1,
        ),
        hoverlabel=dict(
            bgcolor="#1F2937" if not is_dark else "#0F172A",
            font_size=12,
            font_family=FONT_FAMILY,
            font_color="#FFFFFF",
            bordercolor="#374151"
        )
    )

    if title:
        title_text = f"<b>{title}</b>"
        if subtitle:
            title_text += f"<br><span style='font-size:11px; font-weight:normal; color:{text_sec_color}'>{subtitle}</span>"
        fig.update_layout(
            title=dict(
                text=title_text,
                font=dict(size=14, color=text_color),
                x=0.01,
                xanchor="left",
                y=0.98
            )
        )

    # Style des axes X et Y
    fig.update_xaxes(
        showgrid=True,
        gridcolor=grid_color,
        gridwidth=1,
        zeroline=False,
        linecolor=line_color,
        linewidth=1,
        tickfont=dict(size=11, color=text_sec_color),
        title_font=dict(size=12, color=text_sec_color)
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor=grid_color,
        gridwidth=1,
        zeroline=False,
        linecolor=line_color,
        linewidth=1,
        tickfont=dict(size=11, color=text_sec_color),
        title_font=dict(size=12, color=text_sec_color)
    )
    return fig
