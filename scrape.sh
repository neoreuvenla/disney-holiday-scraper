#!/bin/bash

# activate the virtual environment
source venv/bin/activate

# function to get user script choice
show_menu() {
    echo "******************************"
    echo "*** DISNEY BOOKING SCRAPER ***"
    echo "******************************"
    echo " "
    echo "   Using parameters set in src/config.py"
    echo " "
    echo "   1 - Disney flight, hotel, and ticket scraping"
    echo "   2 - Disney hotel scraping"
    echo "   3 - Disney ticket scraping"
    echo "   4 - Edit config in terminal"
    echo "   5 - Exit"
    echo " "
    read -p "   Select data to scrape: [eg: 1 2 3]: " -a choices
    echo " "
}

# function to run the selected scripts
run_scripts() {
    for choice in "${choices[@]}"; do
        case $choice in
            1)
                echo "### Running src/disney_flights.py..."
                python3 src/disney_flights.py
                ;;
            2)
                echo "### Running src/disney_hotels.py..."
                python3 src/disney_hotels.py
                ;;
            3)
                echo "### Running src/disney_tickets.py..."
                python3 src/disney_tickets.py
                ;;
            4)
                echo "### Editing src/config.py..."
                sudo nano src/config.py
                ;;
            5)
                echo "!!! Exiting."
                exit 0
                ;;
            *)
                echo "!!! Invalid option: $choice. Skipping."
                ;;
        esac
    done
}

# main script logic
while true; do
    show_menu
    run_scripts
    echo "^^^ All chosen scripts completed"
    echo " "
        break
done

# deactivate the virtual environment
deactivate