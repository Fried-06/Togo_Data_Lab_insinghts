"""
pages/recommendations.py
========================
Page 7 : Pistes d'action analytiques fondées sur les données.
Structure visuelle obligatoire : OBSERVATION -> DONNÉE -> INTERPRÉTATION -> PISTE D'ACTION
"""

from dash import html

RECOMMENDATIONS = [
    {
        "axe": "AXE 1 • ÉQUILIBRE TERRITORIAL DE LA PROXIMITÉ FINANCIÈRE",
        "observation": "Désert bancaire physique dans les régions du Nord et des Plateaux, contrastant avec la densité de Lomé.",
        "donnee": "La région des Savanes ne compte que 0.54 établissement financier pour 10 000 habitants (1 pour 18 444 habitants) contre 3.09 dans la Maritime. Le Mobile Money y compte cependant 2 679 points actifs (23.4 / 10k hab).",
        "interpretation": "L'implantation d'agences bancaires classiques en dur est économiquement non viable pour les banques commerciales dans les zones à faible densité marchande. Le réseau de distribution Mobile Money constitue de facto l'unique infrastructure financière de proximité.",
        "piste": "Développer le statut d'Agent Bancaire Délégué (Agency Banking) permettant aux agents Mobile Money des Savanes et des Plateaux d'opérer des services d'épargne formelle et de micro-assurance pour le compte des institutions financières."
    },
    {
        "axe": "AXE 2 • ACCÉLÉRATION DE LA TRANSITION TECHNOLOGIQUE MOBILE",
        "observation": "Une large part du parc mobile demeure cantonnée à la 2G/3G malgré le lancement commercial de la 4G.",
        "donnee": "En 2019, la 4G ne représentait que 174 474 abonnés (5.1% du parc Internet mobile total), tandis que la 2G comptait encore plus de 1.3 million d'utilisateurs et la 3G 1.88 million.",
        "interpretation": "Le frein à l'adoption de la 4G réside principalement dans le coût d'acquisition des smartphones compatibles 4G pour les ménages à revenu modeste et le déploiement progressif des fréquences 4G en zone rurale.",
        "piste": "Soutenir des programmes d'équipements en smartphones subventionnés ou payables à l'usage (Device Financing / Pay-as-you-go) couplés à des obligations de couverture 4G territoriale pour les deux opérateurs GSM titulaires de licences."
    },
    {
        "axe": "AXE 3 • RACCORDEMENT FIBRE OPTIQUE (FTTH) ET AMÉNAGEMENT NUMÉRIQUE",
        "observation": "L'Internet fixe très haut débit (FTTH) connaît une forte croissance mais reste confiné à l'agglomération côtière.",
        "donnee": "Le nombre d'abonnés FTTH est passé de 92 en 2017 à 6 888 en 2019 (+7400%), principalement déployé par les nouveaux entrants (GVA Togo) et Togocom dans les quartiers de Lomé.",
        "interpretation": "L'accès fixe haut débit est indispensable aux PME, centres de santé, universités et administrations territoriales pour ancrer les gains de productivité de l'économie numérique.",
        "piste": "Accélérer l'exploitation du réseau dorsal national en fibre optique (Backbone national) pour ouvrir des boucles locales FTTH dans les chefs-lieux régionaux (Sokodé, Kara, Atakpamé, Dapaong)."
    },
    {
        "axe": "AXE 4 • VALORISATION DES DONNÉES D'INCLUSION ET INTEROPÉRABILITÉ",
        "observation": "Forte présence des cartes SIM mixtes (Moov + Togocom) chez les agents et duplication des circuits de distribution.",
        "donnee": "Sur 19 788 agents Mobile Money, 12 649 (64%) opèrent simultanément pour les deux réseaux 'Moov, Togocom'.",
        "interpretation": "Les commerçants de proximité absorbent eux-mêmes la charge de l'interopérabilité pour satisfaire la clientèle multi-opérateurs, immobilisant de la trésorerie sur deux comptes de monnaie électronique distincts.",
        "piste": "Consolider la plateforme nationale d'interopérabilité des paiements pour fluidifier le rééquilibrage de liquidité inter-réseaux et réduire les ruptures de trésorerie (float) des agents ruraux."
    }
]

def layout():
    rec_cards = []
    for r in RECOMMENDATIONS:
        rec_cards.append(
            html.Div(
                className="card-box",
                style={"marginBottom": "20px"},
                children=[
                    html.Div(className="card-header", children=[
                        html.Div(r["axe"], className="card-question"),
                        html.H3(r["observation"], className="card-title")
                    ]),
                    html.Div(style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "20px", "marginBottom": "16px"}, children=[
                        html.Div([
                            html.Div("DONNÉE CONSTATÉE DANS LES JEUX", style={"fontSize": "11px", "fontWeight": "700", "color": "#1E40AF", "textTransform": "uppercase", "marginBottom": "4px"}),
                            html.P(r["donnee"], style={"fontSize": "13px", "color": "#1F2937", "lineHeight": "1.5", "backgroundColor": "#EFF6FF", "padding": "12px", "borderRadius": "6px", "border": "1px solid #BFDBFE"})
                        ]),
                        html.Div([
                            html.Div("INTERPRÉTATION STATISTIQUE & SECTORIELLE", style={"fontSize": "11px", "fontWeight": "700", "color": "#92400E", "textTransform": "uppercase", "marginBottom": "4px"}),
                            html.P(r["interpretation"], style={"fontSize": "13px", "color": "#1F2937", "lineHeight": "1.5", "backgroundColor": "#FFFBEB", "padding": "12px", "borderRadius": "6px", "border": "1px solid #FDE68A"})
                        ])
                    ]),
                    html.Div(
                        style={"backgroundColor": "#F0FDF4", "border": "1px solid #BBF7D0", "padding": "14px 16px", "borderRadius": "6px"},
                        children=[
                            html.Div("PISTE D'ACTION ÉMERGENTE (IMPLICATION ANALYTIQUE)", style={"fontSize": "11px", "fontWeight": "700", "color": "#166534", "textTransform": "uppercase", "marginBottom": "4px"}),
                            html.P(r["piste"], style={"fontSize": "13px", "color": "#14532D", "lineHeight": "1.5", "fontWeight": "500"})
                        ]
                    )
                ]
            )
        )

    return html.Div(
        className="main-container",
        children=[
            html.Div(
                className="page-header-box",
                children=[
                    html.Span("AIDE À LA DÉCISION", className="page-question-tag vert"),
                    html.H2("Recommandations et implications analytiques", className="page-title"),
                    html.P(
                        "Pistes d'action concrètes dérivées directement des disparités territoriales et technologiques constatées. "
                        "Chaque implication est rigoureusement ancrée dans la preuve statistique.",
                        className="page-description"
                    )
                ]
            ),
            html.Div(rec_cards)
        ]
    )
