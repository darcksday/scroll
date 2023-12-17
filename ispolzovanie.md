# Использование

Чтобы начать работать надо перейти в папку с пректом и запустить&#x20;

```
source venv/bin/activate
python3 main.py
```

Если все гуд вы должны увидеть:

<figure><img src=".gitbook/assets/Screenshot 2023-12-14 194423.png" alt=""><figcaption></figcaption></figure>



### 6. пункт - Interact with contracts &#x20;

Здесь вы можете депозитить и снимать ETH и таким способом набивать обьем и взамодейсвовать с своими задеплоиными контрактами в сети SCROLL

<figure><img src=".gitbook/assets/Screenshot 2023-12-14 194707 (1).png" alt=""><figcaption></figcaption></figure>

Выбираем пункт и вводим суму, диапазон или пусто (если вся сума) и жмем ENTER - скрипт начинает работу.

### 7. пункт - Bridge USDT to USDV&#x20;

USDT уже должно быть на балансе выбраной сети. Тут доступно 2 варианта:&#x20;

<figure><img src=".gitbook/assets/Screenshot 2023-12-14 195104.png" alt=""><figcaption></figcaption></figure>



### 8. пункт - цепочный бридж Bridge : Bitget->Arbitrum USDT -> BSC USDV-> Bitget

Скрипт пробегаеться кошель за кошелем - актуально для прогона больших сум &#x20;

### 9. пункт - . Orbiter: Bridge ETH: OKX->\[LINEA->RANDOM NETWORKS->LINEA]->OKX&#x20;

Можешь воспользоваться акцией орбитера и прогнать там транзы через Линеа, заработав тем самым поинты + сделать объем бриджей в разных сетях, например прогнать до 2 ЕТН:&#x20;

* из ОКХ в linea
* из linea в zksync
* из zksync в linea
* из linea в scroll
* из scroll в linea
* из linea в nova
* из nova в linea
* из linea в polygon\_zkevm
* из polygon\_zkevm в linea
* из linea в base
* из base в linea
* из linea на ОКХ

Маршрут генериться рандомно. Убрать или добавить сеть а также указать суму <mark style="color:red;">(max 2 ETH)</mark> можно в\
**config/orbiter\_config.py.** Так же в конфиге можно включить задевание лендингов в разных сетях розкоментовав код в переменной ADDITIONAL\_FUNCTIONS.&#x20;

* zksync - eralend
* scroll-laverbank
* zkevm - 0vix



Каждый бридж обойдется в ±1.5$

**Важно:**  Если надо оставлять баланс в нативке вы моежете настроить это в `config/settings.py - MIN_BALANCE`  для каждой из сети (можно диапазоном **'0.008-0.01'** )

