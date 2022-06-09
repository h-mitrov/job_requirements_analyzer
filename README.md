# Job requirements analyzer (web scraper with statistics)

This app helps you find out, what skills are most essential for Junior or Middle Python Developer. You get a JSON file with skills ranked by popularity.

It parses data from [Dou.ua](https://jobs.dou.ua/) and [Djinni.co](https://djinni.co/jobs/) and checks every relevant job description to find
mentions of more than 700 technologies, languages and libraries (for full list check [custom_skills.py](https://github.com/h-mitrov/job_requirements_analyzer/blob/master/custom_skills.py)
and [awesome-python](https://github.com/vinta/awesome-python)
repo).

Any feedback or advise would be really appreciated — I am on my way on becoming a Python developer, so I'd really love to learn from experienced colleagues everything I can.

## Instruments and libraries used
- [Playwright](https://playwright.dev/python/) — a web browser for working with dynamic web pages.
- [beautifulsoup4](https://pypi.org/project/beautifulsoup4/) — for getting data from pages.
- [aiohttp](https://docs.aiohttp.org/en/stable/) — for asynchronous web requests.
- [asyncio](https://docs.python.org/3/library/asyncio.html) — for running asynchronous requests.
- [re](https://docs.python.org/3/library/re.html) — for text searching.

## Results
As of 8th of Jun, 2022, after analyzing 100 jobs on Dou.ua and about 500 jobs on Djinni.co, main skills and technologies for Python Developer
are:
1. Python
2. AWS
3. Django
4. Docker
5. SQL
6. APIs
7. Flask
8. PostgreSQL
9. Linux
10. REST
11. JavaScript
12. Redis
13. MySQL
14. Pandas
15. Azure
16. CSS
17. FastAPI
18. Celery
19. Kafka
20. Pytorch

No data on QA, AQA, Seniors, Team Leads, DevOps or other jobs was analyzed. This statistics is true only for Middle or Junior
Python Developers. But you can make changes to the 'black_list' in  [main.py](https://github.com/h-mitrov/job_requirements_analyzer/blob/master/main.py) 
and run your own search. In this case, make sure to update the [custom_skills.py](https://github.com/h-mitrov/job_requirements_analyzer/blob/master/custom_skills.py)
as well (otherwise, the app won't know what to look for).


## How to run it locally
To run this app locally, stick to the following guide:

0. Clone the project from GitHub using whenever method you prefer. For example, if you're using PyCharm, here's a [guide on how to do this](https://www.jetbrains.com/help/pycharm/set-up-a-git-repository.html#clone-repo).
1. Create a virtual environment, for example using Virtualenv.
Type the following command to your terminal:
```bash
    virtualenv venv             
```
2. Activate the virtual environment:
```bash
    venv/scripts/activate              
```
3. Install the dependencies from the requirements.txt:
```bash
    pip install -r requirements.txt              
```

4. Go to the main.py and run the application.

## License
[MIT](https://choosealicense.com/licenses/mit/)
