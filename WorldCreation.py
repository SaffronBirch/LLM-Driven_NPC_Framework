from LLM import API_helper, get_token_budget
from helper import save_world
from pathlib import Path
from rag import ScriptRAG
import json, re
import os
import sys
import time
from datetime import datetime


############################################## Build RAG index from script #####################################

# The script is indexed into embedded chunks on first run and cached to disk.
# At generation time only the chunks relevant to each query are retrieved.
def build_script_index(filename):

    base_path = Path(__file__).parent
    text_path = base_path / "scriptData" / filename

    if not text_path.exists():
        raise FileNotFoundError(f"File not found: {text_path}")

    if text_path.suffix.lower() != ".txt":
        raise ValueError(f"Expected a .txt file, got: {text_path.suffix}")

    # Cache the index next to the source file so we don't re-embed every run
    index_path = base_path / "scriptData" / "_rag_index" / f"{text_path.stem}.pkl"

    return ScriptRAG.from_file_or_build(text_path=text_path, index_path=index_path)


################################################### System Prompt #########################################

#Create the System Prompt
def create_system_prompt():
    return f"""
    Your job is to help create an immersive fantasy world based on a video game.

    Instructions:
    - Return ONLY valid JSON (no markdown, no extra text).
    - Only generate plain JSON.
    - Do not include explanations or commentary.
    - Use simple clear language.
    - You must stay below 3-5 sentences for each description.
    """

################################################### Prompts for Script Generation #########################################

# Each script-based prompt now takes a pre-retrieved `context` string containing
# only the chunks of the script relevant to that prompt, rather than the full script.

#Create the World Prompt
def create_world_from_script(context):
    return f"""
    - Based on the following excerpts from a video game's script, retrieve the name of the video game
      and generate a description of the world being created.

    Script excerpts:
    \"\"\"
    {context}
    \"\"\"

    Return ONLY valid JSON.

    Schema:
    {{
    "game_name": "Game Name",
    "world_name": "World Name", 
    "world_description": "World Description"
    }}
    """

#Create the Region Prompt
def create_regions_from_script(world_name, context):
    return f"""
    - Based on the following excerpts from the script, generate a description for all of the 
    major locations in {world_name}. Include White Orchard, Vizima, Velen, Novigrad, The Skellige Isles, and Kaer Morhen.
    - For each location's description, detail its main features.

    Script excerpts:
    \"\"\"
    {context}
    \"\"\"

    Return ONLY valid JSON.

    Schema:
    {{
    "regions": 
        {{
        "Region Name": 
            {{
            "name": "Region Name",
            "description": "Region Description"
            }}
        }}
    }}
    """

#Create Characters
def create_characters_from_script(world_name, context):
    return f""" 
    - Based on the following excerpts from the script of the game set in the world of {world_name},
      generate a description for all of the most prominent characters you can identify.
    - Include their name, age, and profession (eg. Wizard, Witcher, Blacksmith, etc.).
    - Describe the chartacters 5 most prevelant personality traits.
    - Describe their their appearance.
    - Describe their backstory.
    - Describe their lifestyle.

    - Describe 

    Script excerpts:
    \"\"\"
    {context}
    \"\"\"

    Return ONLY valid JSON.
    Schema:
    {{
    "characters": 
        {{
        "Character Name":
            {{
            "name": "Character Name",
            "age" : "Character Age",
            "profession" " :Character Profession",
            "personality": ["trait1", "trait2", "trait3", :trait4", "trait5"].
            "appearance": "Character Description", 
            "backstory": "Character Backstory",
            "lifestyle": "Character Lifestyle",
            "currently": "Character Current Activity"
            }}
        }}
    
    }}
  """

  # ─────────────────────── Tension prompts ────────────────────────────

