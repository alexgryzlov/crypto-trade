class Asset:
    def __init__(self, asset_name: str):
        self.name = asset_name

    def __repr__(self) -> str:
        return self.name

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Asset):
            return self.name == other.name
        return False


class AssetPair:
    def __init__(self, main_asset: Asset, secondary_asset: Asset):
        self.main_asset = main_asset
        self.secondary_asset = secondary_asset

    def __repr__(self) -> str:
        return f"{self.main_asset}/{self.secondary_asset}"

    def __reversed__(self) -> 'AssetPair':
        return AssetPair(self.secondary_asset, self.main_asset)
