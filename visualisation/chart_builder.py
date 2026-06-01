import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
from visualisation.themes import PRIMARY_BLUE, ACCENT_TEAL, WARNING_AMBER, RISK_RED, SUCCESS_GREEN, OPTIMAL_YELLOW, CARD_BACKGROUND, TEXT_PRIMARY, TEXT_SECONDARY, BORDER_SUBTLE


class ChartBuilder:
    """Builds highly curated, interactive Plotly charts matching institutional brand design guidelines."""

    @staticmethod
    def build_iss_gauge(score: float, classification: str) -> go.Figure:
        """Constructs the high-fidelity Plotly gauge representing the composite ISS."""
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            title={'text': f"Composite ISS: {classification}", 'font': {'size': 14, 'color': TEXT_PRIMARY}},
            number={'font': {'size': 38, 'color': TEXT_PRIMARY, 'family': 'JetBrains Mono'}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': TEXT_SECONDARY},
                'bar': {'color': TEXT_PRIMARY, 'thickness': 0.35},
                'bgcolor': CARD_BACKGROUND,
                'borderwidth': 1,
                'bordercolor': BORDER_SUBTLE,
                'steps': [
                    {'range': [0, 30], 'color': RISK_RED},
                    {'range': [30, 50], 'color': WARNING_AMBER},
                    {'range': [50, 70], 'color': OPTIMAL_YELLOW},
                    {'range': [70, 85], 'color': SUCCESS_GREEN},
                    {'range': [85, 100], 'color': PRIMARY_BLUE}
                ]
            }
        ))
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=40, b=20),
            height=250
        )
        return fig

    @staticmethod
    def build_vector_scores_chart(vector_scores: Dict[str, float]) -> go.Figure:
        """Renders a beautiful horizontal bar chart showing individual vector scores color-coded by performance."""
        # Convert to lists for plotting
        vectors = list(vector_scores.keys())
        scores = list(vector_scores.values())
        
        # Color coding
        colors = []
        for s in scores:
            if s <= 30: colors.append(RISK_RED)
            elif s <= 50: colors.append(WARNING_AMBER)
            elif s <= 70: colors.append(OPTIMAL_YELLOW)
            elif s <= 85: colors.append(SUCCESS_GREEN)
            else: colors.append(PRIMARY_BLUE)
            
        fig = go.Figure(go.Bar(
            x=scores,
            y=vectors,
            orientation='h',
            marker_color=colors,
            text=scores,
            textposition='auto',
            textfont=dict(color='#FFF', size=11, family='JetBrains Mono'),
            hoverinfo='x+y'
        ))
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(
                range=[0, 100],
                showgrid=True,
                gridcolor=BORDER_SUBTLE,
                tickfont=dict(color=TEXT_SECONDARY),
                title=dict(text="Score (0-100)", font=dict(color=TEXT_SECONDARY, size=11))
            ),
            yaxis=dict(
                autorange="reversed",
                showgrid=False,
                tickfont=dict(color=TEXT_PRIMARY, size=12, weight='bold')
            ),
            margin=dict(l=10, r=10, t=10, b=10),
            height=280
        )
        return fig

    @staticmethod
    def build_portfolio_radar(locations: List[Any], scenario_name: str = "Balanced Developer") -> go.Figure:
        """Constructs an overlaid Plotly Radar chart comparing the 7 vector scores for up to 12 portfolio pins."""
        fig = go.Figure()
        
        categories = ["SRI", "WRP", "HSI", "GIR", "EVI", "RPE", "LSA"]
        
        # Palette for multiple sites
        color_palette = [PRIMARY_BLUE, ACCENT_TEAL, WARNING_AMBER, SUCCESS_GREEN, OPTIMAL_YELLOW, "#9B59B6", "#34495E", "#E74C3C", "#1ABC9C", "#F39C12", "#D35400", "#7F8C8D"]
        
        for i, loc in enumerate(locations):
            scores = [loc.vector_scores.get(cat, 50.0) for cat in categories]
            # Close the loop
            scores_closed = scores + [scores[0]]
            categories_closed = categories + [categories[0]]
            
            color = color_palette[i % len(color_palette)]
            
            fig.add_trace(go.Scatterpolar(
                r=scores_closed,
                theta=categories_closed,
                fill='toself',
                fillcolor=f"{color}1F",  # Add low opacity hex transparency
                line=dict(color=color, width=2),
                name=loc.name
            ))
            
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    showticklabels=True,
                    tickfont=dict(color=TEXT_SECONDARY, size=9),
                    gridcolor=BORDER_SUBTLE
                ),
                angularaxis=dict(
                    gridcolor=BORDER_SUBTLE,
                    tickfont=dict(color=TEXT_PRIMARY, size=11, weight='bold')
                ),
                bgcolor=CARD_BACKGROUND
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=-0.25,
                xanchor='center',
                x=0.5,
                font=dict(color=TEXT_PRIMARY, size=11)
            ),
            margin=dict(l=40, r=40, t=40, b=40),
            height=380
        )
        return fig

    @staticmethod
    def build_tornado_chart(tornado_data: List[Dict[str, Any]]) -> go.Figure:
        """Renders the Tornado sensitivity chart demonstrating marginal vector impact."""
        vectors = [item["vector"] for item in tornado_data]
        baseline = tornado_data[0]["baseline_iss"] if tornado_data else 50.0
        
        iss_lows = [item["iss_low"] for item in tornado_data]
        iss_highs = [item["iss_high"] for item in tornado_data]
        
        # Swings relative to baseline
        left_delta = [low - baseline for low in iss_lows]
        right_delta = [high - baseline for high in iss_highs]
        
        fig = go.Figure()
        
        # Decreasing performance swing
        fig.add_trace(go.Bar(
            y=vectors,
            x=left_delta,
            orientation='h',
            name="Score Delta -20 pts",
            marker_color=RISK_RED,
            base=baseline,
            hovertemplate="ISS Low: %{customdata:.1f}<extra></extra>",
            customdata=iss_lows
        ))
        
        # Increasing performance swing
        fig.add_trace(go.Bar(
            y=vectors,
            x=right_delta,
            orientation='h',
            name="Score Delta +20 pts",
            marker_color=SUCCESS_GREEN,
            base=baseline,
            hovertemplate="ISS High: %{customdata:.1f}<extra></extra>",
            customdata=iss_highs
        ))
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(
                showgrid=True,
                gridcolor=BORDER_SUBTLE,
                tickfont=dict(color=TEXT_SECONDARY),
                title=dict(text="Composite ISS Impact", font=dict(color=TEXT_SECONDARY, size=11))
            ),
            yaxis=dict(
                autorange="reversed",
                tickfont=dict(color=TEXT_PRIMARY, size=12, weight='bold')
            ),
            shapes=[
                dict(
                    type="line",
                    x0=baseline,
                    y0=-0.5,
                    x1=baseline,
                    y1=len(vectors) - 0.5,
                    line=dict(color=PRIMARY_BLUE, width=2, dash="dash")
                )
            ],
            barmode='overlay',
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=-0.2,
                xanchor='center',
                x=0.5,
                font=dict(color=TEXT_PRIMARY)
            ),
            margin=dict(l=10, r=10, t=10, b=10),
            height=300
        )
        return fig

    @staticmethod
    def build_correlation_heatmap(corr_df: pd.DataFrame) -> go.Figure:
        """Renders Pearson correlation matrix of vector scores across portfolio pins."""
        fig = go.Figure(data=go.Heatmap(
            z=corr_df.values,
            x=corr_df.columns,
            y=corr_df.index,
            colorscale='RdBu',
            zmin=-1.0,
            zmax=1.0,
            colorbar=dict(
                tickfont=dict(color=TEXT_SECONDARY),
                title=dict(text="r", font=dict(color=TEXT_SECONDARY))
            ),
            hoverongaps=False
        ))
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(tickfont=dict(color=TEXT_PRIMARY)),
            yaxis=dict(tickfont=dict(color=TEXT_PRIMARY)),
            margin=dict(l=10, r=10, t=10, b=10),
            height=280
        )
        return fig

    @staticmethod
    def build_iss_comparison_bars(ranked_df: pd.DataFrame) -> go.Figure:
        """Renders comparative bar chart of composite ISS scores across pinned locations."""
        if ranked_df.empty:
            return go.Figure()
            
        fig = go.Figure(go.Bar(
            x=ranked_df["Name"],
            y=ranked_df["ISS"],
            marker_color=PRIMARY_BLUE,
            text=ranked_df["ISS"],
            textposition='auto',
            textfont=dict(color='#FFF', size=12, family='JetBrains Mono')
        ))
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(tickfont=dict(color=TEXT_PRIMARY, size=11, weight='bold')),
            yaxis=dict(
                range=[0, 100],
                showgrid=True,
                gridcolor=BORDER_SUBTLE,
                tickfont=dict(color=TEXT_SECONDARY),
                title=dict(text="Composite ISS", font=dict(color=TEXT_SECONDARY, size=11))
            ),
            margin=dict(l=10, r=10, t=10, b=10),
            height=280
        )
        return fig
