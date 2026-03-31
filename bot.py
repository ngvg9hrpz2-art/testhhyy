#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════════╗
║          VPN KEYS BOT  —  единый файл  (main.py)                ║
╠═══════════════════════════════════════════════════════════════════╣
║  Установка зависимостей:                                         ║
║      pip install aiogram==3.7.0 aiosqlite aiohttp               ║
║                                                                   ║
║  Запуск:                                                          ║
║      python main.py                                              ║
╚═══════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ЛОГИКА БОТА
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 1. ПОЛЬЗОВАТЕЛЬ
    • /start → главное меню (4 кнопки)
    • «🔑 Купить ключ» → выбор тарифа → если баланс ок → подтверждение → ключ
    • «💳 Пополнить баланс» → выбор способа:
          ─ CryptoBot (USDT)  → инвойс → оплата → «Проверить» → зачисление
          ─ Telegram Stars    → send_invoice XTR → оплата → зачисление
          ─ СБП / Карта       → ввод суммы → ждать реквизитов → оплатить
                                → «Я оплатил» → ждать подтверждения админа
    • «👤 Профиль» → баланс, кол-во покупок
    • «📋 Мои ключи» → история купленных ключей

 2. РУЧНАЯ ОПЛАТА (СБП/Карта) — подробный флоу:
    Шаг 1. Пользователь нажимает «СБП / Карта», вводит сумму (≥100₽)
    Шаг 2. Бот: «Получение реквизитов займёт 1-10 мин»
           Бот → ВСЕМ АДМИНАМ: уведомление + кнопки [Отправить реквизиты] [Отклонить]
    Шаг 3. Один из админов нажимает «Отправить реквизиты», вводит карту/ссылку
    Шаг 4. Реквизиты → пользователю + кнопка [✅ Я оплатил]
    Шаг 5. Пользователь нажимает «Я оплатил»
           Бот → ВСЕМ АДМИНАМ: уведомление + кнопки [✅ Подтвердить] [❌ Отклонить]
    Шаг 6. Один из админов нажимает «Подтвердить» → баланс зачислен

 3. CRYPTOBOT:
    Шаг 1. Выбор суммы (привязана к тарифам по цене в USDT)
    Шаг 2. Создание инвойса через CryptoBot API
    Шаг 3. Пользователь платит → нажимает «Проверить оплату»
    Шаг 4. Бот проверяет статус через API → зачисляет баланс в рублях

 4. TELEGRAM STARS:
    Шаг 1. Выбор суммы (привязана к тарифам по цене в Stars)
    Шаг 2. send_invoice currency=XTR
    Шаг 3. Стандартный флоу Stars (pre_checkout_query → successful_payment)
    Шаг 4. Зачисление баланса в рублях

 5. ПАНЕЛЬ АДМИНИСТРАТОРА (/admin):
    • Добавить ключи — выбрать тариф, ввести ключи построчно
    • Статистика — пользователи, продажи, выручка, остатки ключей
    • Рассылка — всем или одному (по ID)
    • Заявки — список ожидающих ручных пополнений

 6. ЛОГИРОВАНИЕ:
    Все события (новый юзер, пополнения, покупки, действия админов)
    отправляются в LOG_CHAT_ID.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

# ====================================================================
# ██  КОНФИГУРАЦИЯ — РЕДАКТИРУЙТЕ ТОЛЬКО ЭТОТ БЛОК  ████████████████
# ====================================================================

BOT_TOKEN = "8511611536:AAE9Dmw3Zb4b2sSeYPUNVKSH7wosxy6wJ3I"
# ↑ Получить: @BotFather → /newbot → скопировать токен

ADMIN_IDS = [8577072935]
# ↑ Telegram ID администраторов (можно несколько через запятую).
#   Узнать свой ID: напишите @userinfobot

LOG_CHAT_ID = 0
# ↑ Куда слать логи о событиях.
#   Можно: свой личный ID ИЛИ ID группы/канала (добавьте бота туда).
#   ID группы всегда отрицательный, например: -1001234567890

CRYPTOBOT_TOKEN = "559977:AAvevVm5MNjNSsNsdSHsmge3Uj7SWHmOJtQ"
# ↑ Как получить:
#   — Основная сеть: @CryptoBot → Pay → My Apps → Create App → токен
#   — Тестовая сеть: @CryptoTestnetBot (то же самое)

CRYPTOBOT_API_URL = "https://pay.crypt.bot/api"
# ↑ Для тестовой сети используйте: "https://testnet-pay.crypt.bot/api"

# ════════════════════════════════════════════════════════════════════
# ██  СКИДКА  —  включить/выключить одной строкой  ████████████████
# ════════════════════════════════════════════════════════════════════
#
#   Чтобы ВКЛЮЧИТЬ скидку:   DISCOUNT_ACTIVE = True
#   Чтобы ВЫКЛЮЧИТЬ скидку:  DISCOUNT_ACTIVE = False
#
DISCOUNT_ACTIVE = True

DISCOUNT_LABEL  = "🎉 Открытие"
# ↑ Название акции — показывается пользователям в меню тарифов.
#   Примеры: "🎉 Открытие", "🎄 Новый год", "🌸 8 марта"

# ════════════════════════════════════════════════════════════════════
# ██  ЦЕНЫ  ████████████████████████████████████████████████████████
# ════════════════════════════════════════════════════════════════════
#
# SOLO  — 1 устройство, базовые протоколы
#   Обычная цена за 1 месяц:
SOLO_PRICE_NORMAL = 89   # ₽/мес
#   Цена со скидкой за 1 месяц (когда DISCOUNT_ACTIVE = True):
SOLO_PRICE_SALE   = 79   # ₽/мес
#
# FAMILY — до 3 устройств, 4 протокола, повышенная скорость
#   Обычная цена за 1 месяц:
FAMILY_PRICE_NORMAL = 149  # ₽/мес
#   Цена со скидкой за 1 месяц (когда DISCOUNT_ACTIVE = True):
FAMILY_PRICE_SALE   = 129  # ₽/мес
#
# Пересчёт для периодов: за 3, 6, 12 месяцев даётся доп. скидка
# (коэффициенты умножаются на месячную цену — можно менять):
PERIOD_MULTIPLIERS = {
    "1m": 1,     # × 1   = цена за 1 мес (без доп. скидки)
    "3m": 2.8,   # × 2.8 = дешевле месяца × 3 — ~7% выгода
    "6m": 5.3,   # × 5.3 = дешевле месяца × 6 — ~12% выгода
    "1y": 9.5,   # × 9.5 = дешевле месяца × 12 — ~21% выгода
}
# Пример: SOLO_PRICE_NORMAL=89, PERIOD_MULTIPLIERS["3m"]=2.8 → 89*2.8 = 249₽

# ════════════════════════════════════════════════════════════════════
# ██  ПРОЧИЕ НАСТРОЙКИ  ███████████████████████████████████████████
# ════════════════════════════════════════════════════════════════════

USDT_TO_RUB = 90
# ↑ Курс: 1 USDT = N рублей баланса. Обновляйте по необходимости.

STAR_TO_RUB = 2
# ↑ Курс: 1 Telegram Star = N рублей баланса.

MIN_MANUAL_TOPUP = 89
# ↑ Минимальная сумма ручного пополнения в рублях.

