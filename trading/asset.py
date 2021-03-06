class Asset:
    def __init__(self, asset_name):
        self.name = asset_name

    def __repr__(self):
        return self.name


class AssetPair:
    def __init__(self, main_asset, secondary_asset):
        self.main_asset = main_asset
        self.secondary_asset = secondary_asset

    def __repr__(self):
        return f"{self.main_asset}/{self.secondary_asset}"
