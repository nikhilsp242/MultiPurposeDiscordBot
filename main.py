import os
import datetime
import discord
import pytz
import asyncio  
from discord.ext import tasks
from discord.ext import commands
from discord.embeds import Embed
import random
import requests
import time
import json
from datetime import datetime

intents=discord.Intents.all()

# intents = discord.Intents.default()
# intents.message_content = True
# intents.members = True

client = commands.Bot(command_prefix='.', intents=intents)

generalChannel = 1161992400319807548
billiChannel = 1185976396925894686

# testChannel = 1175730830371455019
chat_ping_id = 1186691210388193400
delMsgChannel = 1192076904254144572
techie_role_id = 1185960107352277032

welcomer_role_id = 1188878861820240062

help_response = '''
# Basic Commands
 `.intro`   `.joke`   `psps`
 `.stats`   `random ping` 
 `!dontpingme`  `!allowping`
 `!dndlist`
 `?afk {reason}`  `?afklist`
  
# Games
 **Multiplayer**
### 1. Truth or Dare
 `!tdin`  `!tdout`   `!spin`
     
 # Moderation
 `.delete {num}` _deletes 'num + 1' messages_
 `.purge {num}` _purges 'num + 1' messages_
 `.snipe {num}` _for admins only_
'''


# Set up a cooldown dictionary to store the last time the command was used for each user
random_ping_cooldown = {}

# Dictionary to store users' ping preferences
ping_preferences = {}

# Dictionary to store the last message timestamp for each channel
last_message_timestamps = {}

registered_users = []

allowed_commands = ['.intro', '.joke', '.members', '.help', '!tdin', '!tdout', '!spin', '!dndlist', '!dontpingme','!allowping']

playlist_data = {}

playlist_file_path = 'playlist_links.json'

def save_playlist_data():
    with open(playlist_file_path, 'w') as file:
        json.dump(playlist_data, file)