# ====================================================================
# ██  ДАЛЬШЕ НЕ ТРОГАТЬ  ████████████████████████████████████████████
# ██  Тарифы строятся автоматически из переменных выше  █████████████
# ====================================================================

def _build_tariffs() -> dict:
    """
    Автоматически строит словарь TARIFFS из настроек выше.
    Solo:   4 периода (solo_1m, solo_3m, solo_6m, solo_1y)
    Family: 4 периода (fam_1m,  fam_3m,  fam_6m,  fam_1y)
    """
    solo_base   = SOLO_PRICE_SALE   if DISCOUNT_ACTIVE else SOLO_PRICE_NORMAL
    family_base = FAMILY_PRICE_SALE if DISCOUNT_ACTIVE else FAMILY_PRICE_NORMAL

    period_meta = {
        "1m": {"label_suffix": "1 месяц",   "days": 30,  "key": "1m"},
        "3m": {"label_suffix": "3 месяца",  "days": 90,  "key": "3m"},
        "6m": {"label_suffix": "6 месяцев", "days": 180, "key": "6m"},
        "1y": {"label_suffix": "1 год",     "days": 365, "key": "1y"},
    }

    tariffs = {}
    for pk, pm in period_meta.items():
        mult = PERIOD_MULTIPLIERS[pk]

        solo_rub   = round(solo_base   * mult)
        family_rub = round(family_base * mult)

        solo_usdt   = round(solo_rub   / USDT_TO_RUB, 2)
        family_usdt = round(family_rub / USDT_TO_RUB, 2)

        solo_stars   = round(solo_rub   / STAR_TO_RUB)
        family_stars = round(family_rub / STAR_TO_RUB)

        # Подпись скидки в label
        sale_tag = f"  {DISCOUNT_LABEL}" if DISCOUNT_ACTIVE else ""

        tariffs[f"solo_{pk}"] = {
            "label":       f"👤 Соло — {pm['label_suffix']}{sale_tag}",
            "plan":        "solo",
            "days":        pm["days"],
            "price_rub":   solo_rub,
            "price_usdt":  solo_usdt,
            "price_stars": solo_stars,
            "description": "1 устройство",
        }
        tariffs[f"fam_{pk}"] = {
            "label":       f"👨‍👩‍👧 Семья/Друзья — {pm['label_suffix']}{sale_tag}",
            "plan":        "family",
            "days":        pm["days"],
            "price_rub":   family_rub,
            "price_usdt":  family_usdt,
            "price_stars": family_stars,
            "description": "до 3 устройств · 4 протокола · ⚡️ выше скорость",
        }

    return tariffs


TARIFFS = _build_tariffs()
# ↑ При смене DISCOUNT_ACTIVE / цен — перезапустите бота, тарифы пересчитаются сами.

# ====================================================================
# ██████████████████  КОНЕЦ КОНФИГУРАЦИИ  ████████████████████████████
# ====================================================================

import asyncio
import logging

import aiohttp
import aiosqlite
from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    LabeledPrice,
    Message,
    PreCheckoutQuery,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
)
log = logging.getLogger(__name__)

DB_PATH = "vpnbot.db"


# ══════════════════════════════════════════════════════════════════════
#  FSM — состояния диалогов
# ══════════════════════════════════════════════════════════════════════

class ManualTopupFSM(StatesGroup):
    waiting_amount      = State()  # пользователь вводит сумму
    waiting_requisites  = State()  # admin вводит реквизиты


class AdminFSM(StatesGroup):
    choose_tariff    = State()  # admin выбирает тариф для добавления ключей
    entering_keys    = State()  # admin вводит ключи построчно
    broadcast_target = State()  # admin вводит ID конкретного пользователя
    broadcast_msg    = State()  # admin вводит текст рассылки


# ══════════════════════════════════════════════════════════════════════
#  База данных
# ══════════════════════════════════════════════════════════════════════

async def db_init():
    """Создаёт все таблицы при первом запуске."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id     INTEGER PRIMARY KEY,
            username    TEXT    DEFAULT '',
            full_name   TEXT    DEFAULT '',
            balance     INTEGER DEFAULT 0,
            created_at  TEXT    DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS vpn_keys (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            tariff_id   TEXT    NOT NULL,
            key_value   TEXT    NOT NULL,
            is_used     INTEGER DEFAULT 0,
            used_by     INTEGER,
            used_at     TEXT,
            added_by    INTEGER,
            created_at  TEXT    DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS purchases (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            tariff_id   TEXT    NOT NULL,
            key_id      INTEGER,
            method      TEXT    NOT NULL,
            amount_rub  INTEGER NOT NULL,
            created_at  TEXT    DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS manual_topups (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            amount_rub  INTEGER NOT NULL,
            status      TEXT    DEFAULT 'pending',
            admin_id    INTEGER,
            requisites  TEXT,
            created_at  TEXT    DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS crypto_invoices (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            invoice_id  TEXT    NOT NULL UNIQUE,
            amount_usdt REAL    NOT NULL,
            amount_rub  INTEGER NOT NULL,
            status      TEXT    DEFAULT 'pending',
            created_at  TEXT    DEFAULT (datetime('now'))
        );
        """)
        await db.commit()


# ── Хелперы работы с пользователями ──────────────────────────────────

async def ensure_user(user_id: int, username: str, full_name: str) -> bool:
    """Создаёт пользователя если не существует. Возвращает True если новый."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT 1 FROM users WHERE user_id=?", (user_id,)) as cur:
            exists = await cur.fetchone()
        if not exists:
            await db.execute(
                "INSERT INTO users (user_id, username, full_name) VALUES (?,?,?)",
                (user_id, username or "", full_name or ""),
            )
            await db.commit()
            return True
        return False


async def get_user(user_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id=?", (user_id,)) as cur:
            row = await cur.fetchone()
        return dict(row) if row else None


async def add_balance(user_id: int, amount: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET balance = balance + ? WHERE user_id=?",
            (amount, user_id),
        )
        await db.commit()


async def deduct_balance(user_id: int, amount: int) -> bool:
    """Списывает сумму. Возвращает False если недостаточно средств."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT balance FROM users WHERE user_id=?", (user_id,)) as cur:
            row = await cur.fetchone()
        if not row or row[0] < amount:
            return False
        await db.execute(
            "UPDATE users SET balance = balance - ? WHERE user_id=?",
            (amount, user_id),
        )
        await db.commit()
        return True


async def all_user_ids() -> list[int]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT user_id FROM users") as cur:
            return [r[0] for r in await cur.fetchall()]


# ── Хелперы работы с ключами ──────────────────────────────────────────

async def get_free_key(tariff_id: str) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM vpn_keys WHERE tariff_id=? AND is_used=0 ORDER BY id LIMIT 1",
            (tariff_id,),
        ) as cur:
            row = await cur.fetchone()
        return dict(row) if row else None


async def mark_key_used(key_id: int, user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE vpn_keys SET is_used=1, used_by=?, used_at=datetime('now') WHERE id=?",
            (user_id, key_id),
        )
        await db.commit()


