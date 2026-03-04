import os
from extract_memo import create_account_memo, save_memo
from update_memo import update_account
from generate_agent_config import generate_agent_specs


DATASET_FOLDER = "dataset"


def run_demo_extractions():

    for file in os.listdir(DATASET_FOLDER):

        if file.startswith("demo_"):
            
            account_id = file.replace("demo_", "").replace(".txt", "")

            transcript_path = os.path.join(DATASET_FOLDER, file)

            memo = create_account_memo(account_id, transcript_path)

            save_memo(memo, account_id, version="v1")

            print(f"Demo extraction completed for {account_id}")


def run_onboarding_updates():

    for file in os.listdir(DATASET_FOLDER):

        if file.startswith("onboarding_"):

            account_id = file.replace("onboarding_", "").replace(".txt", "")

            transcript_path = os.path.join(DATASET_FOLDER, file)

            update_account(account_id, transcript_path)

            print(f"Onboarding update completed for {account_id}")


def generate_agents():

    accounts_folder = "outputs/accounts"

    for account_id in os.listdir(accounts_folder):

        generate_agent_specs(account_id)

        print(f"Agent specs generated for {account_id}")


if __name__ == "__main__":

    print("Running demo extraction pipeline...")
    run_demo_extractions()

    print("Running onboarding update pipeline...")
    run_onboarding_updates()

    print("Generating agent specs...")
    generate_agents()

    print("Pipeline completed successfully.")