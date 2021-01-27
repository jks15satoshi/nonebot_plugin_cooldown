# nonebot-plugin-cooldown

适用于 Nonebot 2 的冷却事件管理插件。

[![time tracker](https://wakatime.com/badge/github/jks15satoshi/nonebot_plugin_cooldown.svg)](https://wakatime.com/badge/github/jks15satoshi/nonebot_plugin_cooldown)

> 由于本人 Python 水平低下，因此源码可能会令人不适。

## 关于冷却事件

冷却事件是一种用以限制用户功能调用频率的机制。在该插件中，冷却事件由事件标签所标识，每个事件包含若干个由事件记录，其中事件记录包含群组 ID、用户 ID 和事件结束时间戳三个字段，事件状态由以上字段共同决定。

根据群组 ID 与用户 ID 设定的不同，该插件的冷却事件分为如下四种：

- **全局冷却事件**：限制任何群组的任何成员调用功能；
- **群组冷却事件**：限制特定群组的任何成员调用功能；
- **一般冷却事件**：限制特定群组的特定成员调用功能；
- **用户冷却事件**：限制特定用户调用功能。

事件优先级由上至下依次递减。

## 安装

### 通过 `nb-cli` 安装

````shell
nb plugin install nonebot-plugin-cooldown
````

### 通过 Poetry 安装

````shell
poetry add nonebot-plugin-cooldown
````

### 通过 `pip` 安装

````shell
pip install nonebot-plugin-cooldown
````

## 使用

### 加载插件

请参考 Nonebot 2 官方文档的 [加载插件](https://v2.nonebot.dev/guide/loading-a-plugin.html) 章节，在项目中加载该插件。

### CRUD

该插件提供了数种方法对冷却事件进行 CRUD 操作，可在 [该文件](nonebot_plugin_cooldown/cooldown.py) 的方法注释中查看使用方法。

### 自定义匹配规则

该插件提供了自定义匹配规则 `is_cooled_down`，用于判断事件生效状态。可在 [该文件](nonebot_plugin_cooldown/rule.py) 的方法注释中查看使用方法。

关于如何使用匹配规则，参考 Nonebot 2 官方文档的 [自定义 rule](https://v2.nonebot.dev/guide/creating-a-matcher.html#%E8%87%AA%E5%AE%9A%E4%B9%89-rule) 章节。

### 配置

该插件可通过在配置文件中添加如下配置项对部分功能进行配置。关于如何设置插件配置项，参考 Nonebot 2 官方文档的 [基本配置](https://v2.nonebot.dev/guide/basic-configuration.html) 章节。

- **`CD_AUTOBACKUP_PERIOD`**：自动备份事件周期（秒），默认为 `600`；
- **`CD_AUTOREMOVE_PERIOD`**：自动移除无效事件周期（秒），默认为 `3600`。
- **`CD_BACKUP_FILE`**：事件备份文件路径（建议在 `bot.py` 文件中使用 `pathlib` 进行配置或使用绝对路径）。

## 许可协议

该项目以 MIT 协议开放源代码，详阅 [LICENSE](LICENSE) 文件。
