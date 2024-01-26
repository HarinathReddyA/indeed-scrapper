import random
import re
import time

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By


driver = webdriver.Chrome()


class Indeed_Scrapper:
    URL = "https://www.indeed.com/jobs?q={}&l={}"

    jobs_list = []

    def sleep(self):
        times = [1, 2]
        time.sleep(random.choice(times))

    def scrape_ids(seff, raw_jobs_list):
        """This method extract job ids from the raw html text recevied from the GET request

        Args:
           raw_jobs_list (list): List of jobs from GET request 
        """
        # List to store job ids

        content = BeautifulSoup(raw_jobs_list, 'lxml')

        for post in content.find_all('div', 'tapItem'):
            try:
                id = post.find('h2', 'jobTitle').find('a').get("id").split("_")[1]
                data = {
                    "indeed_id": id
                }
            except IndexError:
                continue
            Indeed_Scrapper.jobs_list.append(data)

    def get_current_ulr(self, url):
        """This method performs a GET request to the given URL and returns the response

        Args:
            url (string): URL link to be scrapped
        """
        # options = webdriver.ChromeOptions()
        # options.add_argument("headless")
        driver = webdriver.Chrome()
        driver.get(url)

        # Pagination
        while True:
            self.sleep()
            raw_job_lists = driver.find_element(By.CSS_SELECTOR, 'ul.jobsearch-ResultsList').get_attribute('innerHTML')
            self.scrape_ids(raw_job_lists)
            try:
                driver.find_element(By.CSS_SELECTOR, 'div.ecydgvn1:last-child') \
                    .find_element(By.CSS_SELECTOR, "a.e8ju0x50:last-child") \
                    .find_element(By.CSS_SELECTOR, "svg.eac13zx0:last-child").click()
            except Exception as e:
                break

    def scrape_job_ids(self, job: str, location: str):
        """This method scrapes the jobs based on input location from the URL

        Args:
            job (str): Name of the job to scrape
            location (str): Name of the place to find jobs
        """

        job = job.replace(" ", "+")
        location = location.replace(" ", "+")
        # generating URL
        url = Indeed_Scrapper.URL.format(job, location)

        # getting job ids
        self.get_current_ulr(url)

        return Indeed_Scrapper.jobs_list

    def extract_job_details(self, row):
        """This method extracts job details

        Args:
            row (Dataframe): A row in dataframe
        """
        global driver

        job_id = row["indeed_id"]
        url = "https://www.indeed.com/viewjob?jk=" + job_id
        self.sleep()
        driver.get(url)
        page_source = driver.page_source
        content = BeautifulSoup(page_source, 'lxml')
        job_title = content.find('h1', 'jobsearch-JobInfoHeader-title').text
        try:
            salary = content.find('div', 'jobsearch-JobMetadataHeader-item').text
        except:
            salary = "Not Available"
        try:
            company_name = content.find_all('div', {"data-company-name": "true"})[-1].find('a').text
        except:
            company_name = content.find_all('div', {"data-company-name": "true"})[-1].text
        full_job_description = content.find('div', 'jobsearch-jobDescriptionText').text
        complete_tag = str(content.find('div', 'jobsearch-jobDescriptionText')).replace("\n", "")

        sections = {}
        for b in content.find('div', 'jobsearch-jobDescriptionText').find_all('b'):
            tag = b.find_next()
            content = tag.text
            while content == "":
                tag = tag.find_next()
                content = tag.text
            content = content.replace("₹", "rs ").replace("$", "USD ").replace("\n", " ").strip()
            sections[b.text] = content

        job_title = job_title.replace(",", " ")
        salary = salary.replace(",", " ").replace("₹", "rs ").replace("$", "USD ")
        company_name = company_name.replace(",", " ")
        full_job_description = full_job_description.replace(",", " ").replace("\n", " ").strip()
        full_job_description = re.sub(' +', ' ', full_job_description)

        print("Processing: " + str(row["id"]) + " " + str(row["indeed_id"]))
        return pd.Series(
            dict(job_title=job_title, company_name=company_name, salary=salary,
                 full_job_description=full_job_description, sections=sections, complete_tag=complete_tag))
    # "content.find('div', 'jobsearch-jobDescriptionText').find_all('b')"
