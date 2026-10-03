"""
pages/methodology.py
====================
Page Methodologie et Formules.
Documente les donnees, les indicateurs calcules et les limites methodologiques.
"""

from dash import html


def _formula_card(indicator, formula, interpretation, attention=None, domain_color="var(--c-bleu)"):
    """Carte visuelle standardisee pour un indicateur derive."""
    children = [
        html.Div(
            style={
                "borderLeft": f"3px solid {domain_color}",
                "paddingLeft": "12px",
                "marginBottom": "6px"
            },
            children=[
                html.Div(
                    "INDICATEUR",
                    style={"fontSize": "10px", "fontWeight": "700", "color": "var(--text-muted)",
                           "textTransform": "uppercase", "letterSpacing": "0.06em", "marginBottom": "2px"}
                ),
                html.Div(indicator, style={"fontSize": "14px", "fontWeight": "700", "color": "var(--text-primary)"})
            ]
        ),
        html.Div(
            style={
                "backgroundColor": "var(--surface-alt)",
                "border": "1px solid var(--border)",
                "borderRadius": "5px",
                "padding": "10px 14px",
                "marginBottom": "8px",
                "fontFamily": "monospace",
                "fontSize": "14px",
                "color": "var(--text-primary)",
                "letterSpacing": "0.02em"
            },
            children=formula
        ),
        html.Div(
            style={"fontSize": "13px", "color": "var(--text-secondary)", "lineHeight": "1.5", "marginBottom": "6px"},
            children=interpretation
        )
    ]
    if attention:
        children.append(
            html.Div(
                style={
                    "fontSize": "12px",
                    "color": "var(--c-jaune)",
                    "backgroundColor": "var(--c-jaune-light)",
                    "border": "1px solid var(--c-jaune-border)",
                    "borderRadius": "4px",
                    "padding": "6px 10px"
                },
                children=[html.B("A noter : "), attention]
            )
        )
    return html.Div(
        style={
            "backgroundColor": "var(--surface)",
            "border": "1px solid var(--border)",
            "borderRadius": "7px",
            "padding": "16px",
            "boxShadow": "var(--shadow-card)"
        },
        children=children
    )


def _section_header(tag, title, subtitle=None):
    children = [
        html.Span(tag, className="page-question-tag bleu", style={"marginBottom": "6px"}),
        html.H3(title, style={"fontSize": "18px", "fontWeight": "700", "color": "var(--text-primary)",
                               "marginBottom": "4px"}),
    ]
    if subtitle:
        children.append(
            html.P(subtitle, style={"fontSize": "13px", "color": "var(--text-secondary)"})
        )
    return html.Div(style={"marginBottom": "16px"}, children=children)


