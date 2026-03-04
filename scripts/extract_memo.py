import json
import os
import re


# ----------------------------
# Utility
# ----------------------------

def load_template():
    with open("scripts/schema_memo_template.json", "r") as f:
        return json.load(f)


def read_transcript(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Transcript not found at {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def clean_phrase(text):
    text = text.strip()
    text = re.sub(r'[\."]+$', '', text)

    # remove onboarding prefixes
    text = re.sub(
        r"^(an update for|update for|update regarding|this is an update for)\s+",
        "",
        text,
        flags=re.IGNORECASE
    )

    return text.title()


def clean_role(role):

    role = role.lower()

    role = re.sub(
        r"(immediately|right away|as soon as possible|now|promptly)",
        "",
        role
    )

    role = re.sub(r"\bthe\b", "", role)

    return clean_phrase(role)


# ----------------------------
# Company Name
# ----------------------------

def extract_company_name(text):

    patterns = [
        r"this is\s+(.+?)[\.\n]",
        r"thank you for calling\s+(.+?)[\.\n]",
        r"you have reached\s+(.+?)[\.\n]",
        r"welcome to\s+(.+?)[\.\n]"
    ]

    for pattern in patterns:

        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            return clean_phrase(match.group(1))

    return None


# ----------------------------
# Address
# ----------------------------

def extract_office_address(text):

    patterns = [

        r"office address is (.+?)[\.\n]",
        r"our office address is (.+?)[\.\n]",
        r"our office is located at (.+?)[\.\n]",
        r"located at (.+?)[\.\n]",
        r"based at (.+?)[\.\n]"
    ]

    for pattern in patterns:

        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            return clean_phrase(match.group(1))

    return None


# ----------------------------
# Phone Number
# ----------------------------

def extract_phone_number(text):

    pattern = r"\b\d{3}[-\.]\d{3}[-\.]\d{4}\b"

    match = re.search(pattern, text)

    if match:
        return match.group(0)

    return None


# ----------------------------
# Business Hours
# ----------------------------

def extract_business_hours(text):

    text_lower = text.lower()

    days = []
    start = ""
    end = ""
    timezone = ""

    day_order = [
        "monday","tuesday","wednesday",
        "thursday","friday","saturday","sunday"
    ]

    day_range_match = re.search(
        r"(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\s+(through|to|\-)\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)",
        text_lower
    )

    if day_range_match:

        start_day = day_range_match.group(1)
        end_day = day_range_match.group(3)

        start_index = day_order.index(start_day)
        end_index = day_order.index(end_day)

        days = [d.title() for d in day_order[start_index:end_index+1]]

    time_pattern = r'(\d{1,2})\s*(am|pm)\s*(to|\-)\s*(\d{1,2})\s*(am|pm)'

    match = re.search(time_pattern, text_lower)

    if match:

        start = f"{match.group(1)} {match.group(2).upper()}"
        end = f"{match.group(4)} {match.group(5).upper()}"

    for tz in ["central","eastern","mountain","pacific"]:
        if tz in text_lower:
            timezone = tz.title()

    return days, start, end, timezone


# ----------------------------
# Services
# ----------------------------

def extract_services(text):

    services = []

    patterns = [

        r"we provide (.+?)[\.\n]",
        r"we offer (.+?)[\.\n]",
        r"we handle (.+?)[\.\n]",
        r"our services include (.+?)[\.\n]",
        r"we specialize in (.+?)[\.\n]",
        r"we also offer (.+?)[\.\n]",
        r"we are also adding (.+?)[\.\n]",
        r"services include (.+?)[\.\n]"
        r"we provide (.+?)[\.\n]",
        r"we offer (.+?)[\.\n]",
        r"we handle (.+?)[\.\n]",
        r"our services include (.+?)[\.\n]",
        r"we specialize in (.+?)[\.\n]",

        # Variations
        r"we also provide (.+?)[\.\n]",
        r"we also offer (.+?)[\.\n]",
        r"we also handle (.+?)[\.\n]",

        # Additions / updates
        r"we have added (.+?)[\.\n]",
        r"we recently added (.+?)[\.\n]",
        r"we now offer (.+?)[\.\n]",
        r"we now provide (.+?)[\.\n]",
        r"we now support (.+?)[\.\n]",
        r"we now also support (.+?)[\.\n]",
        r"we now also provide (.+?)[\.\n]",

        # Company capability statements
        r"the company provides (.+?)[\.\n]",
        r"the company offers (.+?)[\.\n]",
        r"the business provides (.+?)[\.\n]",
        r"the business offers (.+?)[\.\n]",
        r"our services now include (.+?)[\.\n]",

        # Lists without verbs
        r"services include (.+?)[\.\n]",
        r"services provided include (.+?)[\.\n]",
        r"available services include (.+?)[\.\n]",

        # Feature additions
        r"additional services include (.+?)[\.\n]",
        r"new services include (.+?)[\.\n]"
    ]

    for pattern in patterns:

        matches = re.findall(pattern, text, re.IGNORECASE)

        for match in matches:

            parts = re.split(r",| and ", match)

            for part in parts:

                cleaned = clean_phrase(part)

                if cleaned:
                    services.append(cleaned)

    return list(dict.fromkeys(services))


# ----------------------------
# Emergency Definitions
# ----------------------------

def extract_emergency_definition(text):

    emergencies = []

    patterns = [

        r"emergencies include (.+?)[\.\n]",
        r"emergency situations include (.+?)[\.\n]",
        r"emergency situations now include (.+?)[\.\n]",
        r"emergencies also include (.+?)[\.\n]",
        r"an emergency includes (.+?)[\.\n]",
        r"(.+?) should be treated as an emergency",
        r"(.+?) are considered emergencies"
        r"emergencies include (.+?)[\.\n]",
        r"emergencies also include (.+?)[\.\n]",
        r"emergency situations include (.+?)[\.\n]",
        r"emergency situations also include (.+?)[\.\n]",
        r"emergency situations now also include (.+?)[\.\n]",
        r"emergency situations also include (.+?)[\.\n]",
        r"emergency conditions now also include (.+?)[\.\n]",
        r"emergency conditions also include (.+?)[\.\n]",
        r"emergency conditions include (.+?)[\.\n]",

        # Updated emergency lists
        r"emergency situations now include (.+?)[\.\n]",
        r"emergency situations now also include (.+?)[\.\n]",
        r"additional emergencies include (.+?)[\.\n]",

        # Definition statements
        r"situations considered emergencies include (.+?)[\.\n]",
        r"situations that count as emergencies include (.+?)[\.\n]",
        r"the following are emergencies: (.+?)[\.\n]",

        # Conditional definitions
        r"(.+?) should be treated as an emergency",
        r"(.+?) must be treated as an emergency",

        # Alternative phrasing
        r"(.+?) are considered emergencies",
        r"(.+?) are classified as emergencies",
        r"(.+?) qualify as emergencies"
    ]

    for pattern in patterns:

        matches = re.findall(pattern, text, re.IGNORECASE)

        for match in matches:

            parts = re.split(r",| or | and ", match)

            for part in parts:

                cleaned = clean_phrase(part)

                if cleaned:
                    emergencies.append(cleaned)

    return list(dict.fromkeys(emergencies))


# ----------------------------
# Routing Rules
# ----------------------------

def extract_emergency_routing_rules(text):

    rules = {
        "call_order": [],
        "fallback": ""
    }

    routing_patterns = [

        r"emergency.*?(?:routed|transferred|directed|sent) to (.+?)[\.\n]",
        r"(?:routed|transferred|directed|sent) to (.+?)[\.\n]",
        r"call the (.+?)[\.\n]"
    ]

    for pattern in routing_patterns:

        match = re.search(pattern, text, re.IGNORECASE)

        if match:

            role = clean_role(match.group(1))

            rules["call_order"].append({
                "role": role,
                "phone_number": ""
            })

            break

    fallback_patterns = [

        r"if .* does not answer,? (.+?)[\.\n]",
        r"if .* doesn't answer,? (.+?)[\.\n]",
        r"if no one answers,? (.+?)[\.\n]",
        r"if there is no response,? (.+?)[\.\n]",
        r"if unavailable,? (.+?)[\.\n]",
        r"if .* fails,? (.+?)[\.\n]"
    ]

    for pattern in fallback_patterns:

        match = re.search(pattern, text, re.IGNORECASE)

        if match:

            rules["fallback"] = clean_phrase(match.group(1))
            break

    return rules


# ----------------------------
# Non Emergency Routing
# ----------------------------

def extract_non_emergency_routing_rules(text):

    rules = {
        "during_business_hours": "",
        "after_hours": ""
    }

    patterns_during = [

        r"during .*?hours.*?non[- ]?emergency.*?should be (.+?)[\.\n]",
        r"during .*?hours.*?non[- ]?emergency.*?are (.+?)[\.\n]",
        r"during .*?hours.*?route non[- ]?emergency.*?to (.+?)[\.\n]",
        r"non[- ]?emergency.*?during .*?hours.*?should be (.+?)[\.\n]",
        r"non[- ]?emergency.*?during .*?hours.*?are (.+?)[\.\n]"
    ]

    for pattern in patterns_during:

        match = re.search(pattern, text, re.IGNORECASE)

        if match:

            rules["during_business_hours"] = clean_phrase(match.group(1))
            break

    patterns_after = [

        r"after hours.*?non[- ]?emergency.*?should be (.+?)[\.\n]",
        r"after hours.*?non[- ]?emergency.*?are (.+?)[\.\n]",
        r"after hours.*?route non[- ]?emergency.*?to (.+?)[\.\n]",
        r"non[- ]?emergency.*?after hours.*?should be (.+?)[\.\n]",
        r"non[- ]?emergency.*?after hours.*?are (.+?)[\.\n]"
    ]

    for pattern in patterns_after:

        match = re.search(pattern, text, re.IGNORECASE)

        if match:

            rules["after_hours"] = clean_phrase(match.group(1))
            break

    return rules


# ----------------------------
# Call Transfer Rules
# ----------------------------

def extract_call_transfer_rules(text):

    rules = {
        "timeout_seconds": None,
        "max_retries": None,
        "failure_message": ""
    }

    fallback_patterns = [

        r"if .* does not answer,? (.+?)[\.\n]",
        r"if .* doesn't answer,? (.+?)[\.\n]",
        r"if no one answers,? (.+?)[\.\n]",
        r"if there is no response,? (.+?)[\.\n]",
        r"if unavailable,? (.+?)[\.\n]"
    ]

    for pattern in fallback_patterns:

        match = re.search(pattern, text, re.IGNORECASE)

        if match:

            rules["timeout_seconds"] = 20
            rules["max_retries"] = 1
            rules["failure_message"] = clean_phrase(match.group(1))
            break

    return rules


# ----------------------------
# Integration Constraints
# ----------------------------

def extract_integration_constraints(text):

    constraints = []

    patterns = [

        r"never automatically (.+?)[\.\n]",
        r"do not automatically (.+?)[\.\n]",
        r"must not automatically (.+?)[\.\n]",
        r"manual review required for (.+?)[\.\n]"
    ]

    for pattern in patterns:

        matches = re.findall(pattern, text, re.IGNORECASE)

        for match in matches:

            constraints.append(clean_phrase(match))

    return list(dict.fromkeys(constraints))


# ----------------------------
# Office Hours Flow
# ----------------------------

def extract_office_hours_summary(text):

    patterns = [

        r"during business hours (.+?)[\.\n]",
        r"when open (.+?)[\.\n]",
        r"the receptionist should (.+?)[\.\n]"
    ]

    for pattern in patterns:

        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            return clean_phrase(match.group(1))

    return ""


# ----------------------------
# After Hours Summary
# ----------------------------

def build_after_hours_summary(text, emergency_rules):

    if "after hours" not in text.lower():
        return ""

    if not emergency_rules["call_order"]:
        return ""

    role = emergency_rules["call_order"][0]["role"]
    fallback = emergency_rules["fallback"]

    summary = f"After Hours Emergencies Are Routed To {role}"

    if fallback:
        summary += f". If Unavailable, {fallback}"

    return summary


# ----------------------------
# Core Builder
# ----------------------------

def create_account_memo(account_id, transcript_path):

    memo = load_template()

    text = read_transcript(transcript_path)

    memo["account_id"] = account_id

    company = extract_company_name(text)

    if company:
        memo["company_name"] = company
    else:
        memo["questions_or_unknowns"].append("Company name not clearly stated")

    address = extract_office_address(text)

    if address:
        memo["office_address"] = address

    phone = extract_phone_number(text)

    if phone:
        memo["phone_number"] = phone

    days, start, end, timezone = extract_business_hours(text)

    memo["business_hours"]["days"] = days
    memo["business_hours"]["start"] = start
    memo["business_hours"]["end"] = end
    memo["business_hours"]["timezone"] = timezone

    memo["services_supported"] = extract_services(text)

    memo["emergency_definition"] = extract_emergency_definition(text)

    emergency_rules = extract_emergency_routing_rules(text)

    memo["emergency_routing_rules"] = emergency_rules

    memo["non_emergency_routing_rules"] = extract_non_emergency_routing_rules(text)

    memo["call_transfer_rules"] = extract_call_transfer_rules(text)

    memo["integration_constraints"] = extract_integration_constraints(text)

    memo["after_hours_flow_summary"] = build_after_hours_summary(text, emergency_rules)

    memo["office_hours_flow_summary"] = extract_office_hours_summary(text)

    memo["notes"] = "Generated using rule-based extraction. Manual review recommended."

    return memo


def save_memo(memo, account_id, version="v1"):

    path = f"outputs/accounts/{account_id}/{version}"

    os.makedirs(path, exist_ok=True)

    with open(f"{path}/memo.json", "w") as f:
        json.dump(memo, f, indent=2)


# ----------------------------
# Entry
# ----------------------------

if __name__ == "__main__":

    account_id = "demo_001"
    transcript_path = "dataset/demo_001.txt"

    memo = create_account_memo(account_id, transcript_path)

    save_memo(memo, account_id, version="v1")

    print("Memo extracted successfully.")