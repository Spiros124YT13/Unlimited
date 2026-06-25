import os
import discord
from flask import Flask
from threading import Thread
from discord.ext import commands
from discord.ui import View, Select, Button

app = Flask('')

@app.route('/')
def home():
    return "OK"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

TOKEN = os.getenv("TOKEN")
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

import discord
from discord.ext import commands
from discord.ui import View, Select, Button

TOKEN = "BOT_TOKEN"

ALLOWED_ROLE_ID = 000000000000000

OWNER_ROLE_ID = 000000000000000
STAFF_ROLE_ID = 000000000000000
DONATE_MANAGER_ROLE_ID = 000000000000000

TICKET_CATEGORY_ID = 000000000000000
DONATE_CATEGORY_ID = 000000000000000
APPLICATION_CATEGORY_ID = 000000000000000

class TicketSelect(Select):
    def __init__(self):

        options = [
            discord.SelectOption(
                label="Owner Ticket",
                emoji="👑",
                value="owner"
            ),
            discord.SelectOption(
                label="Staff Ticket",
                emoji="🛡️",
                value="staff"
            ),
            discord.SelectOption(
                label="Report Player",
                emoji="📄",
                value="report"
            ),
            discord.SelectOption(
                label="Other",
                emoji="❓",
                value="other"
            ),
            discord.SelectOption(
                label="Support Ticket",
                emoji="🎫",
                value="support"
            ),
            discord.SelectOption(
                label="Ban Appeal",
                emoji="🔨",
                value="banappeal"
            ),
            discord.SelectOption(
                label="Bug Report",
                emoji="🐛",
                value="bug"
            )
        ]

        super().__init__(
            placeholder="Select Ticket Category",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):

        guild = interaction.guild
        choice = self.values[0]

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(
                view_channel=False
            ),
            interaction.user: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True
            )
        }

        channel = await guild.create_text_channel(
            name=f"{choice}-{interaction.user.name}",
            overwrites=overwrites,
            category=discord.utils.get(
                guild.categories,
                id=TICKET_CATEGORY_ID
            )
        )

        await interaction.response.send_message(
            f"Ticket Created: {channel.mention}",
            ephemeral=True
        )

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

@bot.command()
async def ticketpanel(ctx):

    embed = discord.Embed(
        title="🎫 Ticket System",
        description="Choose a category below.",
        color=discord.Color.blue()
    )

    await ctx.send(
        embed=embed,
        view=TicketView()
    )

class ApplicationView(View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Management",
        style=discord.ButtonStyle.primary
    )
    async def management(
        self,
        interaction,
        button
    ):
        await interaction.response.send_message(
            "Management Application Started",
            ephemeral=True
        )

    @discord.ui.button(
        label="Staff",
        style=discord.ButtonStyle.success
    )
    async def staff(
        self,
        interaction,
        button
    ):
        await interaction.response.send_message(
            "Staff Application Started",
            ephemeral=True
        )

    @discord.ui.button(
        label="Police",
        style=discord.ButtonStyle.secondary,
        disabled=True
    )
    async def police(
        self,
        interaction,
        button
    ):
        pass

    @discord.ui.button(
        label="EKAB",
        style=discord.ButtonStyle.secondary,
        disabled=True
    )
    async def ekab(
        self,
        interaction,
        button
    ):
        pass

@bot.command()
async def applications(ctx):

    embed = discord.Embed(
        title="📋 Applications",
        description="Choose a department.",
        color=discord.Color.green()
    )

    await ctx.send(
        embed=embed,
        view=ApplicationView()
    )

@bot.command()
async def help(ctx):

    embed = discord.Embed(
        title="📚 Commands",
        color=discord.Color.orange()
    )

    embed.add_field(
        name="Panels",
        value="""
!ticketpanel
!applications
!donatepanel
!civilianjobs
!criminaljobs
""",
        inline=False
    )

    embed.add_field(
        name="Admin",
        value="""
!createlogs
!status
!say
!say2
!say3
""",
        inline=False
    )

    await ctx.send(embed=embed)

@bot.command()
async def say(ctx, *, message):

    if not has_access(ctx.author):
        return

    embed = discord.Embed(
        description=message,
        color=discord.Color.blue()
    )

    await ctx.send(embed=embed)

@bot.command()
async def say2(ctx, *, message):

    if not has_access(ctx.author):
        return

    embed = discord.Embed(
        title="Announcement",
        description=message,
        color=discord.Color.green()
    )

    await ctx.send(embed=embed)

@bot.command()
async def say3(ctx, *, message):

    if not has_access(ctx.author):
        return

    await ctx.send(message)

@bot.command()
async def createlogs(ctx):

    if not has_access(ctx.author):
        return

    category = await ctx.guild.create_category(
        "📁 LOGS"
    )

    logs = [
        "join-logs",
        "role-logs",
        "channel-logs",
        "message-logs",
        "ban-logs",
        "kick-logs",
        "voice-logs",
        "timeout-logs",
        "invite-logs",
        "application-logs"
    ]

    for log in logs:
        await ctx.guild.create_text_channel(
            log,
            category=category
        )

    await ctx.send("Logs Created")

# =========================
# RUN BOT
# =========================

if __name__ == "__main__":
 keep_alive()
bot.run(TOKEN)


