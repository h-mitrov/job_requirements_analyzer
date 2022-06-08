import asyncio

from skills_getter import create_skills_list
from vacancies_processor import VacanciesProcessor


black_list = ['Senior', 'Lead', 'QA', 'Automation', 'Data', 'Data Engineer']

skills_list = create_skills_list()
app = VacanciesProcessor()

app.get_dou_vacancies('Python', black_list)
asyncio.run(app.download_dou_descriptions())
app.analyze_vacancies(skills_list)




