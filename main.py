import asyncio
import time
from dataclasses import dataclass
from discord_components import DiscordComponents, ComponentsBot, Button, ActionRow
import discord.ext.commands
from discord.ext import commands, tasks
import random
import json
import os
from datetime import datetime

bot = ComponentsBot(command_prefix=['h!'], case_insensitive=True)
monsterchannel = 901950648768139367

def getCandies(userid:int):
    if not os.path.isfile(f'./candy_jar/{userid}.json'):
        with open(f"./candy_jar/{userid}.json", 'x') as file:
            def_candies = {
                'candy':0,
                'rare_candy':0
            }
            file.write(json.dumps(def_candies))

    with open(f"./candy_jar/{userid}.json", 'r') as c_file:

        raw = json.loads(c_file.read())
        candy, r_candy = raw

    return raw[candy], raw[r_candy]

def addCandies(userid, n_candy, n_r_candy):
    candy, r_candy = getCandies(userid)

    candy = candy + n_candy
    r_candy = r_candy + n_r_candy

    c_dict = {
        'candy':candy,
        'rare_candy':r_candy
    }

    with open(f"./candy_jar/{userid}.json", 'w') as file:
        file.write(json.dumps(c_dict))

def getEnemy():
    enemy_list = {
        # Enemy Text - (Difficulty, Weak, Strength)
        ':ghost: :crossed_swords: :ghost:': 'Dueling Ghouls',  # Dueling Ghosts.
        ':merman::skateboard::merman:': 'Merbros',  # Merbros
        '<a:krisnite:508437089130512416> <:susieSlap:890360533566492712>': 'KRIS WHERE THE FUCK ARE WE?',  # Susie Slap
        '🦷': 'Trickor-Teeth',  # Trickor-Teeth
        '🎃 🍮': 'Jack-O-Flantern',
        '👹 🐎': 'Poni',
        '🐌': 'Pale Snale',
        '🕴️🦞🚬 🕴️': 'The Lobfather',
        '<:wormie:887839709672407072>': 'Wormie',
        ':hole:': 'A Hole',
        '<:napstablook:278804489639690241>': 'a friend',
        '<:mimic:902037857269608478>': 'Mimic',
        ':eggplant:': 'Suspicious Plant',
        '🌜🌚🌛': 'Broken Moon',
        '<:madDummyBro:764589495379034162>':'Bruh Dummy',
        '🙊 🙊':'Snickers',
        ':green_square: :skull_crossbones: :green_square:':'Dancing Greenscreen Skeleton',
        ':race_car: :police_car:':'Hot Pursuit',
        ':flag_gb:':'The British Empire',
        ':heart:':'DETERMINATION',
        '<:botsanstroll:902416763478761474>':'\"Sans\"',
        '<:sansbadtime:278804488889040896>':'Sans',
        ':red_circle::knife:     :blue_circle:':'Crewmates',
        ':hedgehog: :ring: :ring: :ring:':'Sonic The Hedgehog',
        ':tophat:\n:bat:':'Bat in a Hat',
        ':💉🌻:': 'The Experiment',
        ':adhesive_bandage::head_bandage:':'DIY Mummy',
        '⚱️🚬':'Pot Smoker',
        ':nut_and_bolt::man_zombie::nut_and_bolt:':'It\'s Alive!',
        ':peach:':'Suspicious Fruit',
        ':gun::monkey_face:':'Monkioso'
    }

    sel = random.choice(list(enemy_list.items()))
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
        f'Wild {monster} appeared!'
        f'You were accosted by {monster}!'
        f'{monster} has come to make an announcement.'

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


