import os
import discord
import re
import time
from keep_alive import keep_alive

# keep Replit alive
keep_alive()

# 🔑 token comes from Replit secrets
TOKEN = os.environ["TOKEN"]

# 📌 applications channel
APPLICATION_CHANNEL_ID = 1260243799616000042

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# store applicant names by thread ID
# {thread_id: {"nickname": "...", "fullname": "..."}}
thread_applicants = {}

print("🚀 Starting bot...")


@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    # ------- handle new application messages -------
    if (message.channel.id == APPLICATION_CHANNEL_ID
            and not message.content.startswith("!") and
            "New Application Submitted" in message.content.splitlines()[0]):
        content = message.content

        # extract name line after "## "
        username_match = re.search(r">?\s*##\s*(.+)",
                                   content)  # allow leading ">"
        username_full = username_match.group(
            1).strip() if username_match else "Applicant"

        # split around ✧
        parts = username_full.split("✧")
        nickname = parts[0].strip() if len(parts) > 0 else username_full
        fullname = parts[1].strip() if len(parts) > 1 else username_full

        # age & discord
        age_match = re.search(r"-#\s*Age:\s*(.+)", content)
        age = age_match.group(1).strip() if age_match else "N/A"

        discord_match = re.search(r"-#\s*Discord:\s*(.+)", content)
        discord_tag = discord_match.group(
            1).strip() if discord_match else "N/A"

        # messages
        header_message = (f"> ## {username_full}\n"
                          f"> -# Age: {age}\n"
                          f"> -# Discord: {discord_tag}")

        followup_message = (
            f"## Hi {nickname}!\n\n"
            f"We're currently processing your application to Spring Woods! "
            f"We'll get back to you with the results in around 24h!\n"
            f"We do this to give our members a heads up, so please bare with us for these hours! 🌸\n\n"
            f"Please let us know now if you've changed your mind and are no longer interested in joining us!\n\n"
            f"*Thank you for applying, you'll hear from us soon! 🤍*")

        # create thread with full name
        thread_name = username_full[:95]
        thread = await message.create_thread(name=thread_name,
                                             auto_archive_duration=1440)

        # remember both parts for accept command
        thread_applicants[thread.id] = {
            "nickname": nickname,
            "fullname": fullname,
        }

        # send messages in the thread
        await thread.send(header_message)
        await thread.send(followup_message)

        print(f"✅ Thread created for {username_full}")
        return

    # ------- handle staff commands inside threads -------
    if isinstance(message.channel, discord.Thread):
        thread = message.channel
        cmd = message.content.strip().lower()

        if cmd == "!acceptc":
            staff_name = "Caz"
        elif cmd == "!acceptk":
            staff_name = "Kate"
        else:
            return  # not a command we handle

        # look up saved names
        saved = thread_applicants.get(thread.id)
        if saved:
            fullname = saved["fullname"]
        else:
            fullname = "Applicant"

        acceptance_message = (
            f"## Hi {fullname}!\n"
            f"I'm {staff_name} from Spring Woods! You've passed our application stage and we would love to welcome you to our club!\n\n"
            f"### Before joining, here's some information about your trial period:\n"
            f"At the end of this message we've attached a link to our closed discord server, feel free to join that whenever you have time! "
            f"Once you're in make sure to check in and take a look around the server, there's lots of helpful information on how we do things and what channels are for etc.!\n\n"
            f"Your trial will last 3 weeks from the day you join the closed server. We will keep track of this for you but keep in mind that we want you to put your best foot forward regarding both attendance and behaviour!\n"
            f"We don't have a precise attendance requirement but generally we're hoping for around 6!\n\n"
            f"*Would you like to accept this spot in Spring Woods?*\n"
            f"Server link")

        await thread.send(acceptance_message)
        print(f"✅ Acceptance message sent by {staff_name} in {thread.name}")


# run the bot with auto-restart
while True:
    try:
        client.run(TOKEN)
    except Exception as e:
        print(f"❌ Bot crashed with error: {e}")
        print("🔄 Restarting in 5 seconds...")
        time.sleep(5)

