
import discord
from discord.ext import commands

# ==================================================
# FRESH BYPASS BOT - CONFIG
# ==================================================

TOKEN = ""
PREFIX = "!"

# Βάλε τα δικά σου URLs
LOGO_URL = "https://example.com/logo.png"
BANNER_URL = "https://example.com/banner.png"

# Discord Category IDs
BUY_CATEGORY_ID = 1411103018115403776
OWNER_CATEGORY_ID = 1411103018115403776

# Channel αξιολογήσεων
REVIEWS_CHANNEL_ID = 1411103207752470578

# Βάλε τα δικά σου custom emojis ως <:name:ID>

EMOJIS = {
    "title": "<:crown:123456789012345678>",
    "buy": "1476327736208261141",
    "owner": "1253131889225502810",
    "review": "1544996461245112390",
    "username": "1514154378343485500",
    "rating": "1460288819973722142",
    "text": "1533806631589122068",
    "star": "1544996461245112390",
    "close": "1508882460832960592",
}


COLOR = 0x717171

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix=PREFIX,
    intents=intents,
    help_command=None
)


# ==================================================
# HELPERS
# ==================================================

def emoji(key):
    value = EMOJIS.get(key, "")
    if not value:
        return None
    try:
        return discord.PartialEmoji.from_str(value)
    except (ValueError, TypeError):
        return None


def add_banner(container):
    if BANNER_URL.startswith(("https://", "http://")):
        container.add_item(
            discord.ui.MediaGallery(
                discord.MediaGalleryItem(media=BANNER_URL)
            )
        )


def add_logo(container):
    if LOGO_URL.startswith(("https://", "http://")):
        container.add_item(
            discord.ui.Section(
                discord.ui.TextDisplay("**Fresh Bypass**"),
                accessory=discord.ui.Thumbnail(
                    media=discord.UnfurledMediaItem(url=LOGO_URL)
                )
            )
        )


def make_container(*items):
    return discord.ui.Container(
        *items,
        accent_color=discord.Colour(COLOR)
    )


def make_layout(container):
    view = discord.ui.LayoutView(timeout=None)
    view.add_item(container)
    return view


# ==================================================
# TICKET CREATION
# ==================================================

async def create_ticket(interaction, kind, category_id):
    guild = interaction.guild
    user = interaction.user

    if guild is None:
        return await interaction.response.send_message(
            "Χρησιμοποίησε αυτό το κουμπί μέσα στον server.",
            ephemeral=True
        )

    category = guild.get_channel(category_id) if category_id else None

    if not isinstance(category, discord.CategoryChannel):
        return await interaction.response.send_message(
            "Το category ID δεν έχει ρυθμιστεί σωστά.",
            ephemeral=True
        )

    name = f"{kind.lower()}-{user.id}"

    existing = discord.utils.get(
        category.text_channels,
        name=name
    )

    if existing:
        return await interaction.response.send_message(
            f"Έχεις ήδη ανοιχτό ticket: {existing.mention}",
            ephemeral=True
        )

    bot_member = guild.me
    if bot_member is None:
        return await interaction.response.send_message(
            "Δεν βρέθηκε το bot στον server.",
            ephemeral=True
        )

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(
            view_channel=False
        ),
        user: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_message_history=True
        ),
        bot_member: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            read_message_history=True,
            manage_channels=True
        )
    }

    channel = await guild.create_text_channel(
        name=name,
        category=category,
        overwrites=overwrites
    )

    container = make_container(
        discord.ui.TextDisplay(
            f"# {emoji('title') or '🎫'} Fresh Bypass | {kind}\n"
            f"Καλωσήρθες {user.mention}!\n\n"
            "Γράψε το αίτημά σου και η ομάδα μας "
            "θα σε εξυπηρετήσει το συντομότερο."
        ),
        discord.ui.Separator()
    )

    close_button = discord.ui.Button(
        label="Close",
        emoji=emoji("close"),
        style=discord.ButtonStyle.danger,
        custom_id="fresh:ticket:close"
    )

    async def close_callback(interaction):
        if not interaction.user.guild_permissions.manage_channels:
            if not interaction.channel.name.endswith(
                f"-{interaction.user.id}"
            ):
                return await interaction.response.send_message(
                    "Δεν έχεις δικαίωμα να κλείσεις αυτό το ticket.",
                    ephemeral=True
                )

        await interaction.response.send_message(
            "Το ticket θα κλείσει."
        )
        await interaction.channel.delete(
            reason=f"Ticket closed by {interaction.user}"
        )

    close_button.callback = close_callback
    container.add_item(discord.ui.ActionRow(close_button))

    await channel.send(view=make_layout(container))

    await interaction.response.send_message(
        f"Το ticket δημιουργήθηκε: {channel.mention}",
        ephemeral=True
    )


