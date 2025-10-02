import os
import json
import logging
from dotenv import load_dotenv
from pathlib import Path
import pandas as pd
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
from autogen.coding import LocalCommandLineCodeExecutor

load_dotenv()

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Configuration ---
if "NAI_API_KEY" not in os.environ:
    raise ValueError("Please set the NAI_API_KEY environment variable.")

config_list = [
    {
        "model": "grok-4-fast",
        "base_url": "https://api.neosantara.xyz/v1",
        "api_key": os.environ.get("NAI_API_KEY"),
        "api_type": "openai",
        "price": [300/1000000*1000, 1500/1000000*1000]
    }
]

# --- Workspace Setup ---
workdir = Path("result")
workdir.mkdir(exist_ok=True)
logger.info(f"Working directory set to: {workdir}")

# --- Agent Definitions ---

code_executor = UserProxyAgent(
    name="Code_Executor",
    human_input_mode="NEVER",
    system_message="You are a code executor. You receive Python code, execute it, and report the result. Do not write code yourself.",
    code_execution_config={"executor": LocalCommandLineCodeExecutor(work_dir=str(workdir))},
)

user_proxy = UserProxyAgent(
    name="User_Proxy",
    is_termination_msg=lambda msg: "FINISH" in msg.get("content", ""),
    human_input_mode="NEVER",
    code_execution_config=False,
)

profiler = AssistantAgent(
    name="Profiler",
    llm_config={"config_list": config_list},
    system_message="""You are a Python data specialist.
Your ONLY task is to write a Python script block. Do NOT provide any explanation.
The script MUST be directly executable. Do NOT wrap logic in functions or an 'if __name__ == "__main__"' block.
The script must:
1. Find 'guests.csv' by searching up to two parent directories.
2. Read the CSV, convert it to a JSON array, and save it as 'profiles.json'.
3. Print a success message confirming the number of profiles saved.
Provide ONLY the directly executable Python code. End your response with FINISH after code block."""
)

drafter = AssistantAgent(
    name="Drafter",
    llm_config={"config_list": config_list},
    system_message="""You are a content automation engineer.
Your ONLY task is to generate the personalized markdown invitation text for a single guest based on the provided profile data.
Do NOT include any code or extra explanations.
The invitation should be for the "Neosantara AI tech hub" on October 1, 2025, at the Jakarta.
The invitation MUST include the guest's name, and be in the specified language and formality.
Provide ONLY the personalized markdown invitation text. End your response with FINISH."""
)


validator = AssistantAgent(
    name="Validator",
    llm_config={"config_list": config_list},
    system_message="""You are a quality assurance automator.
Your ONLY task is to write a Python script block. Do NOT provide any explanation.
The script MUST be directly executable. Do NOT wrap logic in functions or an 'if __name__ == "__main__"' block.
The script must:
1. Read 'profiles.json'.
2. For each profile, read its corresponding 'invitation_{guest_id}.md' file.
3. Validate that the guest's name, event date, and venue are present.
4. Generate a 'validation_report.json' with a detailed report for each guest ('guest_id', 'status', 'issues').
5. Print a clear, final summary of the validation results to the console.
Provide ONLY the directly executable Python code. End your response with FINISH."""
)


# --- Workflow and Group Chat Definition ---

def state_transition(last_speaker, groupchat):
    logger.info(f"Transitioning from: {last_speaker.name}")
    # Get the list of agents in the current group chat
    agents_in_group = groupchat.agents
    agent_names_in_group = [agent.name for agent in agents_in_group]

    if last_speaker is user_proxy:
        # If Profiler is in the group, go to Profiler first
        if "Profiler" in agent_names_in_group:
            return profiler
        # If Validator is in the group (and Profiler is not), go to Validator
        elif "Validator" in agent_names_in_group:
             return validator
        else:
             logger.warning(f"User_Proxy in group chat with no Profiler or Validator. Terminating.")
             return None

    elif last_speaker is profiler:
        # After Profiler generates code, go to Code_Executor if it's in the group
        if "Code_Executor" in agent_names_in_group:
            logger.info("Profiler finished, moving to Code_Executor.")
            return code_executor
        else:
            logger.warning(f"Profiler finished but Code_Executor not in group. Terminating.")
            return None

    elif last_speaker is validator:
        # After Validator generates code, go to Code_Executor if it's in the group
        if "Code_Executor" in agent_names_in_group:
            logger.info("Validator finished, moving to Code_Executor.")
            return code_executor
        else:
            logger.warning(f"Validator finished but Code_Executor not in group. Terminating.")
            return None

    elif last_speaker is code_executor:
        # After Code_Executor runs code, determine which agent requested it
        prev_speaker_name = None
        # Check if there are at least two messages before accessing the second-to-last
        if len(groupchat.messages) >= 2:
            prev_speaker_name = groupchat.messages[-2]["name"]

        if prev_speaker_name == "Profiler":
             # After Profiler's code is executed in the profiling group chat, terminate that group chat
             logger.info("Code Executor finished Profiler's script. Profiling group chat terminating.")
             return None
        elif prev_speaker_name == "Validator":
             # After Validator's code is executed in the validation group chat, terminate that group chat
             logger.info("Code Executor finished Validator's script. Validation group chat terminating. Workflow complete.")
             return None
        else:
            # This case might happen if Code_Executor is the first agent to speak after user_proxy,
            # or in unexpected scenarios.
            logger.warning(f"Code_Executor finished but previous speaker ({prev_speaker_name}) is not handled. Terminating.")
            return None

    # If none of the expected transitions occur, terminate
    logger.warning(f"Unexpected transition state from {last_speaker.name}. Terminating.")
    return None


