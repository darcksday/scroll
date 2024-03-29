# Использование

Чтобы начать работать надо перейти в папку с пректом и запустить&#x20;

```
source venv/bin/activate
python3 main.py
```

Если все гуд вы должны увидеть:

<figure><img src=".gitbook/assets/Screenshot 2023-12-14 194423.png" alt=""><figcaption></figcaption></figure>

### 5. Swaps on Dex

Выбрать свап в конкретном дексе

<figure><img src=".gitbook/assets/Screenshot 2024-02-21 021650.png" alt=""><figcaption></figcaption></figure>

### 6. пункт - Interact with contracts &#x20;

Здесь вы можете депозитить и снимать ETH и таким способом набивать обьем и взамодейсвовать с своими задеплоиными контрактами в сети SCROLL а так же заклеймить карточки для Orbiter Points

<figure><img src=".gitbook/assets/Screenshot 2023-12-14 194707 (1).png" alt=""><figcaption></figcaption></figure>

Выбираем пункт и вводим суму, диапазон или пусто (если вся сума) и жмем ENTER - скрипт начинает работу.

### 7. пункт - Bridge USDT to USDV&#x20;

USDT уже должно быть на балансе выбраной сети. Тут доступно 2 варианта:&#x20;

<figure><img src=".gitbook/assets/Screenshot 2023-12-14 195104.png" alt=""><figcaption></figcaption></figure>



### 8. пункт - цепочный бридж Bridge : Bitget->Arbitrum USDT-> Avax USDV -> BSC USDV-> Bitget

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

### 10. Nft/Lendings/DMAIL/etc

<figure><img src=".gitbook/assets/Screenshot 2024-02-21 021833.png" alt=""><figcaption></figcaption></figure>



### 11. Swap ETH <=> Random Token / Random Dex

Свап в рандомном Dex - рандомный токен (туда и обратно).  По-дефолту всегда береться ETH и свапаеться  в рандомном дексе на рандомный токен (добавлял только ликвидные).

Список токенов и дексов можно посмотреть и изменить в **config/swap\_routes.py**

### 12. Run Multiple Functions&#x20;

Здесь собраны все доступные функции, с помощью которых случайным образом генерируется маршрут для каждого кошелька. Вы можете настроить список функций в файле **config/multiple\_routes.py**. Каждая из функций будет выполнена на всех аккаунтах в случайном порядке. Также можно дублировать функции, что удобно, например, для случайных свапов. **По умолчанию все уже будет настроено оптимально**, чтобы охватить максимальное количество протоколов.&#x20;

### 13. Unused Functions&#x20;

Скрипт ищет по всем доступным  в скрипте функциям контракты  которые еще не были задействованы на конретном кошеле и если таких функций несколько - он выбирает рандомную и запускает. Таким образом получиться задействовать весь функционала скрипта и повзаемодействовать с максимальным количеством доступных контрактов.



### 14. Bridge/L0 v2 from Scroll to Random

Бридж используя Layer Zero v2 из Scroll в рандомную дешовую сеть. Список:

'astar', 'manta', 'fuse', 'nova', 'harmony', 'moonriver', 'gnosis', 'coredao', 'tomo', 'opBNB', 'orderly', 'horizen', 'xpla', 'beam',