# ==================================================
# TICKET SYSTEM PANEL
# ==================================================

class TicketPanel(discord.ui.LayoutView):
    def __init__(self):
        super().__init__(timeout=None)

        container = make_container()
        add_banner(container)

        container.add_item(
            discord.ui.TextDisplay(
                f"# {emoji('title') or '🎫'} Fresh Bypass\n"
                "## Ticket System\n"
                "Χρειάζεσαι βοήθεια ή θέλεις να αγοράσεις κάτι;\n"
                "Επίλεξε κατηγορία για να ανοίξεις ticket."
            )
        )
        container.add_item(discord.ui.Separator())

        buy = discord.ui.Button(
            label="Buy",
            emoji=emoji("buy"),
            style=discord.ButtonStyle.secondary,
            custom_id="fresh:ticket:buy"
        )

        owner = discord.ui.Button(
            label="Owner",
            emoji=emoji("owner"),
            style=discord.ButtonStyle.secondary,
            custom_id="fresh:ticket:owner"
        )

        async def buy_callback(interaction):
            await create_ticket(interaction, "Buy", BUY_CATEGORY_ID)

        async def owner_callback(interaction):
            await create_ticket(interaction, "Owner", OWNER_CATEGORY_ID)

        buy.callback = buy_callback
        owner.callback = owner_callback

        container.add_item(discord.ui.ActionRow(buy))
        container.add_item(discord.ui.ActionRow(owner))

        self.add_item(container)


# ==================================================
# REVIEW MODAL
# ==================================================

class ReviewModal(discord.ui.Modal, title="Fresh Bypass Review"):
    review = discord.ui.TextInput(
        label="Η αξιολόγησή σου",
        placeholder="Γράψε τη γνώμη σου...",
        style=discord.TextStyle.paragraph,
        min_length=3,
        max_length=1500
    )

    def __init__(self, stars):
        super().__init__()
        self.stars = stars

    async def on_submit(self, interaction):
        channel = bot.get_channel(REVIEWS_CHANNEL_ID)

        if channel is None:
            try:
                channel = await bot.fetch_channel(REVIEWS_CHANNEL_ID)
            except discord.HTTPException:
                return await interaction.response.send_message(
                    "Δεν βρέθηκε το κανάλι αξιολογήσεων.",
                    ephemeral=True
                )

        if not isinstance(channel, discord.TextChannel):
            return await interaction.response.send_message(
                "Το Reviews Channel ID πρέπει να είναι text channel.",
                ephemeral=True
            )

        user = interaction.user
        stars = "⭐" * self.stars + "☆" * (5 - self.stars)

        container = make_container(
            discord.ui.TextDisplay(
                "# Νέα Αξιολόγηση για το Fresh Bypass"
            ),
            discord.ui.Separator(),
            discord.ui.Section(
                discord.ui.TextDisplay(
                    f"{emoji('username') or '👤'} **Όνομα χρήστη**\n"
                    f"{user.mention} (`{user.name}`)\n\n"
                    f"{emoji('rating') or '⭐'} **Αξιολόγηση**\n"
                    f"{stars} — {self.stars}/5\n\n"
                    f"{emoji('text') or '💬'} **Κείμενο**\n"
                    f"{self.review.value}"
                ),
                accessory=discord.ui.Thumbnail(
                    media=discord.UnfurledMediaItem(
                        url=user.display_avatar.url
                    )
                )
            )
        )

        try:
            add_banner(container)
            await channel.send(view=make_layout(container))
        except discord.HTTPException:
            return await interaction.response.send_message(
                "Δεν στάλθηκε η αξιολόγηση. Έλεγξε τα permissions.",
                ephemeral=True
            )

        await interaction.response.send_message(
            "Η αξιολόγησή σου στάλθηκε. Ευχαριστούμε!",
            ephemeral=True
        )