async def add_keys_to_db(tariff_id: str, keys: list[str], admin_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        for k in keys:
            k = k.strip()
            if k:
                await db.execute(
                    "INSERT INTO vpn_keys (tariff_id, key_value, added_by) VALUES (?,?,?)",
                    (tariff_id, k, admin_id),
                )
        await db.commit()


async def count_free_keys(tariff_id: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM vpn_keys WHERE tariff_id=? AND is_used=0",
            (tariff_id,),
        ) as cur:
            r = await cur.fetchone()
        return r[0] if r else 0


async def save_purchase(user_id: int, tariff_id: str, key_id: int, method: str, amount: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO purchases (user_id, tariff_id, key_id, method, amount_rub) VALUES (?,?,?,?,?)",
            (user_id, tariff_id, key_id, method, amount),
        )
        await db.commit()


async def get_user_purchases(user_id: int) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """SELECT p.created_at, p.tariff_id, p.amount_rub, p.method, k.key_value
               FROM purchases p
               LEFT JOIN vpn_keys k ON p.key_id = k.id
               WHERE p.user_id = ?
               ORDER BY p.created_at DESC
               LIMIT 15""",
            (user_id,),
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]


# ── Хелперы ручных пополнений ─────────────────────────────────────────

async def create_manual_topup(user_id: int, amount: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO manual_topups (user_id, amount_rub) VALUES (?,?)",
            (user_id, amount),
        )
        await db.commit()
        return cur.lastrowid


async def get_manual_topup(topup_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM manual_topups WHERE id=?", (topup_id,)) as cur:
            row = await cur.fetchone()
        return dict(row) if row else None


async def update_manual_topup(topup_id: int, **fields):
    set_clause = ", ".join(f"{k}=?" for k in fields)
    values = list(fields.values()) + [topup_id]
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE manual_topups SET {set_clause} WHERE id=?", values)
        await db.commit()


async def get_pending_topups() -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM manual_topups WHERE status IN ('pending','sent','paid') ORDER BY created_at DESC LIMIT 20"
        ) as cur:
            return [dict(r) for r in await cur.fetchall()]


# ── Хелперы CryptoBot ─────────────────────────────────────────────────

async def cryptobot_create_invoice(amount_usdt: float) -> dict | None:
    async with aiohttp.ClientSession() as session:
        try:
            resp = await session.post(
                f"{CRYPTOBOT_API_URL}/createInvoice",
                headers={"Crypto-Pay-API-Token": CRYPTOBOT_TOKEN},
                json={
                    "asset":       "USDT",
                    "amount":      str(amount_usdt),
                    "description": "Пополнение баланса VPN-бота",
                    "expires_in":  3600,
                },
                timeout=aiohttp.ClientTimeout(total=10),
            )
            data = await resp.json()
        except Exception as e:
            log.error(f"CryptoBot create error: {e}")
            return None

    if data.get("ok"):
        return data["result"]
    log.error(f"CryptoBot API error: {data}")
    return None


async def cryptobot_check_invoice(invoice_id: str) -> str:
    """Возвращает статус: 'paid', 'active', 'expired' и т.д."""
    async with aiohttp.ClientSession() as session:
        try:
            resp = await session.get(
                f"{CRYPTOBOT_API_URL}/getInvoices",
                headers={"Crypto-Pay-API-Token": CRYPTOBOT_TOKEN},
                params={"invoice_ids": invoice_id},
                timeout=aiohttp.ClientTimeout(total=10),
            )
            data = await resp.json()
        except Exception as e:
            log.error(f"CryptoBot check error: {e}")
            return "unknown"

    if data.get("ok") and data["result"]["items"]:
        return data["result"]["items"][0]["status"]
    return "unknown"


# ── Логирование в чат ─────────────────────────────────────────────────

