import json
import os


# ----------------------------
# Load Memo
# ----------------------------

def load_memo(path):

    with open(path, "r") as f:
        return json.load(f)


# ----------------------------
# Build Agent Prompt
# ----------------------------

def build_agent_prompt(memo):

    company = memo.get("company_name", "")

    services = ", ".join(memo.get("services_supported", []))

    emergencies = ", ".join(memo.get("emergency_definition", []))

    transfer_role = ""
    routing = memo.get("emergency_routing_rules", {})

    if routing.get("call_order"):
        transfer_role = routing["call_order"][0].get("role", "")

    transfer_rules = memo.get("call_transfer_rules", {})
    fallback = transfer_rules.get("failure_message", "")

    address = memo.get("office_address", "")

    prompt = f"""
ROLE
You are the professional AI receptionist for {company}.
Your responsibility is to answer incoming calls, identify the caller’s needs, and route the call according to company procedures.

SUPPORTED SERVICES
The business provides the following services:
{services}

EMERGENCY CONDITIONS
Situations considered emergencies include:
{emergencies}

GENERAL BEHAVIOR RULES
• Be polite, professional, and concise.
• Ask only the minimum questions required for routing and dispatch.
• Never ask unnecessary questions.

------------------------------------------------
BUSINESS HOURS FLOW
------------------------------------------------

1. Greet the caller politely.
2. Ask how you can assist them today.
3. Identify the purpose of the call.
4. Collect the caller's name and phone number.
5. Determine if the request is an emergency or standard service request.

If emergency:
    Attempt to transfer the call to {transfer_role}

If non-emergency:
    Route according to company procedures.

TRANSFER FAILURE HANDLING
If the transfer fails:
{fallback}

After assisting the caller:
• Confirm next steps.
• Ask if there is anything else you can help with.
• Close the call politely.

------------------------------------------------
AFTER HOURS FLOW
------------------------------------------------

1. Greet the caller politely.
2. Ask how you can help.
3. Determine whether the issue is an emergency.

If emergency:
    Immediately collect:
        • caller name
        • phone number
        • service address

    Attempt to transfer the call to {transfer_role}

If transfer fails:
{fallback}

Assure the caller the team will respond quickly.

If it is not an emergency:
    Inform the caller the office is currently closed.
    Offer to take a message for the next business day.

After assisting the caller:
• Ask if there is anything else you can help with.
• Close the call politely.

------------------------------------------------
LOCATION INFORMATION
------------------------------------------------

If a caller asks about the office location, inform them the office address is:
{address}

------------------------------------------------
QUESTION POLICY
------------------------------------------------

Only ask questions required for routing and dispatch.
Do not ask unnecessary questions.
"""

    return prompt.strip()


# ----------------------------
# Build Agent Config
# ----------------------------

def build_agent_config(memo):

    company = memo.get("company_name", "Company")

    greeting = f"Thank you for calling {company}. How may I assist you today?"

    config = {
        "agent_name": f"{company} AI Receptionist",
        "greeting": greeting,
        "system_prompt": build_agent_prompt(memo),
        "services_supported": memo.get("services_supported", []),
        "emergency_conditions": memo.get("emergency_definition", []),
        "business_hours": memo.get("business_hours", {}),
        "call_transfer_rules": memo.get("call_transfer_rules", {}),
        "emergency_routing": memo.get("emergency_routing_rules", {}),
        "non_emergency_routing": memo.get("non_emergency_routing_rules", {})
    }

    # Include office address if present
    if memo.get("office_address"):
        config["office_address"] = memo["office_address"]

    # Include phone number if present
    if memo.get("phone_number"):
        config["phone_number"] = memo["phone_number"]

    return config


# ----------------------------
# Generate Agent Specs
# ----------------------------

def generate_agent_specs(account_id):

    base_folder = f"outputs/accounts/{account_id}"

    if not os.path.exists(base_folder):
        print("Account folder not found")
        return

    versions = os.listdir(base_folder)

    for version in versions:

        memo_path = f"{base_folder}/{version}/memo.json"

        if not os.path.exists(memo_path):
            continue

        memo = load_memo(memo_path)

        config = build_agent_config(memo)

        save_path = f"{base_folder}/{version}/agent_draft_spec.json"

        with open(save_path, "w") as f:
            json.dump(config, f, indent=2)

        print(f"Generated agent spec for {version}")


# ----------------------------
# Entry
# ----------------------------

if __name__ == "__main__":

    account_id = "demo_001"

    generate_agent_specs(account_id)