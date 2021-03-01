_to_waves = {
    'WAVES': 'WAVES',
    'USDN': 'DG2xFkPdDwKUoBkzGAhQtLpSGzfXLiCYPEzeKH2Ad24p'
}


class Asset:
    def __init__(self, asset_name):
        self.name = asset_name

    def __repr__(self):
        return self.name

    def to_waves_format(self):
        return _to_waves[self.name]


class AssetPair:
    def __init__(self, main_asset, secondary_asset):
        self.main_asset = main_asset
        self.secondary_asset = secondary_asset

    def __repr__(self):
        return f"({self.main_asset}, {self.secondary_asset})"
