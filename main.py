import asyncio
import time
from dataclasses import dataclass
from discord_components import DiscordComponents, ComponentsBot, Button, ActionRow
import discord.ext.commands
from discord.ext import commands
import webhook_manager
import random
from datetime import datetime

bot = ComponentsBot(command_prefix=['h!'], case_insensitive=True)

async def main(name, message):
    await webhook_manager.send(name, message, custom_img=None)


def getEnemy():
    enemy_list = {
        # Enemy Text - (Difficulty, Weak, Strength)
        ':ghost: :crossed_swords: :ghost:':'Dueling Ghouls',  # Dueling Ghosts.
        ':merman::skateboard::merman:':'Merbros', # Merbros
        '<a:krisnite:508437089130512416> <:susieSlap:890360533566492712>':'KRIS WHERE THE FUCK ARE WE?', # Susie Slap
        '🦷':'Trickor-Teeth',# Trickor-Teeth
        '🎃 🍮':'Jack-O-Flantern',
        '👹 🐎':'Poni',
        '🐌':'Pale Snale',
        '🕴️🦞🚬 🕴️':'The Lobfather',
        '<:wormie:887839709672407072>':'Wormie',
        ':hole:':'A Hole',
        '<:napstablook:278804489639690241>':'a friend',
        '<:mimic:902037857269608478>':'Mimic',
        ':eggplant:':'Suspicious Plant'

    }

    sel = random.choice(list(enemy_list.items()))
    print(sel)
    return sel


def getFlavour(monster):
    flavour_list = [
        f'{monster} attacks!',
        f'{monster} wanders by!',
        f'{monster} crossed your path!',
        f'{monster} stakes their claim!',
        f'{monster} fights back!',
        f'{monster} has decided your fate!',
        f'{monster} takes a stab!',
        f'{monster} remembers where they are!',
        f'{monster} took a wrong turn!',
        f'{monster} committed piracy!',
        f'{monster} pinged everyone!',
        f'{monster} repeated 4 times!'
        f'{monster} draws near!'
        f'You are confronted by {monster} and its cohorts.'
        f'{monster} hasn\'t paid their taxes!'
        f'{monster} emerges from the earth!'
        f'{monster} wakes up from a nightmare!'
        f'{monster} forgets what day it is!'
        f'{monster} thinks this is a prank..?'
        f'{monster} jumpscares you!'
        f'{monster} readjusts their Halloween mask.'
        f'{monster} befriends your mom!'
        f'{monster} wavedashes towards you!'
        f'{monster} shuffles towards you!'
        f'{monster} comes out to play!'
        f'{monster} confronts you!'
        f'{monster} draws near!'
        f'Oops! All {monster}!'
    ]

    valid = False

    while not valid:
        temp = random.choice(flavour_list)
        if len(temp) < 256:
            valid = True
    return temp

@bot.event
async def on_ready():
    print("Ready!")
    channel = bot.get_channel(669077343482019870)

def newEmbed(flavour, monster, time, health, maxhealth):

    embed = discord.Embed(title=f"{flavour}",
                          description=f"{monster}", color=0xff0000)
    embed.add_field(name="CURRENT HP", value=f"{health} / {maxhealth}", inline=True)
    embed.add_field(name="ATTACKS IN...", value=f"{time+1} Seconds", inline=True)
    embed.add_field(name="ACTIONS", value="What do you do?", inline=False)

    return embed

difficulty = 0
old_userList = []
battleOngoing = False

