import discord
from discord import channel
from discord import message
from discord.ext import commands, tasks
import random
import json
import os 
import datetime
from datetime import datetime
import pytz 
from pytz import timezone
import asyncio


#Global Variables
client = commands.Bot(command_prefix = '$')
client.remove_command('help')
mainshop = [ {"name": "2002 Dell Computer", "price": 250,"description":"Old PC - Your programs will crash constantly."},
]
servershop = [ {"name": "CustomRoleName", "price": 500000,"description":"Personalized Role Name."},
            {"name": "CustomEmoji", "price": 10000,"description":"Have the owner upload a custom emoji for you."}
]


@client.event
async def on_ready():
    print('Online and Ready to Rock')

# Command to Pin a Message
@client.command()
async def pin(ctx):
    qw_role = discord.utils.get(ctx.guild.roles, name="Queue Work")
    admin_role = discord.utils.get(ctx.guild.roles, name="Admin")
    if qw_role or admin_role in ctx.author.roles:
    
        await ctx.send("What would you like to pin? (Send as a message in this channel)", delete_after=30)
        try:
            msg = await client.wait_for('message', check=lambda message: message.author == ctx.author,timeout=30)
            await msg.pin()
            await ctx.message.delete()
        except asyncio.TimeoutError:
            await ctx.send("Pinning has been cancelled due to timeout.", delete_after=30)
    else:    
        await ctx.send("You do not have permissions to pin messages.", delete_after=15)
        await ctx.message.delete()

# Command to Unpin a Message
@client.command()
async def unpin(ctx):
    qw_role = discord.utils.get(ctx.guild.roles, name="Queue Work")
    admin_role = discord.utils.get(ctx.guild.roles, name="Admin")
    if qw_role or admin_role in ctx.author.roles:
        await ctx.send("What would you like to unpin? (Send as a message in this channel with just the message ID)", delete_after=30)
        try:
            msg = await client.wait_for('message', check=lambda message: message.author == ctx.author,timeout=30)
            msg2 = str(msg.content)
            msg3 = await ctx.fetch_message(msg2)
            await msg3.unpin()
            await ctx.message.delete()
            await msg.delete()

        except asyncio.TimeoutError:
            await ctx.send("Unpinning has been cancelled due to timeout.", delete_after=30)
    else:    
        await ctx.send("You do not have permissions to unpin messages.", delete_after=15)
        await ctx.message.delete()


# Command to Set a Meeting
@client.command()
@commands.has_role('Admin')
async def meet(ctx):
    whodunit = ctx.message.author.display_name
    fmt = "%m/%d/%y %I:%M %p"
    meet_em = discord.Embed(title=f"Meeting Scheduled by {whodunit}", color = ctx.author.color)
    await ctx.send("What date will the meeting take place?\n \n*Format: MM/DD/YYYY HH:MM AM/PM*\n \nExample: 01/01/3021 12:34 pm") 
    msg_date = await client.wait_for('message', check=lambda message: message.author == ctx.author,timeout=30)
    
    ## Variables for Current and Future Time
    now_cst = datetime.now(timezone('US/Central'))
    now_cst2 = now_cst.strftime('%Y-%m-%d %H:%M:%S')
    now_dt = datetime.strptime(f'{now_cst2}', '%Y-%m-%d %H:%M:%S')
    meet_str = str(msg_date.content)
    meet_dt = datetime.strptime(f'{meet_str}', '%m/%d/%Y %I:%M %p')
    # Calculate Difference
    difference = (meet_dt - now_dt)
    total_seconds = difference.total_seconds()
    # Name the Meeting
    await ctx.send("What would you like to name the meeting?")
    mtg_name = await client.wait_for('message', check=lambda message: message.author == ctx.author,timeout=30)
    mtg_str = str(mtg_name.content)
    # Initial Meeting 'Invite'
    meet_em.add_field(name=mtg_str,value=f" \nThis meeting is scheduled for {meet_str}\n ")
    meet_em.set_footer(text="Please react to this message with a '👍' to confirm attendance.")
    meeting_embed = await ctx.send(embed=meet_em)
    await meeting_embed.add_reaction("👍")
    # Wait for meeting time to start
    await asyncio.sleep(total_seconds)
    #Send Meeting Notification to All Participants
    new_msg = await ctx.channel.fetch_message(meeting_embed.id)
    users = await new_msg.reactions[0].users().flatten()
    users.pop(users.index(client.user))
    for user in users:
        meet_em2 = discord.Embed(title="Meeting Reminder", color = ctx.author.color)
        meet_em2.add_field(name=mtg_str,value=f" \nThis meeting is scheduled for {meet_str}\n \nScheduled by {whodunit}")
        await user.send(embed = meet_em2)


