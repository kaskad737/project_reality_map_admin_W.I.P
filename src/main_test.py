import host
import bf2

def init():
    host.registerGameStatusHandler(onGameStatusChanged)

def deinit():
    host.unregisterGameStatusHandler(onGameStatusChanged)

# ------------------------------------------------------------------------
# onGameStatusChanged
# ------------------------------------------------------------------------
def onGameStatusChanged(status):

    if status == bf2.GameStatus.Playing:
        # registering chatMessage handler
        host.registerHandler('ChatMessage', onChatMessage, 1)
        host.registerHandler('PlayerKilled', onPlayerKilled)

        debugMessage('===== FINISHED CUSTOM SCRIPT INIT =====')

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

    # splitting filtered message text to arguments
    args = text.split(' ')

    if args[0] == '!test':
        debugMessage("TEST MESSAGE TEST MESSAGE NEW SCRIPT")
        debugIngame("TEST MESSAGE TEST MESSAGE NEW SCRIPT TO CHAT")     


def debugMessage(msg):
    host.rcon_invoke('echo "%s"' % (str(msg)))
 
def debugIngame(msg):
    #debugMessage(msg)
    try:
        host.rcon_invoke('game.sayAll "%s"' % (str(msg)))
    except:
        host.rcon_invoke('echo "debugIngame(FAIL): %s"' % (str(msg)))


# When a player gets killed, check if he needs to teamswitch
def onPlayerKilled(p, attacker, weapon, assists, obj):
    p.die = 0
    p.killreason = ""
    debugIngame('TEST MESSAGE PLAYER KILLED')
    if hasattr(p, "teamswitch") and p.teamswitch:
        teamSwitchPlayer(p)
        p.teamswitch = False


def teamSwitchPlayer(p):
    # globalMessage( "Teamswitching player %s" % p.getName( ) )
    if hasattr(p, "teamswitch") and p.teamswitch:
        p.teamswitch = False
    if p.getTeam() == 1:
        p.setTeam(2)
    else:
        p.setTeam(1)