async def log_event(bot: Bot, text: str):
    """Отправляет лог-сообщение в LOG_CHAT_ID."""
    try:
        await bot.send_message(
            LOG_CHAT_ID,
            f"📋 {text}",
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        log.error(f"Ошибка отправки лога: {e}")


# ══════════════════════════════════════════════════════════════════════
#  Клавиатуры
# ══════════════════════════════════════════════════════════════════════

def main_menu_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="🔑 Купить ключ")
    kb.button(text="💳 Пополнить баланс")
    kb.button(text="👤 Профиль")
    kb.button(text="📋 Мои ключи")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def buy_tariffs_kb() -> InlineKeyboardMarkup:
    """Кнопки тарифов для покупки — сгруппированы по планам."""
    rows: list[list[InlineKeyboardButton]] = []
    rows.append([InlineKeyboardButton(text="─── 👤 СОЛО (1 устройство) ───", callback_data="noop")])
    for tid, t in TARIFFS.items():
        if t["plan"] == "solo":
            rows.append([InlineKeyboardButton(
                text=f"{t['label']}  —  {t['price_rub']}₽",
                callback_data=f"buy:{tid}",
            )])
    rows.append([InlineKeyboardButton(text="─── 👨‍👩‍👧 СЕМЬЯ / ДРУЗЬЯ (до 3) ───", callback_data="noop")])
    for tid, t in TARIFFS.items():
        if t["plan"] == "family":
            rows.append([InlineKeyboardButton(
                text=f"{t['label']}  —  {t['price_rub']}₽",
                callback_data=f"buy:{tid}",
            )])
    rows.append([InlineKeyboardButton(text="🔙 Назад", callback_data="nav:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def topup_methods_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="💎 CryptoBot (USDT)",   callback_data="topup:crypto")
    b.button(text="⭐ Telegram Stars",      callback_data="topup:stars")
    b.button(text="🏦 СБП / Карта",        callback_data="topup:manual")
    b.button(text="🔙 Назад",              callback_data="nav:main")
    b.adjust(1)
    return b.as_markup()


def crypto_tariffs_kb() -> InlineKeyboardMarkup:
    """Суммы пополнения в USDT."""
    b = InlineKeyboardBuilder()
    for tid, t in TARIFFS.items():
        b.button(
            text=f"{t['label']}  —  {t['price_usdt']} USDT  (≈{int(t['price_usdt'] * USDT_TO_RUB)}₽)",
            callback_data=f"crypto:{tid}",
        )
    b.button(text="🔙 Назад", callback_data="nav:topup")
    b.adjust(1)
    return b.as_markup()


def stars_tariffs_kb() -> InlineKeyboardMarkup:
    """Суммы пополнения в Stars."""
    b = InlineKeyboardBuilder()
    for tid, t in TARIFFS.items():
        b.button(
            text=f"{t['label']}  —  {t['price_stars']} ⭐  (≈{t['price_stars'] * STAR_TO_RUB}₽)",
            callback_data=f"stars:{tid}",
        )
    b.button(text="🔙 Назад", callback_data="nav:topup")
    b.adjust(1)
    return b.as_markup()


def admin_main_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="➕ Добавить ключи",           callback_data="adm:add_keys")
    b.button(text="📊 Статистика",               callback_data="adm:stats")
    b.button(text="📢 Рассылка",                 callback_data="adm:broadcast")
    b.button(text="💰 Заявки на пополнение",     callback_data="adm:pending")
    b.adjust(1)
    return b.as_markup()


def back_to_admin_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="🔙 В панель", callback_data="adm:main")
    return b.as_markup()


# ══════════════════════════════════════════════════════════════════════
#  Роутер и хендлеры
# ══════════════════════════════════════════════════════════════════════

router = Router()


# ─── /start ───────────────────────────────────────────────────────────

@router.message(Command("start"))
async def cmd_start(msg: Message, bot: Bot):
    u = msg.from_user
    is_new = await ensure_user(u.id, u.username or "", u.full_name or "")
    if is_new:
        await log_event(
            bot,
            f"👤 Новый пользователь: <b>{u.full_name}</b> "
            f"(@{u.username}, ID: <code>{u.id}</code>)",
        )
    await msg.answer(
        "👋 <b>Добро пожаловать!</b>\n\n"
        "Здесь вы можете купить VPN-ключи для быстрого и безопасного интернета.\n\n"
        "Выберите действие в меню ниже:",
        reply_markup=main_menu_kb(),
    )


# ─── /cancel — выход из любого состояния ──────────────────────────────

@router.message(Command("cancel"))
async def cmd_cancel(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("❌ Действие отменено.", reply_markup=main_menu_kb())


# ─── /admin ───────────────────────────────────────────────────────────

@router.message(Command("admin"))
async def cmd_admin(msg: Message, state: FSMContext):
    if msg.from_user.id not in ADMIN_IDS:
        await msg.answer("⛔ Нет доступа.")
        return
    await state.clear()
    await msg.answer(
        "⚙️ <b>Панель администратора</b>",
        reply_markup=admin_main_kb(),
    )


# ══════════════════════════════════════════════════════════════════════
#  ПОЛЬЗОВАТЕЛЬСКИЕ ХЕНДЛЕРЫ — главное меню
# ══════════════════════════════════════════════════════════════════════

@router.message(F.text == "🔑 Купить ключ")
async def menu_buy(msg: Message):
    u = await get_user(msg.from_user.id)
    balance = u["balance"] if u else 0
    await msg.answer(
        f"💰 Ваш баланс: <b>{balance}₽</b>\n\nВыберите тариф:",
        reply_markup=buy_tariffs_kb(),
    )


@router.message(F.text == "💳 Пополнить баланс")
async def menu_topup(msg: Message):
    await msg.answer(
        "💳 <b>Выберите способ пополнения:</b>",
        reply_markup=topup_methods_kb(),
    )


@router.message(F.text == "👤 Профиль")
async def menu_profile(msg: Message):
    await ensure_user(msg.from_user.id, msg.from_user.username or "", msg.from_user.full_name or "")
    u = await get_user(msg.from_user.id)
    purchases = await get_user_purchases(msg.from_user.id)
    await msg.answer(
        f"👤 <b>Профиль</b>\n\n"
        f"🆔 ID: <code>{u['user_id']}</code>\n"
        f"💰 Баланс: <b>{u['balance']}₽</b>\n"
        f"🛒 Покупок: <b>{len(purchases)}</b>\n"
        f"📅 Зарегистрирован: {u['created_at'][:10]}",
    )


@router.message(F.text == "📋 Мои ключи")
async def menu_mykeys(msg: Message):
    purchases = await get_user_purchases(msg.from_user.id)
    if not purchases:
        await msg.answer("📋 У вас пока нет купленных ключей.")
        return
    lines = ["📋 <b>Ваши ключи (последние 15):</b>\n"]
    for p in purchases:
        t = TARIFFS.get(p["tariff_id"], {})
        lines.append(
            f"{'─' * 22}\n"
            f"📦 {t.get('label', p['tariff_id'])}\n"
            f"🔑 <code>{p['key_value'] or '—'}</code>\n"
            f"📅 {p['created_at'][:10]}  💳 {p['method']}"
        )
    await msg.answer("\n".join(lines))


# ══════════════════════════════════════════════════════════════════════
#  ПОКУПКА КЛЮЧА
# ══════════════════════════════════════════════════════════════════════

@router.callback_query(F.data == "noop")
async def cb_noop(cq: CallbackQuery):
    await cq.answer()


async def cb_buy_select(cq: CallbackQuery):
    tariff_id = cq.data.split(":", 1)[1]
    tariff = TARIFFS.get(tariff_id)
    if not tariff:
        await cq.answer("Тариф не найден.", show_alert=True)
        return

    u = await get_user(cq.from_user.id)
    balance = u["balance"] if u else 0
    price = tariff["price_rub"]

    if balance < price:
        b = InlineKeyboardBuilder()
        b.button(text="💳 Пополнить баланс", callback_data="nav:topup")
        b.button(text="🔙 Назад к тарифам",  callback_data="nav:buy")
        await cq.message.edit_text(
            f"❌ <b>Недостаточно средств</b>\n\n"
            f"Тариф: {tariff['label']}\n"
            f"Нужно: <b>{price}₽</b>\n"
            f"Ваш баланс: {balance}₽\n"
            f"Не хватает: <b>{price - balance}₽</b>",
            reply_markup=b.as_markup(),
        )
        await cq.answer()
        return

    # Проверяем наличие ключа заранее
    key = await get_free_key(tariff_id)
    if not key:
        b = InlineKeyboardBuilder()
        b.button(text="🔙 К тарифам", callback_data="nav:buy")
        await cq.message.edit_text(
            "😔 Ключи для этого тарифа временно закончились.\n"
            "Попробуйте позже или выберите другой тариф.",
            reply_markup=b.as_markup(),
        )
        await cq.answer()
        return

    b = InlineKeyboardBuilder()
    b.button(text=f"✅ Подтвердить покупку {price}₽", callback_data=f"confirm_buy:{tariff_id}")
    b.button(text="🔙 Назад", callback_data="nav:buy")
    b.adjust(1)
    desc = tariff.get("description", "")
    await cq.message.edit_text(
        f"🛒 <b>Подтверждение покупки</b>\n\n"
        f"Тариф: {tariff['label']}\n"
        f"ℹ️ {desc}\n"
        f"Срок: {tariff['days']} дн.\n"
        f"Цена: <b>{price}₽</b>\n\n"
        f"Ваш баланс: {balance}₽  →  <b>{balance - price}₽</b> после оплаты",
        reply_markup=b.as_markup(),
    )
    await cq.answer()


@router.callback_query(F.data.startswith("confirm_buy:"))
async def cb_confirm_buy(cq: CallbackQuery, bot: Bot):
    tariff_id = cq.data.split(":", 1)[1]
    tariff = TARIFFS.get(tariff_id)
    if not tariff:
        await cq.answer("Тариф не найден.", show_alert=True)
        return

    price = tariff["price_rub"]

    # Списываем деньги
    if not await deduct_balance(cq.from_user.id, price):
        await cq.answer("Недостаточно средств!", show_alert=True)
        return

    # Выдаём ключ
    key = await get_free_key(tariff_id)
    if not key:
        await add_balance(cq.from_user.id, price)  # возврат
        b = InlineKeyboardBuilder()
        b.button(text="🔙 К тарифам", callback_data="nav:buy")
        await cq.message.edit_text(
            "😔 Ключи для этого тарифа только что закончились. Баланс возвращён.",
            reply_markup=b.as_markup(),
        )
        await cq.answer()
        return

    await mark_key_used(key["id"], cq.from_user.id)
    await save_purchase(cq.from_user.id, tariff_id, key["id"], "balance", price)

    await cq.message.edit_text(
        f"✅ <b>Покупка успешна!</b>\n\n"
        f"Тариф: {tariff['label']}\n"
        f"Срок: {tariff['days']} дней\n\n"
        f"🔑 Ваш ключ:\n<code>{key['key_value']}</code>\n\n"
        f"Скопируйте ключ и вставьте в VPN-клиент.",
    )
    await log_event(
        bot,
        f"🛒 Покупка: <b>{cq.from_user.full_name}</b> (@{cq.from_user.username}, "
        f"ID: <code>{cq.from_user.id}</code>)\n"
        f"Тариф: {tariff['label']} — {price}₽",
    )
    await cq.answer()


# ══════════════════════════════════════════════════════════════════════
#  ПОПОЛНЕНИЕ — CRYPTOBOT (USDT)
# ══════════════════════════════════════════════════════════════════════

@router.callback_query(F.data == "topup:crypto")
async def cb_topup_crypto(cq: CallbackQuery):
    await cq.message.edit_text(
        "💎 <b>Пополнение через CryptoBot (USDT)</b>\n\n"
        "Выберите сумму. После оплаты нажмите «Проверить оплату»:",
        reply_markup=crypto_tariffs_kb(),
    )
    await cq.answer()


@router.callback_query(F.data.startswith("crypto:"))
async def cb_crypto_select(cq: CallbackQuery, bot: Bot):
    tariff_id = cq.data.split(":", 1)[1]
    tariff = TARIFFS.get(tariff_id)
    if not tariff:
        await cq.answer("Тариф не найден.", show_alert=True)
        return

    amount_usdt = tariff["price_usdt"]
    amount_rub  = int(amount_usdt * USDT_TO_RUB)

    invoice = await cryptobot_create_invoice(amount_usdt)
    if not invoice:
        await cq.answer(
            "Ошибка создания инвойса. Проверьте CRYPTOBOT_TOKEN или попробуйте позже.",
            show_alert=True,
        )
        return

    inv_id = str(invoice["invoice_id"])

    # Сохраняем в БД
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO crypto_invoices (user_id, invoice_id, amount_usdt, amount_rub) VALUES (?,?,?,?)",
            (cq.from_user.id, inv_id, amount_usdt, amount_rub),
        )
        await db.commit()

    b = InlineKeyboardBuilder()
    b.button(text="💳 Оплатить в CryptoBot", url=invoice["pay_url"])
    b.button(text="✅ Проверить оплату",      callback_data=f"check_crypto:{inv_id}")
    b.button(text="🔙 Назад",                callback_data="topup:crypto")
    b.adjust(1)

    await cq.message.edit_text(
        f"💎 <b>Оплата через CryptoBot</b>\n\n"
        f"Сумма: <b>{amount_usdt} USDT</b> (≈{amount_rub}₽)\n\n"
        f"1. Нажмите «Оплатить в CryptoBot»\n"
        f"2. Завершите оплату\n"
        f"3. Вернитесь и нажмите «Проверить оплату»",
        reply_markup=b.as_markup(),
    )
    await cq.answer()


@router.callback_query(F.data.startswith("check_crypto:"))
async def cb_check_crypto(cq: CallbackQuery, bot: Bot):
    inv_id = cq.data.split(":", 1)[1]

    status = await cryptobot_check_invoice(inv_id)
    if status != "paid":
        await cq.answer(
            f"Оплата не найдена (статус: {status}). Оплатите и повторите.",
            show_alert=True,
        )
        return

    # Защита от двойного зачисления
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM crypto_invoices WHERE invoice_id=? AND user_id=?",
            (inv_id, cq.from_user.id),
        ) as cur:
            inv = await cur.fetchone()

    if not inv:
        await cq.answer("Инвойс не найден.", show_alert=True)
        return

    inv = dict(inv)
    if inv["status"] == "credited":
        await cq.answer("Этот платёж уже зачтён ранее.", show_alert=True)
        return

    await add_balance(cq.from_user.id, inv["amount_rub"])

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE crypto_invoices SET status='credited' WHERE invoice_id=?",
            (inv_id,),
        )
        await db.commit()

    b = InlineKeyboardBuilder()
    b.button(text="🔑 Купить ключ", callback_data="nav:buy")
    await cq.message.edit_text(
        f"✅ <b>Баланс пополнен на {inv['amount_rub']}₽!</b>\n\n"
        f"Оплачено: {inv['amount_usdt']} USDT",
        reply_markup=b.as_markup(),
    )
    await log_event(
        bot,
        f"💎 CryptoBot пополнение: <b>{cq.from_user.full_name}</b> "
        f"(ID: <code>{cq.from_user.id}</code>) +{inv['amount_rub']}₽ "
        f"({inv['amount_usdt']} USDT)",
    )
    await cq.answer("✅ Баланс пополнен!")


