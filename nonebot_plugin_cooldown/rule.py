from nonebot.adapters import Bot
from nonebot.rule import Rule

from . import cooldown


def is_cooled_down(token: str, type='normal', **kwargs) -> Rule:
    """
    检查冷却事件是否已经结束的规则。如果仍在生效则为 `False`，反之为 `True`。

    参数：
    - `token: str`：事件标签。

    关键字参数：
    - `type: str`：事件类型，默认为 `normal`。包括：
        - `global`：全局冷却事件；
        - `group`：群组冷却事件，需要额外的关键字参数 `group: int` 指定群组 ID；
        - `normal`：一般冷却事件，需要额外的关键字参数 `group: int` 和 
          `user: int` 分别指定群组 ID 和用户 ID；
        - `user`：用户冷却事件，需要额外的关键字参数 `user: int` 指定用户 ID。

    返回：
    - `nonebot.rule.Rule`
    """
    async def _is_cooled_down(bot: Bot) -> bool:
        info = cooldown.get_event(token, type=type, **kwargs)
        return not info.get('status')

    return Rule(_is_cooled_down)
