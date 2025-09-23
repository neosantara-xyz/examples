import os
import json
import logging
from pathlib import Path
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
from autogen.coding import LocalCommandLineCodeExecutor

# Setup logging (AG2 best practice)
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
workdir = Path("event_invitations")
workdir.mkdir(exist_ok=True)

# Setup code executor
code_executor = UserProxyAgent(
    name="Code_Executor",
    system_message="Execute code and report results.",
    human_input_mode="NEVER",
    code_execution_config={"executor": LocalCommandLineCodeExecutor(work_dir=workdir)},
    max_consecutive_auto_reply=1,
)

# Agent 1: Guest Profiler
profiler = AssistantAgent(
    name="Profiler",
    llm_config={"config_list": config_list},
    system_message="""You are a Guest Profiler. Write Python code to read guests.csv and extract profiles for each guest. The CSV has columns: guest_id, name, language, formality, context. Output a JSON file with these fields to profiles.json in the working directory. Example code:

```python
import pandas as pd
import json
from pathlib import Path

# Check file existence
if not Path('guests.csv').exists():
    raise FileNotFoundError("guests.csv not found")

# Read CSV
df = pd.read_csv('guests.csv')

# Validate columns
required_columns = ['guest_id', 'name', 'language', 'formality', 'context']
if not all(col in df.columns for col in required_columns):
    raise ValueError("CSV missing required columns")

# Create profiles
profiles = df[required_columns].to_dict(orient='records')

# Save to JSON
with open('event_invitations/profiles.json', 'w') as f:
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
    system_message="""You are an Invitation Drafter. Read profiles.json and, for each guest, write a personalized invitation in markdown for a tech conference on 2025-10-01 at the Global Tech Hub. Use the guest's language (English, Spanish, Mandarin, Arabic, Indonesian) and formality (Formal, Semi-formal, Casual). Save to {guest_id}.md in the working directory. Example code:

```python
import json
from pathlib import Path

# Read profiles
with open('event_invitations/profiles.json', 'r') as f:
    profiles = json.load(f)

# Generate invitations
for profile in profiles:
    guest_id = profile['guest_id']
    name = profile['name']
    language = profile['language'].lower()
    formality = profile['formality'].lower()
    context = profile['context']

    # Customize invitation
    if language == 'english':
        if formality == 'formal':
            greeting = f"Dear {name},"
            body = "We are honored to invite you to the Global Tech Conference on October 1, 2025, at the Global Tech Hub. Your expertise as a {context} will greatly enrich our event."
            closing = "Sincerely,\nThe Conference Team"
        elif formality == 'semi-formal':
            greeting = f"Dear {name},"
            body = "We are excited to invite you to join us at the Global Tech Conference on October 1, 2025, at the Global Tech Hub. Your participation as a {context} will be invaluable."
            closing = "Best regards,\nThe Conference Team"
        else:  # casual
            greeting = f"Hi {name},"
            body = "We'd love for you to join us at the Global Tech Conference on Oct 1, 2025, at the Global Tech Hub! It'll be a blast, and your {context} vibe will make it even better."
            closing = "Cheers,\nThe Conference Team"
    elif language == 'spanish':
        if formality == 'formal':
            greeting = f"Estimado/a {name},"
            body = "Nos complace invitarle al Congreso Mundial de Tecnología el 1 de octubre de 2025 en el Global Tech Hub. Su experiencia como {context} enriquecerá nuestro evento."
            closing = "Atentamente,\nEl Equipo del Congreso"
        elif formality == 'semi-formal':
            greeting = f"Estimado/a {name},"
            body = "¡Estamos emocionados de invitarte al Congreso Mundial de Tecnología el 1 de octubre de 2025 en el Global Tech Hub! Tu participación como {context} será clave."
            closing = "Saludos cordiales,\nEl Equipo del Congreso"
        else:  # casual
            greeting = f"¡Hola {name}!"
            body = "Te invitamos al Congreso Mundial de Tecnología el 1 de oct de 2025 en el Global Tech Hub. ¡Va a estar genial, y tu energía como {context} lo hará aún mejor!"
            closing = "¡Un abrazo!\nEl Equipo del Congreso"
    elif language == 'mandarin':
        if formality == 'formal':
            greeting = f"尊敬的{name}先生/女士，"
            body = "我们很荣幸邀请您参加2025年10月1日在全球科技中心举办的全球科技大会。您作为{context}的专业知识将极大地丰富我们的活动。"
            closing = "此致\n敬礼，\n大会团队"
        elif formality == 'semi-formal':
            greeting = f"亲爱的{name}，"
            body = "我们诚邀您参加2025年10月1日在全球科技中心举办的全球科技大会。您作为{context}的参与将非常宝贵。"
            closing = "祝好，\n大会团队"
        else:  # casual
            greeting = f"嗨，{name}！"
            body = "我们邀请你来参加2025年10月1日在全球科技中心的全球科技大会！会超有趣的，你作为{context}的加入会让它更棒！"
            closing = "再见啦！\n大会团队"
    elif language == 'arabic':
        if formality == 'formal':
            greeting = f"السيد/السيدة {name} الموقر/ة،"
            body = "يسعدنا دعوتكم لحضور المؤتمر التقني العالمي في 1 أكتوبر 2025 في مركز التكنولوجيا العالمي. خبرتكم كـ{context} ستثري فعالياتنا بشكل كبير."
            closing = "مع أطيب التحيات،\nفريق المؤتمر"
        elif formality == 'semi-formal':
            greeting = f"عزيزي/عزيزتي {name}،"
            body = "ندعوكم بحماس لحضور المؤتمر التقني العالمي في 1 أكتوبر 2025 في مركز التكنولوجيا العالمي. مشاركتكم كـ{context} ستكون ذات قيمة كبيرة."
            closing = "تحياتنا،\nفريق المؤتمر"
        else:  # casual
            greeting = f"مرحبًا {name}!"
            body = "ندعوك للمشاركة في المؤتمر التقني العالمي يوم 1 أكتوبر 2025 في مركز التكنولوجيا العالمي! سيكون رائعًا، وطاقتك كـ{context} ستجعله أفضل!"
            closing = "إلى اللقاء!\nفريق المؤتمر"
    elif language == 'indonesian':
        if formality == 'formal':
            greeting = f"Yth. {name},"
            body = "Kami dengan hormat mengundang Anda untuk menghadiri Konferensi Teknologi Global pada 1 Oktober 2025 di Global Tech Hub. Keahlian Anda sebagai {context} akan sangat memperkaya acara kami."
            closing = "Hormat kami,\nTim Konferensi"
        elif formality == 'semi-formal':
            greeting = f"Dear {name},"
            body = "Kami senang mengundang Anda bergabung dalam Konferensi Teknologi Global pada 1 Oktober 2025 di Global Tech Hub. Partisipasi Anda sebagai {context} akan sangat berharga."
            closing = "Salam hangat,\nTim Konferensi"
        else:  # casual
            greeting = f"Hai {name}!"
            body = "Kami undang kamu ke Konferensi Teknologi Global tanggal 1 Okt 2025 di Global Tech Hub! Bakal seru banget, dan vibe kamu sebagai {context} pasti bikin makin asyik."
            closing = "Cheers!\nTim Konferensi"
    else:
        # Fallback to English casual
        greeting = f"Hi {name},"
        body = "We'd love for you to join us at the Global Tech Conference on Oct 1, 2025, at the Global Tech Hub!"
        closing = "Cheers,\nThe Conference Team"

    # Create invitation
    invitation = f"# Invitation for {name}\n\n{greeting}\n\n{body}\n\n{closing}"
    
    # Save to markdown
    with open(f'event_invitations/{guest_id}.md', 'w') as f:
        f.write(invitation)
    print(f"Invitation for {guest_id} generated.")
```

End with 'FINISH'.""",
    max_consecutive_auto_reply=1,
)

# Agent 3: Invitation Validator
validator = AssistantAgent(
    name="Validator",
    llm_config={"config_list": config_list},
    system_message="""You are an Invitation Validator. For each invitation in {guest_id}.md, read the file and check for tone consistency, cultural appropriateness, and language accuracy based on profiles.json. Output validation results to validation_{guest_id}.md. Example code:

```python
import json
from pathlib import Path

# Read profiles
with open('event_invitations/profiles.json', 'r') as f:
    profiles = json.load(f)

# Validate each invitation
for profile in profiles:
    guest_id = profile['guest_id']
    language = profile['language'].lower()
    formality = profile['formality'].lower()
    
    # Read invitation
    with open(f'event_invitations/{guest_id}.md', 'r') as f:
        invitation = f.read()
    
    # Validation checks
    tone_ok = formality in invitation.lower()
    lang_ok = language in invitation.lower() or any(word in invitation.lower() for word in ['dear', 'estimado', '尊敬', 'السيد', 'yth'] if language == 'english' else ['estimado', 'querido'] if language == 'spanish' else ['尊敬', '亲爱'] if language == 'mandarin' else ['السيد', 'عزيزي'] if language == 'arabic' else ['yth', 'dear', 'hai'] if language == 'indonesian' else False)
    suggestions = []
    if not tone_ok:
        suggestions.append(f"Tone does not match {formality} formality.")
    if not lang_ok:
        suggestions.append(f"Language does not match {language}.")
    
    # Create validation report
    validation = f"# Validation for {guest_id}\n\n- Tone: {'Consistent' if tone_ok else 'Inconsistent'}\n- Language: {'Correct' if lang_ok else 'Incorrect'}\n- Suggestions: {', '.join(suggestions) if suggestions else 'None'}"
    
    # Save validation
    with open(f'event_invitations/validation_{guest_id}.md', 'w') as f:
        f.write(validation)
    print(f"Validation for {guest_id} completed.")
```

End with 'FINISH'.""",
    max_consecutive_auto_reply=1,
)

# State transition function
def state_transition(last_speaker, groupchat):
    logger.info(f"Transitioning from {last_speaker.name}")
    if last_speaker is user_proxy:
        return profiler
    elif last_speaker in [profiler, drafter, validator]:
        return code_executor
    elif last_speaker is code_executor:
        last_second_speaker_name = groupchat.messages[-2]["name"]
        if "error" in groupchat.messages[-1]["content"].lower():
            logger.error(f"Error in {last_second_speaker_name} execution, retrying")
            return groupchat.agent_by_name(last_second_speaker_name)
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
user_proxy = UserProxyAgent(
    name="User",
    code_execution_config=False,
    is_termination_msg=lambda msg: "FINISH" in msg.get("content", ""),
    human_input_mode="NEVER",
    max_consecutive_auto_reply=1,
)
manager = GroupChatManager(
    groupchat=group_chat,
    llm_config={"config_list": config_list}
)

# Start personalization
logger.info("Starting invitation generation workflow")
user_proxy.initiate_chat(
    manager,
    message="Create personalized invitations for all guests in guests.csv for a tech conference on 2025-10-01 at the Global Tech Hub. Ensure each invitation matches the guest's language and formality preferences.",
    clear_history=True,
)
logger.info("Workflow completed")