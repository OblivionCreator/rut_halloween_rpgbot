import asyncio
import json
import operator
import os
import random
import time
import disnake.ext.commands
from disnake.ext import commands, tasks
from disnake import Button, ActionRow

intents = disnake.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=['h!'], case_insensitive=True, intents=intents)
monsterchannel = 903869168636551218


def getCandies(userid: int):
    if not os.path.isfile(f'./candy_jar/{userid}.json'):
        with open(f"./candy_jar/{userid}.json", 'x') as file:
            def_candies = {
                'candy': 0,
                'rare_candy': 0
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
        'candy': candy,
        'rare_candy': r_candy
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
        '<:madDummyBro:764589495379034162>': 'Bruh Dummy',
        '🙊 🙊': 'Snickers',
        ':green_square: :skull_crossbones: :green_square:': 'Dancing Greenscreen Skeleton',
        ':race_car: :police_car:': 'Hot Pursuit',
        ':flag_gb:': 'The British Empire',
        ':heart:': 'DETERMINATION',
        '<:botsanstroll:902416763478761474>': '\"Sans\"',
        '<:sansbadtime:278804488889040896>': 'Sans',
        ':red_circle::knife:     :blue_circle:': 'Crewmates',
        ':hedgehog: :ring: :ring: :ring:': 'Sonic The Hedgehog',
        ':tophat:\n:bat:': 'Bat in a Hat',
        '💉🌻': 'The Experiment',
        ':adhesive_bandage::head_bandage:': 'DIY Mummy',
        '⚱️🚬': 'Pot Smoker',
        ':nut_and_bolt::man_zombie::nut_and_bolt:': 'It\'s Alive!',
        ':peach:': 'Suspicious Fruit',
        ':gun::monkey_face:': 'Monkioso',
        ':skull::skull::adhesive_bandage::skull::skull:': 'Skeleton Band',
        '<:crow1:903391005246619658><:crow2:903391005108215868><:crow3:903391005053698088><:crow4:903391005045309480><:crow5:903391004953042945><:crow6:903391004776882210>': 'A Murder of Crows',
        '🥜 🛒': 'Nutdealer',
        '<:spamdude:903964210533388369>': '{{NUMBER 2 RATED SALESMAN 1997}}'
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


def newEmbed(flavour, monster, time, health, maxhealth, actions='ATTACKS IN...', color=0xff0000):
    global hitpoints, old_deadlist, deadlist

    aliveFighters = []
    deadFighters = []
    t_deadText = ''
    t_aliveText = ''
    aliveText = "Nobody is fighting!"
    deadText = "Nobody is wounded!"
    playerDead = False
    playerAlive = False
    if len(hitpoints) < 1:
        aliveText = "Nobody has entered this battle!"
        deadText = "Nobody is wounded!"
    else:
        for i in hitpoints:
            tempHP = hitpoints[i]
            if tempHP <= 0:
                playerDead = True
                if i not in deadlist:
                    deadlist.append(i)
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

    embed = disnake.Embed(title=f"{flavour}",
                          description=f"{monster}", color=color)
    embed.add_field(name="CURRENT HP", value=f"{health} / {maxhealth}", inline=True)
    if actions: embed.add_field(name=actions, value=f"{time + 1} Seconds", inline=True)
    embed.add_field(name="COMBATANTS:", value="_ _", inline=False)
    embed.add_field(name="THE FIGHTERS", value=aliveText, inline=True)
    embed.add_field(name="THE FALLEN", value=deadText, inline=True)

    return embed


difficulty = 0
old_userList = []
old_deadlist = []
deadlist = []
battleOngoing = False
monster_HP = 0
hitpoints = {}
dmgDone = {}
lastAttacker = 0
userList = []
turn = False
loss = False


async def attackHandler(interaction):
    global monster_HP, hitpoints, lastAttacker
    lastAttacker = interaction.author.id
    if monster_HP > 0:
        m_dam, p_hp = await attack(interaction, hitpoints[interaction.author.id])
        hitpoints[interaction.author.id] = p_hp
        monster_HP = monster_HP - m_dam
    else:
        sadEmbed = disnake.Embed(title='Too Late!',
                                 description='The monster has already been killed so you cannot attack it!')
        interaction.send(embed=sadEmbed, ephemeral=True)

async def candyHandler(interaction):
    global hitpoints
    cur_can, r_c = getCandies(interaction.author.id)
    candyToLose = random.randrange(10, 30)

    if cur_can < candyToLose:
        candyToLose = cur_can

    finalcandy = cur_can - candyToLose

    dead_players = []

    for i in hitpoints:
        if hitpoints[i] == 0:
            dead_players.append(i)

    if len(dead_players) == 0 or candyToLose == 0:
        if candyToLose > 0:
            cEmbed = disnake.Embed(title=f'You throw out some candy.', description=f'You threw away {candyToLose} candies. Good job..? You now have {finalcandy} candies.\n_(...what a waste of candy.)_', color=0x388500)
        else:
            cEmbed = disnake.Embed(title='You tried to throw out some candy.', description='But you have no candy to throw!', color=0x388500)
    else:
        player = random.choice(dead_players)
        guild = interaction.guild
        user = guild.get_member(player)
        cEmbed = disnake.Embed(title=f'You threw {candyToLose} candies at {user.name}.',
                               description=f'<@{player}> was healed by {candyToLose} health!', color=0x65EA00)
        hitpoints[player] = candyToLose
        deadlist.remove(player)

    addCandies(interaction.author.id, -candyToLose, 0)

    await interaction.send(embed=cEmbed, ephemeral=True)

async def healHandler(interaction):
    return await heal(interaction, hitpoints[interaction.author.id])


@commands.is_owner()
@bot.command(name='generate')
async def generate(ctx=None, channel=None):
    global old_userList, deadlist, old_deadlist, battleOngoing, hitpoints, monster_HP, lastAttacker, userList, turn, loss, dmgDone

    old_deadlist = deadlist
    deadlist = []

    if ctx:
        channel = ctx.channel

    if battleOngoing:
        return

    hitpoints = {}
    dmgDone = {}
    monster, mname = getEnemy()
    flavour = getFlavour(mname)

    monster_HP_MAX = round(((len(old_userList)) * 400) * random.uniform(0.9, 1.3))
    if loss:
        monster_HP_MAX = int(monster_HP_MAX * 0.75)
    if monster_HP_MAX < 3200:
        monster_HP_MAX = 3200
    if mname == 'Sans':
        monster_HP_MAX = 1
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
        disnake.ui.ActionRow(disnake.ui.Button(label="🗡️ Attack Enemy", custom_id=f"attack_enemy", style=disnake.Color(4), disabled=False),
                  disnake.ui.Button(label="💊 Heal Yourself", custom_id=f"heal_player", style=disnake.Color(3), disabled=False),
                  disnake.ui.Button(label="🍬 Throw Candy", custom_id=f"throw_candy", style=disnake.Color(1), disabled=False))])
    while battleOngoing:
        userList = []
        if monster_HP <= 0:
            turn = False
            battleOngoing = False
            victory = True
        elif turnCount >= 10:
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
                                   monster_HP_MAX), components=[
        disnake.ui.ActionRow(disnake.ui.Button(label="🗡️ Attack Enemy", custom_id=f"attack_enemy", style=disnake.Color(4), disabled=False),
                  disnake.ui.Button(label="💊 Heal Yourself", custom_id=f"heal_player", style=disnake.Color(3), disabled=False),
                  disnake.ui.Button(label="🍬 Throw Candy", custom_id=f"throw_candy", style=disnake.Color(1), disabled=False))])
            except Exception as e:
                print("Threw Exception! ", e)
            if battleTime + turnTime < int(time.time()):
                userList = []
                battleTime = int(time.time())
                turnCount += 1
                turn = False

        if monster_HP > 0 and turnCount < 10:
            await message.edit(components=[
                disnake.ui.ActionRow(disnake.ui.Button(label="🗡️ Attack Enemy", custom_id=f"attack_enemy", style=disnake.Color(4), disabled=True),
                          disnake.ui.Button(label="💊 Heal Yourself", custom_id=f"heal_player", style=disnake.Color(3), disabled=True),
                          disnake.ui.Button(label="🍬 Throw Candy", custom_id=f"throw_candy", style=disnake.Color(1), disabled=True))])
            attacking = True
            attacked = {}
            attackstring = ''

            validTargets = []
            targetList = []

            for i in hitpoints:
                if hitpoints[i] > 0:
                    validTargets.append(i)

            atkcount = round((len(validTargets)) / 4)
            if atkcount > 15:
                atkcount = 15
            elif atkcount == 0:
                attacking = False
        else:
            attacking = False
        if attacking:
            attackstring = ''
            while atkcount > 0 and attacking:
                if len(validTargets) == 0:
                    embed = newEmbed(f"{mname} is taking their turn!", monster, 14, monster_HP,
                                     monster_HP_MAX, actions=f"Turn Length:", color=0xFFD800)
                    embed.add_field(name=f'{mname} Tried Attacking...', value="But they weren't able to attack anyone!",
                                    inline=False)
                    attacking = False
                    break
                t_dmg = random.randrange(10, 35)
                t_crit = random.randrange(1, 100)
                targetValid = False
                while not targetValid:
                    t_attacked = random.choice(validTargets)
                    if t_attacked not in targetList:
                        targetValid = True
                        targetList.append(t_attacked)

                if t_crit >= 98:
                    t_dmg = t_dmg * 2
                attacked[t_attacked] = t_dmg
                hitpoints[t_attacked] = hitpoints[t_attacked] - t_dmg
                if hitpoints[t_attacked] < 0:
                    t_dmg = t_dmg + hitpoints[t_attacked]
                    hitpoints[t_attacked] = 0
                attackstring = f'{attackstring}<@{t_attacked}> for {t_dmg} Damage!\n'
                embed = newEmbed(f"{mname} is taking their turn!", monster, (14 + atkcount), monster_HP,
                                 monster_HP_MAX, actions=f"Turn Length:", color=0xFFD800)
                embed.add_field(name=f'{mname} attacked:', value=attackstring, inline=False)
                await message.edit(embed=embed)
                await asyncio.sleep(1)
                atkcount -= 1
            await asyncio.sleep(15)
        elif monster_HP > 0:
            embed = newEmbed(f"{mname} is taking their turn!", monster, 4, monster_HP,
                             monster_HP_MAX, actions=f"Turn Length:", color=0xFFD800)
            embed.add_field(name=f'{mname} tried attacking!', value="But they weren't able to attack anyone!",
                            inline=False)
            await message.edit(embed=embed, components=[
        disnake.ui.ActionRow(disnake.ui.Button(label="🗡️ Attack Enemy", custom_id=f"attack_enemy", style=disnake.Color(4), disabled=True),
                  disnake.ui.Button(label="💊 Heal Yourself", custom_id=f"heal_player", style=disnake.Color(3), disabled=True),
                  disnake.ui.Button(label="🍬 Throw Candy", custom_id=f"throw_candy", style=disnake.Color(1), disabled=True))])
            await asyncio.sleep(5)

        battleTime = int(time.time())
        if turnCount < 10:
            turn = True
    await message.edit(components=ActionRow())
    if victory:
        msg = f"{mname} was defeated!"
        vEmbed = newEmbed(msg, monster, 0, 0, monster_HP_MAX, actions=False)
        reg_c = random.randrange(35, 75)
        nar_c = random.randrange(2, 6)

        dmg_c = random.randrange(35, 75)
        dmg_r = random.randrange(2, 6)

        bestAttacker = None
        tmpDMG = 0
        tmpUSR = 0
        for i in dmgDone:
            if dmgDone[i] > tmpDMG and lastAttacker is not i:
                tmpDMG = dmgDone[i]
                tmpUSR = i

        if tmpUSR != 0:
            vEmbed.add_field(name='Monster Defeated',
                             value=f'<@{lastAttacker}> got the final hit! They have been awarded with {reg_c} Candies and {nar_c} Rare Candies! (+{nar_c / 2}% Candy Multiplier)\n<@{tmpUSR}> did the most damage with {tmpDMG} damage! They have been awarded with {dmg_c} candies and {dmg_r} rare candies.',
                             inline=False)
        else:
            vEmbed.add_field(name='Monster Defeated',
                             value=f'<@{lastAttacker}> got the final hit! They have been awarded with {reg_c} Candies and {nar_c} Rare Candies! (+{nar_c / 2}% Candy Multiplier)',
                             inline=False)
        loss = False
        addCandies(lastAttacker, reg_c, nar_c)
        if tmpUSR != 0:
            addCandies(tmpUSR, dmg_c, dmg_r)
    else:
        msg = f"{mname} got away!"
        vEmbed = newEmbed(msg, monster, -1, monster_HP, monster_HP_MAX, actions=False)
        vEmbed.add_field(name=f'{mname} Escaped', value=f'{mname} escaped, so nobody won anything! :(', inline=False)
        loss = True
    candyLeaderboard = {}
    rareCandyLeaderboard = {}
    trueCandyLeaderboard = {}
    s_CL = {}
    s_RL = {}
    for i in os.listdir('./candy_jar'):
        print(i)
        user = int(i[:-5])
        with open(f'./candy_jar/{i}', 'r') as file:
            raw = json.loads(file.read())
            candy, r_candy = raw
            r_C = raw[candy]
            r_R = raw[r_candy]
        candyLeaderboard[user] = r_C
        rareCandyLeaderboard[user] = r_R

    c_length = len(candyLeaderboard)

    lv1Str = ''
    lv2Str = ''
    lv3Str = ''
    lv4Str = ''
    lv5Str = ''
    lv6Str = ''
    lv7Str = ''
    lv8Str = ''
    lv9Str = ''

    for i in candyLeaderboard:
        value = candyLeaderboard[i]
        rare_value = rareCandyLeaderboard[i]
        true_value = round(value * (1 + min(0.5, (rare_value / 200))))
        trueCandyLeaderboard[i] = true_value

        lvEmbed = disnake.Embed(title='Level Up!', description='The Following users have levelled up!')

        guild = message.guild
        user = guild.get_member(i)

        try:
            if 0 < true_value < 100:
                role = disnake.utils.get(guild.roles, id=903193578979868683)
                if role not in user.roles:
                    await user.add_roles(role)
                    if len(lv1Str) < 924:
                        lv1Str = f'{lv1Str}<@{i}>, '
            elif 100 < true_value < 250:
                role = disnake.utils.get(guild.roles, id=903193687171948574)
                if role not in user.roles:
                    await user.add_roles(role)
                    if len(lv2Str) < 924:
                        lv2Str = f'{lv2Str}<@{i}>, '
            elif 250 < true_value < 500:
                role = disnake.utils.get(guild.roles, id=903193808685113385)
                if role not in user.roles:
                    await user.add_roles(role)
                    if len(lv3Str) < 924:
                        lv3Str = f'{lv3Str}<@{i}>, '
            elif 500 < true_value < 1000:
                role = disnake.utils.get(guild.roles, id=903194375360757761)
                if role not in user.roles:
                    await user.add_roles(role)
                    if len(lv4Str) < 924:
                        lv4Str = f'{lv4Str}<@{i}>, '
            elif 1000 < true_value < 1500:
                role = disnake.utils.get(guild.roles, id=903194550175154176)
                if role not in user.roles:
                    await user.add_roles(role)
                    if len(lv5Str) < 924:
                        lv5Str = f'{lv5Str}<@{i}>, '
            elif 1500 < true_value < 2500:
                role = disnake.utils.get(guild.roles, id=903194918208569384)
                if role not in user.roles:
                    await user.add_roles(role)
                    if len(lv6Str) < 924:
                        lv6Str = f'{lv6Str}<@{i}>, '
            elif 2500 < true_value < 5000:
                role = disnake.utils.get(guild.roles, id=904482997556895794)
                if role not in user.roles:
                    await user.add_roles(role)
                    if len(lv7Str) < 924:
                        lv7Str = f'{lv7Str}<@{i}>, '
            elif 5000 < true_value < 10000:
                role = disnake.utils.get(guild.roles, id=905084335747637249)
                if role not in user.roles:
                    await user.add_roles(role)
                    if len(lv8Str) < 924:
                        lv8Str = f'{lv8Str}<@{i}>, '
            elif 10000 < true_value:
                role = disnake.utils.get(guild.roles, id=905088080095109120)
                if role not in user.roles:
                    await user.add_roles(role)
                    if len(lv9Str) < 924:
                        lv9Str = f'{lv9Str}<@{i}>, '

        except Exception as e:
            print(e, true_value, user, role)

    embCount = 0

    if len(lv1Str) > 0: lvEmbed.add_field(name='Candy Consumer (1-100)', value=lv1Str, inline=False); embCount += 1
    if len(lv2Str) > 0: lvEmbed.add_field(name='Candy Collector (100-250)', value=lv2Str, inline=False); embCount += 1
    if len(lv3Str) > 0: lvEmbed.add_field(name='Candy Curator (250-500)', value=lv3Str, inline=False); embCount += 1
    if len(lv4Str) > 0: lvEmbed.add_field(name='Candy Celebrator (500-1000)', value=lv4Str, inline=False); embCount += 1
    if len(lv5Str) > 0: lvEmbed.add_field(name='Candy Chieftain (1000-1500)', value=lv5Str, inline=False); embCount += 1
    if len(lv6Str) > 0: lvEmbed.add_field(name='Candy Cosmopolitan! (1500-2500)', value=lv6Str,
                                          inline=False); embCount += 1
    if len(lv7Str) > 0: lvEmbed.add_field(name='Candy Confidant!!! (2500-5000)', value=lv7Str,
                                          inline=False); embCount += 1
    if len(lv8Str) > 0: lvEmbed.add_field(name='Candy Corporal!!! (5000-10000)', value=lv8Str,
                                          inline=False); embCount += 1
    if len(lv9Str) > 0: lvEmbed.add_field(name='Candy Connoisseur!!! (10,000+)', value=lv9Str,
                                          inline=False); embCount += 1

    if embCount > 0:
        levelup = await message.reply(embed=lvEmbed)

    sorted_tCL = dict(sorted(trueCandyLeaderboard.items(), key=operator.itemgetter(1), reverse=True))

    # while len(s_CL) < c_length and len(s_CL) < 10:
    #    temp = (0, 0)
    #    for i in candyLeaderboard:
    #        t_v, t_u = temp
    #        i_mult = candyLeaderboard[i]
    #        i_mult = int(i_mult * ((((rareCandyLeaderboard[i])/100)/2)+1))

    #        if i_mult > t_v:
    #            temp = i_mult, i

    #    t_v, t_u = temp
    #    s_CL[t_u] = t_v
    #    candyLeaderboard.pop(t_u)

    l_STR = ""

    count = 1
    for u in sorted_tCL:
        if count > 10:
            break
        l_STR = f'{l_STR}{count}) <@{u}> - {sorted_tCL[u]} Candies | {rareCandyLeaderboard[u]} Rare Candies ({min(50.0, rareCandyLeaderboard[u] / 2)}% Bonus Multiplier)\n'
        count += 1

    vEmbed.add_field(name='Candy Leaderboard!', value=l_STR, inline=True)

    await message.edit(embed=vEmbed)

    old_userList = hitpoints.items()


