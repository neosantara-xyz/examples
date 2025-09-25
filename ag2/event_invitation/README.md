# Agent Automation Invitations

On this example, you will learn how to build Event Invitations Workflow with Autogen (AG2)

**How does is work?**
We are about to build 3 Agent. Profiler, Drafter, and Validator agent

The **Profiler** jobs is to read `guests.csv` then convert it to `profiles.json`

The **Drafter** jobs is to personalized the profile.json to markdown content as this is the goal

The **Validator** jobs is to validate the markdown file that generate done by the profiler agent

## Get started

```bash
git clone https://github.com/neosantara-xyz/examples
cd examples/ag2/event_invitation
pip install -r requirements.txt -q
python main.py
```

# Constribute

Feel free to constribute to Neosantara Examples Integrations by open an pull request