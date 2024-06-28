from io import BytesIO
import os, requests
from PIL import Image


MARKDOWN_TEMPLATE = \
'''
# How to Download and Prepare "{GAME_NAME_CAPITALIZED}" Game Files

{GAME_NAME_CAPITALIZED} is an indie game available on itch.io. This tutorial will guide you through downloading the game file, renaming it, and moving it to the appropriate folder.

## Step 1: Download the Game File

1. Visit the {GAME_NAME_CAPITALIZED} game page on itch.io: [{GAME_NAME_CAPITALIZED}]({GAME_LINK}).
2. Locate the download section on the page.
3. Click on the download link (Linux or MacOS) to start downloading the game file. Ensure you download the `.pck` file.

## Step 2: Rename the Game File

1. Once the download is complete, navigate to the folder where the file is saved.
2. Find the downloaded `.pck` file. It might be named something like `{GAME_NAME_LOWER_SNAKE_CASE}_vX.XX.pck`.
3. Right-click on the file and select "Rename" (or simply click on the filename once to select it and then press `F2` on your keyboard).
4. Rename the file to `game.pck`. Make sure to keep the `.pck` extension unchanged.

## Step 3: Move the File to the Game Data Folder

1. Locate the folder where you have the game installed or where you plan to install it.
2. Inside this folder, find or create a subfolder named `gamedata` (if it doesn't already exist).
3. Move the `game.pck` file into the `gamedata` folder. You can do this by dragging and dropping the file into the folder.

## Step 4: Launch the Game

1. After moving the file, you can now launch {GAME_NAME_CAPITALIZED}.
2. The game should recognize the `game.pck` file in the `gamedata` folder and load the necessary resources.

Congratulations! You've successfully downloaded and prepared {GAME_NAME_CAPITALIZED} for gameplay.

'''

GAMEINFO_XML_TEMPLATE = \
'''
<?xml version="1.0" encoding="utf-8"?>
<gameList>
  <game>
    <path>./{GAME_NAME_CAPITALIZED}.sh</path>
    <name>{GAME_NAME_CAPITALIZED}</name>
    <desc>{GAME_DESCRIPTION}</desc>
    <developer>{GAME_DEVELOPER}</developer>
    <publisher>{GAME_PUBLISHER}</publisher>
    <genre>{GAME_GENRE}</genre>
    <image>./{GAME_NAME_LOWER_NO_SPACES}/screenshot.jpg</image>
  </game>
</gameList>

'''

GAME_PORT_JSON = '''
{{
  "version": 2,
  "name": "{GAME_NAME_LOWER_NO_SPACES}.zip",
  "items": [
    "{GAME_NAME_CAPITALIZED}.sh",
    "{GAME_NAME_LOWER_NO_SPACES}"
  ],
  "items_opt": [],
  "attr": {{
    "title": "{GAME_NAME_CAPITALIZED}",
    "porter": [
      "ogregorio"
    ],
    "desc": "{GAME_DESCRIPTION}",
    "inst": "To download and prepare the '{GAME_NAME_CAPITALIZED}' game, visit {GAME_LINK}, download the '.pck' file, rename it to 'game.pck', move it to the 'gamedata' folder in your game directory, and launch the game.",
    "genres": [
      "{GAME_GENRE}"
    ],
    "image": null,
    "rtr": true,
    "exp": false,
    "runtime": "frt_3.5.2.squashfs",
    "reqs": [],
    "arch": []
  }}
}}
'''

