import os
import json
import re

# Version to pack format mapping
VERSION_TO_PACK_FORMAT = {
    "1.13-1.14.4": 4,
    "1.15-1.16.1": 5,
    "1.16.2-1.16.5": 6,
    "1.16.5": 7,
    "1.17-1.17.1": 8,
    "1.18-1.18.1": 9,
    "1.18.2": 10,
    "1.19-1.19.3": 12,
    "1.19.4": 15,
    "1.20-1.20.1": 18,
    "1.20.2": 26,
    "1.20.3-1.20.4": 41,
    "1.20.5-1.20.6": 48,
    "1.21-1.21.1": 57,
    "1.21.2-1.21.3": 61,
    "1.21.4": 61
}

# Valid folder names
VALID_FOLDERS = {
    "advancement", "advancements",
    "banner_pattern", "cat_variant", "chat_type", 
    "chicken_variant", "cow_variant", "damage_type", "dimension",
    "dimension_type", "enchantment", "enchantment_provider", 
    "frog_variant", "instrument", "jukebox_song", "loot_table",
    "painting_variant", "pig_variant", "recipe", "structure",
    "tags", "test_environment", "test_instance", 
    "trial_spawner/trial_chamber", "trim_material", "trim_pattern",
    "wolf_variant", "worldgen"
}

# Legay Folder changes
LEGACY_CHANGES = {
    "advancement": "advancements",
    "function": "functions",
    "item_modifier": "item_modifiers",
    "loot_table": "loot_tables",
    "predicate": "predicates",
    "recipe": "recipes",
    "structure": "structures",
    "tags/block": "tags/blocks",
    "tags/entity_type": "tags/entity_types",
    "tags/fluid": "tags/fluids",
    "tags/function": "tags/functions",
    "tags/game_event": "tags/game_events",
    "tags/item": "tags/items"
}

def validate_minecraft_name(name):
    if not name:
        return False
    if not re.match(r'^[a-z0-9_\-\.]+$', name):
        return False
    return True

def get_pack_format(version):
    if not re.match(r'^\d+\.\d+(\.\d+)?$', version):
        raise ValueError("Invalid version format. Expected format: X.Y.Z or X.Y")
    
    version_parts = list(map(int, version.split('.')))
    while len(version_parts) < 3:
        version_parts.append(0)
    
    for version_range, format_num in VERSION_TO_PACK_FORMAT.items():
        if '-' in version_range:
            start, end = version_range.split('-')
            start_parts = list(map(int, start.split('.')))
            end_parts = list(map(int, end.split('.')))
            
            while len(start_parts) < 3:
                start_parts.append(0)
            while len(end_parts) < 3:
                end_parts.append(999)
                
            if tuple(start_parts) <= tuple(version_parts) <= tuple(end_parts):
                return format_num
        else:
            exact_version = list(map(int, version_range.split('.')))
            while len(exact_version) < 3:
                exact_version.append(0)
            if tuple(version_parts) == tuple(exact_version):
                return format_num
    
    raise ValueError("Unsupported Minecraft version")

def get_folder_name(folder, pack_format):
    # Handle both singular and plural inputs
    folder_singular = folder
    folder_plural = folder
    
    for sing, plur in LEGACY_CHANGES.items():
        if folder == sing or folder == plur:
            folder_singular = sing
            folder_plural = plur
            break
    
    if pack_format >= 48:  # (1.21+)
        return folder_singular
    else:
        return folder_plural

def create_folders(target_dir, created_folders, pack_format, directory_type):
    print(f"\nCreating folders for {directory_type} directory")
    print("Enter folder names (press Enter when done)")
    
    while True:
        folder = input(f"Enter folder name for {directory_type}: ").strip()
        
        if not folder:
            break
            
        # Convert folder name based on version if needed
        original_folder = folder
        folder = get_folder_name(folder, pack_format)
        
        if original_folder != folder:
            print(f"Note: Folder name adjusted to '{folder}' based on Minecraft version")
        
        if folder in created_folders:
            print(f"This folder already exists in the {directory_type} directory.")
            continue
            
        # Check if folder is valid (either in singular or plural form)
        folder_valid = False
        for base_folder in VALID_FOLDERS:
            if folder == get_folder_name(base_folder, pack_format):
                folder_valid = True
                break
                
        if not folder_valid:
            print(f"'{folder}' is not a valid Minecraft datapack folder.")
            continue
            
        os.makedirs(os.path.join(target_dir, folder), exist_ok=True)
        created_folders.add(folder)
        print(f"Created folder: {folder}")

