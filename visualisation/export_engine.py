import io
import json
import pandas as pd
from typing import Dict, List, Any, Tuple
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

class ExportEngine:
    """Handles report compilation, CSV breakdowns, GeoJSON assets, and professional PDF generation."""

    @staticmethod
    def export_csv(locations: List[Any], scenario_name: str = "Balanced Developer") -> str:
        """Compiles portfolio vector scores and composite statistics into a standard CSV format."""
        records = []
        for loc in locations:
            rec = {
                "Location Name": loc.name,
                "Latitude": loc.latitude,
                "Longitude": loc.longitude,
                "Radius (km)": loc.radius_km,
                "Composite ISS Score": loc.iss_score,
                "ISS Classification": loc.iss_classification,
                "Scenario Applied": scenario_name
            }
            # Unpack vector scores
            for vec, v_score in loc.vector_scores.items():
                # Supports Pydantic VectorScore or simple dicts
                score_val = v_score.score if hasattr(v_score, "score") else v_score.get("score", 50.0)
                rec[f"{vec} Score"] = score_val
                
                # Try raw values
                raw_val = v_score.raw_value if hasattr(v_score, "raw_value") else v_score.get("raw_value", 0.0)
                unit = v_score.unit if hasattr(v_score, "unit") else v_score.get("unit", "")
                rec[f"{vec} Raw Value ({unit})"] = raw_val
                
            records.append(rec)
            
        df = pd.DataFrame(records)
        return df.to_csv(index=False)

    @staticmethod
    def export_geojson(loc: Any) -> str:
        """Converts an analyzed location point into a structured GeoJSON asset."""
        scores = {}
        for vec, v_score in loc.vector_scores.items():
            scores[vec] = v_score.score if hasattr(v_score, "score") else v_score.get("score", 50.0)
            
        properties = {
            "name": loc.name,
            "latitude": loc.latitude,
            "longitude": loc.longitude,
            "radius_km": loc.radius_km,
            "composite_iss": loc.iss_score,
            "classification": loc.iss_classification,
            "vector_scores": scores
        }
        
        geojson = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [loc.longitude, loc.latitude]
            },
            "properties": properties
        }
        return json.dumps(geojson, indent=2)

    @staticmethod
    def generate_pdf_memo(
        loc_name: str,
        lat: float,
        lon: float,
        result: Any,
        memo_text: str,
        scenario_name: str = "Balanced Developer"
    ) -> bytes:
        """
        Compiles a professional PDF memo report using ReportLab.
        Includes a formal letterhead, tabular scorecards, and AI assessment narratives.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=54,
            leftMargin=54,
            topMargin=54,
            bottomMargin=54
        )
        
        styles = getSampleStyleSheet()
        
        # Custom Corporate styles
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=22,
            textColor=colors.HexColor("#1B6CA8"),
            spaceAfter=15
        )
        
        subtitle_style = ParagraphStyle(
            'DocSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            textColor=colors.HexColor("#8FA3B1"),
            spaceAfter=25
        )
        
        h1_style = ParagraphStyle(
            'H1',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=14,
            textColor=colors.HexColor("#1B6CA8"),
            spaceBefore=15,
            spaceAfter=8,
            keepWithNext=True
        )
        
        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#2C3E50"),
            spaceAfter=10
        )
        
        meta_label_style = ParagraphStyle(
            'MetaLabel',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10,
            textColor=colors.HexColor("#8FA3B1")
        )
        
        meta_val_style = ParagraphStyle(
            'MetaVal',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            textColor=colors.HexColor("#2C3E50")
        )

        story = []
        
        # 1. Letterhead Banner
        letterhead_data = [
            [Paragraph("RenewSense", title_style), Paragraph("INVESTMENT MEMORANDUM", ParagraphStyle('MemoHeader', fontName='Helvetica-Bold', fontSize=10, alignment=2, textColor=colors.HexColor("#8FA3B1")))]
        ]
        letterhead_table = Table(letterhead_data, colWidths=[3 * inch, 4 * inch])
        letterhead_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
            ('LINEBELOW', (0,0), (-1,-1), 1.5, colors.HexColor("#1B6CA8")),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ]))
        story.append(letterhead_table)
        story.append(Spacer(1, 15))
        
        # 2. Metadata Block
        meta_table_data = [
            [Paragraph("DATE:", meta_label_style), Paragraph(result.metadata.get("calculation_timestamp", "2026-05-24"), meta_val_style),
             Paragraph("LOCATION:", meta_label_style), Paragraph(f"{loc_name} ({lat:.4f}°, {lon:.4f}°)", meta_val_style)],
            [Paragraph("SCENARIO:", meta_label_style), Paragraph(scenario_name, meta_val_style),
             Paragraph("COMPOSITE ISS:", meta_label_style), Paragraph(f"<b>{result.iss_score:.1f}/100</b> ({result.iss_classification})", meta_val_style)]
        ]
        meta_table = Table(meta_table_data, colWidths=[1.2 * inch, 2.3 * inch, 1.2 * inch, 2.3 * inch])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8F9FA")),
            ('PADDING', (0,0), (-1,-1), 8),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 20))
        
        # 3. Vector Scores Card Grid
        story.append(Paragraph("Vector Performance Scorecard", h1_style))
        
        # Construct tabular score representation
        score_rows = [
            [Paragraph("<b>Vector Dimension</b>", meta_label_style), 
             Paragraph("<b>Raw Metric</b>", meta_label_style), 
             Paragraph("<b>Normalized Score</b>", meta_label_style)]
        ]
        
        for vec, v_score in result.vector_scores.items():
            # Color indicator for scores
            score_color = "#C0392B" if v_score.score < 30 else ("#E67E22" if v_score.score < 50 else ("#27AE60" if v_score.score > 70 else "#F1C40F"))
            score_p = Paragraph(f"<font color='{score_color}'><b>{v_score.score:.1f}</b></font>", meta_val_style)
            
            score_rows.append([
                Paragraph(vec, meta_val_style),
                Paragraph(f"{v_score.raw_value:.2f} {v_score.unit}", meta_val_style),
                score_p
            ])
            
        score_table = Table(score_rows, colWidths=[2.5 * inch, 2.5 * inch, 2 * inch])
        score_table.setStyle(TableStyle([
            ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
            ('PADDING', (0,0), (-1,-1), 6),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EDF2F7")),
        ]))
        story.append(score_table)
        story.append(Spacer(1, 20))
        
        # 4. Narratives (AI Memo)
        story.append(Paragraph("Geospatial & Risk Assessment Commentary", h1_style))
        
        # Split memo text by newlines or paragraphs and add to story
        paragraphs = memo_text.split('\n\n')
        for p_text in paragraphs:
            if not p_text.strip():
                continue
            # Basic styling/bold parsing
            text = p_text.replace('\n', '<br/>')
            # Check if it is a section header (e.g. "1. Executive Summary")
            if text.strip().startswith(("1.", "2.", "3.", "4.", "5.")):
                story.append(Paragraph(f"<b>{text}</b>", ParagraphStyle('SectionHeading', parent=body_style, fontName='Helvetica-Bold', fontSize=11, spaceBefore=8)))
            else:
                story.append(Paragraph(text, body_style))
                
        # Build PDF Document
        doc.build(story)
        
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes
