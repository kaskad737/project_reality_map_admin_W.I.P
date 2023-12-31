import host
import bf2
import random
from game.realitymaplist import MAPLISTALL
from config import config


def init():
    host.registerGameStatusHandler(onGameStatusChanged)

def deinit():
    host.unregisterGameStatusHandler(onGameStatusChanged)

def debugMessage(msg):
    host.rcon_invoke('echo "%s"' % (str(msg)))

def debugIngame(msg):
    try:
        host.rcon_invoke('game.sayAll "%s"' % (str(msg)))
    except:
        host.rcon_invoke('echo "debugIngame(FAIL): %s"' % (str(msg)))

def onGameStatusChanged(status):

    if status == bf2.GameStatus.Playing:
        global tickets_limit_big_maps
        global players_limit_for_skirmish

        tickets_limit_big_maps = int(config['tickets_limit_big_maps'])
        players_limit_for_skirmish = int(config['players_limit_for_skirmish'])

        global server_maplist
        server_maplist = host.rcon_invoke("maplist.list")

        global is_map_set
        is_map_set = False

        global mock_maps_statistics
        mock_maps_statistics = {
            "route": 12,
            "vadso_city": 16,
            "ulyanovsk": 8,
            "op_barracuda": 8,
            "beirut": 25,
            "ramiel": 15,
            "saaremaa": 17,
            "burning_sands": 20,
            "ascheberg": 36,
            "kokan": 14,
            "muttrah_city_2": 13,
            "dovre_winter": 13,
            "nuijamaa": 9,
            "black_gold": 25,
            "khamisiyah": 71,
            "asad_khal": 28,
            "albasrah_2": 17,
            "silent_eagle": 63,
            "operation_falcon": 16,
            "outpost": 11,
            "dragon_fly": 10,
            "adak": 38,
            "road_to_damascus": 27,
            "masirah": 14,
            "gaza_2": 39,
            "fallujah_west": 54,
            "battle_of_ia_drang": 8,
            "wanda_shan": 11,
            "shipment": 2,
            "dovre": 13,
            "deagle5": 3,
            "korengal": 2,
            "fields_of_kassel": 9,
            "operation_marlin": 18,
            "pavlovsk_bay": 19,
            "xiangshan": 10,
            "lashkar_valley": 3,
            "sbeneh_outskirts": 15,
            "the_falklands": 6,
            "tad_sae": 3,
            "shijiavalley": 10,
            "shahadah": 8,
            "hades_peak": 8,
            "korbach_offensive": 11,
            "musa_qala": 6,
            "assault_on_grozny": 21,
            "fools_road": 10,
            "carentan": 8,
            "operation_bobcat": 15,
            "sahel": 4,
            "kunar_province": 8,
            "karbala": 10,
            "bamyan": 13,
            "charlies_point": 9,
            "kafar_halab": 14,
            "brecourt_assault": 5,
            "operation_thunder": 15,
            "assault_on_mestia": 10,
            "kashan_desert": 20,
            "ras_el_masri_2": 9,
            "zakho": 16,
            "kozelsk": 9,
            "reichswald": 7,
            "omaha_beach": 9,
            "iron_ridge": 16,
            "hill_488": 4,
            "goose_green": 2,
            "operation_soul_rebel": 4,
            "operation_ghost_train": 4,
            "merville": 1
        }

        # registering chatMessage handler
        host.registerHandler('ChatMessage', onChatMessage)
        host.registerHandler('PlayerKilled', onPlayerKilled)

        debugMessage('START CUSTOM SCRIPT INIT') 

def onChatMessage(playerId, text, channel, flags):
    # fix for local non-dedicated servers
    if playerId == -1:
        playerId = 255

    # getting player object by player index
    player = bf2.playerManager.getPlayerByIndex(playerId)

    # standart check for invalid players
    if player is None or player.isValid() is False:
        return

    # common way to filter chat message
    # clearing text as any channel except Global are prefixed
    text = text.replace('HUD_TEXT_CHAT_COMMANDER', '')
    text = text.replace('HUD_TEXT_CHAT_TEAM', '')
    text = text.replace('HUD_TEXT_CHAT_SQUAD', '')
    text = text.replace('HUD_CHAT_DEADPREFIX', '')
    text = text.replace('* ', '')
    text = text.strip()

    args = text.split(' ')
    if args[0] == '!test':
        # for test map change logic
        bf2.gameLogic.setTickets(1, 99)
    if args[0] == '!test2':
        # for test map change logic (skirmish)
        bf2.gameLogic.setTickets(1, 45)

