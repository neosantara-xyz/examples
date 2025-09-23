import os
import json
import logging
from pathlib import Path
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
from autogen.coding import LocalCommandLineCodeExecutor

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Neosantara API configuration
config_list = [
    {
        "model": "nusantara-base",
        "base_url": "https://api.neosantara.xyz/v1",
        "api_key": os.environ.get("NAI_API_KEY"),
        "api_type": "openai",
        "stream": False,
        "price": [300/1000000*1000, 1500/1000000*1000]
    }
]

# Setup working directory
workdir = Path.cwd() / "event_invitations"
workdir.mkdir(exist_ok=True)

# Test API (uncomment to debug)
# from openai import OpenAI
# def test_api():
#     client = OpenAI(base_url="https://api.neosantara.xyz/v1", api_key=os.environ.get("NAI_API_KEY"))
#     try:
#         response = client.chat.completions.create(model="nusantara-base", messages=[{"role": "user", "content": "Test"}])
#         logger.info(f"API test response: {response.choices[0].message.content}")
#     except Exception as e:
#         logger.error(f"API test failed: {e}")
# test_api()

# Setup code executor
code_executor = UserProxyAgent(
    name="Code_Executor",
    system_message="Execute Python code to save files and report results.",
    human_input_mode="NEVER",
    code_execution_config={"executor": LocalCommandLineCodeExecutor(work_dir=workdir)},
    max_consecutive_auto_reply=2,
)

# User Proxy Agent
user_proxy = UserProxyAgent(
    name="User",
    code_execution_config=False,
    is_termination_msg=lambda msg: "FINISH" in msg.get("content", ""),
    human_input_mode="NEVER",
    max_consecutive_auto_reply=1,
)

# Agent 1: Guest Profiler
profiler = AssistantAgent(
    name="Profiler",
    llm_config={"config_list": config_list},
    system_message="""Write Python code to read guests.csv and save profiles (guest_id, name, language, formality, context) to event_invitations/profiles.json. Example:

```python
import pandas as pd
import json
from pathlib import Path

csv_path = Path.cwd() / 'guests.csv'
if not csv_path.exists():
    raise FileNotFoundError("guests.csv not found")
df = pd.read_csv(csv_path)
required_columns = ['guest_id', 'name', 'language', 'formality', 'context']
if not all(col in df.columns for col in required_columns):
    raise ValueError("CSV missing required columns")
profiles = df[required_columns].to_dict(orient='records')
with open(Path.cwd() / 'event_invitations/profiles.json', 'w') as f:
    json.dump(profiles, f, indent=4)
print("Profiles saved successfully.")
```

End with 'FINISH'.""",
    max_consecutive_auto_reply=1,
)

# Agent 2: Invitation Drafter
drafter = AssistantAgent(
    name="Drafter",
    llm_config={"config_list": config_list},
    system_message="""Write Python code to read event_invitations/profiles.json and generate a markdown invitation for each guest for a tech conference on 2025-10-01 at the Global Tech Hub. Use the guest's language (English, Indonesian) and formality (Formal, Semi-formal, Casual). Save to event_invitations/{guest_id}.md. If unable to generate, use a fallback English casual invitation. Example:

```python
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
profiles_path = Path.cwd() / 'event_invitations/profiles.json'
with open(profiles_path, 'r') as f:
    profiles = json.load(f)
for profile in profiles:
    guest_id = profile['guest_id']
    name = profile['name']
    language = profile['language'].lower()
    formality = profile['formality'].lower()
    context = profile['context']
    if language == 'english':
        if formality == 'formal':
            greeting = f"Dear {name},"
            body = "We are honored to invite you to the Global Tech Conference on October 1, 2025, at the Global Tech Hub. Your expertise as a {context} will enrich our event."
            closing = "Sincerely,\nThe Conference Team"
        elif formality == 'semi-formal':
            greeting = f"Dear {name},"
            body = "We are excited to invite you to the Global Tech Conference on October 1, 2025, at the Global Tech Hub. Your participation as a {context} will be invaluable."
            closing = "Best regards,\nThe Conference Team"
        else:  # casual
            greeting = f"Hi {name},"
            body = "Join us at the Global Tech Conference on Oct 1, 2025, at the Global Tech Hub! Your {context} vibe will make it awesome."
            closing = "Cheers,\nThe Conference Team"
    elif language == 'indonesian':
        if formality == 'formal':
            greeting = f"Yth. {name},"
            body = "Kami dengan hormat mengundang Anda ke Konferensi Teknologi Global pada 1 Oktober 2025 di Global Tech Hub. Keahlian Anda sebagai {context} akan memperkaya acara kami."
            closing = "Hormat kami,\nTim Konferensi"
        elif formality == 'semi-formal':
            greeting = f"Dear {name},"
            body = "Kami senang mengundang Anda ke Konferensi Teknologi Global pada 1 Oktober 2025 di Global Tech Hub. Partisipasi Anda sebagai {context} sangat berharga."
            closing = "Salam hangat,\nTim Konferensi"
        else:  # casual
            greeting = f"Hai {name}!"
            body = "Kami undang kamu ke Konferensi Teknologi Global tanggal 1 Okt 2025 di Global Tech Hub! Vibe kamu sebagai {context} pasti bikin seru."
            closing = "Cheers!\nTim Konferensi"
    else:
        greeting = f"Hi {name},"
        body = "Join us at the Global Tech Conference on Oct 1, 2025, at the Global Tech Hub!"
        closing = "Cheers,\nThe Conference Team"
    invitation = f"# Invitation for {name}\n\n{greeting}\n\n{body}\n\n{closing}"
    with open(Path.cwd() / f'event_invitations/{guest_id}.md', 'w') as f:
        f.write(invitation)
    print(f"Invitation for {guest_id} generated.")
print("All invitations generated successfully.")
```

End with 'FINISH'.""",
    max_consecutive_auto_reply=1,
)