def newEmbed(flavour, monster, time, health, maxhealth):
    global hitpoints

    aliveFighters = []
    deadFighters = []
    t_deadText = ''
    t_aliveText = ''

    aliveText = "Nobody is fighting!"
    deadText = "Nobody has fallen!"
    playerDead = False
    playerAlive = False
    if len(hitpoints) < 1:
        aliveText = "Nobody has entered this battle!"
        deadText = "Nobody has fallen!"
    else:
        for i in hitpoints:
            tempHP = hitpoints[i]
            if tempHP <= 0:
                playerDead = True
                if len(t_deadText) >= 900:
                    t_deadText = f'{t_deadText}(+ more...)'
                    break
                t_deadText = f'{t_deadText}<@{i}> (0/100 HP)\n'
            else:
                playerAlive = True
                if len(t_aliveText) >= 900:
                    t_aliveText = f'{t_aliveText}(+ more...)'
                    break
                t_aliveText = f'{t_aliveText}<@{i}> ({tempHP}/100 HP)\n'

    if playerDead:
        deadText = t_deadText
    if playerAlive:
        aliveText = t_aliveText

    embed = discord.Embed(title=f"{flavour}",
                          description=f"{monster}", color=0xff0000)
    embed.add_field(name="CURRENT HP", value=f"{health} / {maxhealth}", inline=True)
    embed.add_field(name="ATTACKS IN...", value=f"{time + 1} Seconds", inline=True)
    embed.add_field(name="COMBATANTS:", value="_ _", inline=False)
    embed.add_field(name="THE FIGHTERS", value=aliveText, inline=True)
    embed.add_field(name="THE FALLEN", value=deadText, inline=True)
    embed.add_field(name="ACTIONS", value="What do you do?", inline=False)

    return embed


difficulty = 0
old_userList = []
battleOngoing = False
monster_HP = 0
hitpoints = {}
lastAttacker = 0
userList = []


async def attackHandler(interaction):
    global monster_HP, hitpoints, lastAttacker
    m_dam, p_hp = await attack(interaction, hitpoints[interaction.author.id])
    hitpoints[interaction.author.id] = p_hp
    monster_HP = monster_HP - m_dam
    lastAttacker = interaction.author.id


async def healHandler(interaction):
    await heal(interaction, hitpoints[interaction.author.id])


@commands.is_owner()
@bot.command(name='generate')
async def generate(ctx=None, channel=None):
    global old_userList, battleOngoing, hitpoints, monster_HP, lastAttacker, userList

    if ctx:
        channel = ctx.channel

    if battleOngoing:
        await channel.reply("There is already an ongoing battle!")
        return

    hitpoints = {}
    monster, mname = getEnemy()
    flavour = getFlavour(mname)

    monster_HP_MAX = 1000 + int(((len(old_userList)) * 100) * random.uniform(0.9, 1.4))
    monster_HP = monster_HP_MAX
    turnTime = 60

    embed = newEmbed(flavour, monster, turnTime - 1, monster_HP, monster_HP_MAX)

    battleOngoing = True
    turn = True
    battleTime = int(time.time())
    print(battleTime)
    turnCount = 0
    lastAttacker = None

    message = await channel.send(embed=embed, components=[
        ActionRow(Button(label="🗡️", custom_id=f"attack_enemy", style=4),
                  Button(label="💊", custom_id=f"heal_player", style=3))])
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
            await asyncio.sleep(1)
            if monster_HP <= 0:
                break
            try:
                await message.edit(
                    embed=newEmbed(flavour, monster, ((battleTime + turnTime) - int(time.time())), monster_HP,
                                   monster_HP_MAX))
            except Exception as e:
                print("Threw Exception! ", e)
            if battleTime + turnTime < int(time.time()):
                userList = []
                battleTime = int(time.time())
                turnCount += 1
                turn = False
        battleTime = int(time.time())
        turn = True
    await message.edit(components=ActionRow())
    if victory:
        msg = f"{mname} was defeated!"
        vEmbed = newEmbed(msg, monster, 0, 0, monster_HP_MAX)
        reg_c = random.randrange(45, 55)
        nar_c = random.randrange(2, 5)
        vEmbed.add_field(name='Monster Defeated',
                         value=f'<@{lastAttacker}> got the final hit! They have been awarded with {reg_c} Candies and {nar_c} Rare Candies!')
        await message.edit(embed=vEmbed)
        addCandies(lastAttacker, reg_c, nar_c)
    else:
        msg = f"{mname} got away!"
        vEmbed = newEmbed(msg, monster, 0, monster_HP, monster_HP_MAX)
        vEmbed.add_field(name='Monster Escaped', value=f'The monster escaped, so nobody won anything! :(')

    old_userList = hitpoints.items()