# When a player gets killed, check if he needs to teamswitch
def onPlayerKilled(p, attacker, weapon, assists, obj):
    global is_map_set
    debugMessage('TEST MESSAGE PLAYER KILLED')
    if not is_map_set:
        # Get tickets for each team
        first_team_tickets = int(bf2.gameLogic.getTickets(1))
        second_team_tickets = int(bf2.gameLogic.getTickets(2))
        debugMessage(str(first_team_tickets))
        debugMessage(str(second_team_tickets))
        if ((first_team_tickets < tickets_limit_big_maps) or (second_team_tickets < tickets_limit_big_maps)):
            debugMessage('ONE TEAM HAVE LESS THEN 100 TICKETS, SETTING NEW MAP')
            is_map_set = True
            total_players_on_server_count = get_players_count()
            mapStatisticsCounter(actual_total_players=total_players_on_server_count)

def mapStatisticsCounter(actual_total_players):
    '''
    Map choose logic (Work in progress)
    '''
    # map_name = bf2.gameLogic.getMapName()
    # map_state = bf2.serverSettings.getGameMode()
    maps_statistics_new = sorted(mock_maps_statistics.items(), key=lambda x: x[1])
    # take five less playes maps (w.i.p.)
    five_least_frequently_played = maps_statistics_new[:5]
    # random choose three maps from these five
    random_choise_of_three_maps = random.sample(five_least_frequently_played, 3)
    # random choose one map from these three
    random_choise = random.choice(random_choise_of_three_maps)
    # take only map name
    next_map_name = random_choise[0]

    # search for all kinds of modes for our map
    possible_map_configurations = []
    for element in MAPLISTALL:
        if element[0] == next_map_name:
            possible_map_configurations.append(element)

    # gpm_insurgency
    # gpm_cq
    # gpm_skirmish
    # here we filter the game modes for the map
    # we search for skirmish mode in map modes
    if actual_total_players < players_limit_for_skirmish:
        if 'gpm_skirmish' in possible_map_configurations[0][1]:
            possible_map_configurations_sorted = possible_map_configurations
    # or, in case of "big" map, we take only insurgency and aas mode's
    # TODO: need add logic to choose ins or aas 
    else:
        possible_map_configurations_sorted = [map for map in possible_map_configurations if map[1] in ('gpm_insurgency', 'gpm_cq')]

    choose_possible = random.choice(possible_map_configurations_sorted)
    choose_mapname, choose_mode, choose_map_mode  = choose_possible

    debugMessage(str(choose_possible))

    # Echo: 414: silent_eagle gpm_vehicles 64
    for i in server_maplist.strip().split("\n"):
        res1 = i.split(':')
        mapid = int(res1[0])
        mapname = res1[1].split(' ')[1].strip('"')
        mode = res1[1].split(' ')[2].strip()
        map_int = int(res1[1].split(' ')[3])
        map_mode = None
        if map_int == 128:
            map_mode = "Lrg"
        if map_int == 64:
            map_mode = "Std"
        if map_int == 32:
            map_mode = "Alt"
        if map_int == 16:
            map_mode = "Inf"
        if (mapname == choose_mapname) and (mode == choose_mode) and (map_mode == choose_map_mode):
            debugMessage('SET SUCCES')
            host.rcon_invoke("admin.nextLevel %i" % mapid)
            break

def get_players_count():
    team_one_players_count = bf2.playerManager.getNumberOfPlayersInTeam(1)
    team_two_players_count = bf2.playerManager.getNumberOfPlayersInTeam(2)
    total_players_count = int(team_one_players_count) + int(team_two_players_count)
    return total_players_count