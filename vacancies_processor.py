# standard library imports
import re
import json
import time
import asyncio
from urllib.request import urlopen


# third party imports
import aiohttp
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


async def gather_with_concurrency(n: int, *tasks: list):
    """
    This function helps to limit the number of simultaneous requests to Dou.ua or Djinni.co websites.

    :param n: Integer. The limit of simultaneous tasks.
    :param tasks: List. A list of coroutines that need to be executed.
    :return: It returns the result of coroutines execution.
    """
    semaphore = asyncio.Semaphore(n)

    async def sem_task(task):
        async with semaphore:
            return await task
    return await asyncio.gather(*(sem_task(task) for task in tasks))


class VacanciesProcessor:
    """
    Class that makes all the heavy lifting: parses the jobs, descriptions,
    analyzes skills popularity, etc.

    — 'vacancies' attribute stores a list of all jobs.
    — 'skills_rating' is an attribute that stores the skills rating.
    """
    vacancies = {'results': []}
    skills_rating = {'skills': []}

    def get_dou_vacancies(self, technology: str, banned_list: list) -> None:
        """
        This method parses relevant vacancies from Dou.ua. But not their descriptions.

        :param technology: Can be 'Python', 'Java', etc. But tested only with 'Python'.
        :param banned_list: A list of unwanted keywords you want to exclude from search.
        :return: None. Vacancies are automatically stored in the 'vacancies' object attribute.
        """
        vacancies_link = 'https://jobs.dou.ua/vacancies/?category={}'.format(technology.lower())

        with sync_playwright() as play:
            print('Opening browser...')
            browser = play.chromium.launch()
            page = browser.new_page()
            page.goto(vacancies_link)

            more_button = page.locator('text=Більше вакансій')

            while True:
                if more_button.is_visible():
                    more_button.click()
                    print('Clicked "More vacancies" button to load more entries')
                else:
                    break
                time.sleep(0.5)

            page_content = page.content()

            print('Parsing vacancies...')
            soup = BeautifulSoup(page_content, features='html.parser')

            for link in soup.findAll('a', class_='vt'):
                quality_link = True

                for banned_keyword in banned_list:
                    if banned_keyword in link.text:
                        quality_link = False
                        break

                if not quality_link:
                    continue

                dictionary = dict()
                dictionary['job_title'] = link.text
                dictionary['link'] = link.get('href')
                self.vacancies['results'].append(dictionary)

            browser.close()
            print('Collected all links. Processing...')

    async def get_djinni_vacancies(self, technology: str, banned_list: list) -> None:
        """
        This method parses relevant vacancies from Djinni.co. But not their descriptions.

        :param technology: Can be 'Python', 'Java', etc. But tested only with 'Python'.
        :param banned_list: A list of unwanted keywords you want to exclude from search.
        :return: None. Vacancies are automatically stored in the 'vacancies' object attribute.
        """
        vacancies_link = 'https://djinni.co/jobs/keyword-{}/'.format(technology.lower())

        async def process_one_page(url: str) -> None:
            """
            Processes a single search page once given an url.

            :param url: Link to Dou.ua or Djinni.co vacancy.
            :return: None. Vacancies are automatically stored in the 'vacancies' object attribute.
            """
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers={'User-Agent': 'Mozilla/5.0'}) as response:
                    html_code = await response.read()
                    soup = BeautifulSoup(html_code, features='html.parser')

                    for link in soup.findAll('a', class_='profile'):
                        quality_link = True

                        for banned_keyword in banned_list:
                            if banned_keyword in link.text:
                                quality_link = False
                                break

                        if not quality_link:
                            continue

                        dictionary = dict()
                        dictionary['job_title'] = link.text
                        dictionary['link'] = 'https://djinni.co{}'.format(link.get('href'))
                        self.vacancies['results'].append(dictionary)

        print('Launching Djinni parser...')

        first_response = str(urlopen(vacancies_link).read(), 'utf-8')
        soup = BeautifulSoup(first_response, features='html.parser')
        search = soup.findAll('a', class_='page-link')
        max_page = int(max([link.getText() for link in search]))

        links_list = [vacancies_link + '?page={}'.format(num) for num in range(2, max_page)]

        coroutines = []

        for link in links_list:
            coroutine = process_one_page(link)
            coroutines.append(coroutine)

        await gather_with_concurrency(15, *coroutines)
        print('Collected all links. Processing...')

    async def download_description(self, source: str, job: dict) -> dict:
        """
        This method adds a description to a certain vacancy (Dou.ua or Djinni.co).
        It updates the object's 'vacancies' attribute.

        :param source: String. Can be only 'Dou' or 'Djinni'.
        :param job: String. Can be only 'Python' or 'Java', etc. But tested only with 'Python'.
        :return: Dictionary. Adds 'description' key and its value.
        """
        async with aiohttp.ClientSession() as session:
            url = job.get('link')
            async with session.get(url, headers={'User-Agent': 'Mozilla/5.0'}) as response:
                html_code = await response.read()
                soup = BeautifulSoup(html_code, features='html.parser')
                try:
                    if source.lower() == 'dou':
                        job['description'] = soup.find('div', class_='vacancy-section').text
                    elif source.lower() == 'djinni':
                        job['description'] = soup.find('div', class_='row-mobile-order-2').text
                except:
                    print('Error with', url)
                return job

    async def download_all_descriptions(self, source: str) -> None:
        """
        This method downloads job descriptions for every job in the 'vacancies' attribute.
        And saves a JSON file with all vacancies.

        :param source: String. Can be only 'Dou' or 'Djinni'.
        :return: None. Vacancies are automatically updated in the 'vacancies' object attribute.
        """
        print('Downloading all job descriptions...')

        coroutines = []

        for job in self.vacancies.get('results'):
            coroutine = self.download_description(source=source, job=job)
            coroutines.append(coroutine)

        await gather_with_concurrency(15, *coroutines)

        print('Saving .json with vacancies to the hard drive...')
        with open('relevant_jobs.json', 'w', encoding='utf-8') as relevant_jobs:
            json.dump(self.vacancies, relevant_jobs, indent=4)

    def analyze_vacancies(self, tech_stack: set) -> None:
        """
        This method analyzes all skills, checking for matches in the vacancies' descriptions.

        :param tech_stack: Set. A set of skills that we are looking for.
        :return: None. The result is automatically stored in a JSON file.
        """

        jobs_quantity = len(self.vacancies.get('results'))

        print('Analyzing tech skills frequency...')

        for tech in tech_stack:
            mentions = 0
            for job in self.vacancies.get('results'):
                description = job.get('description').lower() if job.get('description') else ''
                matches = re.search(rf'\b{re.escape(tech.lower())}\b', description)
                if matches:
                    mentions += 1
            if mentions:
                dictionary = {'name': tech,
                              'mentioned_in_jobs': mentions,
                              'importance': round(mentions / jobs_quantity, 2)}

                self.skills_rating['skills'].append(dictionary)

        print('Sorting results...')
        self.skills_rating['skills'] = sorted(self.skills_rating['skills'], reverse=True, key=lambda x: x['importance'])

        with open('results.json', 'w', encoding='utf-8') as results:
            json.dump(self.skills_rating, results, indent=4)

        print('Success! Check the results.json for the skills statistics.')
