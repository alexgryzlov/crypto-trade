import typing as tp


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
    def __init__(self, amount_asset: tp.Union[Asset, str], price_asset: tp.Union[Asset, str]):
        self.amount_asset: Asset = amount_asset if isinstance(amount_asset, Asset) else Asset(amount_asset)
        self.price_asset: Asset = price_asset if isinstance(price_asset, Asset) else Asset(price_asset)

    @classmethod
    def from_string(cls, amount_asset: str, price_asset: str):
        return cls(Asset(amount_asset), Asset(price_asset))

    def __repr__(self) -> str:
        return f"{self.amount_asset}/{self.price_asset}"

    def __reversed__(self) -> 'AssetPair':
        return AssetPair(self.price_asset, self.amount_asset)
