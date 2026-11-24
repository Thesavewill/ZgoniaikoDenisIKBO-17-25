# Транслятор учебного конфигурационного языка (Вариант №8)

## 1. Общее описание

Инструмент командной строки для трансляции учебного конфигурационного языка в формат JSON.
Входной текст считывается из стандартного потока ввода (`stdin`), а результирующий JSON выводится в стандартный поток вывода (`stdout`). При обнаружении синтаксических ошибок или ошибок вычисления в `stderr` выводится диагностическое сообщение, и программа завершается с ненулевым кодом возврата.

Для синтаксического разбора используется специализированный инструмент **`lark`** (LALR-парсер) с отдельной формальной грамматикой (`src/grammar.lark`).

### Поддерживаемый синтаксис языка

* **Однострочные комментарии:** `# текст комментария`
* **Многострочные комментарии:** `{{! текст комментария }}`
* **Числа:** вещественные числа формата `\d+\.\d*` (например, `42.`, `3.14`, `0.0`)
* **Имена:** идентификаторы формата `[_a-zA-Z][a-zA-Z0-9]*`
* **Словари:** `table(имя => значение, имя => значение,)` (поддерживается произвольная вложенность и опциональная завершающая запятая)
* **Объявление констант:** `имя is значение`
* **Константные выражения (постфиксная запись):** `$[операнд1 операнд2 оператор]`
  * Операции: `+`, `-`, `*`, `/`
  * Функции: `sqrt()`, `pow()`

---

## 2. Описание всех функций и настроек

Проект организован модульно в каталоге `HW/src/`:

| Модуль | Назначение и ключевые компоненты |
| --- | --- |
| `grammar.lark` | Формальная LALR-грамматика языка (числа, комментарии, словари, константы, постфиксные выражения). |
| `errors.py` | Иерархия исключений: `ConfigError` (базовое), `ConfigSyntaxError` (ошибки синтаксиса), `ConfigEvaluationError` (ошибки вычисления). |
| `evaluator.py` | Стековый вычислитель `evaluate_postfix(items, constants)` с проверкой типов операндов, делением на ноль, извлечением корня из отрицательных чисел и контролем баланса стека. |
| `parser.py` | `build_parser()` (загрузка грамматики), `ConfigTransformer` (обход AST и хранение таблицы констант), `parse_config(text)` (разбор в структуры Python). |
| `cli.py` | `translate(text)` (преобразование в JSON с отступом 2 пробела), `main()` (чтение `stdin` с очисткой UTF-8 BOM, запись в `stdout`/`stderr`). |

### Коды возврата CLI

* `0` (`EXIT_SUCCESS`) — успешная трансляция.
* `1` (`EXIT_ERROR`) — синтаксическая ошибка или ошибка вычисления константного выражения.

---

## 3. Команды для сборки проекта и запуска тестов

Команды выполняются из корня репозитория.

### Установка зависимостей

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r HW\requirements.txt
```

**Linux / macOS / WSL:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r HW/requirements.txt
```

### Запуск транслятора

**Через модуль Python (из корня репозитория):**
```powershell
Get-Content HW\examples\game_balance.conf -Raw | .\.venv\Scripts\python.exe -m HW.src.cli
```

```bash
python3 -m HW.src.cli < HW/examples/game_balance.conf
```

**Через скрипты запуска (из каталога `HW/`):**
```powershell
.\run.bat < examples\game_balance.conf
```

```bash
./run.sh < examples/game_balance.conf
```

### Запуск тестов

```powershell
.\.venv\Scripts\python.exe -m pytest HW/tests -v
```

Набор из 60 тестов (`HW/tests/`) покрывает примитивы, комментарии, словари, глубокую вложенность, объявление и подстановку констант, все операции постфиксного вычислителя, обработку ошибок, запуск CLI в отдельном процессе (`subprocess`) и все три примера предметных областей.

---

## 4. Примеры использования

Готовые конфигурации из трёх разных предметных областей находятся в папке `HW/examples/`.

### Пример 1: Игровой баланс (`examples/game_balance.conf`)

**Вход:**
```text
# Конфигурация характеристик и баланса персонажа
{{! Расчёт базовых параметров и урона
    для тестового сценария }}

baseHp is 100.0
armorRating is 25.0
critMult is 1.5
baseDmg is 20.0

table(
  health => table(
    base => $[baseHp],
    effective => $[baseHp armorRating 100.0 / 1.0 + *],
  ),
  combat => table(
    attack => $[baseDmg],
    critDamage => $[baseDmg critMult *],
    burstPower => $[baseDmg 2.0 pow() critMult + sqrt()],
  ),
)
```

**Выход (JSON):**
```json
{
  "health": {
    "base": 100.0,
    "effective": 125.0
  },
  "combat": {
    "attack": 20.0,
    "critDamage": 30.0,
    "burstPower": 20.037464909513878
  }
}
```

### Пример 2: Сетевая инфраструктура (`examples/server_cluster.conf`)

**Вход:**
```text
# Настройки кластера и тайм-аутов сервисов
workersPerNode is 4.0
nodesCount is 3.0
baseTimeout is 1.5

table(
  cluster => table(
    nodes => $[nodesCount],
    totalWorkers => $[workersPerNode nodesCount *],
    {{! Запас по времени на сетевые повторы }}
    requestTimeout => $[baseTimeout 2.0 * 0.5 +],
  ),
  healthcheck => table(
    intervalSec => 5.0,
    jitterWindow => $[baseTimeout sqrt()],
  ),
)
```

**Выход (JSON):**
```json
{
  "cluster": {
    "nodes": 3.0,
    "totalWorkers": 12.0,
    "requestTimeout": 3.5
  },
  "healthcheck": {
    "intervalSec": 5.0,
    "jitterWindow": 1.224744871391589
  }
}
```

### Пример 3: Финансовая модель (`examples/finance_model.conf`)

**Вход:**
```text
# Параметры расчёта ставки и бюджетных лимитов
principal is 50000.0
annualRate is 0.12
years is 2.0

table(
  loan => table(
    amount => $[principal],
    monthlyRate => $[annualRate 12.0 /],
    growthFactor => $[1.0 annualRate + years pow()],
    totalProjected => $[principal 1.0 annualRate + years pow() *],
  ),
  reserve => table(
    minBuffer => $[principal 0.1 *],
    riskIndex => $[annualRate 100.0 * sqrt()],
  ),
)
```

**Выход (JSON):**
```json
{
  "loan": {
    "amount": 50000.0,
    "monthlyRate": 0.01,
    "growthFactor": 1.2544000000000002,
    "totalProjected": 62720.00000000001
  },
  "reserve": {
    "minBuffer": 5000.0,
    "riskIndex": 3.4641016151377544
  }
}
```