SCRIPT = \
'''
#!/bin/bash

XDG_DATA_HOME=${{XDG_DATA_HOME:-$HOME/.local/share}}

if [ -d "/opt/system/Tools/PortMaster/" ]; then
  controlfolder="/opt/system/Tools/PortMaster"
elif [ -d "/opt/tools/PortMaster/" ]; then
  controlfolder="/opt/tools/PortMaster"
elif [ -d "$XDG_DATA_HOME/PortMaster/" ]; then
  controlfolder="$XDG_DATA_HOME/PortMaster"
else
  controlfolder="/roms/ports/PortMaster"
fi

source $controlfolder/control.txt
source $controlfolder/device_info.txt

[ -f "${{controlfolder}}/mod_${{CFW_NAME}}.txt" ] && source "${{controlfolder}}/mod_${{CFW_NAME}}.txt"

get_controls

GAMEDIR=/$directory/ports/{GAME_NAME_LOWER_NO_SPACES}/
CONFDIR="$GAMEDIR/conf/"

# Ensure the conf directory exists
mkdir -p "$GAMEDIR/conf"

# Set the XDG environment variables for config & savefiles
export XDG_CONFIG_HOME="$CONFDIR"
export XDG_DATA_HOME="$CONFDIR"

cd $GAMEDIR

runtime="frt_3.5.2"
if [ ! -f "$controlfolder/libs/${{runtime}}.squashfs" ]; then
  # Check for runtime if not downloaded via PM
  if [ ! -f "$controlfolder/harbourmaster" ]; then
    echo "This port requires the latest PortMaster to run, please go to https://portmaster.games/ for more info." > /dev/tty0
    sleep 5
    exit 1
  fi

  $ESUDO $controlfolder/harbourmaster --quiet --no-check runtime_check "${{runtime}}.squashfs"
fi

# Setup Godot
godot_dir="$HOME/godot"
godot_file="$controlfolder/libs/${{runtime}}.squashfs"
$ESUDO mkdir -p "$godot_dir"
$ESUDO umount "$godot_file" || true
$ESUDO mount "$godot_file" "$godot_dir"
PATH="$godot_dir:$PATH"

export FRT_NO_EXIT_SHORTCUTS=FRT_NO_EXIT_SHORTCUTS

$ESUDO chmod 666 /dev/uinput
$GPTOKEYB "$runtime" -c "./game.gptk" &
SDL_GAMECONTROLLERCONFIG="$sdl_controllerconfig" "$runtime" $GODOT_OPTS --main-pack "gamedata/game.pck"

$ESUDO umount "$godot_dir"
$ESUDO kill -9 $(pidof gptokeyb)
$ESUDO systemctl restart oga_events &
printf "\\033c" > /dev/tty0
'''

README = \
'''
# {GAME_NAME_CAPITALIZED}

{GAME_DESCRIPTION}

## Game Overview

**Gameplay:**
- Engage in blackjack battles using a deck filled with unique cards.

# {GAME_NAME_CAPITALIZED}: Gamepad Button Conversion

- **A:** C
- **B:** Space
- **X:** X
- **Up:** Up
- **Down:** Down
- **Left:** Left
- **Right:** Right
- **Start:** Esc
- **Select:** P

'''

GAME_LINK = ""
GAME_NAME_CAPITALIZED = ""
GAME_NAME_LOWER_SNAKE_CASE = ""
GAME_NAME_LOWER_NO_SPACES = ""
GAME_DESCRIPTION = ""
GAME_DEVELOPER = ""
GAME_PUBLISHER = ""
GAME_GENRE = ""

GAME_LINK = input("Digite o link do jogo: ")
GAME_NAME_CAPITALIZED = input("Digite o nome do jogo (capitalizado): ")
GAME_DESCRIPTION = input("Digite a descrição do jogo: ")
GAME_GENRE = input("Digite o gênero do jogo: ")
GAME_DEVELOPER = input("Nome do desenvolvedor do jogo: ")
GAME_PUBLISHER = input("Nome da publicadora do jogo: ")
SCREENSHOT_URL = input("Url da imagem dentro do portmaster: ")
IMAGE_URL = input("Url da imagem dentro do console: ")
GAME_NAME_LOWER_SNAKE_CASE = GAME_NAME_CAPITALIZED.lower().replace(' ', '_').replace("&", "and")
GAME_NAME_LOWER_NO_SPACES = GAME_NAME_LOWER_SNAKE_CASE.lower().replace('_', '')


xml_content = GAMEINFO_XML_TEMPLATE.format(
    GAME_NAME_CAPITALIZED=GAME_NAME_CAPITALIZED,
    GAME_NAME_LOWER_NO_SPACES=GAME_NAME_LOWER_NO_SPACES,
    GAME_DESCRIPTION=GAME_DESCRIPTION,
    GAME_DEVELOPER=GAME_DEVELOPER,
    GAME_PUBLISHER=GAME_PUBLISHER,
    GAME_GENRE=GAME_GENRE
)

