import discord
from discord.ext import commands
import json
import random
import os
# Bot setup with case-insensitive commands
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents, case_insensitive=True)
# File to store memories
MEMORIES_FILE = 'memories.json'
def load_memories():
    """Load memories from JSON file"""
    try:
        with open(MEMORIES_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Create empty memories file if it doesn't exist
        return {"memories": [], "next_id": 1}
    except json.JSONDecodeError:
        # Handle corrupted JSON file
        return {"memories": [], "next_id": 1}
def save_memories(memories_data):
    """Save memories to JSON file"""
    try:
        with open(MEMORIES_FILE, 'w') as f:
            json.dump(memories_data, f, indent=2)
    except Exception as e:
        print(f"Error saving memories: {e}")
@bot.event
async def on_ready():
    """Event triggered when bot is ready"""
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is ready and listening for commands.')
@bot.command(name='addmemory')
async def add_memory(ctx, *, memory_text=None):
    """Add a new memory to the pool"""
    if memory_text is None:
        await ctx.send("❌ Please provide a memory to add! Usage: `!addmemory Your memory here`")
        return
    
    # Load current memories
    memories_data = load_memories()
    
    # Create new memory entry
    new_memory = {
        "id": memories_data["next_id"],
        "text": memory_text.strip(),
        "author": str(ctx.author),
        "author_id": ctx.author.id
    }
    
    # Add to memories list
    memories_data["memories"].append(new_memory)
    memories_data["next_id"] += 1
    
    # Save to file
    save_memories(memories_data)
    
    await ctx.send(f"✅ Memory #{new_memory['id']} has been added to the memory pool!")
@bot.command(name='randommemory')
async def random_memory(ctx):
    """Retrieve and display a random memory"""
    memories_data = load_memories()
    
    if not memories_data["memories"]:
        await ctx.send("📭 No memories found! Add some memories first using `!addmemory`")
        return
    
    # Select random memory
    random_memory = random.choice(memories_data["memories"])
    
    # Format memory output
    memory_text = f"Remember when - {random_memory['text']}... #{random_memory['id']}"
    
    await ctx.send(memory_text)
@bot.command(name='removememory')
async def remove_memory(ctx, memory_id=None):
    """Remove a specific memory by ID"""
    if memory_id is None:
        await ctx.send("❌ Please provide a memory number to remove! Usage: `!removememory <memory_number>`")
        return
    
    try:
        memory_id = int(memory_id)
    except ValueError:
        await ctx.send("❌ Invalid memory number! Please provide a valid number.")
        return
    
    # Load current memories
    memories_data = load_memories()
    
    # Find memory with matching ID
    memory_to_remove = None
    for i, memory in enumerate(memories_data["memories"]):
        if memory["id"] == memory_id:
            memory_to_remove = memories_data["memories"].pop(i)
            break
    
    if memory_to_remove is None:
        await ctx.send(f"❌ Memory #{memory_id} not found! Use `!randommemory` to see existing memories.")
        return
    
    # Save updated memories
    save_memories(memories_data)
    
    await ctx.send(f"🗑️ Memory #{memory_id} has been removed from the memory pool!")
@bot.command(name='listmemories')
async def list_memories(ctx):
    """List all memories with their IDs (bonus command for easier management)"""
    memories_data = load_memories()
    
    if not memories_data["memories"]:
        await ctx.send("📭 No memories found! Add some memories first using `!addmemory`")
        return
    
    # Create formatted list
    memory_list = "📚 **All Memories:**\n"
    for memory in memories_data["memories"]:
        # Truncate long memories for the list view
        preview = memory["text"][:50] + "..." if len(memory["text"]) > 50 else memory["text"]
        memory_list += f"**#{memory['id']}** - {preview}\n"
    
    # Discord has a 2000 character limit for messages
    if len(memory_list) > 2000:
        memory_list = memory_list[:1950] + "\n... (list truncated)"
    
    await ctx.send(memory_list)
@bot.command(name='commands')
async def commands_list(ctx):
    """Display all available commands"""
    help_text = """
🤖 **Memory Bot Commands**
📝 **!addmemory** `<your memory>` - Add a new memory to the pool
🎲 **!randommemory** - Display a random memory from the collection
🗑️ **!removememory** `<memory_number>` - Remove a specific memory by its ID number
📚 **!listmemories** - Show all memories with their ID numbers
❓ **!commands** - Show this command list
**Example Usage:**
• `!addmemory We had pizza last Friday night`
• `!randommemory`
• `!removememory 3`
*All commands are case-insensitive!*
    """
    await ctx.send(help_text)
@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    if isinstance(error, commands.CommandNotFound):
        # Don't respond to unknown commands to avoid spam
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing required argument. Check the command usage!")
    else:
        await ctx.send(f"❌ An error occurred: {str(error)}")
        print(f"Error in command {ctx.command}: {error}")
# Run the bot
if __name__ == "__main__":
    # Get bot token from environment variable
    token = os.getenv('DISCORD_BOT_TOKEN')
    
    if not token:
        print("❌ ERROR: DISCORD_BOT_TOKEN environment variable not found!")
        print("Please set your Discord bot token as an environment variable.")
        exit(1)
    
    try:
        bot.run(token)
    except discord.LoginFailure:
        print("❌ ERROR: Invalid bot token! Please check your DISCORD_BOT_TOKEN.")
    except Exception as e:
        print(f"❌ ERROR: Failed to start bot: {e}")
