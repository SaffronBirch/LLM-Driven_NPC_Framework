import gradio as gr
from LLM import API_helper, _content_to_str
from src.helper import load_world, save_world, load_env, get_ollama_api_key
from datetime import datetime
from pathlib import Path
import json

############################################## Load World ###############################################

# World file and save file paths
base_path = Path(__file__).parent 
world_path = base_path / "saved_worlds/TheContinent.json"
save_path = base_path / "Yourworld.json"
logs_dir = base_path / "Chat_Logs"

# Load the world/region/character information from the JSON file
world = load_world(world_path)

# List of regions that the chat can be initialized with
all_region_names = list(world["regions"].keys())

# Enter starting region and character 
input_region_name = input(f"Which region do what to start in? \n Available regions: {', '.join(world['regions'].keys())} \n")
input_character_name = input(f"Which character do you want to chat with? \n Available characters: {', '.join(world['characters'].keys())} \n")


############################################## System Prompts ###############################################

# Give the LLM instructions on how the act and respond when chatting with a user for the first time
def system_prompt_initial(world):
    return f""" 
    - You must imitate and act as the character {input_character_name} from from the video game {world["game_name"]}.
    - Your job is to create an incredibly realistic virtual simulation of {world["game_name"]} by talking to the user as if they 
        are a forign stranger in {world["world_name"]}. 

    Instructions:
    - You MUST use only 2-4 sentences. 
    - You MUST write in first person. For example: "My name is...". 
    - You MUST write in present tense. For example: "I am looking for...". 
    - First describe your character and your backstory. Then describe where you are, and what you see around you. 
    - Do not make any references that {input_character_name} would not know. \
    - You must stay in character, even if the user references something outside the scope of the {world["game_name"]}. If this happens, 
        respond as if you are unaware of what the user is talking about, and in a way in which {input_character_name} would respond. 
    - Your knowledge should only include game knowledge, quests, and events that are known and accessible to {input_character_name}. 
    - You are aware of in-game knowledge and characters that pertain directly to {input_character_name}, 
        outside of quests (friends, family, relationships, etc.). 
    """

# Define what happens when AI responds to user interactions
def system_prompt_chat(world):
    return f"""
    - Your job is to imitate and act as the character {input_character_name} from the video game {world["game_name"]}. 

    Instructions:
    - You MUST use only 2-4 sentences. 
    - You MUST write in first person.  
    - Do not make any references that {input_character_name} would not know. 
    - You must stay in character, even if the user references something outside the scope of the {world["game_name"]}. If this happens, 
        respond as if you are unaware of what the user is talking about, and in a way in which {input_character_name} would respond. 
    - Your knowledge should only include game knowledge, quests, and events that are known and accessible to {input_character_name}. 
    - You are aware of in-game knowledge and characters that pertain directly to {input_character_name}, outside of quests 
        (friends, family, relationships, etc.). 
    """
############################################## Save Chat Logs ##############################################

# Create unique filename to save chat logs
date_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
logs_path = logs_dir / f"chat_logs_{date_id}.json"

logs = {"chat_logs": {}}
save_world(logs, logs_path)

# Function to save chat logs to json file
def save_chat(region_name, user_message, chatbot_message):
    if "chat_logs" not in logs:
        logs["chat_logs"] = {}

    if region_name not in logs["chat_logs"]:
        logs["chat_logs"][region_name] = []

    logs["chat_logs"][region_name].append({"user": user_message, "chatbot": chatbot_message,})

    save_world(logs, logs_path)

############################################## Initialize Chat ##############################################

# Chat state
chat_state = {
    "world": world.get("description", ""),
    "region_name": "",
    "region": "",
    "character": "",
    "start": "",
    "initialized": False,
}

# Initialize starting region and chat state
def initialize_chat(region_name: str, character_name:str):
    region = world["regions"][region_name]
    character = world["characters"][character_name]

    chat_state["region_name"] = region_name
    chat_state["region"] = region.get("description", "")
    chat_state['character'] = character.get("description", "")

    # Load the world info
    world_info_initial = f"""
    World: {world}
    Region: {region}
    Character: {character}
    """
    # Generate the starting output when the user first starts the chat
    model_messages=[
            {"role": "system", "content": system_prompt_initial(world)},
            {"role": "user", "content": world_info_initial + '\nYour Start:'}
        ]

    # Starting message to initialize the chat
    chat_state["start"] = API_helper(model_messages)
    chat_state["initialized"] = True

    # Save the starting message to your world's JSON file
    world["start"] = chat_state["start"]
    save_world(world, save_path)
    

############################################## Create Chat UI ##############################################

demo = None

def start_chat(main_loop, share=False):
    # added code to support restart
    global demo
    # If demo is already running, close it first
    if demo is not None:
        demo.close()

    demo = gr.ChatInterface(
        fn=main_loop,
        chatbot=gr.Chatbot(height=250, placeholder="Type 'Hello' to begin"),
        textbox=gr.Textbox(placeholder="What do you say next?", container=False, scale=7),
        title="Chat with a smart NPC",
        cache_examples=False,
        additional_inputs=[gr.Dropdown(choices=all_region_names, value=input_region_name, label="Start Region")],
        theme=gr.themes.Soft()
                           )
    demo.launch(share=share)

def test_main_loop(message, history):
    return 'Entered Action: ' + message

############################################## User Interactions ##############################################

# Define what happens when the user starts the chat for thr first time
def run_interaction(message, history, chat_state, region_name, character_name):
    message_str = _content_to_str(message).strip()

    # Reset chat state if region is changed
    if chat_state.get("initialized", False) and chat_state.get("region_name") != region_name:
        chat_state["initialized"] = False
        chat_state["start"] = ""
        chat_state["region"] = ""
        chat_state["character"] = ""
        chat_state["region_name"] = ""

        # Clear chat history
        history = []

        return f"Alright. We’ll start over in **{region_name}**. Say **'Hello'** to begin."

    # If chat is not yet initialized, do so now to initialize starting region
    if not chat_state.get("initialized", False):
        initialize_chat(region_name, character_name)
    
    # Start chat, and save starting message to chat logs
    if(message_str == "Hello"):
        reply = chat_state['start']
    
        save_chat(
            region_name=chat_state["region_name"],
            user_message=message_str,
            chatbot_message=reply,
        )
        return reply
    
    # Provide world info
    world_info = f"""
    World: {chat_state['world']}
    Region: {chat_state['region']}
    Character: {chat_state['character']}
    """
    # System and world messages that get fed into model
    messages = [{"role": "system", "content": system_prompt_chat(world)}]
    messages.append({"role": "user", "content": world_info})
    
    if history:
            if isinstance(history[0], dict):
                # already message dicts
                for h in history:
                    messages.append({
                        "role": h.get("role", "user"),
                        "content": _content_to_str(h.get("content", "")),
                    })
            else:
                # tuples: (user, assistant)
                for u, a in history:
                    if u is not None:
                        messages.append({"role": "user", "content": _content_to_str(u)})
                    if a is not None:
                        messages.append({"role": "assistant", "content": _content_to_str(a)})

    messages.append({"role": "user", "content": message_str})

    reply = API_helper(messages)

    save_chat(
        region_name=chat_state["region_name"],
        user_message=message_str,
        chatbot_message=reply,
    )

    return reply


def main_loop(message, history, region_name):
     return run_interaction(message, history, chat_state, region_name, input_character_name)

start_chat(main_loop)