@commands.is_owner()
@bot.command(name='generate')
async def generate(ctx):
    global old_userList, battleOngoing

    if battleOngoing:
        await ctx.reply("There is already an ongoing battle!")
        return

    hitpoints = {}
    monster, mname = getEnemy()
    flavour = getFlavour(mname)

    monster_HP_MAX = 1000 + int(((len(old_userList))*100)*random.uniform(0.9, 1.4))
    monster_HP = monster_HP_MAX
    turnTime = 2

    embed = newEmbed(flavour, monster, turnTime-1, monster_HP, monster_HP_MAX)

    message = await ctx.send(embed=embed, components=[ActionRow(Button(label = "🗡️", custom_id = f"attack_enemy", style=4), Button(label = "💊", custom_id=f"heal_player", style=3))])
    battleOngoing = True
    turn = True
    battleTime = int(time.time())
    print(battleTime)
    turnCount = 0
    lastAttacker = None
    while battleOngoing:
        userList = []
        if monster_HP <= 0:
            turn = False
            battleOngoing = False
            victory = True
        elif turnCount > 4:
            turn = False
            battleOngoing = False
            victory = False
        while turn:
            if monster_HP <= 0:
                break
            pending = [
                bot.wait_for("button_click", check=lambda i: i.custom_id == f"attack_enemy"),
                bot.wait_for("button_click", check=lambda i: i.custom_id == f"heal_player")
            ]
            done_tasks, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED, timeout=1)
            await message.edit(embed = newEmbed(flavour, monster, ((battleTime + turnTime) - int(time.time())), monster_HP, monster_HP_MAX))
            if done_tasks:
                for task in done_tasks:
                    action = await task

                    if action.author.id not in hitpoints:
                        hitpoints[action.author.id] = 100

                    if battleTime + turnTime < int(time.time()):
                        userList = []
                        battleTime = int(time.time())

                    if action.author.id not in userList:
                        if action.component.custom_id == f'attack_enemy':
                            m_dam, p_hp = await attack(action, hitpoints[action.author.id])
                            hitpoints[action.author.id] = p_hp
                            monster_HP = monster_HP - m_dam
                            lastAttacker = action.author.id
                        elif action.component.custom_id == f'heal_player':
                            await heal(action, hitpoints[action.author.id])
                        userList.append(action.author.id)
                        print(userList)
                    else:
                        await action.send(content="You have already acted this turn!")
                for task in pending:
                    task.cancel()
            if battleTime + turnTime < int(time.time()):
                turnCount += 1
                turn = False

        battleTime = int(time.time())
        turn = True
    await message.edit(components = ActionRow())
    if victory:
        msg = f"{mname} was defeated!"
        vEmbed = newEmbed(msg , monster, 0, monster_HP, monster_HP_MAX)
        vEmbed.add_field(name='Defeated', value=f'<@{lastAttacker}> got the final hit! They have been awarded with X')
        await message.edit(embed = vEmbed)
    else:
        msg = f"{mname} got away safely!"

    old_userList = hitpoints.items()


async def attack(action, hitpoints):
    attackLow = 75
    attackHigh = 150
    attackDmg = random.randrange(attackLow, attackHigh)

    if hitpoints < 50:
        attackDmg = int(attackDmg*1.15)
    elif hitpoints < 25:
        attackDmg = int(attackDmg*1.25)

    HPLoss = random.randrange(0, 35)
    hitpoints = hitpoints - HPLoss
    crit = random.randrange(1, 100)

    if crit >= 95:
        attackDmg = attackDmg*2
        pmEmbed = discord.Embed(title="You attack the enemy!", color=0xFFD800)
        pmEmbed.description = f"CRITICAL HIT! You deal {attackDmg} damage!"
        hitpoints = hitpoints + HPLoss
        pmEmbed.set_image(url='https://media.discordapp.net/attachments/669077343482019870/902003156924379156/tumblr_m0biocwpJC1rnm2iko1_500.png')
    else:
        pmEmbed = discord.Embed(title="You attack the enemy!", color=0xD95249)
        if HPLoss == 0:
            dmgText = ' and take no'
        else:
            dmgText = f', but take {HPLoss}'
        pmEmbed.description = f'You deal {attackDmg} damage{dmgText} damage in return.\nYou currently have **{hitpoints}/100** health remaining.'
    await action.send(embed=pmEmbed)

    return attackDmg, hitpoints

async def heal(action, hitpoints):
    healLow = 20
    healHigh = 65
    heal = random.randrange(healLow, healHigh)

    if hitpoints > 75:
        heal = int(heal*0.75)

    hlEmbed = discord.Embed(title="You take a moment to heal your wounds.", color=0x59A361)

    if hitpoints + heal >= 100:
        hlEmbed.description = "You were fully healed!\nYou have **100/100** health remaining."
    else:
        hitpoints = hitpoints + heal
        hlEmbed.description = f"You were healed by {heal} hitpoints.\nYou now have **{hitpoints}/100** health remaining."

    await action.send(embed=hlEmbed)

    return hitpoints

if __name__ == '__main__':
    print("Starting!")
    bot.run('to do: enable token thing so i dont have to copy it out for github')