import json
from datetime import datetime

import pandas as pd

from indeed_scrapper import Indeed_Scrapper


def main():
    # intializing Indeed Scrapper Object
    indeed_scrapper_obj = Indeed_Scrapper()

    # reading config file
    try:
        configs = json.load(open('config.json', 'r'))
    except Exception as e:
        configs = {}
        print(e)

    # this list stores the paths of csv files with job ids
    job_ids_file_paths = []
    for i in configs.keys():
        config = configs[str(i)]
        for location in config["locations"]:
            job_ids_list = indeed_scrapper_obj.scrape_job_ids(config["job"], location)
            job_ids_df = pd.DataFrame(job_ids_list)
            job_ids_df.index.name = "id"

            job_ids_df_sub_path = config["job"] + "_" + location + "_" + str(datetime.now().date())
            job_ids_df_path = "extracted_jobs/"+job_ids_df_sub_path.replace(" ", "") + ".csv"
            job_ids_df.to_csv(job_ids_df_path, index=True)
            job_ids_file_paths.append(job_ids_df_path)

    # Extrating Job details
    for job_ids_file_path in job_ids_file_paths:
        # reading csv files with job ids
        job_ids_df = pd.read_csv(job_ids_file_path)

        # Extrating job details
        job_details_columns = job_ids_df.apply(indeed_scrapper_obj.extract_job_details, axis=1)

        # Updatating the job details
        job_details_df = job_ids_df.join(job_details_columns)

        # saving as CSV files
        csv_file_path = job_ids_file_path.split('.')[0] + "_job_details.csv"
        job_details_df.to_csv(csv_file_path, index=False)


main()
