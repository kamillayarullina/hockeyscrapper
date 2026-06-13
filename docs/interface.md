# Interface Telegram-bot for notifications

## Interface Type
Telegram-bot

## Intended users
Registered website users who have linked their Telegram account to their account.

## Commands/messages/functions

| Command | Description |
|---------|----------|
| `/start` | Initializing the bot, checking the binding, issuing instructions |
| `/subscribe` | Subscribing to the team | 
| `/unsubscribe` | Unsubscribing the team | 
| `/list` | Current subscribtions | 
| `/matches` | Upcoming current matches | 
| `/teams` | List of all KHL hockey teams | 
| `/help` | Instructions for using the bot |
| `/admin` | Check if user is admin |
| `/admin_interval` | Set interval for parsing |
| `/admin_proxy` | List of proxy |
| `/admin_proxy_add` | Add proxy|
| `/admin_proxy_del` | Delete proxy |
| `/admin_proxy_toggle` | On/off proxy |
| `/admin_run` | Forced parsing cycle |


# Input and Outputs
## Success examples


| Input | Output |
|-------|--------|
| `/start` | `👋 Привет! Я бот для отслеживания хоккейных билетов. Подпишись на любимые команды КХЛ и получай уведомления, как только появятся билеты на их матчи!`<br><br>`📋 Команды для управления:`<br>`• /subscribe ЦСКА — подписаться на команду`<br>`• /unsubscribe ЦСКА — отписаться`<br>`• /list — мои подписки`<br>`• /matches — все актуальные матчи`<br>`• /teams — все доступные команды`<br>`• /help — помощь`<br><br>`🏒 Популярные команды:`<br>`• /цска — ЦСКА`<br>`• /спартак — Спартак`<br>`• /динамо — Динамо Москва`<br>`• /ска — СКА`<br>`• /авангард — Авангард`<br>`• /ак — Ак Барс`<br>`• /салават — Салават Юлаев`<br>`• /трактор — Трактор`<br>`• /металлург — Металлург`<br>`• /локомотив — Локомотив`<br>`...и ещё 12 команд. Полный список: /teams` |
| `/subscribe "ЦСКА"` | `✅ Вы подписались на "ЦСКА"!`<br>`🏟 Автоматически добавлена подписка на стадион: "ЦСКА Арена".`<br>`Теперь вы будете получать уведомления о билетах.` |
| `/unsubscribe "Ак Барс"` | `❌ Вы отписались от Ак Барс.` |
| `/list` | `📋 Ваши подписки:`<br>`🏟 Стадионы (1):`<br>`• Казань, Татнефть Арена`<br><br>`Чтобы отписаться: /unsubscribe ЦСКА` |
| `/matches` | `🏒 Актуальные матчи (3):`<br><br>`1. Матч года. Все звёзды хоккея`<br>`   📅 25 июля, 18:00, СБ`<br>`   📍 г. Санкт-Петербург, СКА Арена`<br>`   💰 6000 ₽ – 6100 ₽`<br>`   ✅ Да`<br><br>`2. Матч Звёзд КХЛ 2027. День 1`<br>`   📅 6 февраля 2027, СБ`<br>`   📍 г. Минск, Минск-Арена`<br>`   💰 6000 ₽ – 6000 ₽`<br>`   ✅ Да`<br><br>`3. Матч Звёзд КХЛ 2027. День 2`<br>`   📅 7 февраля 2027, ВС`<br>`   📍 г. Минск, Минск-Арена`<br>`   💰 6000 ₽ – 6000 ₽`<br>`   ✅ Да`<br><br>`Подробности: /match <номер>`<br>`Например: /match 1` |
| `/match` | `🏒 Новое событие: Матч года. Все звезды хоккея`<br>`📅 Дата: 25 июля, 18:00, СБ`<br>`📍 Место: г. Санкт-Петербург, СКА Арена`<br>`⚔️ Команды: Не определены`<br>`💰 Цена: 6000 ₽ – 6100 ₽`<br>`✅ Наличие: Да`<br><br>`🔗 Купить билет (ссылка появится при старте продаж)` |
| `/teams` | `🏒 Доступные команды (22):`<br><br>`• ЦСКА`<br>`• Спартак`<br>`• Динамо Москва`<br>`• СКА`<br>`• Авангард`<br>`• Ак Барс`<br>`• Салават Юлаев`<br>`• Трактор`<br>`• Металлург`<br>`• Локомотив`<br>`• Сибирь`<br>`• Торпедо`<br>`• Лада`<br>`• Витязь`<br>`• Северсталь`<br>`• Нефтехимик`<br>`• Амур`<br>`• Адмирал`<br>`• Куньлунь`<br>`• Барыс`<br>`• Динамо Минск`<br>`• Сочи`<br><br>`Подписаться: /subscribe ЦСКА` |
| `/help` | `🤖 Как пользоваться ботом:`<br><br>`1️⃣ Подпишитесь на команды: /subscribe ЦСКА`<br>`2️⃣ Можете подписаться на несколько команд`<br>`3️⃣ Как только появятся билеты на матч с вашей командой — я пришлю вам уведомление с ценой и ссылкой`<br><br>`📋 Команды:`<br>`• /subscribe команда — подписка`<br>`• /unsubscribe команда — отписка`<br>`• /list — посмотреть подписки`<br>`• /matches — все актуальные матчи`<br>`• /match номер — детали матча`<br>`• /teams — все команды`<br>`• /stats — статистика бота`<br>`• /help — эта справка` |
| `/stats` | `📊 Статистика бота:`<br><br>`👥 Пользователей: `<br>`🏒 Подписок на команды: 1`<br>`🏟 Подписок на стадионы: 2`<br>`🎟 Матчей в базе: 3` |
| `/admin` | `Now we do not have proxy.` |
| `/admin_interval "minutes "(only for admin)` | `✅ Интервал парсинга изменён на "minutes" мин.` |
| `/admin_proxy (only for admin)` | `Now we do not have proxy.` |
| `/admin_proxy_add (only for admin)` | `Now we do not have proxy.` |
| `/admin_proxy_del (only for admin)` | `Now we do not have proxy.` |
| `/admin_proxy_toggle (only for admin)` | `Now we do not have proxy.` |
| `/admin_run (only for admin)` | `⏳ Запуск принудительного цикла парсинга...`<br>`✅ Цикл парсинга завершён.` |