# ══════════════════════════════════════════════════════════════════════
#  ПОПОЛНЕНИЕ — TELEGRAM STARS
# ══════════════════════════════════════════════════════════════════════

@router.callback_query(F.data == "topup:stars")
async def cb_topup_stars(cq: CallbackQuery):
    await cq.message.edit_text(
        "⭐ <b>Пополнение через Telegram Stars</b>\n\nВыберите сумму:",
        reply_markup=stars_tariffs_kb(),
    )
    await cq.answer()


@router.callback_query(F.data.startswith("stars:"))
async def cb_stars_select(cq: CallbackQuery, bot: Bot):
    tariff_id = cq.data.split(":", 1)[1]
    tariff = TARIFFS.get(tariff_id)
    if not tariff:
        await cq.answer("Тариф не найден.", show_alert=True)
        return

    stars = tariff["price_stars"]
    rub   = stars * STAR_TO_RUB

    # Stars: currency=XTR, amount в единицах (1 = 1 Star)
    await bot.send_invoice(
        chat_id=cq.from_user.id,
        title=f"Пополнение баланса — {tariff['label']}",
        description=f"Пополнение баланса VPN-бота на {rub}₽",
        payload=f"stars:{tariff_id}:{cq.from_user.id}",
        currency="XTR",
        prices=[LabeledPrice(label="Пополнение баланса", amount=stars)],
    )
    await cq.answer()


@router.pre_checkout_query()
async def pre_checkout_handler(pcq: PreCheckoutQuery):
    """Обязательный хендлер для платежей Stars — просто подтверждаем."""
    await pcq.answer(ok=True)


@router.message(F.successful_payment)
async def stars_payment_success(msg: Message, bot: Bot):
    payload = msg.successful_payment.invoice_payload
    if not payload.startswith("stars:"):
        return

    _, tariff_id, uid_str = payload.split(":", 2)
    tariff = TARIFFS.get(tariff_id)
    if not tariff:
        return

    stars = tariff["price_stars"]
    rub   = stars * STAR_TO_RUB
    uid   = int(uid_str)

    await add_balance(uid, rub)
    await msg.answer(
        f"⭐ Оплачено {stars} Stars!\n✅ Баланс пополнен на <b>{rub}₽</b>",
        reply_markup=main_menu_kb(),
    )
    await log_event(
        bot,
        f"⭐ Stars пополнение: <b>{msg.from_user.full_name}</b> "
        f"(ID: <code>{uid}</code>) +{rub}₽ ({stars} Stars)",
    )


