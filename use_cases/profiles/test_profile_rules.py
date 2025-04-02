import json
from business_rules.variables import BaseVariables, string_rule_variable, select_multiple_rule_variable
from business_rules.actions import BaseActions, rule_action
from business_rules.fields import FIELD_TEXT, FIELD_SELECT_MULTIPLE
from business_rules import run_all
import smtplib  # For actual email sending (example)
from email.message import EmailMessage  # For actual email sending (example)

# --- Configuration (Replace with your actual email settings if sending real emails) ---
SMTP_SERVER = 'smtp.example.com'
SMTP_PORT = 587
SMTP_USERNAME = 'your_email@example.com'
SMTP_PASSWORD = 'your_app_password'  # Use App Password if using Gmail/etc.
SENDER_EMAIL = 'your_email@example.com'

# --- Define Variables ---
# How to get data points from a profile object


class ProfileVariables(BaseVariables):

    def __init__(self, profile):
        self.profile = profile

    @string_rule_variable
    def profile_email(self):
        # Crucial for the action
        return self.profile.get('email')

    @string_rule_variable
    def profile_name(self):
        # Good for personalization
        return self.profile.get('name')

    @string_rule_variable
    def business_unit(self):
        # Used in conditions
        return self.profile.get('business_unit')

    @string_rule_variable
    def job_title(self):
        # Used in conditions
        return self.profile.get('job_title')

    @string_rule_variable
    def personal_interests(self):
        # Used in conditions with 'contains' operator
        # Return empty list if missing
        return self.profile.get('personal_interests', '')

# --- Define Actions ---
# What to do when rules are met


class EmailActions(BaseActions):

    def __init__(self):
        # Can initialize email connection here if sending many emails
        pass

    @rule_action(params={
        "recipient_email": FIELD_TEXT,
        "recipient_name": FIELD_TEXT,
        "campaign_id": FIELD_TEXT  # Added parameter from rules.json
    })
    def send_targeted_email(self, recipient_email, recipient_name, campaign_id):
        if not recipient_email:
            print(
                f"ACTION SKIPPED: Missing email for profile name: {recipient_name or 'Unknown'}")
            return

        print(f"\n--- ACTION TRIGGERED ---")
        print(f"Rule Match Found! Preparing email for Campaign: {campaign_id}")
        print(
            f"  Recipient: {recipient_name or 'Valued Contact'} <{recipient_email}>")

        # ** SIMULATION **
        print(f"  SIMULATING Email Send:")
        subject = f"Information relevant to your interests ({campaign_id})"
        body = f"Dear {recipient_name or 'Valued Contact'},\n\nBased on your profile (e.g., role, interests), we thought you might find this information useful...\n\nBest regards,\nYour Company"
        print(f"  Subject: {subject}")
        print(f"  Body: {body[:100]}...")  # Print first 100 chars of body
        print(f"--- ACTION COMPLETE ---")

        # ** !! REAL EMAIL SENDING (Optional - Uncomment and Configure Carefully) !! **
        # msg = EmailMessage()
        # msg.set_content(body)
        # msg['Subject'] = subject
        # msg['From'] = SENDER_EMAIL
        # msg['To'] = recipient_email
        #
        # try:
        #     print("  Attempting REAL email send...")
        #     with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        #         server.starttls() # Secure connection
        #         server.login(SMTP_USERNAME, SMTP_PASSWORD)
        #         server.send_message(msg)
        #     print(f"  Successfully sent email to {recipient_email}")
        # except smtplib.SMTPAuthenticationError:
        #     print(f"  ERROR: SMTP Authentication failed. Check username/password.")
        # except smtplib.SMTPConnectError:
        #      print(f"  ERROR: Could not connect to SMTP server {SMTP_SERVER}:{SMTP_PORT}")
        # except Exception as e:
        #     print(f"  ERROR sending email to {recipient_email}: {e}")
        # print(f"--- ACTION COMPLETE (Real Send Attempted) ---")


