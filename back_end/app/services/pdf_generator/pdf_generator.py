import pdfkit
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pdfkit.configuration import Configuration

from app import schemas
from app.config import WKHTMLTOPDF_PATH
from app.log_config import logger

WKHTMLTOPDF_IO_ERROR_MESSAGE = "No wkhtmltopdf executable found at WKHTMLTOPDF_PATH, PDF generator not available."

config: Configuration | None = None
try:
    config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)
    PDF_GENERATOR_AVAILABLE = True
except IOError:
    logger.warning(WKHTMLTOPDF_IO_ERROR_MESSAGE)
    PDF_GENERATOR_AVAILABLE = False

options = {
    "page-size": "A4",
    "encoding": "UTF-8",
    "enable-local-file-access": "",
}


class PdfGenerator:
    def __init__(self):
        pass

    def generate_analysis_report(self, data: schemas.AnalysisReportData) -> bytes:
        """
        Generate analysis report PDF.

        :param data: The data.
        :returns: The PDF file bytes.
        """

        if not PDF_GENERATOR_AVAILABLE:
            raise Exception(WKHTMLTOPDF_IO_ERROR_MESSAGE)

        # Render template
        render = self.__render(data=data.model_dump(mode="json"), template="analysis-report.html")

        # Create PDF
        pdf_bytes = pdfkit.from_string(render, options=options, configuration=config)

        return pdf_bytes

    @staticmethod
    def __render(data: dict, template: str) -> str:
        """
        Render data into template.

        :param data: The data.
        :param template: The template.
        :returns: The HTML string.
        """

        env = Environment(
            loader=FileSystemLoader(
                [
                    "app/services/pdf_generator/templates",
                    "app/services/pdf_generator/macros",
                ]
            ),
            autoescape=select_autoescape(['html', 'xml'])
        )

        # Template
        j2_template = env.get_template(template)

        # Render template
        render = j2_template.render(data)

        return render
