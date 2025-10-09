from mcdreforged.api.all import *
import random
import time

# 玩家列表
players = []

# 帮助信息
help_msg = '''--------§a 赛博轮盘赌重制版V1.1 命令列表§r--------
                  §a By LBY123165 & daa0v0
§b!!tnt help §f- §c显示帮助菜单
§b!!tnt list §f- §c显示已加入游戏的玩家列表
§b!!tnt clear §f- §c清除所有玩家
§b!!tnt leave §f- §c离开当前的对局
§b!!add §f- §c加入TNT赌局
§b!!tnt §f- §c随机挑选一名玩家进行爆破

§c本插件所有指令均支持大小写，前缀支持中英文感叹号
§a例：“!!tnt” “!!TNT” "！！tnt" “！！TNT”均可触发
---------------------------------------------
'''

def on_load(server, old):
    server.logger.info('赛博轮盘赌TNT插件V1.2加载成功！')

def on_load(server: PluginServerInterface, old_module):
    def register_tnt_command(prefix):
        server.register_command(
            Literal(prefix)
            .then(Literal('help').runs(lambda src: show_help(src)))
            .then(Literal('HELP').runs(lambda src: show_help(src)))
            .then(Literal('list').runs(lambda src: list_players(src)))
            .then(Literal('LIST').runs(lambda src: list_players(src, server)))
            .then(Literal('clear').runs(lambda src: clear_players(src, server)))
            .then(Literal('CLEAR').runs(lambda src: clear_players(src, server)))
            .then(Literal('leave').runs(lambda src: leave_game(src, server)))
            .then(Literal('LEAVE').runs(lambda src: leave_game(src, server)))
            .runs(lambda src: start_tnt_game(src, server))
        )

    prefixes = ['!!tnt', '!!TNT', '！！tnt', '！！TNT']
    for prefix in prefixes:
        register_tnt_command(prefix)


    def register_add_command(prefix):
        server.register_command(
          Literal(prefix).runs(lambda src: add_player(src, server))
        )
      
    add_prefixes = ['!!add', '!!ADD', '！！add', '！！ADD']
    for prefix in add_prefixes:
      register_add_command(prefix)


    # 帮助信息注册 
    server.register_help_message(
        '!!tnt help',
        '显示赛博轮盘赌的帮助菜单'
    )


def show_help(source: CommandSource):
    for line in help_msg.splitlines():
        source.reply(line)

def add_player(source: CommandSource, server: PluginServerInterface):
    global players
    if source.player not in players:
        players.append(source.player)
        
        # 使用 tellraw 通知全服该玩家已加入游戏
        message = f'{{"text":"{source.player} 加入了TNT赌局!","color":"green"}}'
        server.execute(f'tellraw @a {message}')
        
    else:
        source.reply(f'{source.player} , 你已经在玩家列表之中了')


def list_players(source: CommandSource):
    global players
    if not players:
        source.reply('目前没有玩家加入游戏')
        return

    # 生成玩家列表消息
    player_list = ', '.join(players)
    message = f'已加入游戏的玩家有: {player_list}'
    source.reply(message)

def clear_players(source: CommandSource, server: PluginServerInterface):
    global players
    # 检查玩家权限
    if source.get_permission_level() < 3:
        source.reply('你没有权限使用此指令')
        return

    # 向所有已加入的玩家发送游戏结束消息
    end_message = '{"text":"你所参加的TNT赌局已被管理员结束","color":"red"}'
    for player in players:
        server.execute(f'tellraw {player} {end_message}')

    # 清空玩家列表
    players.clear()

    # 使用 tellraw 通知全服玩家列表已清空
    message = '{"text":"所有玩家已被管理员从TNT赌局列表中清空!","color":"red"}'
    server.execute(f'tellraw @a {message}')

def leave_game(source: CommandSource, server: PluginServerInterface):
    global players
    if source.player in players:
        players.remove(source.player)
        
        # 使用 tellraw 通知全服该玩家已离开游戏
        message = f'{{"text":"{source.player} 离开了TNT赌局!","color":"yellow"}}'
        server.execute(f'tellraw @a {message}')
        source.reply(f'{source.player} 成功离开了赌局')
    else:
        source.reply(f'{source.player} 你本来就不在玩家列表中！')

def start_tnt_game(source: CommandSource, server: PluginServerInterface):
    global players
    
    # 检查指令执行者是否在已加入的玩家列表中
    if source.player not in players:
        source.reply('你必须先使用!!add加入之后才能使用这个指令')
        return

    if len(players) < 2:
        source.reply('玩家人数不足，至少需要两个玩家才能开始游戏')
        return
  
    if not players:
        source.reply('列表中还没有玩家')
        return

    # 随机选择一个玩家作为目标
    target_player = random.choice(players)
    
    # 使用 tellraw 通知全服已加入的玩家和被选中的玩家
    joined_players = ', '.join(players)
    game_start_message = f'{{"text":"游戏开始! 本局加入的玩家有: {joined_players}","color":"yellow"}}'
    target_message = f'{{"text":"{target_player} 是被选中的倒霉蛋!","color":"red"}}'
    server.execute(f'tellraw @a {game_start_message}')
    time.sleep(1)
    server.execute(f'tellraw @a {target_message}')

    # 应用 instant_damage 效果来模拟致命伤害
    server.execute(f'execute as {target_player} run damage @s 50 minecraft:magic')
    time.sleep(1)

    # 通知所有玩家游戏结束
    end_game_message = '{"text":"游戏结束，如需开始下一局请重新使用!!add加入!","color":"gray"}'
    server.execute(f'tellraw @a {end_game_message}')

    # 清空玩家列表
    players.clear()