def create_world_tensions_from_script(world_name, context):
    """Prompt for world-wide group tensions from script excerpts.

    Tensions here are the fiction's fault lines — racial, national,
    factional, religious, class-based, occupational — that exist at the
    world scale (everywhere, not just in one region). A character's
    personal prejudices are NOT tensions; tensions are properties of the
    world that characters can report on, agree with, push back against,
    or ignore. Used by bias-mitigation validation to distinguish in-world
    diegetic statements from endorsement of player-introduced bias.
    """
    return f"""
    - Based on the following excerpts from the script of the game set in
      the world of {world_name}, identify the major group-level tensions
      that exist across the WHOLE WORLD (not specific to one region).
    - Tensions can be racial, ethnic, national, factional, religious,
      class-based, or occupational.
    - For each tension, write 1-2 sentences describing the groups involved
      and the shape of the tension, as a neutral observer would describe
      it. Do not editorialize.
    - Only include tensions actually supported by the excerpts. If the
      script doesn't evidence a tension, don't invent one.

    Script excerpts:
    \"\"\"
    {context}
    \"\"\"

    Return ONLY valid JSON.

    Schema:
    {{
      "world_tensions": {{
        "tension_key": "1-2 sentence neutral description",
        ...
      }}
    }}

    Example keys: "nonhumans", "witchers", "mages", "nilfgaard",
    "religious_factions". Use short snake_case identifiers.
    """


def create_region_tensions_from_script(world_name, region_name, region_description, context):
    """Prompt for region-specific tension overlays.

    Only local intensifications or distinctive local dynamics — NOT a
    restatement of world-level tensions. Returns an empty dict if the
    region has no notable overlay, which is fine: most regions won't.
    """
    return f"""
    - Based on the following excerpts from the script of the game set in
      {world_name}, identify any group tensions SPECIFIC to the region
      "{region_name}" ({region_description}).
    - Only report local intensifications or unique local dynamics — do
      NOT restate world-wide tensions.
    - If this region has no notable local tension beyond the world-wide
      baseline, return an empty object. This is common and expected.

    Script excerpts:
    \"\"\"
    {context}
    \"\"\"

    Return ONLY valid JSON.

    Schema:
    {{
      "region_tensions": {{
        "tension_key": "1-2 sentence neutral description of the LOCAL dynamic",
        ...
      }}
    }}
    """

################################################### Prompts for User Input Generation #########################################

#Create the World Prompt
def create_world_from_input():
    return f"""
    - Generate a name and description for a fictional fantasy world.

    Return ONLY valid JSON.

    Schema:
    {{
    "name": "World Name", 
    "description": "World Description"
    }}
    """

#Create the Region Prompt
def create_regions_from_input(world):
    return f"""
    - Generate a name and description for a region in {world}.
    - For the regions's description, detail its location in the world, main features and residents.

    Return ONLY valid JSON.

    Schema:
    {{
    "regions": 
        {{
        "Region Name": 
            {{
            "name": "Region Name",
            "description": "Region Description"
            }}
        }}
    }}
    """

#Create Character
def create_character_from_input(world):
    return f""" 
    - Generate a description for a character that exist in the world of {world}. 
    - Include their name, age, and profession (eg. Wizard, Witcher, Blacksmith, etc.).
    - Describe the chartacters 5 most prevelant personality traits.
    - Describe their their appearance.
    - Describe their backstory.
    - Describe their lifestyle.

    Return ONLY valid JSON.

    Schema:
    {{
    "characters": 
        {{
        "Character Name":
            {{
            "name": "Character Name",
            "age" : "Character Age",
            "profession" " :Character Profession",
            "personality": ["trait1", "trait2", "trait3", :trait4", "trait5"].
            "appearance": "Character Description", 
            "backstory": "Character Backstory",
            "lifestyle" : "Character Lifestyle"
            }}
        }}
    
    }}
  """

def create_world_tensions_from_input(world_name, world_description):
    return f"""
    - Generate the major group-level tensions in the world "{world_name}"
      ({world_description}). These are fault lines that exist world-wide.
    - Keep descriptions neutral and factual, not editorialized.
    - Generate 2-5 tensions.

    Return ONLY valid JSON.

    Schema:
    {{
      "world_tensions": {{
        "tension_key": "1-2 sentence neutral description",
        ...
      }}
    }}
    """