# Replacement Help Command

client.remove_command('help')
@client.command()
async def help(ctx, arg='None'):
    em1 = discord.Embed(title='Music Peep! Commands')

    em2 = discord.Embed(title='Moderator Commands')
    await ctx.message.delete()
    if arg=='None':
        await ctx.author.send(embed=em1)
    elif arg=='moderator' or arg=='Moderator':
        await ctx.author.send(embed=em2)
    else:
        await ctx.author.send(embed=em1)

# Add Role
@client.command()
@commands.has_role("Admin")
async def addrole(ctx, role: discord.Role, user: discord.Member):
    await user.add_roles(role)
    await ctx.message.delete()

# Remove Role
@client.command()
@commands.has_role("Admin")
async def rmrole(ctx, role: discord.Role, user: discord.Member):
    await user.remove_roles(role)
    await ctx.message.delete()

# Purge Channel
@client.command()
async def purge(ctx, arg=None):
    if arg == "f" or arg == "F":
        await ctx.channel.purge()
        return
    else:    
        await ctx.send("Purge Channel? (Y/N)")
        msg = await client.wait_for('message', check=lambda message: message.author == ctx.author)
        if msg.content.lower() == "y":
            await ctx.channel.purge()
            await ctx.send("This channel has been purged.", delete_after=15)
        else:
            await ctx.send("Purging has been canceled.")

# Mute Member
@client.command()
@commands.has_role("Admin")
async def mute(ctx, user: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name="Muted")
    if role not in user.roles:
        await user.add_roles(role)
        await ctx.message.delete()
    else:
        await ctx.message.delete()
        await ctx.send("They are already muted.", delete_after=5)

#Unmute Member
@client.command()
@commands.has_role("Admin")
async def unmute(ctx, user: discord.Member):
    role = discord.utils.get(ctx.guild.roles,name="Muted")
    if role in user.roles:
        await user.remove_roles(role)
        await ctx.message.delete()
    else:
        await ctx.message.delete()
        await ctx.send("Why are you trying to unmute someone who is not muted?", delete_after=5)

### Economy Bot

# Check Balance
@client.command(aliases=['bal'])
async def balance(ctx):
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()

    wallet_amt = users[str(user.id)]["wallet"]
    bank_amt = users[str(user.id)]["bank"]

    em = discord.Embed(title = f"{ctx.author.name}'s balance", color = discord.Color.purple())
    em.add_field(name="Wallet balance", value = f"${wallet_amt}")
    em.add_field(name="Bank balance", value = f"${bank_amt}")

    await ctx.send(embed = em)

async def open_account(user):
    users = await get_bank_data()

    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]["wallet"] = 50
        users[str(user.id)]["bank"] = 500
    with open("mainbank.json", "w") as f:
        json.dump(users, f)
    return True
async def get_bank_data():
    with open("mainbank.json", "r") as f:
        users = json.load(f)   
    return users
async def update_bank(user, change = 0,mode = "wallet"):
    users = await get_bank_data()

    users[str(user.id)][mode] += change

    with open("mainbank.json", "w") as f:
        json.dump(users, f)
    
    bal = [users[str(user.id)]["wallet"],users[str(user.id)]["bank"]]
    return bal


# Command to Get a Few 'Dollars'
@client.command()
@commands.cooldown(1, 60, commands.BucketType.user)
async def beg(ctx):
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()
    earnings = random.randrange(10)

    await ctx.send(f"Someone felt so bad for you that they gave you ${earnings}.")

    users[str(user.id)]["wallet"] += earnings

    with open("mainbank.json", "w") as f:
        json.dump(users, f)

# Command to get a lot of 'Dollars'
@client.command()
@commands.cooldown(1, 600, commands.BucketType.user)
async def work(ctx):
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()
    earnings = random.randrange(300)

    await ctx.send(f"You went out and hustled to make ${earnings}.")

    users[str(user.id)]["wallet"] += earnings

    with open("mainbank.json", "w") as f:
        json.dump(users, f)