# ══════════════════════════════════════════════════════════════════════
#  ПОПОЛНЕНИЕ — РУЧНАЯ ОПЛАТА (СБП / КАРТА)
# ══════════════════════════════════════════════════════════════════════

@router.callback_query(F.data == "topup:manual")
async def cb_topup_manual(cq: CallbackQuery, state: FSMContext):
    b = InlineKeyboardBuilder()
    b.button(text="🔙 Отмена", callback_data="nav:topup")
    await cq.message.edit_text(
        f"🏦 <b>Пополнение через СБП / Карту</b>\n\n"
        f"Введите желаемую сумму пополнения в рублях\n"
        f"(минимум {MIN_MANUAL_TOPUP}₽):",
        reply_markup=b.as_markup(),
    )
    await state.set_state(ManualTopupFSM.waiting_amount)
    await cq.answer()


@router.message(ManualTopupFSM.waiting_amount, F.text)
async def manual_amount_input(msg: Message, state: FSMContext, bot: Bot):
    text = msg.text.strip()
    if not text.isdigit():
        await msg.answer("Пожалуйста, введите число без знаков и пробелов. Попробуйте ещё раз:")
        return
    amount = int(text)
    if amount < MIN_MANUAL_TOPUP:
        await msg.answer(f"Минимальная сумма — {MIN_MANUAL_TOPUP}₽. Введите другую сумму:")
        return

    await state.clear()

    topup_id = await create_manual_topup(msg.from_user.id, amount)

    await msg.answer(
        f"⏳ Ваша заявка на пополнение <b>{amount}₽</b> принята!\n\n"
        f"Получение реквизитов займёт <b>1–10 минут</b>.\n"
        f"Ожидайте — бот пришлёт карту или ссылку для оплаты.",
        reply_markup=main_menu_kb(),
    )

    # Уведомляем ВСЕХ администраторов
    for admin_id in ADMIN_IDS:
        b = InlineKeyboardBuilder()
        b.button(text="💳 Отправить реквизиты", callback_data=f"adm_req:{topup_id}")
        b.button(text="❌ Отклонить заявку",    callback_data=f"adm_reject:{topup_id}")
        b.adjust(1)
        try:
            await bot.send_message(
                admin_id,
                f"💰 <b>Новая заявка на пополнение</b>\n\n"
                f"👤 {msg.from_user.full_name} (@{msg.from_user.username})\n"
                f"🆔 ID: <code>{msg.from_user.id}</code>\n"
                f"💵 Сумма: <b>{amount}₽</b>\n"
                f"🔖 Заявка: #{topup_id}",
                reply_markup=b.as_markup(),
            )
        except Exception as e:
            log.warning(f"Не удалось уведомить admin {admin_id}: {e}")

    await log_event(
        bot,
        f"💰 Новая заявка #{topup_id}: <b>{msg.from_user.full_name}</b> "
        f"(ID: <code>{msg.from_user.id}</code>) — {amount}₽",
    )


# ── Администратор: отправить реквизиты ────────────────────────────────

@router.callback_query(F.data.startswith("adm_req:"))
async def adm_send_req_start(cq: CallbackQuery, state: FSMContext):
    if cq.from_user.id not in ADMIN_IDS:
        await cq.answer("⛔ Нет доступа.", show_alert=True)
        return

    topup_id = int(cq.data.split(":", 1)[1])
    topup = await get_manual_topup(topup_id)
    if not topup:
        await cq.answer("Заявка не найдена.", show_alert=True)
        return
    if topup["status"] not in ("pending", "sent"):
        await cq.answer("Заявка уже обработана.", show_alert=True)
        return

    await state.update_data(topup_id=topup_id)
    await state.set_state(ManualTopupFSM.waiting_requisites)
    await cq.message.answer(
        f"💳 Заявка #{topup_id} — {topup['amount_rub']}₽\n\n"
        f"Введите реквизиты (номер карты, номер телефона, или ссылку):\n\n"
        f"Отправьте /cancel чтобы отменить.",
    )
    await cq.answer()


@router.message(ManualTopupFSM.waiting_requisites, F.text)
async def adm_requisites_input(msg: Message, state: FSMContext, bot: Bot):
    if msg.from_user.id not in ADMIN_IDS:
        return

    data = await state.get_data()
    topup_id = data.get("topup_id")
    requisites = msg.text.strip()
    await state.clear()

    topup = await get_manual_topup(topup_id)
    if not topup:
        await msg.answer("Заявка не найдена.")
        return

    await update_manual_topup(topup_id, status="sent", admin_id=msg.from_user.id, requisites=requisites)

    # Отправляем реквизиты пользователю
    b = InlineKeyboardBuilder()
    b.button(text="✅ Я оплатил", callback_data=f"user_paid:{topup_id}")
    try:
        await bot.send_message(
            topup["user_id"],
            f"💳 <b>Реквизиты для оплаты {topup['amount_rub']}₽:</b>\n\n"
            f"<code>{requisites}</code>\n\n"
            f"После перевода нажмите кнопку ниже:",
            reply_markup=b.as_markup(),
        )
        await msg.answer(f"✅ Реквизиты для заявки #{topup_id} отправлены пользователю.")
    except Exception as e:
        await msg.answer(f"❌ Не удалось отправить реквизиты: {e}")

    await log_event(
        bot,
        f"💳 Реквизиты отправлены по заявке #{topup_id} "
        f"(admin: {msg.from_user.id}, user: {topup['user_id']})",
    )


# ── Пользователь: «Я оплатил» ─────────────────────────────────────────

@router.callback_query(F.data.startswith("user_paid:"))
async def user_paid_callback(cq: CallbackQuery, bot: Bot):
    topup_id = int(cq.data.split(":", 1)[1])
    topup = await get_manual_topup(topup_id)

    if not topup or topup["user_id"] != cq.from_user.id:
        await cq.answer("Заявка не найдена.", show_alert=True)
        return
    if topup["status"] not in ("sent", "pending"):
        await cq.answer("Эта заявка уже обработана.", show_alert=True)
        return

    await update_manual_topup(topup_id, status="paid")
    await cq.message.edit_text(
        "⏳ Ваш платёж передан на проверку администратору.\n"
        "Обычно подтверждение занимает несколько минут."
    )

    # Уведомляем ВСЕХ администраторов
    for admin_id in ADMIN_IDS:
        b = InlineKeyboardBuilder()
        b.button(text="✅ Подтвердить оплату", callback_data=f"adm_confirm:{topup_id}")
        b.button(text="❌ Отклонить",          callback_data=f"adm_reject:{topup_id}")
        b.adjust(2)
        try:
            await bot.send_message(
                admin_id,
                f"⚠️ <b>Требуется подтверждение оплаты</b>\n\n"
                f"🔖 Заявка: #{topup_id}\n"
                f"👤 ID пользователя: <code>{cq.from_user.id}</code>\n"
                f"💵 Сумма: <b>{topup['amount_rub']}₽</b>\n"
                f"💳 Реквизиты: <code>{topup['requisites']}</code>",
                reply_markup=b.as_markup(),
            )
        except Exception as e:
            log.warning(f"Не удалось уведомить admin {admin_id}: {e}")

    await log_event(
        bot,
        f"💸 Пользователь <code>{cq.from_user.id}</code> нажал «Я оплатил» "
        f"по заявке #{topup_id} ({topup['amount_rub']}₽)",
    )
    await cq.answer("Ожидайте подтверждения администратора.")


