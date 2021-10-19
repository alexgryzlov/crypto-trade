## Strategies
### Requirements
Each strategy should be inherited from [StrategyBase](strategy_base.py).
It will receive loaded `config.json` as a dict in initialization.
See [RSI+MACD Strategy](rsi_macd_strategy) for the best practices.

### Structure
```
<name>/
       <name>.py   – file with strategy
       config.json – config, empty if not needed
       ...         – other files
```
