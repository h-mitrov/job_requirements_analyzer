# standard library imports
import asyncio

# local app imports
from skills_getter import create_skills_list
from vacancies_processor import VacanciesProcessor

black_list = ['Senior', 'Lead', 'QA', 'Automation', 'Data', 'Data Engineer', 'DevOps']

skills_list = create_skills_list()
app = VacanciesProcessor()


while True:
    decision = input('Would you like to parse jobs from dou.ua or from djinni.co?\nEnter 1 or 2: ')
    if decision == '1':
        app.get_dou_vacancies('Python', black_list)
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(app.download_all_descriptions(source='dou'))
        app.analyze_vacancies(skills_list)
        break

    elif decision == '2':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(app.get_djinni_vacancies('Python', black_list))
        asyncio.run(app.download_all_descriptions(source='djinni'))
        app.analyze_vacancies(skills_list)
        break

    else:
        print('Error. Choose another option.\n\n')
