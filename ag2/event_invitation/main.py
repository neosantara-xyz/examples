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

# Simplified Profiler
profiler = AssistantAgent(
    name="Profiler",
    llm_config={"config_list": config_list},
    system_message="""You must write Python code to read guests.csv and save profiles to profiles.json.

Example code:
```python
import pandas as pd
import json

# Read CSV
df = pd.read_csv('guests.csv')
profiles = df.to_dict(orient='records')

# Save profiles
with open('event_invitations/profiles.json', 'w') as f:
    json.dump(profiles, f, indent=2)
    
print(f"Saved {len(profiles)} profiles successfully")
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
    except Exception as e:
        logger.error(f"Test workflow failed: {e}")
        raise