# ==================================================
# STAR SELECTION
# ==================================================

class StarPanel(discord.ui.LayoutView):
    def __init__(self):
        super().__init__(timeout=180)

        container = make_container(
            discord.ui.TextDisplay(
                "# Fresh Bypass | Reviews\n"
                "Επίλεξε πόσα αστέρια θέλεις να βάλεις."
            )
        )

        row = discord.ui.ActionRow()

        for number in range(1, 6):
            button = discord.ui.Button(
                label=str(number),
                emoji=emoji("star"),
                style=discord.ButtonStyle.secondary
            )

            async def callback(
                interaction,
                selected=number
            ):
                await interaction.response.send_modal(
                    ReviewModal(selected)
                )

            button.callback = callback
            row.add_item(button)

        container.add_item(row)
        self.add_item(container)


# ==================================================
# REVIEW PANEL
# ==================================================

class ReviewsPanel(discord.ui.LayoutView):
    def __init__(self):
        super().__init__(timeout=None)

        container = make_container()
        add_banner(container)

        container.add_item(
            discord.ui.TextDisplay(
                f"# {emoji('review') or '⭐'} Fresh Bypass Reviews\n"
                "Η γνώμη σου μετράει!\n"
                "Πάτησε το κουμπί για να αφήσεις αξιολόγηση."
            )
        )

        button = discord.ui.Button(
            label="Make a Review",
            emoji=emoji("review"),
            style=discord.ButtonStyle.secondary,
            custom_id="fresh:reviews:open"
        )

        async def callback(interaction):
            await interaction.response.send_message(
                view=StarPanel(),
                ephemeral=True
            )

        button.callback = callback
        container.add_item(discord.ui.ActionRow(button))

        self.add_item(container)


# ==================================================
# COMMANDS
# ==================================================

@bot.command()
@commands.has_permissions(administrator=True)
async def ticketsystem(ctx):
    await ctx.send(view=TicketPanel())


@bot.command()
@commands.has_permissions(administrator=True)
async def say(ctx, *, message):
    await ctx.send(message)


@bot.command()
@commands.has_permissions(administrator=True)
async def say2(ctx, *, message):
    embed = discord.Embed(
        description=message,
        color=discord.Colour(COLOR)
    )
    if LOGO_URL.startswith(("https://", "http://")):
        embed.set_thumbnail(url=LOGO_URL)
    await ctx.send(embed=embed)


@bot.command()
@commands.has_permissions(administrator=True)
async def say3(ctx, *, message):
    container = make_container(
        discord.ui.TextDisplay(message)
    )
    add_banner(container)
    add_logo(container)
    await ctx.send(view=make_layout(container))


@bot.command()
@commands.has_permissions(administrator=True)
async def reviews(ctx):
    await ctx.send(view=ReviewsPanel())


# ==================================================
# STARTUP
# ==================================================

@bot.event
async def on_ready():
    print(f"Connected as {bot.user}")
    print(f"Prefix: {PREFIX}")


async def setup_hook():
    bot.add_view(TicketPanel())
    bot.add_view(ReviewsPanel())


bot.setup_hook = setup_hook

bot.run(TOKEN)

# =========================
# RUN BOT
# =========================

if __name__ == "__main__":
 keep_alive()
bot.run(TOKEN)


