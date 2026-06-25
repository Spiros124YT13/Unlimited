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

TICKET_CATEGORY_NAME = "TICKETS"
STAFF_ROLE_NAME = "Support"

TICKET_CATEGORY_ID = 1411103018115403776
STAFF_ROLE_ID = 1366509730583023768

class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Support", emoji="🛠️", description="Βοήθεια / Υποστήριξη"),
            discord.SelectOption(label="Report", emoji="⚠️", description="Αναφορά χρήστη / bug"),
            discord.SelectOption(label="Appeal", emoji="📨", description="Αίτηση / Unban appeal"),
        ]

        super().__init__(
            placeholder="Επίλεξε κατηγορία ticket...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="ticket_select_v2"
        )

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user
        category = guild.get_channel(TICKET_CATEGORY_ID)

        if category is None:
            return await interaction.response.send_message(
                "❌ Δεν βρέθηκε η κατηγορία ticket.", ephemeral=True
            )

        # Έλεγχος αν έχει ήδη ticket
        existing = discord.utils.get(guild.text_channels, name=f"ticket-{user.id}")
        if existing:
            return await interaction.response.send_message(
                f"Έχεις ήδη ticket: {existing.mention}", ephemeral=True
            )

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            guild.get_role(STAFF_ROLE_ID): discord.PermissionOverwrite(
                view_channel=True, send_messages=True, read_message_history=True
            ),
            user: discord.PermissionOverwrite(
                view_channel=True, send_messages=True, read_message_history=True
            )
        }

        channel = await guild.create_text_channel(
            name=f"ticket-{user.id}",
            category=category,
            overwrites=overwrites,
            reason=f"Ticket από {user}"
        )

        embed = discord.Embed(
            title=f"🎫 Ticket: {self.values[0]}",
            description="Πες μας το θέμα σου. Όταν τελειώσεις, πάτα **Κλείσιμο Ticket**.",
            color=discord.Color.green()
        )

        await channel.send(
            content=f"{user.mention} <@&{STAFF_ROLE_ID}>",
            embed=embed,
            view=TicketCloseView()
        )

        await interaction.response.send_message(
            f"✅ Το ticket σου δημιουργήθηκε: {channel.mention}",
            ephemeral=True
        )


# ======================================================
#   VIEW ΓΙΑ ΤΟ SELECT MENU
# ======================================================
class TicketSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())


# ======================================================
#   VIEW ΓΙΑ ΚΛΕΙΣΙΜΟ TICKET
# ======================================================
class TicketCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="🔒 Κλείσιμο Ticket",
        style=discord.ButtonStyle.danger,
        custom_id="close_ticket_btn_v2"
    )
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):

        channel = interaction.channel

        if not channel.name.startswith("ticket-"):
            return await interaction.response.send_message(
                "❌ Αυτό δεν είναι ticket.", ephemeral=True
            )

        await interaction.response.send_message(
            "🔒 Το ticket θα κλείσει σε 5 δευτερόλεπτα...", ephemeral=True
        )

        await discord.utils.sleep_until(
            discord.utils.utcnow() + discord.utils.timedelta(seconds=5)
        )

        await channel.delete(reason=f"Closed by {interaction.user}")


# ======================================================
#   COMMAND: !ticketsetup (Container V2)
# ======================================================
@bot.command()
async def ticketsetup(ctx):
    embed = discord.Embed(
        title="🎫 Ticket Panel (Container V2)",
        description=(
            "**Καλωσήρθες στο AP-style Ticket System!**\n"
            "Επίλεξε κατηγορία από το menu παρακάτω."
        ),
        color=discord.Color.blurple()
    )

    # Banner (εσύ βάζεις όποια εικόνα θέλεις)
    file = discord.File("banner.png", filename="banner.png")

    embed.set_image(url="https://imgur.com/a/1ZVby8N")

    await ctx.send(
        embed=embed,
        file=file,
        view=TicketSelectView()
    )

# =========================
# RUN BOT
# =========================

if __name__ == "__main__":
 keep_alive()
bot.run(TOKEN)


