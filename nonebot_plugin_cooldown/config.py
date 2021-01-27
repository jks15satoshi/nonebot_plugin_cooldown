from pathlib import Path
from typing import Union

from pydantic import BaseSettings


class Config(BaseSettings):
    cd_autobackup_period: int = 600
    cd_autoremove_period: int = 3600
    cd_backup_file: Union[Path, str] = (Path(__file__).parent / '.cache' /
                                        'cooldown_backup.json')

    class Config:
        extra = 'ignore'