# Agent 3: Invitation Validator
validator = AssistantAgent(
    name="Validator",
    llm_config={"config_list": config_list},
    system_message="""Write Python code to validate each invitation in event_invitations/{guest_id}.md for tone, language, and appropriateness based on event_invitations/profiles.json. Save results to event_invitations/validation_{guest_id}.md. Example:

```python
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
profiles_path = Path.cwd() / 'event_invitations/profiles.json'
with open(profiles_path, 'r') as f:
    profiles = json.load(f)
for profile in profiles:
    guest_id = profile['guest_id']
    language = profile['language'].lower()
    formality = profile['formality'].lower()
    with open(Path.cwd() / f'event_invitations/{guest_id}.md', 'r') as f:
        invitation = f.read()
    tone_ok = formality in invitation.lower()
    lang_ok = language in invitation.lower() or any(word in invitation.lower() for word in ['dear', 'yth'] if language == 'english' else ['yth', 'hai'] if language == 'indonesian' else False)
    suggestions = []
    if not tone_ok:
        suggestions.append(f"Tone does not match {formality} formality.")
    if not lang_ok:
        suggestions.append(f"Language does not match {language}.")
    validation = f"# Validation for {guest_id}\n\n- Tone: {'Consistent' if tone_ok else 'Inconsistent'}\n- Language: {'Correct' if lang_ok else 'Incorrect'}\n- Suggestions: {', '.join(suggestions) if suggestions else 'None'}"
    with open(Path.cwd() / f'event_invitations/validation_{guest_id}.md', 'w') as f:
        f.write(validation)
    print(f"Validation for {guest_id} completed.")
print("All validations completed successfully.")
```

End with 'FINISH'.""",
    max_consecutive_auto_reply=1,
)

# Fallback function to save default invitations
def save_default_invitations():
    logger.info("Executing fallback to save default invitations")
    profiles_path = Path.cwd() / 'event_invitations/profiles.json'
    try:
        with open(profiles_path, 'r') as f:
            profiles = json.load(f)
    except Exception as e:
        logger.error(f"Error reading profiles.json: {e}")
        return
    for profile in profiles:
        guest_id = profile['guest_id']
        name = profile['name']
        greeting = f"Hi {name},"
        body = "Join us at the Global Tech Conference on Oct 1, 2025, at the Global Tech Hub!"
        closing = "Cheers,\nThe Conference Team"
        invitation = f"# Invitation for {name}\n\n{greeting}\n\n{body}\n\n{closing}"
        try:
            with open(Path.cwd() / f'event_invitations/{guest_id}.md', 'w') as f:
                f.write(invitation)
            print(f"Fallback invitation for {guest_id} generated.")
        except Exception as e:
            logger.error(f"Error saving fallback invitation for {guest_id}: {e}")

# State transition function
def state_transition(last_speaker, groupchat):
    logger.info(f"Transitioning from {last_speaker.name}")
    if last_speaker is user_proxy:
        return profiler
    elif last_speaker in [profiler, drafter, validator]:
        return code_executor
    elif last_speaker is code_executor:
        last_second_speaker_name = groupchat.messages[-2]["name"]
        if "error" in groupchat.messages[-1]["content"].lower() or not groupchat.messages[-1]["content"].strip():
            logger.error(f"Error or empty response in {last_second_speaker_name} execution")
            if last_second_speaker_name == "Drafter":
                save_default_invitations()  # Run fallback
            return None  # Terminate to save tokens
        elif last_second_speaker_name == "Profiler":
            return drafter
        elif last_second_speaker_name == "Drafter":
            return validator
        elif last_second_speaker_name == "Validator":
            return None  # End conversation
    return None

# Group chat
group_chat = GroupChat(
    agents=[user_proxy, profiler, drafter, validator, code_executor],
    messages=[],
    max_round=12,
    speaker_selection_method=state_transition,
)

# Group chat manager
manager = GroupChatManager(
    groupchat=group_chat,
    llm_config={"config_list": config_list}
)

# Start personalization
logger.info("Starting invitation generation workflow")
try:
    user_proxy.initiate_chat(
        manager,
        message="Create personalized invitations for all guests in guests.csv for a tech conference on 2025-10-01 at the Global Tech Hub. Ensure each invitation matches the guest's language and formality preferences.",
        clear_history=True,
    )
except Exception as e:
    logger.error(f"Workflow failed: {e}")
    save_default_invitations()  # Ensure files are saved on failure
    raise
logger.info("Workflow completed")