async def attack(action, player_hp):
    global dmgDone
    attackLow = 95
    attackHigh = 175
    attackDmg = random.randrange(attackLow, attackHigh)

    if player_hp < 50:
        attackDmg = int(attackDmg * 1.25)
    elif player_hp < 25:
        attackDmg = int(attackDmg * 1.35)

    n_C = random.randrange(5, 15)

    rareChance = 98
    if random.randrange(0, 100) >= rareChance:
        r_C = 1
    else:
        r_C = 0
    c_C, c_R = getCandies(action.author.id)

    HPLoss = random.randrange(0, 45)
    player_hp = player_hp - HPLoss

    if HPLoss > 30:
        attackDmg = int(attackDmg * 1.10)

    crit = random.randrange(1, 100)

    if crit >= 95:
        r_C += 1
        attackDmg = attackDmg * 3
        pmEmbed = disnake.Embed(title="You attack the enemy!", color=0xFFD800)
        pmEmbed.description = f"**CRITICAL HIT!** You deal {attackDmg} damage!\nThe enemy dropped {n_C} candies and {r_C} rare candy. You now have {c_C + n_C} candies and {c_R + r_C} rare candies."
        player_hp = player_hp + HPLoss
        pmEmbed.set_image(
            url='https://media.discordapp.net/attachments/669077343482019870/902003156924379156/tumblr_m0biocwpJC1rnm2iko1_500.png')
    else:
        pmEmbed = disnake.Embed(title="You attack the enemy!", color=0xD95249)

        if player_hp < 0:
            HPLoss = HPLoss + player_hp
            player_hp = 0

        if HPLoss == 0:
            dmgText = ' and take no'
        else:
            dmgText = f', but take {HPLoss}'

        if r_C == 0:
            pmEmbed.description = f'You deal {attackDmg} damage{dmgText} damage in return.\nYou currently have **{player_hp}/100** health remaining.\nThe enemy dropped {n_C} candies. You now have {c_C + n_C} candies'
        else:
            pmEmbed.description = f'You deal {attackDmg} damage{dmgText} damage in return.\nYou currently have **{player_hp}/100** health remaining.\nThe enemy dropped {n_C} candies and {r_C} rare candy!. You now have {c_C + n_C} candies and {c_R + r_C} rare candies.'
    await action.send(embed=pmEmbed,ephemeral=True)

    addCandies(action.author.id, n_C, r_C)

    if action.author.id not in dmgDone:
        dmgDone[action.author.id] = attackDmg
    else:
        dmgDone[action.author.id] = dmgDone[action.author.id] + attackDmg

    return attackDmg, player_hp