port_json_content = GAME_PORT_JSON.format(
    GAME_NAME_LOWER_NO_SPACES=GAME_NAME_LOWER_NO_SPACES,
    GAME_NAME_CAPITALIZED=GAME_NAME_CAPITALIZED,
    GAME_DESCRIPTION=GAME_DESCRIPTION,
    GAME_GENRE=GAME_GENRE,
    GAME_LINK=GAME_LINK
)

markdown_content = MARKDOWN_TEMPLATE.format(
    GAME_NAME_CAPITALIZED=GAME_NAME_CAPITALIZED,
    GAME_LINK=GAME_LINK,
    GAME_NAME_LOWER_SNAKE_CASE=GAME_NAME_LOWER_SNAKE_CASE
)

script_content = SCRIPT.format(
    GAME_NAME_LOWER_NO_SPACES=GAME_NAME_LOWER_NO_SPACES
)

readme_content = README.format(
    GAME_NAME_CAPITALIZED=GAME_NAME_CAPITALIZED,
    GAME_DESCRIPTION=GAME_DESCRIPTION
)

print(xml_content)

# Pastas para salvar

markdown_directory = "../markdown"
screenshot_directory = "../images"
port_directory = "../ports/{GAME_NAME_LOWER_NO_SPACES}".format(GAME_NAME_LOWER_NO_SPACES=GAME_NAME_LOWER_NO_SPACES)
port_directory_assets = "../ports/{GAME_NAME_LOWER_NO_SPACES}/{GAME_NAME_LOWER_NO_SPACES}".format(GAME_NAME_LOWER_NO_SPACES=GAME_NAME_LOWER_NO_SPACES)

# Filenames para salvar
xml_filename = os.path.join(port_directory_assets, "gameinfo.xml")
port_json_filename = os.path.join(port_directory_assets, "{GAME_NAME_LOWER_NO_SPACES}.port.json".format(GAME_NAME_LOWER_NO_SPACES=GAME_NAME_LOWER_NO_SPACES))
script_filename = os.path.join(port_directory, "{GAME_NAME_CAPITALIZED}.sh".format(GAME_NAME_CAPITALIZED=GAME_NAME_CAPITALIZED))
markdown_filename = os.path.join(markdown_directory, "{GAME_NAME_LOWER_NO_SPACES}.md".format(GAME_NAME_LOWER_NO_SPACES=GAME_NAME_LOWER_NO_SPACES))
readme_filename = os.path.join(port_directory_assets, "README.md")
gitkeep_filename = os.path.join(port_directory_assets + "/gamedata", ".gitkeep")

def create_directory(directory):
    try:
        os.makedirs(directory, exist_ok=True)
        print(f"Diretório {directory} verificado/criado com sucesso.")
    except Exception as e:
        print(f"Erro ao criar diretório {directory}: {e}")
        exit(1)

def save_file(filename, content):
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"O arquivo foi salvo como {filename}")
    except Exception as e:
        print(f"Erro ao salvar o arquivo {filename}: {e}")

def download_image(url, directory, filename):
    try:
        # Verifica se o diretório existe, senão cria
        os.makedirs(directory, exist_ok=True)

        # Requisição GET para obter a imagem
        response = requests.get(url)
        if response.status_code == 200:
            # Abre a imagem da resposta
            image = Image.open(BytesIO(response.content))

            # Converte para RGB se não estiver no modo RGB
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Caminho completo do arquivo
            file_path = os.path.join(directory, filename)
            
            # Salva a imagem como JPG
            image.save(file_path, 'JPEG')
            
            print(f"Imagem salva com sucesso em: {file_path}")
            return True
        else:
            print(f"Falha ao baixar a imagem. Código de status: {response.status_code}")
            return False
    except Exception as e:
        print(f"Erro ao baixar e salvar a imagem: {e}")
        return False


create_directory(markdown_directory)
create_directory(screenshot_directory)
create_directory(port_directory)
create_directory(port_directory_assets)
create_directory(port_directory_assets + "/gamedata")

save_file(xml_filename, xml_content)
save_file(port_json_filename, port_json_content)
save_file(script_filename, script_content)
save_file(markdown_filename, markdown_content)
save_file(readme_filename, readme_content)

save_file(gitkeep_filename, readme_content)

download_image(SCREENSHOT_URL, screenshot_directory, GAME_NAME_LOWER_NO_SPACES + ".screenshot.jpg")
download_image(IMAGE_URL, port_directory_assets, "screenshot.jpg")