## Unsuccess examples


| Input | Output |
|-------|--------|
| `/subscribe (without team name)` | `❗️ Укажите название команды.`<br>`Пример: /subscribe ЦСКА\`<br>`Список команд: /teams` |
| `/unsubscribe (without team name)` | `❗️ Укажите название команды.`<br>`Пример: /subscribe ЦСКА` |
| `/match (without number)` | `❗️ Укажите номер матча.`<br>`Пример: /match 1` |
| `/admin (if user is not admin)` | `⛔️ У вас нет доступа к админ-панели.` |
| `/admin (if there is no proxy)` | `Прокси: не настроены.` |
| `/admin_interval (without minutes)` | `❗️ Укажите интервал в минутах.`<br>`Пример: /admin_interval 15` |
| `/admin_proxy (if there is no proxy)` | `📭 Прокси не настроены.`<br>`Добавить: /admin_proxy_add http://user:pass@host:port` |
| `/admin_proxy_add (without URL proxy)` | `❗️ Укажите URL прокси.`<br>`Пример:`<br>`/admin_proxy_add http://user:pass@1.2.3.4:8080 `<br>`/admin_proxy_add socks5://1.2.3.4:1080 ru мой_прокси` |
| `/admin_proxy_del (without ID proxy)` | `❗️ Укажите ID прокси.`<br>`Список: /admin_proxy` |
| `/admin_proxy_toggle (without ID proxy)` | `❗️ Укажите ID прокси.`<br>`Список: /admin_proxy` |
