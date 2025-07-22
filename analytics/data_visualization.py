import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
import pandas as pd
import numpy as np
from dataclasses import dataclass, asdict
import warnings
warnings.filterwarnings('ignore')

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import plotly.offline as pyo
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

@dataclass
class ChartConfig:
    """차트 설정 클래스"""
    chart_type: str
    title: str
    x_label: str = ""
    y_label: str = ""
    width: int = 800
    height: int = 600
    colors: List[str] = None
    template: str = "plotly_white"
    show_legend: bool = True
    interactive: bool = True
    
    def __post_init__(self):
        if self.colors is None:
            self.colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

@dataclass
class ReportTemplate:
    """리포트 템플릿 클래스"""
    name: str
    title: str
    sections: List[Dict]
    layout: Dict
    styling: Dict
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class DataVisualization:
    """데이터 시각화 및 리포트 생성 시스템"""
    
    def __init__(self, config: Dict = None):
        self.config = config or self._get_default_config()
        self.logger = self._setup_logger()
        
        # 차트 저장소
        self.charts = {}
        self.chart_templates = {}
        
        # 리포트 저장소
        self.reports = {}
        self.report_templates = {}
        
        # 기본 차트 템플릿 설정
        self._setup_default_chart_templates()
        self._setup_default_report_templates()
    
    def _get_default_config(self) -> Dict:
        """기본 설정 반환"""
        return {
            "charts": {
                "default_width": 800,
                "default_height": 600,
                "default_template": "plotly_white",
                "color_palette": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"],
                "font_family": "Arial, sans-serif",
                "font_size": 12
            },
            "reports": {
                "default_format": "html",
                "include_charts": True,
                "include_tables": True,
                "include_summary": True,
                "auto_refresh": False
            },
            "export": {
                "formats": ["html", "png", "pdf"],
                "quality": "high",
                "include_metadata": True
            }
        }
    
    def _setup_logger(self) -> logging.Logger:
        """로거 설정"""
        logger = logging.getLogger('data_visualization')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _setup_default_chart_templates(self):
        """기본 차트 템플릿 설정"""
        self.chart_templates = {
            "line": {
                "type": "line",
                "default_config": {
                    "show_legend": True,
                    "interactive": True,
                    "template": "plotly_white"
                }
            },
            "bar": {
                "type": "bar",
                "default_config": {
                    "show_legend": True,
                    "interactive": True,
                    "template": "plotly_white"
                }
            },
            "pie": {
                "type": "pie",
                "default_config": {
                    "show_legend": True,
                    "interactive": True,
                    "template": "plotly_white"
                }
            },
            "scatter": {
                "type": "scatter",
                "default_config": {
                    "show_legend": True,
                    "interactive": True,
                    "template": "plotly_white"
                }
            },
            "heatmap": {
                "type": "heatmap",
                "default_config": {
                    "show_legend": True,
                    "interactive": True,
                    "template": "plotly_white"
                }
            }
        }
    
    def _setup_default_report_templates(self):
        """기본 리포트 템플릿 설정"""
        self.report_templates = {
            "executive_summary": ReportTemplate(
                name="executive_summary",
                title="경영진 요약 리포트",
                sections=[
                    {"name": "overview", "title": "개요", "type": "summary"},
                    {"name": "kpi_dashboard", "title": "KPI 대시보드", "type": "charts"},
                    {"name": "trends", "title": "트렌드 분석", "type": "charts"},
                    {"name": "recommendations", "title": "권장사항", "type": "text"}
                ],
                layout={"columns": 2, "rows": 2},
                styling={"theme": "professional", "color_scheme": "blue"}
            ),
            "detailed_analysis": ReportTemplate(
                name="detailed_analysis",
                title="상세 분석 리포트",
                sections=[
                    {"name": "data_overview", "title": "데이터 개요", "type": "summary"},
                    {"name": "statistical_analysis", "title": "통계 분석", "type": "charts"},
                    {"name": "trend_analysis", "title": "트렌드 분석", "type": "charts"},
                    {"name": "correlation_analysis", "title": "상관관계 분석", "type": "charts"},
                    {"name": "predictions", "title": "예측 분석", "type": "charts"},
                    {"name": "conclusions", "title": "결론", "type": "text"}
                ],
                layout={"columns": 3, "rows": 2},
                styling={"theme": "detailed", "color_scheme": "multi"}
            )
        }
    
    def create_line_chart(self, data: Dict, config: ChartConfig = None) -> Dict:
        """선 차트 생성"""
        if not PLOTLY_AVAILABLE:
            return {"error": "Plotly를 사용할 수 없습니다."}
        
        if config is None:
            config = ChartConfig("line", "Line Chart")
        
        try:
            x = data.get('x', [])
            y = data.get('y', [])
            
            fig = go.Figure()
            
            # 단일 선 또는 다중 선
            if isinstance(y[0], (list, tuple)):
                # 다중 선
                for i, y_series in enumerate(y):
                    fig.add_trace(go.Scatter(
                        x=x,
                        y=y_series,
                        mode='lines+markers',
                        name=data.get('names', [f'Series {i+1}'])[i] if 'names' in data else f'Series {i+1}',
                        line=dict(color=config.colors[i % len(config.colors)])
                    ))
            else:
                # 단일 선
                fig.add_trace(go.Scatter(
                    x=x,
                    y=y,
                    mode='lines+markers',
                    name=data.get('name', 'Data'),
                    line=dict(color=config.colors[0])
                ))
            
            fig.update_layout(
                title=config.title,
                xaxis_title=config.x_label,
                yaxis_title=config.y_label,
                width=config.width,
                height=config.height,
                template=config.template,
                showlegend=config.show_legend
            )
            
            chart_data = json.loads(fig.to_json())
            chart_id = f"line_chart_{int(datetime.now().timestamp())}"
            self.charts[chart_id] = chart_data
            
            return {
                "chart_id": chart_id,
                "chart_type": "line",
                "chart_data": chart_data,
                "config": asdict(config)
            }
            
        except Exception as e:
            return {"error": f"선 차트 생성 실패: {str(e)}"}
    
    def create_bar_chart(self, data: Dict, config: ChartConfig = None) -> Dict:
        """막대 차트 생성"""
        if not PLOTLY_AVAILABLE:
            return {"error": "Plotly를 사용할 수 없습니다."}
        
        if config is None:
            config = ChartConfig("bar", "Bar Chart")
        
        try:
            x = data.get('x', [])
            y = data.get('y', [])
            
            fig = go.Figure()
            
            # 단일 막대 또는 그룹 막대
            if isinstance(y[0], (list, tuple)):
                # 그룹 막대
                for i, y_series in enumerate(y):
                    fig.add_trace(go.Bar(
                        x=x,
                        y=y_series,
                        name=data.get('names', [f'Series {i+1}'])[i] if 'names' in data else f'Series {i+1}',
                        marker_color=config.colors[i % len(config.colors)]
                    ))
            else:
                # 단일 막대
                fig.add_trace(go.Bar(
                    x=x,
                    y=y,
                    name=data.get('name', 'Data'),
                    marker_color=config.colors[0]
                ))
            
            fig.update_layout(
                title=config.title,
                xaxis_title=config.x_label,
                yaxis_title=config.y_label,
                width=config.width,
                height=config.height,
                template=config.template,
                showlegend=config.show_legend
            )
            
            chart_data = json.loads(fig.to_json())
            chart_id = f"bar_chart_{int(datetime.now().timestamp())}"
            self.charts[chart_id] = chart_data
            
            return {
                "chart_id": chart_id,
                "chart_type": "bar",
                "chart_data": chart_data,
                "config": asdict(config)
            }
            
        except Exception as e:
            return {"error": f"막대 차트 생성 실패: {str(e)}"}
    
    def create_pie_chart(self, data: Dict, config: ChartConfig = None) -> Dict:
        """파이 차트 생성"""
        if not PLOTLY_AVAILABLE:
            return {"error": "Plotly를 사용할 수 없습니다."}
        
        if config is None:
            config = ChartConfig("pie", "Pie Chart")
        
        try:
            labels = data.get('labels', [])
            values = data.get('values', [])
            
            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=data.get('hole', 0),
                marker_colors=config.colors[:len(labels)]
            )])
            
            fig.update_layout(
                title=config.title,
                width=config.width,
                height=config.height,
                template=config.template,
                showlegend=config.show_legend
            )
            
            chart_data = json.loads(fig.to_json())
            chart_id = f"pie_chart_{int(datetime.now().timestamp())}"
            self.charts[chart_id] = chart_data
            
            return {
                "chart_id": chart_id,
                "chart_type": "pie",
                "chart_data": chart_data,
                "config": asdict(config)
            }
            
        except Exception as e:
            return {"error": f"파이 차트 생성 실패: {str(e)}"}
    
    def create_scatter_chart(self, data: Dict, config: ChartConfig = None) -> Dict:
        """산점도 차트 생성"""
        if not PLOTLY_AVAILABLE:
            return {"error": "Plotly를 사용할 수 없습니다."}
        
        if config is None:
            config = ChartConfig("scatter", "Scatter Chart")
        
        try:
            x = data.get('x', [])
            y = data.get('y', [])
            color = data.get('color', None)
            size = data.get('size', None)
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=x,
                y=y,
                mode='markers',
                name=data.get('name', 'Data'),
                marker=dict(
                    size=size if size else 8,
                    color=color if color else config.colors[0],
                    colorscale=data.get('colorscale', 'Viridis'),
                    showscale=color is not None
                )
            ))
            
            fig.update_layout(
                title=config.title,
                xaxis_title=config.x_label,
                yaxis_title=config.y_label,
                width=config.width,
                height=config.height,
                template=config.template,
                showlegend=config.show_legend
            )
            
            chart_data = json.loads(fig.to_json())
            chart_id = f"scatter_chart_{int(datetime.now().timestamp())}"
            self.charts[chart_id] = chart_data
            
            return {
                "chart_id": chart_id,
                "chart_type": "scatter",
                "chart_data": chart_data,
                "config": asdict(config)
            }
            
        except Exception as e:
            return {"error": f"산점도 차트 생성 실패: {str(e)}"}
    
    def create_heatmap_chart(self, data: Dict, config: ChartConfig = None) -> Dict:
        """히트맵 차트 생성"""
        if not PLOTLY_AVAILABLE:
            return {"error": "Plotly를 사용할 수 없습니다."}
        
        if config is None:
            config = ChartConfig("heatmap", "Heatmap Chart")
        
        try:
            z = data.get('z', [])
            x = data.get('x', [])
            y = data.get('y', [])
            
            fig = go.Figure(data=go.Heatmap(
                z=z,
                x=x,
                y=y,
                colorscale=data.get('colorscale', 'Viridis'),
                colorbar=dict(title=data.get('colorbar_title', 'Value'))
            ))
            
            fig.update_layout(
                title=config.title,
                xaxis_title=config.x_label,
                yaxis_title=config.y_label,
                width=config.width,
                height=config.height,
                template=config.template
            )
            
            chart_data = json.loads(fig.to_json())
            chart_id = f"heatmap_chart_{int(datetime.now().timestamp())}"
            self.charts[chart_id] = chart_data
            
            return {
                "chart_id": chart_id,
                "chart_type": "heatmap",
                "chart_data": chart_data,
                "config": asdict(config)
            }
            
        except Exception as e:
            return {"error": f"히트맵 차트 생성 실패: {str(e)}"}
    
    def create_dashboard(self, charts: List[Dict], layout: Dict = None) -> Dict:
        """대시보드 생성"""
        if not PLOTLY_AVAILABLE:
            return {"error": "Plotly를 사용할 수 없습니다."}
        
        if layout is None:
            layout = {"rows": 2, "cols": 2}
        
        try:
            rows = layout.get("rows", 2)
            cols = layout.get("cols", 2)
            
            fig = make_subplots(
                rows=rows, cols=cols,
                subplot_titles=[chart.get("title", f"Chart {i+1}") for i, chart in enumerate(charts[:rows*cols])],
                specs=[[{"secondary_y": False} for _ in range(cols)] for _ in range(rows)]
            )
            
            for i, chart_info in enumerate(charts[:rows*cols]):
                row = (i // cols) + 1
                col = (i % cols) + 1
                
                chart_data = chart_info.get("chart_data", {})
                if "data" in chart_data:
                    for trace in chart_data["data"]:
                        fig.add_trace(trace, row=row, col=col)
            
            fig.update_layout(
                title="대시보드",
                width=1200,
                height=800,
                template="plotly_white",
                showlegend=True
            )
            
            dashboard_data = json.loads(fig.to_json())
            dashboard_id = f"dashboard_{int(datetime.now().timestamp())}"
            
            return {
                "dashboard_id": dashboard_id,
                "dashboard_data": dashboard_data,
                "layout": layout,
                "charts_count": len(charts[:rows*cols])
            }
            
        except Exception as e:
            return {"error": f"대시보드 생성 실패: {str(e)}"}
    
    def create_report(self, template_name: str, data: Dict, 
                     charts: List[Dict] = None) -> Dict:
        """리포트 생성"""
        if template_name not in self.report_templates:
            return {"error": f"템플릿을 찾을 수 없습니다: {template_name}"}
        
        template = self.report_templates[template_name]
        
        try:
            report_content = {
                "title": template.title,
                "generated_at": datetime.now().isoformat(),
                "template": template_name,
                "sections": []
            }
            
            # 섹션별 콘텐츠 생성
            for section in template.sections:
                section_content = self._generate_section_content(
                    section, data, charts
                )
                report_content["sections"].append(section_content)
            
            # 리포트 저장
            report_id = f"report_{int(datetime.now().timestamp())}"
            self.reports[report_id] = report_content
            
            return {
                "report_id": report_id,
                "report_content": report_content,
                "template": asdict(template)
            }
            
        except Exception as e:
            return {"error": f"리포트 생성 실패: {str(e)}"}
    
    def _generate_section_content(self, section: Dict, data: Dict, 
                                charts: List[Dict]) -> Dict:
        """섹션 콘텐츠 생성"""
        section_type = section.get("type", "text")
        section_name = section.get("name", "")
        
        content = {
            "name": section_name,
            "title": section.get("title", ""),
            "type": section_type
        }
        
        if section_type == "summary":
            content["data"] = self._generate_summary_content(data, section_name)
        elif section_type == "charts":
            content["data"] = self._generate_charts_content(charts, section_name)
        elif section_type == "text":
            content["data"] = self._generate_text_content(data, section_name)
        elif section_type == "table":
            content["data"] = self._generate_table_content(data, section_name)
        
        return content
    
    def _generate_summary_content(self, data: Dict, section_name: str) -> Dict:
        """요약 콘텐츠 생성"""
        if section_name == "overview":
            return {
                "total_records": data.get("total_records", 0),
                "date_range": data.get("date_range", {}),
                "key_metrics": data.get("key_metrics", {}),
                "summary_text": data.get("summary_text", "데이터 분석이 완료되었습니다.")
            }
        elif section_name == "data_overview":
            return {
                "data_quality": data.get("data_quality", {}),
                "missing_values": data.get("missing_values", {}),
                "outliers": data.get("outliers", {}),
                "data_distribution": data.get("data_distribution", {})
            }
        
        return {"message": f"{section_name} 섹션의 요약 데이터"}
    
    def _generate_charts_content(self, charts: List[Dict], section_name: str) -> List[Dict]:
        """차트 콘텐츠 생성"""
        if not charts:
            return []
        
        # 섹션별 차트 필터링
        filtered_charts = []
        for chart in charts:
            if section_name in chart.get("tags", []) or section_name == "all":
                filtered_charts.append(chart)
        
        return filtered_charts[:4]  # 최대 4개 차트
    
    def _generate_text_content(self, data: Dict, section_name: str) -> Dict:
        """텍스트 콘텐츠 생성"""
        if section_name == "recommendations":
            return {
                "recommendations": data.get("recommendations", [
                    "데이터 품질을 개선하세요.",
                    "추가 분석이 필요합니다."
                ])
            }
        elif section_name == "conclusions":
            return {
                "conclusions": data.get("conclusions", [
                    "분석이 완료되었습니다.",
                    "추가 모니터링이 필요합니다."
                ])
            }
        
        return {"text": f"{section_name} 섹션의 텍스트 콘텐츠"}
    
    def _generate_table_content(self, data: Dict, section_name: str) -> Dict:
        """테이블 콘텐츠 생성"""
        if section_name == "statistical_analysis":
            return {
                "table_data": data.get("statistical_summary", []),
                "columns": ["Metric", "Value", "Description"]
            }
        
        return {"table_data": [], "columns": []}
    
    def export_chart(self, chart_id: str, format: str = "html", 
                    filepath: str = None) -> Dict:
        """차트 내보내기"""
        if chart_id not in self.charts:
            return {"error": f"차트를 찾을 수 없습니다: {chart_id}"}
        
        if not PLOTLY_AVAILABLE:
            return {"error": "Plotly를 사용할 수 없습니다."}
        
        try:
            chart_data = self.charts[chart_id]
            fig = go.Figure(chart_data)
            
            if format == "html":
                if filepath is None:
                    filepath = f"chart_{chart_id}.html"
                fig.write_html(filepath)
            elif format == "png":
                if filepath is None:
                    filepath = f"chart_{chart_id}.png"
                fig.write_image(filepath)
            elif format == "pdf":
                if filepath is None:
                    filepath = f"chart_{chart_id}.pdf"
                fig.write_image(filepath)
            else:
                return {"error": f"지원하지 않는 형식: {format}"}
            
            return {
                "success": True,
                "filepath": filepath,
                "format": format,
                "chart_id": chart_id
            }
            
        except Exception as e:
            return {"error": f"차트 내보내기 실패: {str(e)}"}
    
    def export_report(self, report_id: str, format: str = "html", 
                     filepath: str = None) -> Dict:
        """리포트 내보내기"""
        if report_id not in self.reports:
            return {"error": f"리포트를 찾을 수 없습니다: {report_id}"}
        
        try:
            report_content = self.reports[report_id]
            
            if format == "html":
                html_content = self._generate_html_report(report_content)
                if filepath is None:
                    filepath = f"report_{report_id}.html"
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                return {
                    "success": True,
                    "filepath": filepath,
                    "format": format,
                    "report_id": report_id
                }
            else:
                return {"error": f"지원하지 않는 형식: {format}"}
            
        except Exception as e:
            return {"error": f"리포트 내보내기 실패: {str(e)}"}
    
    def _generate_html_report(self, report_content: Dict) -> str:
        """HTML 리포트 생성"""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .section {{ margin-bottom: 30px; }}
                .section-title {{ font-size: 18px; font-weight: bold; margin-bottom: 15px; }}
                .chart-container {{ margin: 20px 0; }}
                .table {{ width: 100%; border-collapse: collapse; }}
                .table th, .table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                .table th {{ background-color: #f2f2f2; }}
                .summary {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{title}</h1>
                <p>생성일: {generated_at}</p>
            </div>
            
            {sections}
        </body>
        </html>
        """
        
        sections_html = ""
        for section in report_content["sections"]:
            section_html = f"""
            <div class="section">
                <div class="section-title">{section['title']}</div>
                {self._generate_section_html(section)}
            </div>
            """
            sections_html += section_html
        
        return html_template.format(
            title=report_content["title"],
            generated_at=report_content["generated_at"],
            sections=sections_html
        )
    
    def _generate_section_html(self, section: Dict) -> str:
        """섹션 HTML 생성"""
        section_type = section.get("type", "text")
        data = section.get("data", {})
        
        if section_type == "summary":
            return self._generate_summary_html(data)
        elif section_type == "charts":
            return self._generate_charts_html(data)
        elif section_type == "text":
            return self._generate_text_html(data)
        elif section_type == "table":
            return self._generate_table_html(data)
        
        return "<p>섹션 콘텐츠를 생성할 수 없습니다.</p>"
    
    def _generate_summary_html(self, data: Dict) -> str:
        """요약 HTML 생성"""
        html = '<div class="summary">'
        
        if "total_records" in data:
            html += f'<p><strong>총 레코드:</strong> {data["total_records"]:,}</p>'
        
        if "key_metrics" in data:
            html += '<h4>주요 지표:</h4><ul>'
            for key, value in data["key_metrics"].items():
                html += f'<li><strong>{key}:</strong> {value}</li>'
            html += '</ul>'
        
        if "summary_text" in data:
            html += f'<p>{data["summary_text"]}</p>'
        
        html += '</div>'
        return html
    
    def _generate_charts_html(self, charts: List[Dict]) -> str:
        """차트 HTML 생성"""
        html = ""
        for chart in charts:
            if "chart_data" in chart:
                html += f'<div class="chart-container" id="chart_{chart["chart_id"]}"></div>'
                html += f'<script>{chart["chart_data"]}</script>'
        return html
    
    def _generate_text_html(self, data: Dict) -> str:
        """텍스트 HTML 생성"""
        html = ""
        
        if "recommendations" in data:
            html += '<h4>권장사항:</h4><ul>'
            for rec in data["recommendations"]:
                html += f'<li>{rec}</li>'
            html += '</ul>'
        
        if "conclusions" in data:
            html += '<h4>결론:</h4><ul>'
            for conclusion in data["conclusions"]:
                html += f'<li>{conclusion}</li>'
            html += '</ul>'
        
        return html
    
    def _generate_table_html(self, data: Dict) -> str:
        """테이블 HTML 생성"""
        table_data = data.get("table_data", [])
        columns = data.get("columns", [])
        
        if not table_data:
            return "<p>테이블 데이터가 없습니다.</p>"
        
        html = '<table class="table">'
        
        # 헤더
        html += '<tr>'
        for col in columns:
            html += f'<th>{col}</th>'
        html += '</tr>'
        
        # 데이터
        for row in table_data:
            html += '<tr>'
            for cell in row:
                html += f'<td>{cell}</td>'
            html += '</tr>'
        
        html += '</table>'
        return html
    
    def get_chart_list(self) -> List[Dict]:
        """차트 목록 조회"""
        charts = []
        for chart_id, chart_data in self.charts.items():
            charts.append({
                "chart_id": chart_id,
                "chart_type": chart_data.get("layout", {}).get("title", "Unknown"),
                "created_at": datetime.now().isoformat()  # 실제로는 생성 시간을 저장해야 함
            })
        return charts
    
    def get_report_list(self) -> List[Dict]:
        """리포트 목록 조회"""
        reports = []
        for report_id, report_content in self.reports.items():
            reports.append({
                "report_id": report_id,
                "title": report_content.get("title", "Unknown"),
                "template": report_content.get("template", "Unknown"),
                "generated_at": report_content.get("generated_at", "")
            })
        return reports

# 사용 예시
if __name__ == "__main__":
    # 데이터 시각화 시스템 초기화
    viz = DataVisualization()
    
    # 샘플 데이터
    dates = pd.date_range('2024-01-01', periods=30, freq='D')
    values = np.random.randn(30).cumsum() + 100
    
    # 선 차트 생성
    line_chart = viz.create_line_chart({
        'x': dates.tolist(),
        'y': values.tolist(),
        'name': 'Daily Values'
    }, ChartConfig("line", "일별 값 추이", "날짜", "값"))
    
    print(f"선 차트 생성: {line_chart.get('chart_id', 'error')}")
    
    # 막대 차트 생성
    bar_chart = viz.create_bar_chart({
        'x': ['A', 'B', 'C', 'D', 'E'],
        'y': [10, 20, 15, 25, 30],
        'name': 'Category Values'
    }, ChartConfig("bar", "카테고리별 값", "카테고리", "값"))
    
    print(f"막대 차트 생성: {bar_chart.get('chart_id', 'error')}")
    
    # 파이 차트 생성
    pie_chart = viz.create_pie_chart({
        'labels': ['A', 'B', 'C', 'D'],
        'values': [30, 25, 20, 25]
    }, ChartConfig("pie", "비율 분포"))
    
    print(f"파이 차트 생성: {pie_chart.get('chart_id', 'error')}")
    
    # 대시보드 생성
    charts = [line_chart, bar_chart, pie_chart]
    dashboard = viz.create_dashboard(charts, {"rows": 2, "cols": 2})
    
    print(f"대시보드 생성: {dashboard.get('dashboard_id', 'error')}")
    
    # 리포트 생성
    report_data = {
        "total_records": 1000,
        "date_range": {"start": "2024-01-01", "end": "2024-01-30"},
        "key_metrics": {"평균": 100, "최대": 150, "최소": 50},
        "recommendations": ["데이터 품질 개선", "추가 분석 필요"],
        "conclusions": ["분석 완료", "모니터링 필요"]
    }
    
    report = viz.create_report("executive_summary", report_data, charts)
    print(f"리포트 생성: {report.get('report_id', 'error')}")
    
    # 차트 내보내기
    if 'chart_id' in line_chart:
        export_result = viz.export_chart(line_chart['chart_id'], "html")
        print(f"차트 내보내기: {export_result.get('filepath', 'error')}")
    
    # 리포트 내보내기
    if 'report_id' in report:
        export_result = viz.export_report(report['report_id'], "html")
        print(f"리포트 내보내기: {export_result.get('filepath', 'error')}") 