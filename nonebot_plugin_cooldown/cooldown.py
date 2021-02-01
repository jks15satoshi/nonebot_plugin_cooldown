import json
import time
from typing import Any

import nonebot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from nonebot.adapters import Bot
from nonebot.log import logger

from .config import Config


_cooldown_events = {}

driver = nonebot.get_driver()
config = Config(**driver.config.dict())

BACKUP_FILE = config.cd_backup_file

scheduler = AsyncIOScheduler()


def set_event(token: str, duration: int, event_type='normal', **kwargs) -> (
        None):
    """
    添加/更新冷却事件

    参数：
    - `token: str`：事件标签。
    - `duration: int`：冷却事件持续时间（秒）。

    关键字参数：
    - `event_type: str`：事件类型，默认为 `normal`。包括：
        - `global`：全局冷却事件；
        - `group`：群组冷却事件，需要额外的关键字参数 `group: int` 指定群组 ID；
        - `normal`：一般冷却事件，需要额外的关键字参数 `group: int` 和
          `user: int` 分别指定群组 ID 和用户 ID；
        - `user`：用户冷却事件，需要额外的关键字参数 `user: int` 指定用户 ID。
    """
    global _cooldown_events

    group = kwargs.get('group') if event_type in ('group', 'normal') else 0
    user = kwargs.get('user') if event_type in ('normal', 'user') else 0

    if not _cooldown_events.get(token):
        _cooldown_events[token] = []

    current_time = int(time.time())
    result = {
        'group': group,
        'user': user,
        'expired_time': current_time + duration
    }

    # 更新记录
    for i, record in enumerate(_cooldown_events[token]):
        if record.get('group') == group and record.get('user') == user:
            _cooldown_events[token][i] = result
            logger.debug(f'Cooldown event {token}({result}) has been updated.')
            return

    # 添加记录
    _cooldown_events[token].append(result)
    logger.warning(_cooldown_events)
    logger.debug(f'Cooldown event {token}({result}) has been set.')


def get_event(token: str, ignore_priority=False, event_type='normal',
              **kwargs) -> dict[str, Any]:
    """
    获取冷却事件状态。

    通常情况下，当存在较高优先级的事件正在生效时，返回较高优先级的事件状态。详
    见参数 `ignore_priority` 注释。

    参数：
    - `token: str`：事件标签。

    关键字参数：
    - `ignore_priority: bool`：忽略事件优先级，默认为 `False`。当忽略事件优先级
      时，将严格根据事件类型返回对应的事件状态，否则返回较高优先级的事件状态。
    - `event_type: str`：事件类型，默认为 `normal`。包括：
        - `global`：全局冷却事件；
        - `group`：群组冷却事件，需要额外的关键字参数 `group: int` 指定群组 ID；
        - `normal`：一般冷却事件，需要额外的关键字参数 `group: int` 和
          `user: int` 分别指定群组 ID 和用户 ID；
        - `user`：用户冷却事件，需要额外的关键字参数 `user: int` 指定用户 ID。

    返回：
    - `Dict[str, Any]`：事件状态。包含两个字段：
        - `status: bool`：冷却状态，其中 `True` 表示冷却正在生效，反之则为
          `False`；
        - `remaining: int`：冷却剩余时间（秒），当 `status` 字段值为 `False` 时
          该字段值为 0。
    """
    global _cooldown_events

    status = False
    remaining = 0
    current_time = int(time.time())

    group = kwargs.get('group') if event_type in ('group', 'normal') else 0
    user = kwargs.get('user') if event_type in ('normal', 'user') else 0

    if (records := _cooldown_events.get(token)):
        for record in records:
            record_group = record.get('group')
            record_user = record.get('user')
            expired_time = record.get('expired_time')

            # 冷却事件正在生效
            is_valid = expired_time - current_time >= 0
            # 事件记录为全局冷却事件
            is_global_record = not record_group and not record_user
            # 事件记录为群组冷却事件
            is_group_record = record_group == group and not record_user
            # 事件记录为一般冷却事件
            is_normal_record = record_group == group and record_user == user
            # 事件记录为用户冷却事件
            is_user_record = not record_group and record_user == user

            # 忽略优先级模式
            ignore_priority_pattern = ignore_priority and is_normal_record
            # 一般模式
            normal_pattern = (is_global_record or is_group_record or
                              is_normal_record or is_user_record)

            if (ignore_priority_pattern or normal_pattern) and is_valid:
                status = True
                remaining = expired_time - current_time

    return {
        'status': status,
        'remaining': remaining
    }


