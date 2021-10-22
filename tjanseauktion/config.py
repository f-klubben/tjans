import os
from configparser import ConfigParser


class Config:
    FILE_NAME = 'cfg.ini'

    def __init__(self):
        self.cfg = self._open_config()

    def _open_config(self) -> ConfigParser:
        """
        Open config file as ConfigParser object
        """
        if not os.path.isfile(self.FILE_NAME):
            print(f'Error: could not find config file, please ensure that {self.FILE_NAME} exists '
                  f'in run directory')
            exit(1)

        cfg = ConfigParser()
        cfg.read(self.FILE_NAME)

        return cfg

    def auction_n_teams(self) -> int:
        """
        Retrieve how many teams we need to generate
        """
        return int(self.cfg.get('auction', 'n_teams'))

    def auction_n_secrets(self) -> int:
        """
        Retrieve how many secret auctions we need to generate
        """
        return int(self.cfg.get('auction', 'n_secrets'))

    def auction_min_overbid_factor(self) -> float:
        """
        Retrieve minimum overbid factor
        """
        return int(self.cfg.get('auction', 'min_overbid_percent')) / 100

    def currency_high_name(self) -> str:
        """
        Retrieve high currency name
        """
        return self.cfg.get('currency', 'high_name')

    def currency_mid_name(self) -> str:
        """
        Retrieve mid currency name
        """
        return self.cfg.get('currency', 'mid_name')

    def currency_low_name(self) -> str:
        """
        Retrieve low currency name
        """
        return self.cfg.get('currency', 'low_name')

    def currency_instant_win_name(self) -> str:
        """
        Retrieve instant win name
        """
        return self.cfg.get('currency', 'instant_win_name')