def create_region_tensions_from_input(world_name, region_name, region_description):
    return f"""
    - Generate any group tensions SPECIFIC to "{region_name}"
      ({region_description}) in the world {world_name}.
    - Only report local intensifications or unique local dynamics.
    - If the region has no distinctive local tension, return an empty object.

    Return ONLY valid JSON.

    Schema:
    {{
      "region_tensions": {{
        "tension_key": "1-2 sentence description",
        ...
      }}
    }}
    """

############################################## Content Generation ##############################################

from abc import ABC, abstractmethod

# Abstract class 
class Generator(ABC):
    def __init__(self):
        self.world = {}
    
    @abstractmethod
    def generate_world(self):
        pass

    @abstractmethod
    def generate_world_tensions(self): 
        pass  

    @abstractmethod
    def generate_regions(self):
        pass

    @abstractmethod
    def generate_region_tensions(self): 
        pass 

    @abstractmethod
    def generate_characters(self, region_name):
        pass

    def save_to_file(self, filename):
        if self.world is None:
            print("No world has been generated.")

        base_path = Path(__file__).parent
        save_path = base_path/filename

        save_world(self.world, save_path)


# Generate JSON file from user input data
class inputDataGenerator(Generator):
    def __init__(self):
        super().__init__()

     # Collect world information from user   
    def generate_world(self):
        print('''
            Let's start with where your character lives. Do you want to describe the world yourself,
            or have a world generated for you? \n
            Create world from scratch: Press 1 \n
            Generate world: Press 2 \n
            ''')
        
        choice = input("Enter choice: ").strip()

        if choice == '1':
            self.world['name'] = input("World Name: ").strip()
            self.world['description'] = input("World Description: ").strip()
            self.world['regions'] = {}
            return self.world
       
        elif choice == '2':
            print(f"generating world...")
       
            world_messages = [
                {"role": "system", "content": create_system_prompt()},
                {"role": "user", "content": create_world_from_input()}]
                
            world_output = API_helper(world_messages)
            world_data = json.loads(world_output)

            self.world = {
                "name": world_data["name"].strip(),
                "description": world_data["description"].strip(),
                "regions": {},
                "characters": {}
            }

            print(f"Created world: {self.world['name']}")
            return self.world


    # Collect region information from user
    def generate_regions(self):
        print('''
            Now let's describe any regions that populate your world. Do you want to describe the regions yourself,
            or have them generated for you? \n
            Create region from scratch: Press 1 \n
            Generate region: Press 2 \n
            ''')
        
        choice = input("Enter choice: ").strip()
        
        if choice == '1':
            add_region = True
            while add_region == True:
                region_name = input("Region Name: ").strip()

                self.world['regions'][region_name] = {
                    "name": region_name,
                    "description": input("Region Description: ").strip()
                }
                another = ("Add another region? (y/n)")

                if another == 'y':
                    add_region = True
                elif another == 'n': 
                    add_region = False
                    break
                
            return self.world['regions']

        elif choice == '2':
            add_region = True
            print(f"Generating regions for {self.world['name']}...")

            while add_region == True:
                region_messages = [
                    {"role": "system", "content": create_system_prompt()},
                    {"role": "user", "content": create_regions_from_input(self.world)}
                ]
                region_output = API_helper(region_messages)
                region_data = json.loads(region_output)
                                    
                for region_name, region_info in region_data['regions'].items():
                    self.world['regions'][region_name] = {
                        "name": region_name,
                        "description": region_info['description'].strip(),
                        "characters": {}
                    }
                    print(f"created region {region_name}")

                    another = input("Add another region? (y/n) \n").strip()

                    if another == 'y':
                        add_region = True
                    elif another == 'n': 
                        add_region = False
                        break
                
            return self.world['regions']


    # Collect character information from user
    def generate_characters(self, region_name=None):
        print("Finally let's create your NPC profile.  \n")

        print('''
            Do you want to create your character from scratch or have one generated for you? \n
            Create character from scratch: Press 1 \n
            Generate character: Press 2 \n
            ''')
        
        choice = input("Enter choice: ").strip()
        
        if choice == '1':
            add_character = True

            while add_character == True:
                #region_name = input(f"Which region does your character live in? \n Available regions: {', '.join(self.world['regions'].keys())} \n")

                character_name = input("Character Name: ").strip()
                character_age = input("Character Age: ").strip()
                character_profession = input("Character Profession: ").strip()
                character_appearance = input("Character appearance: ").strip()
                character_backstory = input("Character Backstory: ").strip()
                character_lifestyle = input("Character lifestyle: ").strip()

                print("Enter 5 personality traits for your character: ")
                character_personality = []
                for i in range(5):
                    trait = input(f"Trait {i+1}: ").strip()
                    character_personality.append(trait)

                #region = self.world['regions'][region_name]

                self.world['characters'][character_name] = {
                    "name": character_name,
                    "age": character_age,
                    "profession": character_profession,
                    "personality": character_personality,
                    "appearance": character_appearance,
                    "backstory": character_backstory,
                    "lifestyle": character_lifestyle
                }
                another = input("Add another character? (y/n) \n").strip()

                if another == 'y':
                    add_character = True
                elif another == 'n': 
                    add_character = False
                    break

            return self.world['characters']

        elif choice == '2':
            add_character = True

            while add_character == True:
                #region_name = input(f"Which region does your character live in? \n Available regions: {', '.join(self.world['regions'].keys())} \n")

                print(f"Generating character...")

                #region = self.world['regions'][region_name]

                character_messages = [
                    {"role": "system", "content": create_system_prompt()},
                    {"role": "user", "content": create_character_from_input(self.world)}
                ]

                character_output = API_helper(character_messages)
                character_data = json.loads(character_output)

                for character_name, character_info in character_data['characters'].items():     
                    self.world["characters"][character_name] = {
                        "name": character_name,
                        "age": character_info["age"].strip(),
                        "profession": character_info["profession"].strip(),
                        "personality": character_info['personality'],
                        "appearance": character_info["appearance"].strip(),
                        "backstory": character_info['backstory'].strip(),
                        "lifestyle": character_info["lifestyle"].strip(),
   

                    }
                    print(f"created character {character_name}")

                    another = input("Add another character? (y/n) \n").strip()

                    if another == 'y':
                        add_character = True
                    elif another == 'n': 
                        add_character = False
                        break

            return self.world['characters']