async def heal(action, hitpoints):
    healLow = 20
    healHigh = 60
    heal = random.randrange(healLow, healHigh)

    if hitpoints > 75:
        heal = int(heal * 0.75)

    hlEmbed = disnake.Embed(title="You take a moment to heal your wounds.", color=0x59A361)
    hitpoints = min(100, (hitpoints + heal))
    if hitpoints == 69:
        hitpoints = 70
        heal = heal + 1
    if hitpoints == 100:
        hitpoints = 100
        hlEmbed.description = "You were fully healed!\nYou have **100/100** health remaining."
    else:
        hlEmbed.description = f"You were healed by {heal} hitpoints.\nYou now have **{hitpoints}/100** health remaining."

    await action.send(embed=hlEmbed, ephemeral=True)

    return hitpoints


@commands.is_owner()
@bot.command()
async def send(ctx, channel, title, *, message: str):
    currentC, c_r_c = getCandies(ctx.author.id)
    ch = bot.get_channel(int(channel))
    embed = disnake.Embed(title=title, description=message, color=0xff0000)
    await ch.send(embed=embed)


@tasks.loop(minutes=25)
async def m_start():
    await generate(channel=bot.get_channel(monsterchannel))


@bot.command()
async def start(ctx):
    guild = ctx.guild
    role = disnake.utils.get(guild.roles, id=244328249801310219)

    if role in ctx.author.roles or ctx.author.id == 110399543039774720:
        await m_start.start()