def del_event(token: str, event_type='normal', **kwargs) -> None:
    """
    移除冷却事件。

    参数：
    - `token: str`：事件标签。

    关键字参数：
    - `event_type: str`：事件类型，默认为 `normal`。包括：
        - `global`：全局冷却事件；
        - `group`：群组冷却事件，需要额外的关键字参数 `group: int` 指定群组 ID；
        - `normal`：一般冷却事件，需要额外的关键字参数 `group: int` 和
          `user: int` 分别指定群组 ID 和用户 ID；
        - `user`：用户冷却事件，需要额外的关键字参数 `user: int` 指定用户 ID。
    """
    global _cooldown_events

    group = kwargs.get('group') if event_type in ('group', 'normal') else 0
    user = kwargs.get('user') if event_type in ('normal', 'user') else 0

    records = _cooldown_events.get(token)
    for i, record in enumerate(records):
        if record.get('group') == group and record.get('user') == user:
            del records[i]
            logger.info(f'Event {token}({record}) has been removed manually.')


@driver.on_startup
def _init() -> None:
    """初始化 scheduler。"""
    if not scheduler.running:
        scheduler.start()
        logger.info('Scheduler started')


@driver.on_startup
def _restore() -> None:
    """驱动启动时从备份文件恢复数据。"""
    global _cooldown_events

    if BACKUP_FILE.exists():
        with open(BACKUP_FILE) as backup:
            _cooldown_events = json.load(backup)
            logger.debug(f'Restored data from file {BACKUP_FILE.absolute()}.')
    else:
        logger.warning(f'Backup file {BACKUP_FILE.absolute()} does not exist, '
                       'skip restoring.')


@driver.on_startup
@scheduler.scheduled_job('interval', seconds=config.cd_autoremove_period)
def _remove_expired() -> None:
    """
    自动移除过期事件。

    自动移除时间间隔可通过配置项 `CD_AUTOREMOVE_PERIOD` 自定义，默认时间为 3600
    秒。
    """
    global _cooldown_events
    count = 0
    current_time = int(time.time())

    # 移除过期的事件记录
    for _, records in _cooldown_events.items():
        for i, record in enumerate(records):
            if record.get('expired_time') - current_time <= 0:
                del records[i]
                count += 1

    # 移除无事件记录的事件标签
    _cooldown_events = {k: v for k, v in _cooldown_events.items() if v}

    logger.debug(f'Automatically removed expired cooldown records: '
                 f'{count} {"records" if count != 1 else "event"} removed.')


@driver.on_startup
@scheduler.scheduled_job('interval', seconds=config.cd_autobackup_period)
def _auto_backup() -> None:
    """
    自动备份数据。

    自动备份时间周期可通过配置项 `CD_AUTOBACKUP_PERIOD` 自定义，默认时间为 600
    秒。
    """
    _backup()


@driver.on_bot_disconnect
async def _backup_on_disconnect(bot: Bot) -> None:
    """
    Bot 断开连接时备份数据。

    参数：
    - `bot: nonebot.adapters.cqhttp.Bot`：Bot 对象。
    """
    _backup()


def _backup() -> None:
    """备份冷却事件。"""
    global _cooldown_events

    if not (path := BACKUP_FILE.parent).is_dir():
        path.mkdir()

    with open(BACKUP_FILE, 'w') as backup:
        json.dump(_cooldown_events, backup, indent=4)
        logger.debug(f'Backed up cooldown data to file '
                     f'{BACKUP_FILE.absolute()}.')
