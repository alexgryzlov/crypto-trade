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
    def __init__(self, amount_asset: Asset, price_asset: Asset):
        self.amount_asset = amount_asset
        self.price_asset = price_asset

    def __repr__(self) -> str:
        return f"{self.amount_asset}/{self.price_asset}"

    def __reversed__(self) -> 'AssetPair':
        return AssetPair(self.price_asset, self.amount_asset)