def load_playlist_data():
    try:
        with open(playlist_file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        return {}

afk_data = {}
afk_file_path = 'afk_data.json'

def save_afk_data():
    with open(afk_file_path, 'w') as file:
        json.dump(afk_data, file)

def load_afk_data():
    try:
        with open(afk_file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        return {}

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    greeting_task.start()
    check_inactive_task.start()
    global playlist_data
    playlist_data = load_playlist_data()
    global afk_data
    afk_data = load_afk_data()

@tasks.loop(minutes=5)  # Check every 30 minutes, adjust as needed
async def check_inactive_task():
    # Get the current time in the specified timezone
    channel_tz = pytz.timezone('Asia/Kolkata')
    now = datetime.datetime.now(tz=channel_tz)

    # Check if the current time is within your desired active hours
    active_start_time = now.replace(hour=10, minute=0, second=0)
    active_end_time = now.replace(hour=22, minute=30, second=0)

    if active_start_time <= now <= active_end_time:
        # Your existing logic here
        now_utc = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
        channel = client.get_channel(generalChannel)

        if channel is not None:
            messages = [message async for message in channel.history(limit=50)]
            latest_message_time = max(message.created_at for message in messages)
            latest_message_time_tz = latest_message_time.replace(tzinfo=datetime.timezone.utc).astimezone(channel_tz)

            time_difference = now_utc - latest_message_time_tz

            if time_difference.total_seconds() > 60 * 60:
                await channel.send(f'{channel.guild.get_role(chat_ping_id).mention} This channel seems quiet. Anyone around?')
        else:
            print(f"Channel with ID {generalChannel} not found or bot doesn't have access.")
    else:
        print("It's nighttime. Skipping check_inactive_task.")

@tasks.loop(minutes=1)
async def greeting_task():
    # Get the current time in the specified timezone
    channel_tz = pytz.timezone('Asia/Kolkata')
    now = datetime.datetime.now(tz=channel_tz)
    print(f'Checking time: {now.strftime("%H:%M")}')
    
    
    if now.hour == 22 and now.minute == 30:    
        channel = client.get_channel(generalChannel)
        print(f'Sending message to channel: {channel.name}')
        await channel.send('**Good night guys, sweet dreams**')

    if now.hour == 9 and now.minute == 30:
        channel = client.get_channel(generalChannel)
        print(f'Sending message to channel: {channel.name}')
        await channel.send('**good morning chat!** :smile:')


async def getting_started(member):
    channel = client.get_channel(generalChannel)

    # Creating an embed object
    embed = discord.Embed(
        title=f"Welcome to the server, {member.display_name}!",
        description=f"We're glad to have you here, {member.mention}! Let me help you get started.",
        color=0x000000  # You can set the color of the embed
    )

    embed.add_field(
        name="Getting Started",
        value=f"- Please customize your experience by heading to **Channels & Roles**.\n"
              f"- Make sure to follow all the important categories.\n"
              f"- Choose the channels that you are interested in."
    )

    # Send the embed
    await channel.send(embed=embed)

    # Introduce more delays if needed
    await asyncio.sleep(5)

    # Mention the welcomer role and ask for a welcome
    await channel.send(f'{channel.guild.get_role(welcomer_role_id).mention} please welcome our new member!') 


@client.event
async def on_member_join(member):
    channel = client.get_channel(generalChannel)

    if member.bot:
        await channel.send(f"Hello {member.mention}! Welcome, fellow bot!")
    else:
        await getting_started(member)
        

@client.event
async def on_member_remove(member):
    channel = client.get_channel(generalChannel)

    if member.bot:
        goodbye_message = f"Farewell, {member.name} (a bot) has left the server."
    else:
        goodbye_message = f"Goodbye, {member.name} has left the server. We'll miss you!"

    await channel.send(goodbye_message)

async def get_channel_counts(guild):
    try:
        text_channels = len([channel for channel in guild.channels if isinstance(channel, discord.TextChannel)])
        voice_channels = len([channel for channel in guild.channels if isinstance(channel, discord.VoiceChannel)])
        categories = len(guild.categories)

        return {
            "Text Channels": text_channels,
            "Voice Channels": voice_channels,
            "Categories": categories
        }
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

async def server_info(guild):
    try:
        channel_info = await get_channel_counts(guild)

        # Get the server owner
        owner = guild.owner

        total_members = len(guild.members)
        human_members = sum(1 for member in guild.members if not member.bot)
        bot_members = sum(1 for member in guild.members if member.bot)

        online_members = sum(1 for member in guild.members if member.status != discord.Status.offline)

        server_icon_url = guild.icon.url if guild.icon else None

        return {
            "Server Name": guild.name,
            "Server ID": guild.id,
            "Server Icon": server_icon_url,
            "Owner": f"{owner.name}#{owner.discriminator}",
            "Total Members": total_members,
            "Human Members": human_members,
            "Bot Members": bot_members,
            "Online Members": online_members,
            "Channels": channel_info,
            "Created At": guild.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")  # Format creation date
        }
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

async def dont_ping_me(message):
    user = message.author
    if user.id not in ping_preferences:
        ping_preferences[user.id] = False
        await message.channel.send(f'{user.mention}, you will not be pinged randomly.')

async def allow_ping_me(message):
    user = message.author
    if user.id in ping_preferences:
        ping_preferences[user.id] = True
        await message.channel.send(f'{user.mention}, you are now eligible for random pings.')

async def ping_random_member(channel):
    # Check if the channel is in cooldown
    if channel.id in random_ping_cooldown:
        # Get the last time the command was used
        last_used_time = random_ping_cooldown[channel.id]

        # Calculate the time difference
        cooldown_time = 300  # 5 minutes cooldown
        elapsed_time = time.time() - last_used_time

        # Check if the cooldown period has passed
        if elapsed_time < cooldown_time:
            await channel.send(f"Spamming isn't cool bro. Someone used this command in the last 5 minutes. Please try again later.")
            return

    guild = channel.guild
    members = guild.members

    # Filter out bots and users who don't want to be pinged
    non_bot_members = [member for member in members if not member.bot and ping_preferences.get(member.id, True)]

    if non_bot_members:
        # Choose a random member
        random_member = random.choice(non_bot_members)

        # Ping the random member
        await channel.send(f'Pinging {random_member.mention}!')

        # Update the cooldown timestamp for the channel
        random_ping_cooldown[channel.id] = time.time()

    else:
        await channel.send('No eligible members found in the server.')

async def display_dont_ping_list(message):
    guild = message.guild
    dont_ping_list = [str(guild.get_member(user_id)) for user_id, allow_ping in ping_preferences.items() if not allow_ping]
    
    if dont_ping_list:
        dont_ping_list_str = '\n'.join(dont_ping_list)
        await message.channel.send(f"Users who opted for `!dontpingme`:\n {dont_ping_list_str}")
    else:
        await message.channel.send("No users have opted for `!dontpingme`.")

async def clear(member, channel, amount):
    # Check if the member has the 'Manage Messages' permission
    if member.guild_permissions.manage_messages:
        # Your logic to delete the last 'amount' messages
        messages = [msg async for msg in channel.history(limit=amount + 1)]
        
        for msg in messages:
            await msg.delete()
            # await asyncio.sleep(delay)
    else:
        await channel.send(f"{member.mention}, you don't have the 'Manage Messages' permission.")

async def fastClear(member, channel, amount):
    if member.guild_permissions.manage_messages:
        await channel.purge(limit=amount + 1)  # Including the command message
    else:
        await channel.send("You do not have the necessary permissions to manage messages.")

async def register_td(message):
    if message.author.id not in registered_users:
        registered_users.append(message.author.id)
        await message.channel.send(f"{message.author.mention}, you are now registered for the Truth or Dare game.")
    else:
        await message.channel.send(f"{message.author.mention}, you are already registered.")

async def deregister_td(message):
    if message.author.id in registered_users:
        registered_users.remove(message.author.id)
        await message.channel.send(f"{message.author.mention}, you are now unregistered from the Truth or Dare game.")
    else:
        await message.channel.send(f"{message.author.mention}, you are not registered.")


async def spin(message):
    if len(registered_users) < 2:
        await message.channel.send("Not enough registered users to spin.")
        return

    # Choose two random users
    chosen_users = random.sample(registered_users, 2)
    user1, user2 = chosen_users

    # Specify who gets to ask the question and who receives it
    asker, receiver = random.choice([(user1, user2), (user2, user1)])

    asker_user = client.get_user(asker)
    receiver_user = client.get_user(receiver)

    selected_question = random.choice(["Truth", "Dare"])

    await message.channel.send(f"{message.author.mention} has spun the wheel!\n"f"{asker_user.mention}, you get to ask {selected_question} to {receiver_user.mention}!")

async def display_tord_users(message):
    if registered_users:
        users_names = [str(client.get_user(user)) for user in registered_users]
        users_list = "\n".join(users_names)
        await message.channel.send(f"Registered users:\n{users_list}")
    else:
        await message.channel.send("No users are registered.")

async def add_playlist(user_id, playlist_link):
    # Check if the user already has playlists
    if user_id in playlist_data:
        # Append the new playlist link to the existing list
        playlist_data[user_id].append(playlist_link)
    else:
        # Create a new list with the playlist link
        playlist_data[user_id] = [playlist_link]

    # Save the updated playlist links to the file
    save_playlist_data()

async def display_playlists(user_id, channel):
    # Retrieve the playlist links from the dictionary
    playlist_links_user = playlist_data.get(user_id)

    if playlist_links_user:
        # Display all playlist links for the user with index
        for idx, playlist_link in enumerate(playlist_links_user, start=1):
            await channel.send(f'Your Playlist {idx}: {playlist_link}')
    else:
        await channel.send('You have no playlist links.')

async def display_all_playlists(channel):
    # Create an embedded message with all users' playlists
    embed = Embed(title="All Playlists", color=0x3498db)

    for user_id, playlist_links_user in playlist_data.items():
        member = channel.guild.get_member(int(user_id))
        username = member.name if member else f"Unknown User ({user_id})"

        # Combine all playlist links for the user into a single string
        playlists_combined = '\n'.join([f'[Playlist {idx}]({playlist_link}): ```{playlist_link}```' for idx, playlist_link in enumerate(playlist_links_user, start=1)])

        # Add a field for the user with their playlists
        embed.add_field(name=username, value=playlists_combined, inline=False)

    await channel.send(embed=embed)

async def set_afk(message):
    # Extract the status from the message content
    parts = message.content.split(' ', 1)
    if len(parts) == 2:
        status = parts[1]
    else:
        status = None

    user_id = str(message.author.id)
    timestamp = datetime.utcnow().isoformat()
    afk_data[user_id] = {'reason': status, 'timestamp': timestamp}
    save_afk_data()

    if status:
        await message.channel.send(f"{message.author.display_name}, you are now AFK! | reason: {status}")
    else:
        await message.channel.send(f"{message.author.display_name}, you are now AFK!")

def format_afk_duration(timestamp):
    afk_time = datetime.fromisoformat(timestamp)
    now = datetime.utcnow()
    duration = now - afk_time

    days = duration.days
    hours, remainder = divmod(duration.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    # Format days
    days_str = f"{days} day{'s' if days != 1 else ''}" if days > 0 else ''

    # Format hours
    hours_str = f"{hours} hour{'s' if hours != 1 else ''}" if hours > 0 else ''

    # Format minutes
    minutes_str = f"{minutes} minute{'s' if minutes != 1 else ''}" if minutes > 0 else ''

    # Format seconds
    seconds_str = f"{seconds} second{'s' if seconds != 1 else ''}" if seconds > 0 else ''

    # Join the formatted components with commas and "and"
    components = [comp for comp in [days_str, hours_str, minutes_str, seconds_str] if comp]
    formatted_duration = ', '.join(components[:-1]) + (' and ' if len(components) > 1 else '') + components[-1]

    return formatted_duration

async def display_all_afk_users(channel):
    embed = discord.Embed(title="AFK Users", color=0x3498db)

    for user_id, afk_status_user in afk_data.items():
        member = channel.guild.get_member(int(user_id))
        username = member.display_name if member else f"Unknown User ({user_id})"
        duration = format_afk_duration(afk_status_user['timestamp'])
        reason = afk_status_user['reason']

        if reason:
            embed.add_field(name=username, value=f"AFK for {duration} | reason: {reason}", inline=False)
        else:
            embed.add_field(name=username, value=f"AFK for {duration}", inline=False)

    await channel.send(embed=embed)

@client.event
async def on_message_delete(message):
    if message.author == client.user:
        return

    # Check if the message was deleted in a specific channel
    if message.channel.id == delMsgChannel:
        return

    # Get the private channel where you want to log deleted messages
    private_channel = client.get_channel(delMsgChannel)

    # Check if the private channel exists
    if private_channel:

        # Get the original author of the message
        original_author = message.guild.get_member(message.author.id)
        original_author_str = f"{original_author}" if original_author else "Original author is not in the server"

        # Create an embed for the deleted message details
        embed = discord.Embed(
            title="Deleted Message",
            color=0xFF0000,  # Red color (adjust as needed)
        )

        # Set a timestamp for the embed
        embed.timestamp = message.created_at

        # Add details to the embed
        embed.add_field(name="Author", value=original_author_str, inline=False)
        embed.add_field(name="Channel", value=f"#{message.channel.name}", inline=False)

        # Check if the message has text content
        if message.content:
            embed.add_field(name="Content", value=message.content, inline=False)

        # Check if the message has attachments
        if message.attachments:
            # Check if the first attachment is an image or gif
            if message.attachments[0].content_type.startswith(('image', 'video')):
                embed.set_image(url=message.attachments[0].url)
            else:
                # If not an image or gif, include the attachment URL in the description
                embed.add_field(name="Attachment", value=message.attachments[0].url, inline=False)

        # Check if the message has stickers
        if message.stickers:
            sticker = message.stickers[0]
            embed.add_field(name="Sticker", value=f"ID: {sticker.id}\nName: {sticker.name}", inline=False)

        # Check if the message has embeds
        if message.embeds:
            # Include the first embed's description in the content field
            embed.add_field(name="Embed Content", value=message.embeds[0].description, inline=False)

        # Send the embed to the private channel
        await private_channel.send(embed=embed)
    else:
        print("Private channel not found")

async def snipe_deleted_messages(limit, channel_id, messageChannel):
    # Get the private channel where deleted messages are logged
    private_channel = client.get_channel(channel_id)

    # Check if the private channel exists
    if private_channel:
        # Fetch the last N messages from the private channel
        messages = [message async for message in private_channel.history(limit=limit)]

        # Reverse the list to show older messages on top
        messages.reverse()

        # Iterate through each deleted message
        for message in messages:
            # Check if the message has embeds
            if message.embeds:
                # Assume the first embed contains the relevant information
                embed = message.embeds[0]

                # Send the entire embed
                await messageChannel.send(embed=embed)
            else:
                # If there's no embed, send the content of the message
                await messageChannel.send(f"{message.content}")

    else:
        print("Private channel not found")

@commands.command(name='joke')
async def get_joke(ctx):
    joke_api_url = 'https://v2.jokeapi.dev/joke/Any?type=single'
    
    try:
        response = requests.get(joke_api_url)
        joke_data = response.json()
        
        if joke_data['type'] == 'single':
            joke = joke_data['joke']
        elif joke_data['type'] == 'twopart':
            joke = f"{joke_data['setup']} {joke_data['delivery']}"
        else:
            joke = 'Sorry, I couldn\'t fetch a joke this time.'
        
        await ctx.send(joke)

    except Exception as e:
        print(f"An error occurred: {e}")
        await ctx.send('Sorry, I couldn\'t fetch a joke this time.')

client.add_command(get_joke)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    elif message.content == '?afklist':
        afk_status_self = afk_data.get(str(message.author.id))
        if afk_status_self:
            del afk_data[str(message.author.id)]
            save_afk_data()
            await message.channel.send(f"{message.author.display_name}, you were AFK for {format_afk_duration(afk_status_self['timestamp'])}")

        await display_all_afk_users(message.channel)

    elif message.content.startswith('?afk'):
        # Call the set_afk function if the message starts with '?afk'
        await set_afk(message)
    
    else:
        # Check if the author is marked as AFK
        afk_status = afk_data.get(str(message.author.id))
        if afk_status:
            await message.channel.send(f"Welcome back {message.author.mention}! | You were AFK for {format_afk_duration(afk_status['timestamp'])}")
            # Optionally, remove the AFK status once the user sends a message
            del afk_data[str(message.author.id)]
            save_afk_data()

        # Check if the message mentions other users
        for mention in message.mentions:
            afk_status_mentioned = afk_data.get(str(mention.id))
            if afk_status_mentioned:
                duration = format_afk_duration(afk_status_mentioned['timestamp'])
                reason = afk_status_mentioned['reason']
                if reason:
                    await message.channel.send(f"{mention.display_name} is currently AFK for {duration} | reason: {reason}")
                else:
                    await message.channel.send(f"{mention.display_name} is currently AFK for {duration}")

    introduction = f'''Greetings, {message.author.mention}. I am Billi!
My primary function is to extend a warm welcome to new members and bid farewell to those who part ways with the server.
I thrive in an active server environment and may notify the community with a gentle ping if the chat remains inactive for an extended period.
In addition, I am programmed to automatically greet everyone twice a day.
Your presence is valued, and I am here to enhance your server experience.
Should you have any inquiries or requests, feel free to reach out to our {message.guild.get_role(techie_role_id).mention}.
Enjoy your stay!'''

    if message.content.startswith(".purge"):
        # Extract the number from the message content
        try:
            number = int(message.content.split()[1])
        except IndexError:
            await message.channel.send("Invalid command usage.\nExample usage: `.purge 10`")

        await fastClear(message.author,message.channel, amount=number)

    elif message.content.startswith(".delete"):
        # Extract the number from the message content
        try:
            number = int(message.content.split()[1])
        except IndexError:
            number = 5  # Default to 5 if no number is provided

        # Call the clear command with the extracted number
        await clear(message.author, message.channel, amount=number)

    elif message.content.startswith('.snipe') :
        is_admin_or_owner = message.author.id == message.guild.owner_id or any(
            role.permissions.administrator for role in message.author.roles
        )

        if is_admin_or_owner:
            # Split the command to get the specified limit
            command_parts = message.content.split()

            # Set a default limit in case the user doesn't provide one
            limit = 1

            # Check if the user provided a limit in the command
            if len(command_parts) > 1 and command_parts[1].isdigit():
                limit = int(command_parts[1])
            if limit > 50:
                await message.channel.send(":warning: 50 is the limit!")
            # Ensure the limit is reasonable (e.g., prevent abuse)
            limit = min(limit, 50)  # You can adjust the maximum limit as needed

            # Call the snipe_deleted_messages function
            channel_id = delMsgChannel
            await snipe_deleted_messages(limit, channel_id, message.channel)
        else:
            await message.channel.send(f"{message.author.mention} , you need to have Administrator permissions to use this command")

    elif message.content == '.stats':
        server_info_result = await server_info(message.guild)
        if server_info_result:
            # Creating an embed object
            embed = discord.Embed(
                title="Server Info",
                color=0x607080,  # Grey color 
            )

            # Adding fields to the embed
            for key, value in server_info_result.items():
                if key == "Server Icon" and value:
                    embed.set_thumbnail(url=value)  # Set server icon as thumbnail if available
                else:
                    embed.add_field(name=key, value=value, inline=False)

            # Send the embed
            await message.channel.send(embed=embed)

    elif any(message.content.lower() == command for command in allowed_commands) and message.channel.id == generalChannel :
        billi_channel = client.get_channel(billiChannel)  # Replace billi_channel_id with the actual ID

        if billi_channel:
            # Ping the user in the 'billi' channel
            await billi_channel.send(f"{message.author.mention}, please use the bot in this channel.")
        else:
            print("The 'billi' channel was not found.")

    elif message.content == '.intro':
        await message.channel.send(introduction)

    elif message.content == 'billi' or message.content == 'Billi' :
        await message.channel.send('Did someone call me ? :eyes:')

    elif message.content == '.joke':
        ctx = await client.get_context(message)
        await ctx.invoke(client.get_command('joke'))

    elif message.content.startswith('psps') or message.content.startswith('Psps'):
        await message.channel.send('meow')

    elif message.content == 'random ping':
        await ping_random_member(message.channel)

    elif message.content == ".help":
        embed = discord.Embed(
            title="Command Help",
            description=help_response,
            color=0x3498db  # You can set the color of the embed
        )

        # Send the embed
        await message.channel.send(embed=embed)

    # In on_message event
    elif message.content == '!dontpingme':
        await dont_ping_me(message)

    elif message.content == '!allowping':
        await allow_ping_me(message)

    elif message.content == '!dndlist':
        await display_dont_ping_list(message)

    elif message.content == "!tdin":
        await register_td(message)

    elif message.content == "!tdout" :
        await deregister_td(message)

    elif message.content == "!spin":
        await spin(message)

    elif message.content == "!tdlist":
        await display_tord_users(message)

    elif message.content.startswith('.addpl'):
        user_id = str(message.author.id)

        # Extract the playlist link from the message content
        parts = message.content.split(' ')
        if len(parts) == 2:
            playlist_link = parts[1]

            # Call the add_playlist function
            await add_playlist(user_id, playlist_link)

            await message.channel.send('Playlist link added successfully!')
        else:
            await message.channel.send('Invalid command. Usage: .addplaylist [playlist_link]')

    elif message.content == '.mypl':
        user_id = str(message.author.id)

        # Call the display_playlists function
        await display_playlists(user_id, message.channel)
    
    elif message.content == '.pl':
        # Call the display_all_playlists function
        await display_all_playlists(message.channel)



my_secret = os.environ.get('TOKEN', 'MTE3NTcyNjg4MTExMTI4OTg1Ng.GcfFmh.jLLHm9WnBVOcvtr9YWeCdFNIBKR9krjaVdKx5Y')


client.run(my_secret) 