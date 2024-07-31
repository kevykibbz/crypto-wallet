#!/bin/bash

# ANSI color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color
YELLOW='\033[1;33m'

# Clear the screen
clear

# Get current date
CURRENT_DATE=$(date +"%Y-%m-%d")
IP_ADDRESS=$(curl -s ifconfig.me)

# Function to handle cleanup and exit
cleanup_and_exit() {
    echo ""
    echo -e "> ${RED}!${NC} Exiting..."
    exit
}

# Set up signal handling for interrupts (Ctrl+C)
trap cleanup_and_exit INT TERM HUP QUIT

# Enable output buffering
export PYTHONUNBUFFERED=1

echo ""
echo -e "${YELLOW}888     888 8888888888 888     888 8888888888 8888888b.  8888888b.  8888888888 888b     d888 88888888888"
echo -e "888     888 888        888     888 888        888   Y88b 888   Y88b  888        8888b   d8888     888    "
echo -e "888     888 888        888     888 888        888    888 888    888  888        88888b.d88888     888    "
echo -e "888     888 8888888    888     888 8888888    888   d88P 888   d88P  8888888    888Y88888P888     888    "
echo -e "888     888 888        888     888  888        8888888P   8888888P   888        888 Y888P 888     888    "
echo -e "888     888 888        888     888  888        888 T88b   888        888        888  Y8P  888     888    "
echo -e "888     888 888        888     888  888        888  T88b  888        888        888   Y   888     888    "
echo -e "88888888  8888888  8888888   Y8888  8888888  8888888P  8888888   Y8888  8888888  888    Y8888  8888888${NC}"

echo ""
username=$(whoami)
header="--------------------------------------[${username}@${IP_ADDRESS} ${CURRENT_DATE}]--------------------------------------"
# Output header to screen
echo "$header"
echo ""
echo "Welcome to Tevinly v1.1.0"
echo ""

# Check internet connectivity
echo -e "> ${YELLOW}?${NC} Checking internet connectivity..."
echo ""
if curl -s --head https://www.google.com | head -n 1 | grep "200 OK" > /dev/null; then
    echo -e "> ${GREEN}✓${NC} Internet connection is active."
    echo ""
else
    echo -e "> ${YELLOW}⚠${NC} No internet connection. Please check your connection and try again."
    echo ""
    echo -e "> ${RED}!${NC} Exiting..."
    exit 1
fi

# Prompt user to update settings
echo -e "> ${YELLOW}?${NC} Would you like to change some settings? (yes/no)"
echo ""
read -p "Please enter your choice: " choice

if [[ "$choice" =~ ^[yY](es)?$|^YES$ ]]; then
    python scripts/settings.py
fi

echo ""
echo -e "> ${YELLOW}?${NC} Do you wish to continue..."
echo ""
echo -e "> ${GREEN} ✓ yes(y)${NC}"
echo ""
echo -e "> ${RED} X no (n)${NC}"
echo ""

read -p "Please enter your choice: " choice

case "$choice" in
    y|yes|Y|YES)
        while true; do
            echo ""
            echo -e "> ${YELLOW}?${NC} Proceeding with Dropbox file reading..."
            echo ""
            echo -e "> ${YELLOW}?${NC} Validating dropbox access token..."
            echo ""
            python scripts/access_token.py
            
            python scripts/dropbox_files.py

            python scripts/ocr.py
            
            # Validate JSON files
            python scripts/validate.py
            if [ $? -eq 1 ]; then
                echo -e "> ${RED}!${NC} JSON file validation failed. Please select another file."
                python dropbox_files.py  # Prompt the user to select another file
            else
                #python alchemy.py
                # python cleanup.py
                # Prompt to continue after cleanup
                echo ""
                echo -e "> ${YELLOW}?${NC} Do you wish to continue (yes/no)?"
                read -p "Please enter your choice: " choice

                case "$choice" in
                    y|yes|Y|YES)
                        continue
                        ;;
                    n|no|N|NO)
                        echo ""
                        echo -e "> ${RED}!${NC} Logging out..."
                        exit
                        ;;
                    *)
                        echo -e "> ${YELLOW}⚠${NC} Invalid choice. Logging out..."
                        exit
                        ;;
                esac
            fi
        done
        ;;
    n|no|N|NO)
        echo ""
        echo -e "> ${RED}!${NC} Logging out..."
        exit
        ;;
    *)
        echo -e "> ${YELLOW}⚠${NC} Invalid choice. Logging out..."
        exit
        ;;
esac