async def attack(action, player_hp):
    attackLow = 75
    attackHigh = 150
    attackDmg = random.randrange(attackLow, attackHigh)

    if player_hp < 50:
        attackDmg = int(attackDmg * 1.15)
    elif player_hp < 25:
        attackDmg = int(attackDmg * 1.25)

    n_C = random.randrange(1, 10)
    r_C = 0
    c_C, c_R = getCandies(action.author.id)

    HPLoss = random.randrange(10, 35)
    player_hp = player_hp - HPLoss

    if HPLoss > 30:
        attackDmg = int(attackDmg * 1.10)

    crit = random.randrange(1, 100)

    if crit >= 95:
        r_C = 1
        attackDmg = attackDmg * 2
        pmEmbed = discord.Embed(title="You attack the enemy!", color=0xFFD800)
        pmEmbed.description = f"CRITICAL HIT! You deal {attackDmg} damage!\nThe enemy dropped {n_C} candies and {r_C} rare candy. You now have {c_C + n_C} candies and {c_R + r_C} rare candies."
        player_hp = player_hp + HPLoss
        pmEmbed.set_image(
            url='https://media.discordapp.net/attachments/669077343482019870/902003156924379156/tumblr_m0biocwpJC1rnm2iko1_500.png')
    else:
        pmEmbed = discord.Embed(title="You attack the enemy!", color=0xD95249)

        if player_hp < 0:
            HPLoss = HPLoss + player_hp
            player_hp = 0

        if HPLoss == 0:
            dmgText = ' and take no'
        else:
            dmgText = f', but take {HPLoss}'

        pmEmbed.description = f'You deal {attackDmg} damage{dmgText} damage in return.\nYou currently have **{player_hp}/100** health remaining.\nThe enemy dropped {n_C} candies. You now have {c_C + n_C} candies'
    await action.send(embed=pmEmbed)

    addCandies(action.author.id, n_C, r_C)

    return attackDmg, player_hp


async def heal(action, hitpoints):
    healLow = 15
    healHigh = 55
    heal = random.randrange(healLow, healHigh)

    if hitpoints > 75:
        heal = int(heal * 0.75)

    hlEmbed = discord.Embed(title="You take a moment to heal your wounds.", color=0x59A361)
    if hitpoints + heal >= 100:
        hlEmbed.description = "You were fully healed!\nYou have **100/100** health remaining."
    else:
        hitpoints = hitpoints + heal
        hlEmbed.description = f"You were healed by {heal} hitpoints.\nYou now have **{hitpoints}/100** health remaining."

    await action.send(embed=hlEmbed)

    return hitpoints


@bot.command()
async def candytest(ctx):
    currentC, c_r_c = getCandies(ctx.author.id)
    await ctx.send(f"You currently have {currentC} Candies and {c_r_c} rare candies!")
    addCandies(ctx.author.id, 1, 5)
    currentC, c_r_c = getCandies(ctx.author.id)
    await ctx.send(f"You currently have {currentC} Candies and {c_r_c} rare candies!")

@tasks.loop(minutes=15)
async def m_start():
    await generate(channel=bot.get_channel(monsterchannel))


@commands.is_owner()
@bot.command()
async def start(ctx):
    await m_start.start()


@commands.is_owner()
@bot.command()
async def stop(ctx):
    await m_start.stop()

@bot.event
async def on_button_click(interaction):
    global userList, hitpoints

    print("button pushed, ", interaction)

    if interaction.author.id not in hitpoints:
        hitpoints[interaction.author.id] = 100

    if hitpoints[interaction.author.id] <= 0:
        await interaction.send(content="GAME OVER!\nYou were defeated and have been disengaged from the battle!")
        return
    if interaction.author.id in userList:
        await interaction.send(content="You have already acted this turn!")
        return
    else:
        userList.append(interaction.author.id)

    if interaction.custom_id == 'attack_enemy' and battleOngoing is True:
        await attackHandler(interaction)
    elif interaction.custom_id == 'heal_player' and battleOngoing is True:
        await healHandler(interaction)
    else:
        await interaction.send("There's not an ongoing battle!")
        userList = []

if __name__ == '__main__':
    print("Starting!")
    with open('token') as f:
        token = f.readline()
    bot.run(token)
