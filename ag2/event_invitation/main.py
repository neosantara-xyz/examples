import os
import json
import logging
from pathlib import Path
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
from autogen.coding import LocalCommandLineCodeExecutor

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
config_list = [
    {
        "model": "nusantara-base",
        "base_url": "https://api.neosantara.xyz/v1",
        "api_key": os.environ.get("NAI_API_KEY"),
        "api_type": "openai",
        "stream": False,
        "max_tokens": 2000,
        "temperature": 0.3,
        "price": [300/1000000*1000, 1500/1000000*1000]
    }
]

# Dynamic workspace setup
def setup_workspace():
    current_dir = Path.cwd()
    if (current_dir / "guests.csv").exists():
        workdir = current_dir / "event_invitations"
    else:
        workdir = current_dir
    workdir.mkdir(exist_ok=True)
    logger.info(f"Working directory: {workdir}")
    return workdir

workdir = setup_workspace()

# Code executor
code_executor = UserProxyAgent(
    name="Code_Executor",
    system_message="Execute Python code and report results clearly.",
    human_input_mode="NEVER",
    code_execution_config={"executor": LocalCommandLineCodeExecutor(work_dir=workdir)},
    max_consecutive_auto_reply=1,
)

# User proxy
user_proxy = UserProxyAgent(
    name="User",
    code_execution_config=False,
    is_termination_msg=lambda msg: "FINISH" in msg.get("content", ""),
    human_input_mode="NEVER",
    max_consecutive_auto_reply=1,
)

# Agent 1: Profiler
profiler = AssistantAgent(
    name="Profiler",
    llm_config={"config_list": config_list},
    system_message="""Write Python code to find guests.csv and create profiles.json.

```python
import pandas as pd
import json
from pathlib import Path

def find_csv_file(filename='guests.csv'):
    current_dir = Path.cwd()
    print(f"Searching from: {current_dir}")
    
    search_paths = [
        current_dir / filename,
        current_dir.parent / filename,
        current_dir.parent.parent / filename
    ]
    
    for path in search_paths:
        if path.exists():
            print(f"Found CSV: {path}")
            return path
    
    raise FileNotFoundError(f"Could not find {filename}")

# Find and read CSV
csv_file = find_csv_file('guests.csv')
df = pd.read_csv(csv_file)
profiles = df.to_dict(orient='records')

# Save profiles
with open('profiles.json', 'w') as f:
    json.dump(profiles, f, indent=2)
    
print(f"SUCCESS: Saved {len(profiles)} profiles")
print(f"Columns: {list(df.columns)}")
```

End with: FINISH""",
    max_consecutive_auto_reply=1,
)

# Agent 2: Invitation Drafter
drafter = AssistantAgent(
    name="Drafter",
    llm_config={"config_list": config_list},
    system_message="""Write Python code to read profiles.json and generate personalized invitations.

Create markdown invitations for Tech Conference on 2025-10-01 at Global Tech Hub.

```python
import json
from pathlib import Path

# Read profiles
with open('profiles.json', 'r') as f:
    profiles = json.load(f)

print(f"Processing {len(profiles)} guests...")

for profile in profiles:
    guest_id = profile['guest_id']
    name = profile['name']
    language = profile.get('language', 'English').lower()
    formality = profile.get('formality', 'casual').lower()
    context = profile.get('context', 'participant')
    
    print(f"Creating invitation for {name} ({language}, {formality})")
    
    # Generate invitation based on language and formality
    if language == 'english':
        if formality == 'formal':
            greeting = f"Dear Mr./Ms. {name},"
            body = f"We are honored to invite you to the Global Tech Conference on October 1, 2025, at the Global Tech Hub. Your expertise as a {context} will greatly enrich our event. We look forward to your valuable participation."
            closing = "Respectfully yours,\\nThe Conference Organizing Committee"
        elif formality == 'semi-formal':
            greeting = f"Dear {name},"
            body = f"We are excited to invite you to the Global Tech Conference on October 1, 2025, at the Global Tech Hub. Your participation as a {context} will be invaluable to our community. We hope you can join us for this exciting event."
            closing = "Best regards,\\nThe Conference Team"
        else:  # casual
            greeting = f"Hi {name}!"
            body = f"You're invited to our awesome Global Tech Conference on Oct 1, 2025, at the Global Tech Hub! Your {context} vibe will make it even better. Can't wait to see you there!"
            closing = "Cheers,\\nThe Conference Team"
    
    elif language == 'indonesian':
        if formality == 'formal':
            greeting = f"Yth. Bapak/Ibu {name},"
            body = f"Dengan hormat, kami mengundang Anda untuk menghadiri Konferensi Teknologi Global pada tanggal 1 Oktober 2025 di Global Tech Hub. Keahlian Anda sebagai {context} akan sangat memperkaya acara kami. Kami berharap Anda dapat berpartisipasi dalam acara penting ini."
            closing = "Hormat kami,\\nPanitia Penyelenggara Konferensi"
        elif formality == 'semi-formal':
            greeting = f"Halo {name},"
            body = f"Kami dengan senang hati mengundang Anda ke Konferensi Teknologi Global pada 1 Oktober 2025 di Global Tech Hub. Partisipasi Anda sebagai {context} sangat kami harapkan untuk kesuksesan acara ini."
            closing = "Salam hangat,\\nTim Konferensi"
        else:  # casual
            greeting = f"Hai {name}!"
            body = f"Yuk gabung di Konferensi Teknologi Global kita tanggal 1 Oktober 2025 di Global Tech Hub! Vibe kamu sebagai {context} pasti bikin acara makin seru!"
            closing = "Sampai jumpa!\\nTim Konferensi"
    
    else:  # fallback to English casual
        greeting = f"Hi {name}!"
        body = f"Join us at the Global Tech Conference on Oct 1, 2025, at the Global Tech Hub! Looking forward to seeing you there."
        closing = "Best regards,\\nThe Conference Team"
    
    # Create markdown invitation
    invitation = f"\"\"# Invitation - {name}

{greeting}

{body}

**Event Details:**
- Date: October 1, 2025
- Venue: Global Tech Hub
- Type: Technology Conference

{closing}
"\"\"
    
    # Save invitation
    filename = f"invitation_{guest_id}.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(invitation)
    
    print(f"✓ Saved {filename}")

print("SUCCESS: All invitations generated!")
```

End with: FINISH""",
    max_consecutive_auto_reply=1,
)