# ── Администратор: подтвердить оплату ────────────────────────────────

@router.callback_query(F.data.startswith("adm_confirm:"))
async def adm_confirm_payment(cq: CallbackQuery, bot: Bot):
    if cq.from_user.id not in ADMIN_IDS:
        await cq.answer("⛔ Нет доступа.", show_alert=True)
        return

    topup_id = int(cq.data.split(":", 1)[1])
    topup = await get_manual_topup(topup_id)
    if not topup:
        await cq.answer("Заявка не найдена.", show_alert=True)
        return
    if topup["status"] == "confirmed":
        await cq.answer("Эта заявка уже подтверждена.", show_alert=True)
        return

    await update_manual_topup(topup_id, status="confirmed", admin_id=cq.from_user.id)
    await add_balance(topup["user_id"], topup["amount_rub"])

    try:
        await bot.send_message(
            topup["user_id"],
            f"✅ <b>Баланс пополнен на {topup['amount_rub']}₽!</b>\n\n"
            f"Теперь вы можете купить VPN-ключ.",
            reply_markup=main_menu_kb(),
        )
    except Exception as e:
        log.warning(f"Не удалось уведомить пользователя {topup['user_id']}: {e}")

    await cq.message.edit_text(
        f"✅ Заявка #{topup_id} подтверждена. Пользователю зачислено {topup['amount_rub']}₽."
    )
    await log_event(
        bot,
        f"✅ Заявка #{topup_id} подтверждена admin <code>{cq.from_user.id}</code> "
        f"→ user <code>{topup['user_id']}</code> +{topup['amount_rub']}₽",
    )
    await cq.answer("Подтверждено!")


# ── Администратор: отклонить заявку ──────────────────────────────────

@router.callback_query(F.data.startswith("adm_reject:"))
async def adm_reject_topup(cq: CallbackQuery, bot: Bot):
    if cq.from_user.id not in ADMIN_IDS:
        await cq.answer("⛔ Нет доступа.", show_alert=True)
        return

    topup_id = int(cq.data.split(":", 1)[1])
    topup = await get_manual_topup(topup_id)
    if not topup:
        await cq.answer("Заявка не найдена.", show_alert=True)
        return
    if topup["status"] in ("confirmed", "rejected"):
        await cq.answer("Заявка уже закрыта.", show_alert=True)
        return

    await update_manual_topup(topup_id, status="rejected", admin_id=cq.from_user.id)
    try:
        await bot.send_message(
            topup["user_id"],
            f"❌ Заявка #{topup_id} на пополнение {topup['amount_rub']}₽ отклонена.\n"
            f"Если это ошибка — обратитесь к администратору.",
        )
    except Exception:
        pass

    await cq.message.edit_text(f"❌ Заявка #{topup_id} отклонена.")
    await log_event(
        bot,
        f"❌ Заявка #{topup_id} отклонена admin <code>{cq.from_user.id}</code>",
    )
    await cq.answer("Отклонено.")


# ══════════════════════════════════════════════════════════════════════
#  НАВИГАЦИЯ (служебные callback'и)
# ══════════════════════════════════════════════════════════════════════

@router.callback_query(F.data == "nav:main")
async def nav_main(cq: CallbackQuery):
    await cq.message.delete()
    await cq.answer()


@router.callback_query(F.data == "nav:buy")
async def nav_buy(cq: CallbackQuery):
    u = await get_user(cq.from_user.id)
    balance = u["balance"] if u else 0
    await cq.message.edit_text(
        f"💰 Ваш баланс: <b>{balance}₽</b>\n\nВыберите тариф:",
        reply_markup=buy_tariffs_kb(),
    )
    await cq.answer()


@router.callback_query(F.data == "nav:topup")
async def nav_topup(cq: CallbackQuery, state: FSMContext):
    await state.clear()
    await cq.message.edit_text(
        "💳 <b>Выберите способ пополнения:</b>",
        reply_markup=topup_methods_kb(),
    )
    await cq.answer()


# ══════════════════════════════════════════════════════════════════════
#  ПАНЕЛЬ АДМИНИСТРАТОРА
# ══════════════════════════════════════════════════════════════════════

@router.callback_query(F.data == "adm:main")
async def adm_main_panel(cq: CallbackQuery, state: FSMContext):
    if cq.from_user.id not in ADMIN_IDS:
        return
    await state.clear()
    await cq.message.edit_text(
        "⚙️ <b>Панель администратора</b>",
        reply_markup=admin_main_kb(),
    )
    await cq.answer()


# ── Добавление ключей ─────────────────────────────────────────────────

@router.callback_query(F.data == "adm:add_keys")
async def adm_add_keys(cq: CallbackQuery, state: FSMContext):
    if cq.from_user.id not in ADMIN_IDS:
        return

    b = InlineKeyboardBuilder()
    for tid, t in TARIFFS.items():
        cnt = await count_free_keys(tid)
        b.button(
            text=f"{t['label']}  [{cnt} шт. свободно]",
            callback_data=f"adm_pick_tariff:{tid}",
        )
    b.button(text="🔙 Назад", callback_data="adm:main")
    b.adjust(1)

    await cq.message.edit_text(
        "➕ <b>Добавление ключей</b>\n\nВыберите тариф:",
        reply_markup=b.as_markup(),
    )
    await state.set_state(AdminFSM.choose_tariff)
    await cq.answer()


@router.callback_query(AdminFSM.choose_tariff, F.data.startswith("adm_pick_tariff:"))
async def adm_tariff_picked(cq: CallbackQuery, state: FSMContext):
    tariff_id = cq.data.split(":", 1)[1]
    tariff = TARIFFS.get(tariff_id)
    if not tariff:
        await cq.answer("Тариф не найден.", show_alert=True)
        return

    await state.update_data(tariff_id=tariff_id)
    await state.set_state(AdminFSM.entering_keys)
    await cq.message.edit_text(
        f"📝 Тариф: <b>{tariff['label']}</b>\n\n"
        f"Отправьте ключи — <b>каждый ключ с новой строки</b>:\n\n"
        f"Пример:\n"
        f"<code>vless://abc123...@server:port\n"
        f"vless://def456...@server:port</code>\n\n"
        f"Или /cancel для отмены.",
    )
    await cq.answer()


@router.message(AdminFSM.entering_keys, F.text)
async def adm_keys_received(msg: Message, state: FSMContext, bot: Bot):
    if msg.from_user.id not in ADMIN_IDS:
        return

    data = await state.get_data()
    tariff_id = data.get("tariff_id")
    await state.clear()

    keys = [line.strip() for line in msg.text.split("\n") if line.strip()]
    if not keys:
        await msg.answer("Ключи не найдены. Попробуйте снова.")
        return

    await add_keys_to_db(tariff_id, keys, msg.from_user.id)
    tariff = TARIFFS[tariff_id]
    total_free = await count_free_keys(tariff_id)

    await msg.answer(
        f"✅ <b>Добавлено {len(keys)} ключей</b> для тарифа «{tariff['label']}»\n"
        f"Всего свободных: {total_free} шт.",
        reply_markup=admin_main_kb(),
    )
    await log_event(
        bot,
        f"➕ Admin <code>{msg.from_user.id}</code> добавил {len(keys)} ключей "
        f"для тарифа {tariff['label']}",
    )


