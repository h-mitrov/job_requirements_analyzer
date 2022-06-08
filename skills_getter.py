# standard library imports
import os
import re
from urllib.request import urlopen


def create_skills_list() -> set:
    """
    Creates a set of more than 700 frameworks, technologies, etc. from https://github.com/vinta/awesome-python.
    :return: set
    """
    source_link = 'https://raw.githubusercontent.com/vinta/awesome-python/master/README.md'
    skills_list = {'SQL',
                  'NoSQL'
                  'Git',
                  'Bash',
                  'Django',
                  'Flask',
                  'FastAPI',
                  'PostgreSQL',
                  'Docker',
                  'Linux',
                  'REST API',
                  'SQL',
                  'Redis',
                  'JSON',
                  'JavaScript',
                  'Celery',
                  'MySQL',
                  'Django',
                  'Rest Framework',
                  'AWS',
                  'Jira',
                  'API',
                  'REST',
                  'HTML',
                  'CSS',
                  'JavaScript',
                  'asyncio',
                  'OOP',
                  'scraping',
                  'regex',
                  'React',
                  'Angular',
                  'Node.js',
                  'Unix',
                  'Heroku',
                  'Odoo',
                  'Azure',
                  'PEP',
                  'SQLAlchemy',
                  'nginx',
                  'SQLite',
                  'PostgreSQL',
                  'TCP',
                  'Kafka',
                  'Pytest'
                  }

    # checking if we already downloaded the up-to-date technologies source file
    if not os.path.exists('raw_technologies_source.txt'):
        with open('raw_technologies_source.txt', 'w', encoding='utf-8') as tech_source_file:
            response = str(urlopen(source_link).read(), 'utf-8')
            tech_source_file.write(response)

    # creating a list of frameworks, technologies, libraries, etc.
    with open('raw_technologies_source.txt', 'r', encoding='utf-8') as tech_source_file:
        tech = re.findall(r'\[[^]]*]\(http', tech_source_file.read())
        skills_list.update([name.replace('[', '').replace('](http', '') for name in tech])

    return skills_list