# Agent 3: Validator
validator = AssistantAgent(
    name="Validator",
    llm_config={"config_list": config_list},
    system_message="""Write Python code to validate all generated invitations.

Check tone, language appropriateness, and completeness.

```python
import json
import glob
from pathlib import Path

# Read profiles for reference
with open('profiles.json', 'r') as f:
    profiles = json.load(f)

print("=== INVITATION VALIDATION ===\\n")

validation_results = []
invitation_files = glob.glob("invitation_*.md")

print(f"Found {len(invitation_files)} invitation files")

for profile in profiles:
    guest_id = profile['guest_id']
    name = profile['name']
    expected_language = profile.get('language', 'English').lower()
    expected_formality = profile.get('formality', 'casual').lower()
    
    invitation_file = f"invitation_{guest_id}.md"
    
    if invitation_file not in invitation_files:
        result = {
            'guest_id': guest_id,
            'name': name,
            'status': 'MISSING',
            'issues': ['Invitation file not found'],
            'score': 0
        }
        validation_results.append(result)
        print(f"❌ {name}: MISSING FILE")
        continue
    
    # Read invitation content
    with open(invitation_file, 'r', encoding='utf-8') as f:
        content = f.read().lower()
    
    issues = []
    score = 100
    
    # Check language consistency
    if expected_language == 'indonesian':
        indonesian_indicators = ['yth', 'dengan hormat', 'kami', 'anda', 'oktober', 'hai']
        if not any(indicator in content for indicator in indonesian_indicators):
            issues.append('Language mismatch - expected Indonesian')
            score -= 30
    elif expected_language == 'english':
        english_indicators = ['dear', 'we are', 'october', 'conference', 'regards']
        if not any(indicator in content for indicator in english_indicators):
            issues.append('Language mismatch - expected English')  
            score -= 30
    
    # Check formality level
    formal_indicators = ['dear mr./ms.', 'honored', 'respectfully', 'yth.', 'dengan hormat']
    casual_indicators = ['hi ', 'hey', 'awesome', 'yuk', 'hai']
    
    has_formal = any(indicator in content for indicator in formal_indicators)
    has_casual = any(indicator in content for indicator in casual_indicators)
    
    if expected_formality == 'formal' and not has_formal:
        issues.append('Tone too casual for formal requirement')
        score -= 20
    elif expected_formality == 'casual' and has_formal and not has_casual:
        issues.append('Tone too formal for casual requirement')
        score -= 20
    
    # Check essential elements
    required_elements = ['october 1, 2025', 'global tech hub', 'conference']
    missing_elements = [elem for elem in required_elements if elem not in content]
    if missing_elements:
        issues.append(f'Missing elements: {", ".join(missing_elements)}')
        score -= 15 * len(missing_elements)
    
    # Check completeness
    if len(content) < 100:
        issues.append('Invitation too short')
        score -= 10
    
    if name.lower() not in content:
        issues.append('Guest name not found in invitation')
        score -= 25
    
    # Determine status
    if score >= 80:
        status = 'EXCELLENT'
        emoji = '🌟'
    elif score >= 60:
        status = 'GOOD'
        emoji = '✅'
    elif score >= 40:
        status = 'NEEDS IMPROVEMENT'
        emoji = '⚠️'
    else:
        status = 'POOR'
        emoji = '❌'
    
    result = {
        'guest_id': guest_id,
        'name': name,
        'status': status,
        'score': score,
        'issues': issues
    }
    validation_results.append(result)
    
    print(f"{emoji} {name}: {status} (Score: {score}/100)")
    if issues:
        for issue in issues:
            print(f"   • {issue}")

# Save validation report
with open('validation_report.json', 'w') as f:
    json.dump(validation_results, f, indent=2)

# Summary statistics
total = len(validation_results)
excellent = len([r for r in validation_results if r['score'] >= 80])
good = len([r for r in validation_results if 60 <= r['score'] < 80])
poor = len([r for r in validation_results if r['score'] < 60])
avg_score = sum(r['score'] for r in validation_results) / total if total > 0 else 0

print(f"\\n=== VALIDATION SUMMARY ===")
print(f"Total invitations: {total}")
print(f"Excellent (80+): {excellent}")
print(f"Good (60-79): {good}")
print(f"Needs work (<60): {poor}")
print(f"Average score: {avg_score:.1f}/100")
print(f"\\nDetailed report saved to validation_report.json")
```

End with: FINISH""",
    max_consecutive_auto_reply=1,
)

