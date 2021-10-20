# Trading bot
Team project at MIPT.


## Overview
Trading bot for cryptocurrencies via strategies based on technical analysis.
__WavesExchange__ was taken as the exchange.
The structure was created, so it is easy to change the exchange(but something went wrong, and it will take some actions).
You can see strategies in the [strategies/](strategies).

### Basic instances
[__Trading System__](trading_system) – center of the bot  
[__Trading Interface__](trading_interface) – operates with the exchange  
[__Trading Signal Detectors__](trading_signal_detectors) – signals and their detectors needed in strategies  
[__Strategies__](strategies) – strategies themselves  
[__Strategy Runner__](strategies/strategy_runner.py) – runner of the strategy and needed signal detectors  
[__Visualizer__](visualizer) – visualizer of candles, indicators and orders of simulation  


## Running
```shell
python3 main
```


## Running the tests
```shell
pytest .
```


## Authors
[Alex Gryzlov](https://github.com/alexgryzlov) – Developer, Analyst  
[Roman Agureev](https://github.com/romanagureev) – Developer, Analyst  
Anton Kulikov – Developer, Analyst  
Andrei Titov – Developer  
[Mark Nagovitsin](https://github.com/Marchello00) – Developer  
[Denis Shpakovski](https://github.com/Denisson001) – Developer  
[Mehron Bobohonov](https://github.com/BMehron) – Analyst  
[Yulian Gilyazev](https://github.com/yulian-gilyazev) – Analyst  
[Aidar Valiev](https://github.com/AidarValiev) – Analyst  
[Emil Alkin](https://github.com/AlkinEmil) – Analyst  
[Ivan Makeev](https://github.com/Macket) – Supervisor  