# Command to Deposit from Wallet to Bank
@client.command()
async def deposit(ctx, amount = None):
    await open_account(ctx.author)
    if amount == None:
        await ctx.send("Please specify an amount to deposit to your bank")
        return
    bal = await update_bank(ctx.author)
    amount = int(amount)
    if amount > bal[0]:
        await ctx.send(f"You do not have enough money in your wallet to deposit ${amount} into your bank")
        return
    if amount < 0:
        await ctx.send("Deposits must be a positive amount.")
        return
    await update_bank(ctx.author, amount, "bank")
    await update_bank(ctx.author, -1*amount)

    await ctx.send(f"You have depositited ${amount} into your bank.")

# Command to Withdraw from Bank
@client.command()
async def withdraw(ctx, amount = None):
    await open_account(ctx.author)
    if amount == None:
        await ctx.send("Please specify an amount to withdraw from your bank")
        return
    bal = await update_bank(ctx.author)
    amount = int(amount)
    if amount > bal[1]:
        await ctx.send(f"You do not have enough money in your bank to withdraw ${amount}.")
        return
    if amount < 0:
        await ctx.send("Withdraws must be a positive amount.")
        return
    await update_bank(ctx.author, amount)
    await update_bank(ctx.author, -1*amount, "bank")

    await ctx.send(f"You have withdrawn ${amount} into your wallet.")

# Command to give dollars from wallet to another user's wallet
@client.command()
async def give(ctx, member: discord.Member, amount = None):
    await open_account(ctx.author)
    await open_account(member)

    if amount == None:
        await ctx.send("Please specify an amount to send.")
        return
    bal = await update_bank(ctx.author)
    amount = int(amount)
    if amount > bal[0]:
        await ctx.send(f"You do not have enough money in your wallet to send ${amount}.")
        return
    if amount < 0:
        await ctx.send("Amount must be positive.")
        return
    await update_bank(member, amount)
    await update_bank(ctx.author, -1*amount)

    await ctx.send(f"You have sent ${amount}.")

# Command to give dollars from bank to another user's bank
@client.command()
async def transfer(ctx, member: discord.Member, amount = None):
    await open_account(ctx.author)
    await open_account(member)

    if amount == None:
        await ctx.send("Please specify an amount to send.")
        return
    bal = await update_bank(ctx.author)
    amount = int(amount)
    if amount > bal[1]:
        await ctx.send(f"You do not have enough money in your bank to send ${amount}.")
        return
    if amount < 0:
        await ctx.send("Amount must be positive.")
        return
    await update_bank(member, amount, "bank")
    await update_bank(ctx.author, -1*amount, "bank")

    await ctx.send(f"You have transferred ${amount}.")

# Command to gamble money in wallet
@client.command()
async def gamble(ctx, amount = None):
    await open_account(ctx.author)
    if amount == None:
        await ctx.send("Please specify an amount to gamble with.")
        return
    bal = await update_bank(ctx.author)
    amount = int(amount)
    if amount > bal[0]:
        await ctx.send(f"You do not have enough money in your wallet to gamble ${amount}.")
        return
    if amount < 0:
        await ctx.send("Bets must be a positive amount.")
        return
    final = []
    for i in range(3):
        a = random.choice(["1", "2", "3","4","5","6","7"])
        final.append(a)
    await ctx.send(f"If any numbers match, you win: {str(final)}")

    if final[0] == final[1] or final[0] == final[2] or final[1] == final[2]:
        await update_bank(ctx.author, 2*amount)
        await ctx.send(f"Congratulations, {ctx.author} you won ${2*amount}!")
    else:
        await update_bank(ctx.author, -1*amount)
        await ctx.send("Better luck next time.")


# Command to play lottery
@client.command()
@commands.cooldown(1, 6000, commands.BucketType.user)
async def lottery(ctx, amount = 100):
    await open_account(ctx.author)
    bal = await update_bank(ctx.author)
    amount = int(amount)
    if amount > bal[0]:
        await ctx.send(f"You do not have enough money in your wallet to play the lottery. Cost of ticket: ${amount}.")
        return
    
    final = []
    for i in range(2):
        a = random.randrange(10000)
        final.append(a)
    await ctx.send(f"If any numbers match, you win $10,000,000: {str(final)}")

    if final[0] == final[1]:
        await update_bank(ctx.author, 5000000*amount)
        await ctx.send("Congratulations, you won!")
    else:
        await update_bank(ctx.author, -1*amount)
        await ctx.send("Better luck next time.")

