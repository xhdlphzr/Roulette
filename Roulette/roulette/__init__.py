from mcdreforged.api.all import *
from mcdreforged.api.types import PluginServerInterface
import random
import time

# 玩家列表
players = []
god = []
fuck = False

# 帮助信息
help_msg = '''--------§a 赛博轮盘赌重制版V1.3 命令列表§r--------
                  §a By LBY123165 & daa0v0 & EndKing2012
§b!!tnt help §f- §c显示帮助菜单
§b!!tnt list §f- §c显示已加入游戏的玩家列表
§b!!tnt clear §f- §c清除所有玩家
§b!!tnt leave §f- §c离开当前的对局
§b!!add §f- §c加入TNT赌局
§b!!tnt §f- §c随机挑选一名玩家进行爆破

§c本插件所有指令均支持大小写，前缀支持中英文感叹号
§a例："!!tnt" "!!TNT" "！！tnt" "！！TNT"均可触发
---------------------------------------------
'''

def on_load(server: PluginServerInterface, old_module):
    server.logger.info('赛博轮盘赌TNT插件V1.2加载成功！')
    server.register_help_message('!!tnt help', '显示赛博轮盘赌的帮助菜单')

    # 注册 !!tnt 及其变体
    tnt_prefixes = ['!!tnt', '!!TNT', '！！tnt', '！！TNT']
    for prefix in tnt_prefixes:
        server.register_command(
            Literal(prefix).
            then(Literal('help').runs(show_help)).
            then(Literal('list').runs(list_players)).
            then(Literal('clear').requires(lambda src: src.has_permission(3)).runs(lambda src: clear_players(src, server))).
            then(Literal('leave').runs(lambda src: leave_game(src, server))).
            runs(lambda src: start_tnt_game(src, server))
        )

    # 注册 !!add 及其变体
    add_prefixes = ['!!add', '!!ADD', '！！add', '！！ADD']
    for prefix in add_prefixes:
        server.register_command(Literal(prefix).runs(lambda src: add_player(src, server)))

    # 注册管理员命令
    server.register_command(
        Literal('!!god').
        then(Text('player').runs(set_god)).
        requires(lambda src: src.has_permission(3))
    )
    server.register_command(
        Literal('!!fuck').
        runs(toggle_fuck).
        requires(lambda src: src.has_permission(3))
    )

def show_help(source: CommandSource):
    source.reply(help_msg)

def set_god(source: CommandSource, context: CommandContext):
    global god
    player = context['player']
    if player not in god:
        god.append(player)
        source.reply(f'§a已设置 {player} 为神')
    else:
        source.reply(f'§c{player} 已经是神了')

def toggle_fuck(source: CommandSource):
    global fuck
    fuck = not fuck
    status = "开启" if fuck else "关闭"
    source.reply(f'§6fuck模式已{status}')
    source.get_server().execute(f'tellraw @a §6fuck模式已{status}')

def add_player(source: CommandSource, server: PluginServerInterface):
    global players
    if not source.is_player:
        source.reply('§c只有玩家可以执行此命令')
        return
        
    if source.player not in players:
        players.append(source.player)
        message = f'§a{source.player} 加入了TNT赌局!'
        server.say(message)
    else:
        source.reply(f'§c{source.player} , 你已经在玩家列表之中了')

def list_players(source: CommandSource):
    global players
    if not players:
        source.reply('§6目前没有玩家加入游戏')
        return

    player_list = '§a, §a'.join(players)
    source.reply(f'§6已加入游戏的玩家有: §a{player_list}')

def clear_players(source: CommandSource, server: PluginServerInterface):
    global players
    if players:
        server.say('§c你所参加的TNT赌局已被管理员结束')
        players.clear()
        server.say('§c所有玩家已被管理员从TNT赌局列表中清空!')
    else:
        source.reply('§6玩家列表已经是空的')

def leave_game(source: CommandSource, server: PluginServerInterface):
    global players
    if not source.is_player:
        source.reply('§c只有玩家可以执行此命令')
        return
        
    if source.player in players:
        players.remove(source.player)
        server.say(f'§e{source.player} 离开了TNT赌局!')
        source.reply(f'§a{source.player} 成功离开了赌局')
    else:
        source.reply(f'§c{source.player} 你本来就不在玩家列表中！')

def start_tnt_game(source: CommandSource, server: PluginServerInterface):
    global players, god, fuck
    
    # 检查执行者
    if not source.is_player:
        source.reply('§c只有玩家可以执行此命令')
        return
    
    # 检查god模式
    if not god:    
        # 普通模式检查
        if source.player not in players:
            source.reply('§c你必须先使用!!add加入之后才能使用这个指令')
            return

        if len(players) < 2:
            source.reply('§c玩家人数不足，至少需要两个玩家才能开始游戏')
            return
    else:
        # god模式特殊处理
        if source.player not in players or len(players) < 2 or not players:
            players.clear()
            players.append(source.player)
            players.append(god[0])
            server.say(f'§6God模式激活: {source.player} 将与 {god[0]} 对决')

    # 选择目标玩家
    if not fuck:
        target_player = random.choice(players)
    else:
        target_player = source.player
    
    # 游戏开始消息
    joined_players = ', '.join(players)
    server.say(f'§6游戏开始! 本局加入的玩家有: {joined_players}')
    time.sleep(1)
    
    # 目标玩家消息
    if god and target_player in god:
        server.say(f'§c{target_player} 服务器之神被神力反噬了!')
    else:
        server.say(f'§c{target_player} 被服务器之神制裁了!')
    
    # 执行伤害
    try:
        server.execute(f'execute as {target_player} run damage @s 500 minecraft:magic')
    except Exception as e:
        server.logger.error(f'执行伤害命令时出错: {e}')
        # 备用方案
        server.execute(f'effect give {target_player} minecraft:instant_damage 1 255')
    
    time.sleep(1)
    
    # 游戏结束消息
    server.say('§7游戏结束，如需开始下一局请重新使用!!add加入或直接使用!!tnt与腐竹对决!')
    
    # 清空玩家列表
    players.clear()