# ── Статистика ────────────────────────────────────────────────────────

@router.callback_query(F.data == "adm:stats")
async def adm_stats(cq: CallbackQuery):
    if cq.from_user.id not in ADMIN_IDS:
        return

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        async with db.execute("SELECT COUNT(*) as c FROM users") as cur:
            users_count = (await cur.fetchone())["c"]

        async with db.execute("SELECT COUNT(*) as c FROM purchases") as cur:
            sales_count = (await cur.fetchone())["c"]

        async with db.execute("SELECT SUM(amount_rub) as s FROM purchases") as cur:
            revenue = (await cur.fetchone())["s"] or 0

        async with db.execute(
            "SELECT COUNT(*) as c FROM manual_topups WHERE status IN ('pending','sent','paid')"
        ) as cur:
            pending_count = (await cur.fetchone())["c"]

    keys_lines = []
    for tid, t in TARIFFS.items():
        cnt = await count_free_keys(tid)
        emoji = "✅" if cnt > 3 else ("⚠️" if cnt > 0 else "❌")
        keys_lines.append(f"  {emoji} {t['label']}: {cnt} шт.")

    await cq.message.edit_text(
        f"📊 <b>Статистика</b>\n\n"
        f"👤 Пользователей: <b>{users_count}</b>\n"
        f"🛒 Продаж: <b>{sales_count}</b>\n"
        f"💰 Выручка: <b>{revenue}₽</b>\n"
        f"⏳ Ожидают решения: <b>{pending_count}</b>\n\n"
        f"🔑 Свободных ключей:\n" + "\n".join(keys_lines),
        reply_markup=back_to_admin_kb(),
    )
    await cq.answer()


# ── Список заявок ─────────────────────────────────────────────────────

@router.callback_query(F.data == "adm:pending")
async def adm_pending_list(cq: CallbackQuery):
    if cq.from_user.id not in ADMIN_IDS:
        return

    topups = await get_pending_topups()
    if not topups:
        await cq.message.edit_text(
            "✅ Нет активных заявок на пополнение.",
            reply_markup=back_to_admin_kb(),
        )
        await cq.answer()
        return

    status_map = {
        "pending": "⏳ Ожидает реквизитов",
        "sent":    "📤 Реквизиты отправлены",
        "paid":    "💸 Ждёт подтверждения",
    }

    b = InlineKeyboardBuilder()
    lines = ["💰 <b>Активные заявки:</b>\n"]
    for t in topups:
        st = status_map.get(t["status"], t["status"])
        lines.append(f"#{t['id']}  {t['amount_rub']}₽  user:{t['user_id']}  {st}")
        if t["status"] == "pending":
            b.button(text=f"#{t['id']}: Реквизиты →", callback_data=f"adm_req:{t['id']}")
        elif t["status"] == "paid":
            b.button(text=f"#{t['id']}: ✅ Подтвердить", callback_data=f"adm_confirm:{t['id']}")
    b.button(text="🔙 Назад", callback_data="adm:main")
    b.adjust(1)

    await cq.message.edit_text(
        "\n".join(lines),
        reply_markup=b.as_markup(),
    )
    await cq.answer()


# ── Рассылка ──────────────────────────────────────────────────────────

@router.callback_query(F.data == "adm:broadcast")
async def adm_broadcast(cq: CallbackQuery, state: FSMContext):
    if cq.from_user.id not in ADMIN_IDS:
        return

    b = InlineKeyboardBuilder()
    b.button(text="📢 Всем пользователям",         callback_data="bc:all")
    b.button(text="👤 Конкретному пользователю",   callback_data="bc:one")
    b.button(text="🔙 Назад",                      callback_data="adm:main")
    b.adjust(1)
    await cq.message.edit_text(
        "📢 <b>Рассылка</b>\n\nВыберите получателей:",
        reply_markup=b.as_markup(),
    )
    await cq.answer()


@router.callback_query(F.data == "bc:all")
async def bc_all(cq: CallbackQuery, state: FSMContext):
    if cq.from_user.id not in ADMIN_IDS:
        return
    await state.update_data(bc_target="all")
    await state.set_state(AdminFSM.broadcast_msg)
    await cq.message.edit_text(
        "📝 Введите текст рассылки для всех пользователей.\n"
        "Можно использовать HTML-теги: <b>жирный</b>, <i>курсив</i>, <code>код</code>\n\n"
        "/cancel — отменить"
    )
    await cq.answer()


@router.callback_query(F.data == "bc:one")
async def bc_one(cq: CallbackQuery, state: FSMContext):
    if cq.from_user.id not in ADMIN_IDS:
        return
    await state.set_state(AdminFSM.broadcast_target)
    await cq.message.edit_text(
        "🆔 Введите Telegram ID пользователя:\n\n/cancel — отменить"
    )
    await cq.answer()


@router.message(AdminFSM.broadcast_target, F.text)
async def bc_target_input(msg: Message, state: FSMContext):
    if msg.from_user.id not in ADMIN_IDS:
        return
    uid = msg.text.strip().lstrip("-")
    if not uid.isdigit():
        await msg.answer("Введите числовой Telegram ID. Попробуйте снова:")
        return
    await state.update_data(bc_target=msg.text.strip())
    await state.set_state(AdminFSM.broadcast_msg)
    await msg.answer(
        f"📝 Введите текст сообщения для пользователя {msg.text.strip()}:\n\n/cancel — отменить"
    )


@router.message(AdminFSM.broadcast_msg, F.text)
async def bc_send(msg: Message, state: FSMContext, bot: Bot):
    if msg.from_user.id not in ADMIN_IDS:
        return

    data = await state.get_data()
    target = data.get("bc_target", "all")
    text   = msg.text
    await state.clear()

    if target == "all":
        user_ids = await all_user_ids()
        ok_count = 0
        for uid in user_ids:
            try:
                await bot.send_message(uid, text)
                ok_count += 1
                await asyncio.sleep(0.05)  # защита от flood
            except TelegramBadRequest:
                pass
            except Exception as e:
                log.warning(f"Рассылка: не удалось отправить {uid}: {e}")
        await msg.answer(
            f"✅ Рассылка завершена.\n"
            f"Доставлено: {ok_count} из {len(user_ids)}.",
            reply_markup=admin_main_kb(),
        )
        await log_event(
            bot,
            f"📢 Рассылка всем: {ok_count}/{len(user_ids)} доставлено "
            f"(admin: <code>{msg.from_user.id}</code>)",
        )
    else:
        try:
            await bot.send_message(int(target), text)
            await msg.answer(f"✅ Сообщение отправлено пользователю {target}.", reply_markup=admin_main_kb())
        except Exception as e:
            await msg.answer(f"❌ Ошибка: {e}")


# ══════════════════════════════════════════════════════════════════════
#  ЗАПУСК
# ══════════════════════════════════════════════════════════════════════

async def main():
    await db_init()

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    log.info("✅ Бот запущен. Нажмите Ctrl+C для остановки.")
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