# Generate JSON file from script data
class ScriptDataGenerator(Generator):
    # How many chunks to retrieve for each kind of query. Tune these based on
    # your model's context window and how rich you want the context to be.
    TOP_K_WORLD = 6
    TOP_K_REGIONS = 12
    TOP_K_CHARACTERS = 12
    TOP_K_TENSIONS = 10

    WORLD_QUERY = (
        "setting, world, premise, lore, tone, overall story, "
        "title of the game, genre, world name"
    )
    
    WORLD_TENSION_QUERY = (
        "prejudice, discrimination, racism, hatred, mistrust, "
        "oppression, pogrom, persecution, faction rivalry, religious "
        "conflict, class tension, conquered peoples, imperial rule"
    )
    
    REGION_QUERY = (
        "regions, locations, cities, towns, villages, landmarks, "
        "geography, places, maps, environments in {world_name}"
    )
    
    CHARACTER_QUERY = (
        "characters, protagonists, antagonists, NPCs, personalities, "
        "appearance, backstory, dialogue, relationships, roles in {world_name}"
    )
    
    REGION_TENSION_QUERY = (
        "{region_name} local conflict dispute prejudice tension "
        "between groups specific to {region_name}"
    )

    def __init__(self, data_filename=None):
        super().__init__()
        # Instead of loading the whole script into memory as a single string,
        # we build (or load) a RAG index over the script.
        self.rag = build_script_index(data_filename)

    def generate_world(self):
        print(f"generating world...")

        # Retrieve chunks most relevant to describing the setting/premise
        # world_query = (
        #     "setting, world, premise, lore, tone, overall story, "
        #     "title of the game, genre, world name"
        # )
        context = self.rag.retrieve_context(self.WORLD_QUERY, top_k=self.TOP_K_WORLD)

        world_messages = [
            {"role": "system", "content": create_system_prompt()},
            {"role": "user", "content": create_world_from_script(context)}]

        world_output = API_helper(world_messages)
        world_data = json.loads(world_output)

        self.world = {
            "game_name": world_data["game_name"].strip(),
            "world_name": world_data["world_name"].strip(),
            "world_description": world_data["world_description"].strip(),
            "world_tensions": {},
            "regions": {},
            "characters": {}
        }

        print(f"Created world: {self.world['world_name']}")
        return self.world


    def generate_world_tensions(self):
        """Generate world-wide group tensions. Must be called after
        generate_world() because it needs self.world['world_name']."""
        if not self.world:
            raise ValueError("World must be generated first.")

        print(f"Generating world tensions...")

        # Tensions query targets the script's political/social conflict layer
        # tension_query = (
        #     "prejudice, discrimination, racism, hatred, mistrust between "
        #     "groups, war, factions, oppressed minorities, religious conflict, "
        #     "political rivalry, class tension"
        # )
        context = self.rag.retrieve_context(self.WORLD_TENSION_QUERY, top_k=self.TOP_K_REGIONS)

        tension_messages = [
            {"role": "system", "content": create_system_prompt()},
            {"role": "user", "content": create_world_tensions_from_script(
                self.world["world_name"], context
            )},
        ]
        tension_output = API_helper(tension_messages)
        tension_data = json.loads(tension_output)

        self.world["world_tensions"] = tension_data.get("world_tensions", {})
        print(f"  → {len(self.world['world_tensions'])} world tensions")
        return self.world["world_tensions"]


    def generate_regions(self):
        if not self.world:
            raise ValueError("World must be generated first. Call generate_world() first.")

        print(f"Generating regions...")

        # Retrieve chunks most relevant to locations / geography
        region_query = (
            f"regions, locations, cities, towns, villages, landmarks, "
            f"geography, places, maps, environments in {self.world['world_name']}"
        )

        context = self.rag.retrieve_context(region_query, top_k=self.TOP_K_REGIONS)

        region_messages = [
            {"role": "system", "content": create_system_prompt()},
            {"role": "user", "content": create_regions_from_script(self.world["world_name"], context)}
        ]
        regions_output = API_helper(region_messages)
        region_data = json.loads(regions_output)
        
        for region_name, region_info in region_data['regions'].items():
            self.world['regions'][region_name] = {
                "name": region_name,
                "description": region_info['description'].strip(),
                "tensions": {},
            }
            print(f"created region {region_name}")
        
        return self.world['regions']
    

    def generate_region_tensions(self):
        """Generate per-region tension overlays in a single batched call.

        Rationale: most regions have no distinctive local tension beyond
        the world baseline, and calling the LLM once per region wastes
        O(N) round-trips on results that are almost all empty. The LLM
        can handle all regions at once and return only the ones with
        meaningful local overlays.
        """
        if not self.world.get("regions"):
            raise ValueError("Regions must be generated first.")

        print(f"Generating region-specific tensions...")

        # query = (
        #             f"{region_name} local conflicts tensions disputes "
        #             f"prejudice specific to {region_name}"
        #         )
        # context = self.rag.retrieve_context(query, top_k=6)

        for region_name, region_info in self.world["regions"].items():
            # Format NOW, when region_name has a value
            query = self.REGION_TENSION_QUERY.format(region_name=region_name)
            context = self.rag.retrieve_context(query, top_k=self.TOP_K_TENSIONS)

        # Build the region list inline so the LLM can address each by name.
        region_list = "\n".join(
            f"- {name}: {info['description']}"
            for name, info in self.world["regions"].items()
        )

        prompt = f"""
        Based on the following excerpts from the script of {self.world["world_name"]},
        identify any group tensions SPECIFIC to individual regions in the list below.
        Only report LOCAL intensifications or unique local dynamics — do NOT restate
        world-wide tensions (those are handled separately).

        Regions to consider:
        {region_list}

        For each region that has no distinctive local tension, omit it from the
        output (or return an empty object for it). Most regions will have none
        — that is expected and correct.

        Script excerpts:
        \"\"\"{context}\"\"\"

        Return ONLY valid JSON.

        Schema:
        {{
        "regions": {{
            "Region Name": {{
            "tension_key": "1-2 sentence description of the LOCAL dynamic",
            ...
            }},
            ...
        }}
        }}
        """

        messages = [
            {"role": "system", "content": create_system_prompt()},
            {"role": "user", "content": prompt},
        ]
        try:
            output = API_helper(messages)
            data = json.loads(output)
            region_data = data.get("regions", {})
        except (json.JSONDecodeError, KeyError) as e:
            print(f"  [!] Failed to parse region tensions: {e}")
            region_data = {}

        for region_name, region_info in self.world["regions"].items():
            tensions = region_data.get(region_name, {})
            # Sanity: some LLMs will wrap in extra structure; reject non-dicts.
            if not isinstance(tensions, dict):
                tensions = {}
            region_info["tensions"] = tensions
            if tensions:
                print(f"  → {region_name}: {len(tensions)} local tension(s)")

        return self.world["regions"]


    def generate_characters(self):
        print(f"Generating characters...")

        # Retrieve chunks most relevant to characters / dialogue / relationships
        character_query = (
            f"characters, protagonists, antagonists, NPCs, personalities, "
            f"appearance, backstory, dialogue, relationships, roles in {self.world['world_name']}"
        )
        context = self.rag.retrieve_context(character_query, top_k=self.TOP_K_CHARACTERS)

        character_messages = [
            {"role": "system", "content": create_system_prompt()},
            {"role": "user", "content": create_characters_from_script(self.world['world_name'], context)}
        ]

        character_output = API_helper(character_messages)
        character_data = json.loads(character_output)

        for character_name, character_info in character_data['characters'].items():     
            self.world["characters"][character_name] = {
                "name": character_name,
                "age": character_info["age"].strip(),
                "profession": character_info["profession"].strip(),
                "personality": character_info['personality'],
                "appearance": character_info["appearance"].strip(),
                "backstory": character_info['backstory'].strip(),
                "lifestyle": character_info["lifestyle"].strip(),
                "currently": None,
                
            }
            print(f"created character {character_name}")

        return self.world['characters']

############################################## User Input and World Generation ##############################################

print(f'''
      
    \n === Welcome to the Smart NPC Generator === \n
      
      If you are creating a character from scratch: Press 1 \n
      If you are creating a character from an exising script: Press 2 \n
    '''
    )

world = None
generator = None

choice = input("Enter choice: ").strip()

# Build NPC from scratch
if choice == '1':
    generator = inputDataGenerator()
    world = generator.generate_world()
    generator.generate_regions()
    generator.generate_characters()

# Build NPC from existing script
elif choice == '2':
    script_filename = input("Please enter the filename of your script (Ex. SkyrimScript.txt): ")
    generator = ScriptDataGenerator(script_filename)

    world = generator.generate_world()
    generator.generate_world_tensions()
    generator.generate_regions()
    generator.generate_region_tensions()
    generator.generate_characters()

else:
    print("invalid choice, please enter 1 or 2")

if generator and world:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder = Path("saved_worlds")
    filename = folder / f"{world['world_name'].replace(' ', '')}_timestamp.json"
    generator.save_to_file(filename)
else:
    print("No world has been generated, nothing to save")