# --- Main Execution ---
if __name__ == "__main__":
    # 1. Load Rules from JSON file
    RULES_FILE = './use_cases/profiles/rules_for_profile.json'
    try:
        with open(RULES_FILE, 'r') as f:
            loaded_rules = json.load(f)
        print("Successfully loaded rules from "+RULES_FILE)
    except FileNotFoundError:
        print(f"ERROR: {RULES_FILE} not found. Please create the file.")
        exit()
    except json.JSONDecodeError:
        print(f"ERROR: {RULES_FILE}  contains invalid JSON.")
        exit()

    # 2. ***** Sample Profile Data *****
    profiles = [
        {
            "id": 1, "name": "Alice Marketington", "email": "alice.m@example.com",
            "business_unit": "Marketing", "job_title": "Manager",
            "personal_interests": "Technology,Travel,Photography"  # Now a string
        },
        {
            "id": 2, "name": "Bob Marketer", "email": "bob.m@example.com",
            "business_unit": "Marketing", "job_title": "Specialist",
            "personal_interests": "Technology, Reading "  # String, note potential space
        },
        {
            "id": 3, "name": "Charlie Salesman", "email": "charlie.s@example.com",
            "business_unit": "Sales", "job_title": "Manager",
            "personal_interests": "Technology,Sports"  # String
        },
        {
            "id": 4, "name": "Diana Designer", "email": "diana.d@example.com",
            "business_unit": "Marketing", "job_title": "Manager",
            "personal_interests": "Art,Design"  # String
        },
        {
            "id": 5, "name": "Edward Engineer", "email": "ed.e@example.com",
            "business_unit": "Engineering", "job_title": "Developer",
            "personal_interests": "AI, Gaming, Technology"  # String with spaces
        },
        {
            "id": 6, "name": "Fiona Finance", "email": "fiona.f@example.com",
            "business_unit": "Finance", "job_title": "Analyst",
            "personal_interests": "Economics,AI"  # String
        },
        {
            "id": 7, "name": "George Engineer", "email": "george.e@example.com",
            "business_unit": "Engineering", "job_title": "Lead",
            "personal_interests": "Cloud,Hiking,"  # String with trailing comma
        },
        {
            "id": 8, "name": "Hannah HR", "email": "hannah.h@example.com",
            "business_unit": "HR", "job_title": "Coordinator",
            "personal_interests": ""  # Empty string case
        },
        {
            "id": 9, "name": "Ian IT", "email": "ian.i@example.com",
            "business_unit": "IT", "job_title": "Admin",
            # None value case (handled by .get default)
            "personal_interests": None
        }
    ]

    print(f"\nProcessing {len(profiles)} profiles...")

    # 3. Iterate through profiles and run rules (remains the same, includes previous debugging if needed)
    matches_found = 0
    for profile in profiles:
        print(
            f"\nChecking Profile ID: {profile.get('id', 'N/A')}, Name: {profile.get('name', 'N/A')}")

        # --- Optional Debugging ---
        # print("--- DEBUG: Inspecting ProfileVariables instance ---")
        # variables_instance = ProfileVariables(profile)
        # # ... (full debugging inspection code from previous answer if needed) ...
        # print("--- DEBUG: End Inspection ---")
        # ---

        try:
            # If not debugging, create instance directly here:
            variables_instance = ProfileVariables(profile)
            triggered = run_all(rule_list=loaded_rules,
                                defined_variables=variables_instance,
                                defined_actions=EmailActions(),
                                stop_on_first_trigger=True
                                )
            if triggered:
                matches_found += 1
            else:
                print("  No matching rules found for this profile.")
        except Exception as e:
            print(
                f"ERROR during run_all for profile {profile.get('id', 'N/A')}: {e}")
            # Optional: Re-raise if you want the script to stop fully on error
            # raise e

    print(f"\n--- Processing Complete ---")
    print(f"Total profiles processed: {len(profiles)}")
    print(f"Total profiles matching rules: {matches_found}")