# State transition
def state_transition(last_speaker, groupchat):
    logger.info(f"Transition from: {last_speaker.name}")
    
    if last_speaker is user_proxy:
        return profiler
    elif last_speaker in [profiler, drafter, validator]:
        return code_executor
    elif last_speaker is code_executor:
        last_message = groupchat.messages[-1]["content"]
        
        # Check for errors
        error_indicators = ["error", "traceback", "exception", "failed"]
        has_error = any(indicator in last_message.lower() for indicator in error_indicators)
        
        if has_error or not last_message.strip():
            logger.error("Code execution failed")
            return None
            
        # Determine next agent based on previous speaker
        if len(groupchat.messages) >= 2:
            prev_speaker = groupchat.messages[-2]["name"]
            if prev_speaker == "Profiler":
                logger.info("Moving to Drafter")
                return drafter
            elif prev_speaker == "Drafter":
                logger.info("Moving to Validator") 
                return validator
            elif prev_speaker == "Validator":
                logger.info("Workflow complete")
                return None
    
    return None

# Group chat setup
group_chat = GroupChat(
    agents=[user_proxy, profiler, drafter, validator, code_executor],
    messages=[],
    max_round=15,
    speaker_selection_method=state_transition,
)

manager = GroupChatManager(
    groupchat=group_chat,
    llm_config={"config_list": config_list}
)

# Main execution
if __name__ == "__main__":
    logger.info("Starting COMPLETE invitation workflow")
    
    try:
        user_proxy.initiate_chat(
            manager,
            message="Create complete personalized invitations: 1) Process guests.csv, 2) Generate personalized invitations for each guest, 3) Validate all invitations",
            clear_history=True,
        )
        
        # Check final results
        results = {
            'profiles': workdir / "profiles.json",
            'invitations': list(workdir.glob("invitation_*.md")),
            'validation': workdir / "validation_report.json"
        }
        
        print("\n" + "="*50)
        print("FINAL RESULTS:")
        print("="*50)
        
        if results['profiles'].exists():
            with open(results['profiles']) as f:
                profiles = json.load(f)
            print(f"✅ Profiles: {len(profiles)} guests processed")
        
        print(f"✅ Invitations: {len(results['invitations'])} files created")
        for inv_file in results['invitations']:
            print(f"   - {inv_file.name}")
        
        if results['validation'].exists():
            with open(results['validation']) as f:
                validation = json.load(f)
            avg_score = sum(r['score'] for r in validation) / len(validation)
            print(f"✅ Validation: Average score {avg_score:.1f}/100")
        
        print("="*50)
        logger.info("COMPLETE workflow finished successfully!")
        
    except Exception as e:
        logger.error(f"Complete workflow failed: {e}")
        raise