# Command to take dollars from another user's wallet
@client.command()
@commands.cooldown(1, 600, commands.BucketType.user)
async def rob(ctx, member: discord.Member=None):
    await open_account(ctx.author)
    await open_account(member)

    if member == None:
        await ctx.send("Please specify who you are attempting to rob.")
        return
    bal = await update_bank(member)
    if bal[0]<100:
        await ctx.send("You should be ashamed, trying to steal from the poor.")
        return
    earnings = random.randrange(0,int(0.2*bal[0]))
    await update_bank(ctx.author, earnings)
    await update_bank(member, -1*earnings)
    await ctx.send(f"You successfully stole ${earnings}")

#Command to open the shop
@client.command()
async def shop(ctx):
    em = discord.Embed(title="Shop")

    for item in mainshop:
       name = item["name"]
       price = item["price"]
       desc = item["description"]
       em.add_field(name=name,value= f"${price} | {desc} ")

    await ctx.send(embed = em)

# Command to open the server's shop
@client.command()
async def servshop(ctx):
    em = discord.Embed(title="Server Shop")

    for item in servershop:
       name = item["name"]
       price = item["price"]
       desc = item["description"]
       em.add_field(name=name,value= f"${price} | {desc} ")

    await ctx.send(embed = em)

# Command to buy an item from the shop
@client.command()
async def buy(ctx, item, amount = 1):
    await open_account(ctx.author)

    res = await buy_this(ctx.author, item, amount)

    if not res[0]:
        if res[1]==1:
            await ctx.send("That item isn't there!")
            return
        if res[1]==2:
            await ctx.send(f"You don't have enough money in your wallet to buy {amount} {item}")
            return
    await ctx.send(f"You just bought {amount} {item}")

# Command to sell an item to the shop
@client.command()
async def sell(ctx, item, amount = 1):
    await open_account(ctx.author)

    res = await sell_this(ctx.author, item, amount)

    if not res[0]:
        if res[1]==1:
            await ctx.send("That item isn't there!")
            return
        if res[1]==2:
            await ctx.send(f"You don't have enough money in your wallet to buy {amount} {item}")
            return
    await ctx.send(f"You just sold {amount} {item}")

# Command to check what's in your inventory
@client.command()
async def bag(ctx):
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()

    try:
        bag = users[str(user.id)]["bag"]
    except:
        bag = []

    em = discord.Embed(title="Bag")
    for item in bag:
        name = item["item"]
        amount = item["amount"]

        em.add_field(name = name, value = amount)
    
    await ctx.send(embed = em)

async def buy_this(user, item_name,amount):
    item_name = item_name.lower()
    name_ = None
    for item in mainshop:
        name = item["name"].lower()
        if name == item_name:
            name_ = name
            price = item["price"]
            break

    if name_ == None:
        return [False,1]
    cost = price * amount

    users = await get_bank_data()
    bal = await update_bank(user)

    if bal[0] < cost:
        return [False,2]

    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["bag"]:
            n = thing["item"]
            if n == item_name:
                old_amt = thing["amount"]
                new_amt = old_amt + amount
                users[str(user.id)]["bag"][index]["amount"] = new_amt
                t = 1
                break
            index += 1
        if t == None:
            obj = {"item":item_name,"amount":amount}
            users[str(user.id)]["bag"].append(obj)
    except:
        obj = {"item":item_name,"amount":amount}
        users[str(user.id)]["bag"] = [obj]
    
    with open("mainbank.json","w") as f:
        json.dump(users,f)

    await update_bank(user, cost*-1,"wallet")

    return [True, "Worked"]

async def sell_this(user, item_name,amount):
    item_name = item_name.lower()
    name_ = None
    for item in mainshop:
        name = item["name"].lower()
        if name == item_name:
            name_ = name
            price = item["price"]
            break

    if name_ == None:
        return [False,1]
    cost = 0.8*price * amount

    users = await get_bank_data()
    bal = await update_bank(user)


    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["bag"]:
            n = thing["item"]
            if n == item_name:
                old_amt = thing["amount"]
                new_amt = old_amt - amount
                users[str(user.id)]["bag"][index]["amount"] = new_amt
                t = 1
                break
            index += 1
        if t == None:
            obj = {"item":item_name,"amount":amount}
            users[str(user.id)]["bag"].append(obj)
    except:
        obj = {"item":item_name,"amount":amount}
        users[str(user.id)]["bag"] = [obj]
    
    with open("mainbank.json","w") as f:
        json.dump(users,f)

    await update_bank(user, cost,"wallet")

    return [True, "Worked"]




