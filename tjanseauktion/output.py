from .team import Team

from datetime import datetime
from typing import List

DATE = datetime.now()
TIMESTAMP = DATE.strftime('%d-%m-%Y')


class OutputWriter:

    @classmethod
    def write_to_pdf(cls, teams: List[Team]):
        file_name = f'tjanseauktion-{TIMESTAMP}'
        md = f'# Tjanseauktion {DATE.year}\n\n'

        for t in teams:
            md += f'## Team {t.id}\n\n'

            for c in t.chores:
                md += f'- {c.__str__()}\n'

            md += '\n'

        with open(f'{file_name}.md', 'w') as f:
            f.write(md)