@bot.command()
async def stop(ctx):
    guild = ctx.guild
    role = disnake.utils.get(guild.roles, id=244328249801310219)

    if role in ctx.author.roles or ctx.author.id == 110399543039774720:
        m_start.stop()


@bot.listen("on_button_click")
async def on_button_click(interaction):
    global userList, hitpoints

    if turn is False and battleOngoing is True:
        await interaction.send(content="The monster is currently taking their turn so you cannot act!", ephemeral=True)
        return

    if not battleOngoing:
        await interaction.response.send_message("There's not an ongoing battle!", ephemeral=True)
        userList = []
        return

    if interaction.author.id not in hitpoints:
        if interaction.author.id in old_deadlist:
            hitpoints[interaction.author.id] = 50
        else:
            hitpoints[interaction.author.id] = 100

    if hitpoints[interaction.author.id] <= 0:
        await interaction.response.send_message(content="GAME OVER!\nYou were defeated and have been disengaged from the battle!", ephemeral=True)
        return
    if interaction.author.id in userList:
        await interaction.response.send_message(content="You have already acted this turn!", ephemeral=True)
        return
    else:
        userList.append(interaction.author.id)

    if interaction.component.custom_id == 'attack_enemy' and battleOngoing is True:
        await attackHandler(interaction)
    elif interaction.component.custom_id == 'heal_player' and battleOngoing is True:
        hitpoints[interaction.author.id] = await healHandler(interaction)
    elif interaction.component.custom_id == 'throw_candy' and battleOngoing is True:
        await candyHandler(interaction)
    else:
        await interaction.response.send_message("There's not an ongoing battle!", ephemeral=True)
        userList = []


if __name__ == '__main__':
    print("Starting!")
    with open('token') as f:
        token = f.readline()
    bot.run(token)