group_chat_profiling = GroupChat(
    agents=[user_proxy, profiler, code_executor],
    messages=[],
    max_round=10,
    speaker_selection_method=state_transition,
)

manager_profiling = GroupChatManager(
    groupchat=group_chat_profiling,
    llm_config={"config_list": config_list}
)

# Define a separate group chat for validation
group_chat_validation = GroupChat(
    agents=[user_proxy, validator, code_executor],
    messages=[],
    max_round=10,
    speaker_selection_method=state_transition, # Reuse the state_transition function
)

manager_validation = GroupChatManager(
    groupchat=group_chat_validation,
    llm_config={"config_list": config_list}
)


# --- Main Execution Block ---
if __name__ == "__main__":
    logger.info("Starting AI-Powered Event Invitation Workflow...")

    guests_file = Path("guests.csv")
    if not guests_file.exists():
        logger.error(f"Error: '{guests_file}' not found. Please create it as per the README.md instructions.")
    else:
        try:
            logger.info("--- Starting Profiling Stage ---")
            # Initiate the profiling group chat. The result is the manager itself.
            user_proxy.initiate_chat(
                manager_profiling,
                message="Generate profiles.json from guests.csv.",
                clear_history=True,
            )
            # Check if the profiling stage completed successfully by looking at the group chat messages
            # and the existence of profiles.json
            profiling_successful = False
            # Access the group chat messages directly from the manager's groupchat object
            if manager_profiling.groupchat.messages:
                 # Check the last message or look for success indicators in the chat history if needed
                 # For now, rely on the file check and logs
                 logger.info("Profiling group chat finished. Checking for profiles.json.")
                 if (workdir / 'profiles.json').exists():
                      profiling_successful = True
                      logger.info("profiles.json found. Profiling stage considered successful.")
                 else:
                      logger.error("profiles.json not found after profiling stage.")
            else:
                 logger.warning("Profiling group chat did not return expected result or messages.")


            if profiling_successful:
                logger.info("--- Profiling Stage Finished ---")

                logger.info("--- Starting Invitation Drafting Stage ---")
                profiles_path = workdir / 'profiles.json'
                if profiles_path.exists():
                    with open(profiles_path, 'r', encoding='utf-8') as f:
                        guest_profiles = json.load(f)

                    for guest in guest_profiles:
                        guest_id = guest['guest_id']
                        name = guest['name']
                        language = guest['language']
                        formality = guest['formality']
                        context = guest['context']

                        # Construct message for Drafter
                        message = f"""Generate a personalized invitation text for the following guest:
    Guest ID: {guest_id}
    Name: {name}
    Language: {language}
    Formality: {formality}
    Context: {context}

    The event is the "Neosantara AI Tech Hub" on October 1, 2025, at the Jakarta.
    Provide ONLY the personalized markdown invitation text. End your response with FINISH.
    """
                        logger.info(f"Requesting invitation text for guest: {name} ({guest_id})")

                        chat_result = user_proxy.initiate_chat(
                             drafter,
                             message=message,
                             clear_history=True
                        )

                        if chat_result and chat_result.chat_history:
                            invitation_text = chat_result.chat_history[-1]["content"].replace("FINISH", "").strip()
                            invitation_file_path = workdir / f"invitation_{guest_id}.md"
                            with open(invitation_file_path, 'w', encoding='utf-8') as outfile:
                                outfile.write(invitation_text)
                            logger.info(f"Invitation saved for {name} to '{invitation_file_path}'.")
                        else:
                             logger.warning(f"Drafter did not return a message for guest: {name} ({guest_id})")
                    logger.info("--- Invitation Drafting Stage Finished ---")

                    logger.info("--- Starting Validation Stage ---")
                    user_proxy.initiate_chat(
                        manager_validation,
                        message="Validate the generated invitation files.",
                        clear_history=True,
                    )
                    logger.info("--- Validation Stage Finished ---")

                else:
                    logger.error("profiles.json not found after profiling stage. Cannot proceed with invitation drafting or validation.")

            else:
                 logger.error("Profiling stage failed. Workflow terminated.")


            logger.info("Workflow finished successfully!")
        except Exception as e:
            logger.error(f"The workflow failed with an unexpected error: {e}")
            raise