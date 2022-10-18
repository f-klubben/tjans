import re


class InputValidation:
    BID_PATTERN = r'^\d+ \d*,\d*,\d*$'
    BID_INSTANT_WIN_PATTERN = r'^\d+ win$'
    BID_FREEBIE_PATTERN = r'^\d+ free$'
    CONVERT_PATTERN = r'^\d*,\d*,\d*$'

    @classmethod
    def validate_bid_input(cls, bid: str) -> bool:
        """
        Validate bid Textbox input
        Should match InputValidation.BID_PATTERN, e.g., "2 3:2:0", "5 :10:"
        """
        return bool(re.match(cls.BID_PATTERN, bid.strip()))

    @classmethod
    def validate_bid_instant_win(cls, bid: str) -> bool:
        """
        Validate instant win bid
        Should match InputValidation.BID_INSTANT_WIN_PATTERN, e.g., "4 win"
        """
        return bool(re.match(cls.BID_INSTANT_WIN_PATTERN, bid.strip()))

    @classmethod
    def validate_bid_freebie(cls, bid: str) -> bool:
        """
        Validate bid freebie - for when only one team remains
        Should match InputValidation.BID_FREEBIE, e.g., "7 free"
        """
        return bool(re.match(cls.BID_FREEBIE_PATTERN, bid.strip()))

    @classmethod
    def validate_convert_input(cls, conversion: str) -> bool:
        """
        Validate conversion Textbox input
        Should match InputValidation.CONVERT_PATTERN, e.g., "6::9", "4:20:"
        """
        return bool(re.match(cls.CONVERT_PATTERN, conversion.strip()))