def create_datapack():
    while True:
        version = input("Enter Minecraft version (e.g., 1.21.4): ").strip()
        try:
            pack_format = get_pack_format(version)
            break
        except ValueError as e:
            print(f"Error: {e}")
    
    datapack_name = input("Enter datapack name: ").strip()
    os.makedirs(datapack_name, exist_ok=True)
    
    if input("Create spyglasssrc.json? (y/n): ").lower().strip() == 'y':
        with open(os.path.join(datapack_name, 'spyglasssrc.json'), 'w') as f:
            json.dump({"minecraft_version": version}, f, indent=2)
    
    print("Enter pack.mcmeta description JSON (press Enter twice to finish):")
    description_lines = []
    while True:
        line = input()
        if not line and description_lines and not description_lines[-1]:
            break
        description_lines.append(line)
    
    try:
        description_json = json.loads('\n'.join(description_lines))
    except json.JSONDecodeError:
        print("Invalid JSON. Using simple text description instead.")
        description_json = {"text": '\n'.join(description_lines)}
    
    pack_mcmeta = {
        "pack": {
            "pack_format": pack_format,
            "description": description_json
        }
    }
    with open(os.path.join(datapack_name, 'pack.mcmeta'), 'w') as f:
        json.dump(pack_mcmeta, f, indent=2)
    
    # Get namespace with validation
    while True:
        namespace = input("Enter namespace name: ").strip()
        if validate_minecraft_name(namespace):
            break
        print("Invalid namespace name. Make sure to use lowercase and no spaces.")
    
    # Get function names with validation
    while True:
        tick_function = input("Enter tick function name: ").strip()
        if validate_minecraft_name(tick_function):
            break
        print("Invalid function name. Make sure to use lowercase and no spaces.")
        
    while True:
        load_function = input("Enter load function name: ").strip()
        if validate_minecraft_name(load_function):
            break
        print("Invalid function name. Make sure to use lowercase and no spaces.")
    
    data_dir = os.path.join(datapack_name, 'data')
    namespace_dir = os.path.join(data_dir, namespace)
    minecraft_dir = os.path.join(data_dir, 'minecraft')
    
    function_folder = get_folder_name("function", pack_format)
    os.makedirs(os.path.join(namespace_dir, function_folder), exist_ok=True)
    
    with open(os.path.join(namespace_dir, function_folder, f"{tick_function}.mcfunction"), 'w') as f:
        pass
    with open(os.path.join(namespace_dir, function_folder, f"{load_function}.mcfunction"), 'w') as f:
        pass
    
    tags_function_folder = get_folder_name("tags/function", pack_format)
    tags_dir = os.path.join(minecraft_dir, tags_function_folder)
    os.makedirs(tags_dir, exist_ok=True)
    
    tick_json = {"values": [f"{namespace}:{tick_function}"]}
    load_json = {"values": [f"{namespace}:{load_function}"]}
    
    with open(os.path.join(minecraft_dir, tags_function_folder, 'tick.json'), 'w') as f:
        json.dump(tick_json, f, indent=2)
    with open(os.path.join(minecraft_dir, tags_function_folder, 'load.json'), 'w') as f:
        json.dump(load_json, f, indent=2)
    
    created_namespace_folders = set()
    created_minecraft_folders = set()
    
    create_folders(namespace_dir, created_namespace_folders, pack_format, "namespace")
    create_folders(minecraft_dir, created_minecraft_folders, pack_format, "minecraft")

    print(f"\nDatapack '{datapack_name}' created successfully!")

if __name__ == "__main__":
    create_datapack()