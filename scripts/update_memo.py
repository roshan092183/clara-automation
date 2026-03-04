import json
import os
from extract_memo import create_account_memo


# ----------------------------
# Utility Functions
# ----------------------------

def load_json(path):

    with open(path, "r") as f:
        return json.load(f)


def save_json(path, data):

    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def merge_lists(old_list, new_list):

    merged = list(dict.fromkeys(old_list + new_list))

    return merged


def merge_dicts(old_dict, new_dict):

    merged = old_dict.copy()

    for key, value in new_dict.items():

        if value in ["", [], None]:
            continue

        merged[key] = value

    return merged


# ----------------------------
# Smart Merge Logic
# ----------------------------

def merge_memos(old_memo, new_memo):

    merged = old_memo.copy()
    changes = {}

    for key in new_memo:

        if key == "account_id":
            continue

        if key == "questions_or_unknowns":
            continue

        old_value = old_memo.get(key)
        new_value = new_memo.get(key)

        # Ignore empty values
        if new_value in ["", [], None]:
            continue

        # ----------------------------
        # LIST HANDLING
        # ----------------------------

        if isinstance(old_value, list) and isinstance(new_value, list):

            merged_list = merge_lists(old_value, new_value)

            if merged_list != old_value:

                merged[key] = merged_list

                changes[key] = {
                    "old": old_value,
                    "new": merged_list
                }

            continue

        # ----------------------------
        # DICTIONARY HANDLING
        # ----------------------------

        if isinstance(old_value, dict) and isinstance(new_value, dict):

            merged_dict = merge_dicts(old_value, new_value)

            if merged_dict != old_value:

                merged[key] = merged_dict

                changes[key] = {
                    "old": old_value,
                    "new": merged_dict
                }

            continue

        # ----------------------------
        # SIMPLE VALUE UPDATE
        # ----------------------------

        if old_value != new_value:

            merged[key] = new_value

            changes[key] = {
                "old": old_value,
                "new": new_value
            }

    return merged, changes


# ----------------------------
# Update Account Version
# ----------------------------

def update_account(account_id, onboarding_transcript):

    v1_path = f"outputs/accounts/{account_id}/v1/memo.json"

    if not os.path.exists(v1_path):
        raise Exception("v1 memo not found. Run extraction first.")

    # Load previous memo
    old_memo = load_json(v1_path)

    # Extract updated data
    new_memo = create_account_memo(account_id, onboarding_transcript)

    # Merge intelligently
    merged_memo, changes = merge_memos(old_memo, new_memo)

    # Create v2 directory
    v2_folder = f"outputs/accounts/{account_id}/v2"
    os.makedirs(v2_folder, exist_ok=True)

    v2_path = f"{v2_folder}/memo.json"

    save_json(v2_path, merged_memo)

    # Save change log
    changes_path = f"outputs/accounts/{account_id}/changes.json"
    save_json(changes_path, changes)

    print("Update completed successfully.")
    print("v2 memo saved.")
    print("Change log generated.")


# ----------------------------
# Entry Point
# ----------------------------

if __name__ == "__main__":

    account_id = "demo_001"

    onboarding_transcript = "dataset/onboarding_001.txt"

    update_account(account_id, onboarding_transcript)