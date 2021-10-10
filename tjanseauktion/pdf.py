from .team import Team

import os
from datetime import datetime

import markdown
from weasyprint import HTML

DATE = datetime.now()
TIMESTAMP = DATE.strftime('%d-%m-%Y')


class PDFWriter:

    @classmethod
    def write_to_pdf(cls, teams: list[Team]):
        file_name = f'tjanseauktion-{TIMESTAMP}'
        md = f'# Tjanseauktion {DATE.year}\n\n'

        for t in teams:
            md += f'## Team {t.id}\n\n'

            for c in t.chores:
                md += f'- {c.__str__()}\n'

            md += '\n'

        html = markdown.markdown(md)

        with open(f'{file_name}.html', 'w') as f:
            f.write(html)

        HTML(f'{file_name}.html', encoding='utf-8').write_pdf(f'{file_name}.pdf')
        os.remove(f'{file_name}.html')

