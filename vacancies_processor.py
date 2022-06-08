# standard library imports
import re
import json
import time
import asyncio
from urllib.request import urlopen, Request

# third party imports
import aiohttp
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


async def gather_with_concurrency(n, *tasks):
    semaphore = asyncio.Semaphore(n)

    async def sem_task(task):
        async with semaphore:
            return await task
    return await asyncio.gather(*(sem_task(task) for task in tasks))


class VacanciesProcessor:
    vacancies = {'results': []}
    skills_rating = {'skills': []}

    def get_dou_vacancies(self, technology: str, banned_list: list) -> None:
        vacancies_link = 'https://jobs.dou.ua/vacancies/?category={}'.format(technology)

        with sync_playwright() as play:
            print('Opening browser...')
            browser = play.chromium.launch()
            page = browser.new_page()
            page.goto(vacancies_link)

            more_button = page.locator('text=Більше вакансій')
            more_button_exists = True

            while more_button_exists:
                more_button.click()
                print('Clicked "More vacancies" button to load more entries')
                time.sleep(0.5)
                more_button_exists = more_button.is_visible()

            page_content = page.content()

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

    async def download_single_description(self, job: dict) -> dict:
        async with aiohttp.ClientSession() as session:
            url = job.get('link')
            async with session.get(url, headers={'User-Agent': 'Mozilla/5.0'}) as response:
                html_code = await response.read()
                soup = BeautifulSoup(html_code, features='html.parser')
                try:
                    job['description'] = soup.find('div', class_='vacancy-section').text
                except:
                    print('Error with', url)
                return job

    async def download_dou_descriptions(self) -> None:
        print('Collected all links. Processing...')
        print('Downloading all job descriptions...')

        start = time.time()
        coroutines = []

        for job in self.vacancies.get('results'):
            coroutine = self.download_single_description(job)
            coroutines.append(coroutine)

        await gather_with_concurrency(15, *coroutines)

        print('Saving .json with vacancies to the hard drive...')
        with open('relevant_jobs.json', 'w', encoding='utf-8') as relevant_jobs:
            json.dump(self.vacancies, relevant_jobs, indent=4)

    def analyze_vacancies(self, tech_stack: set) -> None:
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
