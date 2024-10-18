# TELEGRAM DATING BOT

This bot allows users to create and post dating-related posts. The main feature of this version is that when a user spends 3 tokens, they must pay 5 Telegram stars to continue using the service.

## Installation Instructions

Follow these steps to install and run the bot:

1. **Create a database folder**  
   In your project directory, create a folder named `database`, and inside this folder, create a file named `database.sqlite`. This will be used as the database for the bot.
   ```bash
   mkdir database
   touch database/database.sqlite
2. **Create a folder with the name `images` in the `storage` folder**
   ```bash
   mkdir storage/images
3. **Create a virtual environment**   
   Create a virtual environment so as not to dirty your operating system.
    ```bash
    python -m venv .venv
4. **Install Package**
   
    You can install package with
    ```bash
   pip install -r requirements.txt
5. **Run program**
   You can run program with
   ```bash
   python main.py
   