async def produce_this(user, item_name,amount):
    item_name = item_name.lower()
    name_ = None
    for item in mainshop:
        name = item["name"].lower()
        if name == item_name:
            name_ = name
            price = item["price"]
            break

    if name_ == None:
        return [False,1]
    royalties = random.randrange(1,2)
    cost = (royalties*price) * amount

    users = await get_bank_data()
    bal = await update_bank(user)


    try:
        index = 0
        t = None
        for thing in users[str(user.id)]["bag"]:
            n = thing["item"]
            if n == item_name:
                old_amt = thing["amount"]
                new_amt = old_amt - amount
                users[str(user.id)]["bag"][index]["amount"] = new_amt
                t = 1
                break
            index += 1
        if t == None:
            obj = {"item":item_name,"amount":amount}
            users[str(user.id)]["bag"].append(obj)
    except:
        obj = {"item":item_name,"amount":amount}
        users[str(user.id)]["bag"] = [obj]
    
    with open("mainbank.json","w") as f:
        json.dump(users,f)

    await update_bank(user, cost,"wallet")

    return [True, "Worked"]


# Bot Commands How To
@client.command()
async def howtobe(ctx):
    # definition of embed
    embed=discord.Embed(title="Admin Commands and Testing", description="Prefix for all commands is $ \n Designed by Andy", color=discord.Color.purple())
    embed.add_field(name="addrole", value="Adds a role to a given user. \n Syntax: $addrole ~role~ ~@user~", inline=False)
    embed.add_field(name="rmrole", value="Adds a role to a given user. \n Syntax: $addrole ~role~ ~@user~", inline=False)
    embed.add_field(name="purge", value="Deletes all messages in the current channel. \n Syntax: $purge", inline=False)
    embed.add_field(name="mute",value="Mutes a given user. \n Syntax: $mute ~@user~", inline=False)
    embed.add_field(name="unmute",value="Unmutes a given muted user. \n Syntax: $unmute ~@user~", inline=False)
    
    await ctx.send(embed = embed)
    await ctx.message.delete()
@client.command()
async def banker(ctx):
    embed = discord.Embed(title="List of Banking Commands - Designed by Andy")

    embed.add_field(name="balance",value="Tells you how much you have in your bank and wallet. \n Syntax: $balance", inline=False)
    embed.add_field(name="give",value="Give another user some money from your wallet. \n Syntax: $give ~@user~ ~amount~", inline=False)
    embed.add_field(name="transfer",value="Transfer another user some money from your bank. \n Syntax: $transfer ~@user~ ~amount~", inline=False)
    embed.add_field(name="rob",value="Rob another user of some money. \n Syntax: $rob ~@user~", inline=False)
    embed.add_field(name="deposit",value="Deposit money from wallet into your bank. \n Syntax: $deposit ~amount~", inline=False)
    embed.add_field(name="withdraw",value="Withdraw money from your bank to wallet. \n Syntax: $withdraw ~amount~", inline=False)
    embed.add_field(name="gamble",value="Play a game of chance to double your money. \n Syntax: $gamble ~amount~", inline=False)
    embed.add_field(name="beg",value="Beg for money. (60 sec cooldown) \n Syntax: $beg", inline=False)
    embed.add_field(name="work",value="Go out and hustle. (10 min cooldown) \n Syntax: $work", inline=False)
    embed.add_field(name="shop",value="Opens the shop. \n Syntax: $shop", inline=False)
    embed.add_field(name="buy",value="Buy an item from the shop. (Default amount is 1) \n Syntax: $buy ~item~ ~amount~", inline=False)
    embed.add_field(name="sell",value="Sell an item to the shop. (Default amount is 1) \n Syntax: $sell ~item~ ~amount~", inline=False)
    embed.add_field(name="banker",value="Ask a banker how to use your money. \n Syntax: $banker", inline=False)
    
    await ctx.send(embed=embed)
    await ctx.message.delete()

client.run('Enter Token Here')