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
        "max_tokens": 1500,
        "temperature": 0.3,
        "price": [300/1000000*1000, 1500/1000000*1000]
    }
]

# Setup working directory
workdir = Path.cwd() / "event_invitations"
workdir.mkdir(exist_ok=True)

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

# Smart Profiler - auto-detects file paths
profiler = AssistantAgent(
    name="Profiler",
    llm_config={"config_list": config_list},
    system_message="""You must write Python code to read guests.csv and save profiles to profiles.json.

Auto-detect the CSV file location and use dynamic paths:

```python
import pandas as pd
import json
from pathlib import Path
import os

def find_csv_file(filename='guests.csv'):
    "\"\"Search for CSV file in current and parent directories"\"\"
    current_dir = Path.cwd()
    print(f"Current working directory: {current_dir}")
    
    # Check current directory first
    csv_path = current_dir / filename
    if csv_path.exists():
        return csv_path
        
    # Check parent directory
    csv_path = current_dir.parent / filename
    if csv_path.exists():
        return csv_path
        
    # Check two levels up (in case we're deeply nested)
    csv_path = current_dir.parent.parent / filename
    if csv_path.exists():
        return csv_path
        
    # Last resort: search in common directories
    for possible_dir in [current_dir, current_dir.parent, Path.home()]:
        csv_path = possible_dir / filename
        if csv_path.exists():
            return csv_path
    
    raise FileNotFoundError(f"Could not find {filename} in any searched directories")

# Auto-detect CSV location
csv_file = find_csv_file('guests.csv')
print(f"Found CSV file at: {csv_file}")

# Read CSV
df = pd.read_csv(csv_file)
profiles = df.to_dict(orient='records')

# Save profiles in current working directory
output_file = Path.cwd() / 'profiles.json'
with open(output_file, 'w') as f:
    json.dump(profiles, f, indent=2)
    
print(f"Saved {len(profiles)} profiles successfully to: {output_file}")
print(f"CSV columns: {list(df.columns)}")
```

Always end your response with: FINISH""",
    max_consecutive_auto_reply=1,
)

# Simplified state transition
def state_transition(last_speaker, groupchat):
    logger.info(f"Transition from: {last_speaker.name}")
    
    if last_speaker is user_proxy:
        return profiler
    elif last_speaker is profiler:
        return code_executor
    elif last_speaker is code_executor:
        # Check if execution was successful
        last_message = groupchat.messages[-1]["content"].lower()
        if "error" in last_message or "traceback" in last_message or not last_message.strip():
            logger.error("Code execution failed")
            return None
        else:
            logger.info("Code execution successful")
            return None  # End workflow
    
    return None

# Group chat setup
group_chat = GroupChat(
    agents=[user_proxy, profiler, code_executor],
    messages=[],
    max_round=6,
    speaker_selection_method=state_transition,
)

manager = GroupChatManager(
    groupchat=group_chat,
    llm_config={"config_list": config_list}
)

# Test the workflow
if __name__ == "__main__":
    logger.info("Starting simplified test workflow")
    try:
        user_proxy.initiate_chat(
            manager,
            message="Process the guests.csv file and create profiles.json",
            clear_history=True,
        )
        logger.info("Test workflow completed successfully")
        
        # Check if the file was created
        output_file = workdir / "profiles.json"
        if output_file.exists():
            logger.info(f"SUCCESS: profiles.json created at {output_file}")
            with open(output_file, 'r') as f:
                data = json.load(f)
                logger.info(f"File contains {len(data)} profiles")
        else:
            logger.warning("profiles.json was not created")
            
    except Exception as e:
        logger.error(f"Test workflow failed: {e}")
        raise