def layout():
    return html.Div(
        className="main-container",
        children=[
            # En-tete
            html.Div(
                className="page-header-box",
                children=[
                    html.Span("TRANSPARENCE ANALYTIQUE", className="page-question-tag bleu"),
                    html.H2("Methodologie et formules", className="page-title"),
                    html.P(
                        "Documentation des sources de donnees, des traitements appliques, "
                        "des indicateurs calcules et des limites methodologiques a prendre en compte.",
                        className="page-description"
                    )
                ]
            ),

            # -------------------------------------------------------
            # A. Donnees utilisees
            # -------------------------------------------------------
            html.Div(
                className="card-box",
                style={"marginBottom": "20px"},
                children=[
                    _section_header("A. DONNEES", "Sources de donnees"),
                    html.Div(
                        style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(280px, 1fr))",
                               "gap": "12px"},
                        children=[
                            _data_source_block(
                                "Population",
                                "INSEED Togo - RGPH-5 (2022)",
                                "Donnees de population par region (5 regions) et par prefecture (39 prefectures). "
                                "Annee de reference : 2022. Utilise comme denominateur pour tous les ratios de densite."
                            ),
                            _data_source_block(
                                "Internet",
                                "Banque Mondiale / ITU - WDI (2023)",
                                "Serie temporelle 1990-2022. Indicateur : individus utilisant Internet (% de la "
                                "population). Methode enquete menage / declarations ITU."
                            ),
                            _data_source_block(
                                "Telecoms",
                                "ARCEP Togo - Rapports annuels 2013-2019",
                                "Abonnes Internet par technologie (2G, 3G, 4G, ADSL, FTTH, Wimax, GVA), "
                                "taux de penetration, revenus, parts de marche par operateur."
                            ),
                            _data_source_block(
                                "Etablissements financiers",
                                "Repertoire financier - Janvier 2025",
                                "Inventaire des agences bancaires, microfinances, assurances et mutuelles "
                                "avec localisation geographique (prefecture, region)."
                            ),
                            _data_source_block(
                                "Agents Mobile Money",
                                "Cartographie terrain - Decembre 2024",
                                "Recensement des points d'agents Mobile Money actifs, avec operateur(s) "
                                "desservis et localisation geographique (prefecture, region)."
                            ),
                            _data_source_block(
                                "Territoires",
                                "Shapefile GADM / OpenStreetMap",
                                "Geometries des 5 regions administratives du Togo au format GeoJSON. "
                                "Identifiant de jointure : shapeISO (TG-S, TG-K, TG-C, TG-P, TG-M)."
                            ),
                        ]
                    )
                ]
            ),

            # -------------------------------------------------------
            # B. Preparation des donnees
            # -------------------------------------------------------
            html.Div(
                className="card-box",
                style={"marginBottom": "20px"},
                children=[
                    _section_header("B. TRAITEMENT", "Preparation des donnees"),
                    html.Div(
                        style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "16px",
                               "fontSize": "13px", "color": "var(--text-secondary)", "lineHeight": "1.6"},
                        children=[
                            html.Div([
                                html.H4("Controles de qualite",
                                        style={"fontSize": "13px", "fontWeight": "700",
                                               "color": "var(--text-primary)", "marginBottom": "8px"}),
                                html.Ul(style={"paddingLeft": "18px"}, children=[
                                    html.Li("Verification et conversion des types numeriques (annee, valeur)"),
                                    html.Li("Identification et traitement des valeurs manquantes (NaN conserves, "
                                            "non remplaces par zero)"),
                                    html.Li("Suppression des doublons exacts sur les lignes de donnees"),
                                    html.Li("Verification des unites : pourcentages, abonnes absolus, ratios"),
                                    html.Li("Controle de coherence : ratios calcules uniquement si denominateur > 0"),
                                ])
                            ]),
                            html.Div([
                                html.H4("Harmonisation geographique",
                                        style={"fontSize": "13px", "fontWeight": "700",
                                               "color": "var(--text-primary)", "marginBottom": "8px"}),
                                html.Ul(style={"paddingLeft": "18px"}, children=[
                                    html.Li("Normalisation des noms de regions en majuscules "
                                            "(SAVANES, KARA, CENTRALE, PLATEAUX, MARITIME)"),
                                    html.Li("Consolidation de la region Maritime : la prefecture du Golfe "
                                            "(Grand Lome) est integree a la region Maritime pour les calculs "
                                            "de densite, conformement au decoupage administratif officiel"),
                                    html.Li("Jointure GeoJSON par identifiant shapeISO (TG-S, TG-K, TG-C, "
                                            "TG-P, TG-M)"),
                                    html.Li("Donnees de population reference : RGPH-5 2022 (INSEED)"),
                                ])
                            ])
                        ]
                    )
                ]
            ),

            # -------------------------------------------------------
            # C. Indicateurs derives et formules
            # -------------------------------------------------------
            html.Div(
                className="card-box",
                style={"marginBottom": "20px"},
                children=[
                    _section_header(
                        "C. FORMULES",
                        "Indicateurs derives",
                        "Formules calculees dans le module utils/calculations.py"
                    ),
                    html.Div(
                        style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(320px, 1fr))",
                               "gap": "16px"},
                        children=[
                            _formula_card(
                                indicator="Agents Mobile Money pour 10 000 habitants",
                                formula="(Nombre d'agents / Population) x 10 000",
                                interpretation="Permet de comparer la densite de points d'acces Mobile Money "
                                               "entre territoires de tailles demographiques differentes. "
                                               "Un ratio eleve indique une bonne couverture relative.",
                                domain_color="var(--c-violet)"
                            ),
                            _formula_card(
                                indicator="Habitants par agent Mobile Money",
                                formula="Population / Nombre d'agents",
                                interpretation="Plus cette valeur est elevee, plus un agent doit potentiellement "
                                               "desservir un grand nombre de residents. Indicateur de charge de "
                                               "service et d'accessibilite de proximite.",
                                domain_color="var(--c-violet)"
                            ),
                            _formula_card(
                                indicator="Etablissements financiers pour 10 000 habitants",
                                formula="(Nombre d'etablissements / Population) x 10 000",
                                interpretation="Mesure la densite des agences bancaires, microfinances et assurances "
                                               "physiques par rapport a la population locale.",
                                domain_color="var(--c-vert)"
                            ),
                            _formula_card(
                                indicator="Habitants par etablissement financier",
                                formula="Population / Nombre d'etablissements",
                                interpretation="Nombre de residents par agence physique. Permet d'identifier "
                                               "les zones ou l'infrastructure bancaire est insuffisante "
                                               "par rapport a la population.",
                                domain_color="var(--c-vert)"
                            ),
                            _formula_card(
                                indicator="Ecart a la moyenne nationale (%)",
                                formula="((Ratio_region - Ratio_national) / Ratio_national) x 100",
                                interpretation="Mesure le sur- ou sous-equipement relatif d'une region par "
                                               "rapport a la moyenne nationale ponderee. "
                                               "Valeur positive : region mieux couverte. "
                                               "Valeur negative : region sous la moyenne nationale.",
                                attention="La moyenne nationale est ponderee par la population de chaque "
                                          "region, pas une simple moyenne arithmetique.",
                                domain_color="var(--c-rouge)"
                            ),
                            _formula_card(
                                indicator="Taux de penetration Internet (ARCEP)",
                                formula="(Abonnes Internet / Population) x 100",
                                interpretation="Rapport entre le nombre d'abonnements Internet declares par "
                                               "les operateurs et la population totale. Peut depasser 100% "
                                               "si un individu detient plusieurs SIM ou abonnements.",
                                attention="Ne pas confondre avec le taux d'utilisation individuelle (ITU/Banque "
                                          "Mondiale) qui mesure la proportion de personnes ayant utilise Internet "
                                          "dans les 3 derniers mois.",
                                domain_color="var(--c-bleu)"
                            ),
                            _formula_card(
                                indicator="Part de marche d'un operateur",
                                formula="(Abonnes_operateur / Total_abonnes) x 100",
                                interpretation="Pourcentage des abonnements Internet detenus par un operateur "
                                               "sur le total du marche declare a l'ARCEP Togo.",
                                domain_color="var(--c-bleu)"
                            ),
                            _formula_card(
                                indicator="Part du Mobile Internet",
                                formula="(Abonnes_mobile / Abonnes_total) x 100",
                                interpretation="Proportion des abonnements Internet realises via le reseau "
                                               "mobile (2G/3G/4G) par rapport au total toutes technologies "
                                               "confondues (fixe + mobile).",
                                domain_color="var(--c-bleu)"
                            ),
                            _formula_card(
                                indicator="Seuil de qualification territoriale",
                                formula=[
                                    html.Div("Favorable   : Ratio > +15% de la moyenne nationale"),
                                    html.Div("Intermediaire : Ratio entre -20% et +15%"),
                                    html.Div("Deficit      : Ratio < -20% de la moyenne nationale"),
                                ],
                                interpretation="Classification utilisee dans l'onglet Diagnostic pour qualifier "
                                               "l'acces relatif de chaque region aux services financiers et "
                                               "Mobile Money.",
                                attention="Ces seuils sont des conventions methodologiques, pas des normes "
                                          "officielles. Ils doivent etre interpretes avec le contexte "
                                          "socioeconomique de chaque territoire.",
                                domain_color="var(--c-jaune)"
                            ),
                        ]
                    )
                ]
            ),

            # -------------------------------------------------------
            # D. Croisements de donnees
            # -------------------------------------------------------
            html.Div(
                className="card-box",
                style={"marginBottom": "20px"},
                children=[
                    _section_header("D. CROISEMENTS", "Rapprochements entre sources"),
                    html.Div(
                        style={"fontSize": "13px", "color": "var(--text-secondary)", "lineHeight": "1.7"},
                        children=[
                            html.Table(
                                className="data-table-simple",
                                children=[
                                    html.Thead(html.Tr([
                                        html.Th("Source A"),
                                        html.Th("Source B"),
                                        html.Th("Indicateur produit"),
                                        html.Th("Niveau de granularite")
                                    ])),
                                    html.Tbody([
                                        html.Tr([html.Td("Population RGPH-5"), html.Td("Agents Mobile Money"),
                                                 html.Td("Agents / 10 000 hab, Habitants / Agent"),
                                                 html.Td("Region, Prefecture")]),
                                        html.Tr([html.Td("Population RGPH-5"), html.Td("Etablissements financiers"),
                                                 html.Td("Etablissements / 10 000 hab, Habitants / Agence"),
                                                 html.Td("Region, Prefecture")]),
                                        html.Tr([html.Td("Abonnes ARCEP"), html.Td("Population RGPH"),
                                                 html.Td("Taux de penetration Internet (%)"),
                                                 html.Td("National")]),
                                        html.Tr([html.Td("Agents Mobile Money"), html.Td("Etablissements financiers"),
                                                 html.Td("Facteur multiplicateur MM vs agences physiques"),
                                                 html.Td("Region")]),
                                        html.Tr([html.Td("Territories GeoJSON"), html.Td("Ratios calcules"),
                                                 html.Td("Carte choropleth des disparites regionales"),
                                                 html.Td("Region (5 regions)")]),
                                    ])
                                ]
                            )
                        ]
                    )
                ]
            ),

            # -------------------------------------------------------
            # E. Limites methodologiques
            # -------------------------------------------------------
            html.Div(
                className="card-box",
                children=[
                    _section_header("E. LIMITES", "Points d'attention"),
                    html.Div(
                        style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(300px, 1fr))",
                               "gap": "12px"},
                        children=[
                            _limit_block(
                                "Decalage temporel entre sources",
                                "Les donnees de population sont issues du RGPH-5 (2022). "
                                "Les donnees telcoms ARCEP couvrent 2013-2019. "
                                "Les donnees Mobile Money sont de decembre 2024 et les etablissements "
                                "financiers de janvier 2025. "
                                "Ces decalages doivent etre pris en compte dans l'interpretation des ratios."
                            ),
                            _limit_block(
                                "ARPU GSM : valeur brute conservee",
                                "Les valeurs d'ARPU (revenu moyen par utilisateur) GSM presentent "
                                "des anomalies de magnitude possiblement liees a la definition de l'unite "
                                "(FCFA par mois vs FCFA par an) ou a une modification de perimetre. "
                                "Ces valeurs sont conservees sans correction arbitraire et signalees "
                                "comme necessitant une verification de definition."
                            ),
                            _limit_block(
                                "Valeurs manquantes",
                                "Les valeurs manquantes (NaN) dans les series temporelles sont conservees "
                                "telles quelles et ne sont pas remplaces par zero. "
                                "L'absence de donnee ne signifie pas une valeur nulle."
                            ),
                            _limit_block(
                                "Indicateurs descriptifs",
                                "Tous les indicateurs de ce tableau de bord sont de nature descriptive. "
                                "Ils documentent des constats sur les donnees disponibles. "
                                "Ils ne doivent pas etre interpretes comme des preuves de causalite."
                            ),
                            _limit_block(
                                "Granularite geographique",
                                "La cartographie est realisee au niveau des 5 regions administratives. "
                                "Les donnees prefectorales (39 prefectures) sont disponibles pour les "
                                "etablissements financiers et les agents Mobile Money, mais pas pour "
                                "la population Internet (disponible uniquement au niveau national)."
                            ),
                            _limit_block(
                                "Consolidation Maritime - Grand Lome",
                                "Dans les donnees administratives de terrain, la prefecture du Golfe "
                                "(Grand Lome, 1 305 681 hab) est parfois traitee separement de la "
                                "region Maritime. Dans ce tableau de bord, elle est systematiquement "
                                "integree a la region Maritime pour les calculs, conformement au "
                                "decoupage officiel des 5 regions du Togo."
                            ),
                        ]
                    )
                ]
            )
        ]
    )


def _data_source_block(title, source, description):
    return html.Div(
        style={
            "backgroundColor": "var(--surface-alt)",
            "border": "1px solid var(--border)",
            "borderRadius": "6px",
            "padding": "14px"
        },
        children=[
            html.Div(title, style={"fontSize": "13px", "fontWeight": "700", "color": "var(--text-primary)",
                                    "marginBottom": "3px"}),
            html.Div(source, style={"fontSize": "11px", "fontWeight": "600", "color": "var(--c-bleu)",
                                     "textTransform": "uppercase", "letterSpacing": "0.03em",
                                     "marginBottom": "6px"}),
            html.P(description, style={"fontSize": "12px", "color": "var(--text-secondary)",
                                        "lineHeight": "1.5", "margin": "0"})
        ]
    )


def _limit_block(title, description):
    return html.Div(
        style={
            "backgroundColor": "var(--c-jaune-light)",
            "border": "1px solid var(--c-jaune-border)",
            "borderRadius": "6px",
            "padding": "14px"
        },
        children=[
            html.Div(title, style={"fontSize": "13px", "fontWeight": "700", "color": "var(--text-primary)",
                                    "marginBottom": "6px"}),
            html.P(description, style={"fontSize": "12px", "color": "var(--text-secondary)",
                                        "lineHeight": "1.5", "margin": "0"})
        ]
    )
