
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.database.db import save_user
from config import CHANNEL_URL

router = Router()

def get_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Subscribe to channel", url=CHANNEL_URL)],
        [
            InlineKeyboardButton(text="Generate ideas", callback_data="btn_ideas"),
            InlineKeyboardButton(text="Optimize text", callback_data="btn_optimize")
        ],
        [
            InlineKeyboardButton(text="Analyze post", callback_data="btn_analyze"),
            InlineKeyboardButton(text="My stats", callback_data="btn_stats")
        ]
    ])

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    save_user(message.from_user.id, message.from_user.username)
    
    welcome_text = (
        f"Hello, {message.from_user.first_name}!\n\n"
        f"I'm SocialPilotBot - your AI assistant for social media content.\n\n"
        f"What I can do:\n"
        f"✓ Generate post ideas\n"
        f"✓ Optimize text for any platform\n"
        f"✓ Analyze competitor posts\n\n"
        f"Commands:\n"
        f"/idea <topic> - Generate post ideas\n"
        f"/optimize <platform> <text> - Optimize for platform\n"
        f"/analyze <text> - Analyze competitor post\n\n"
        f"Subscribe to our channel for SMM tips!"
    )
    
    await message.answer(
        welcome_text,
        reply_markup=get_main_keyboard()
    )

@router.callback_query(F.data == "btn_ideas")
async def callback_ideas(callback: types.CallbackQuery):
    text = (
        "Send me a topic and I'll generate 5 post ideas!\n\n"
        "Example: /idea fitness for moms\n"
        "Example: /idea startup tips"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Back", callback_data="btn_back")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data == "btn_optimize")
async def callback_optimize(callback: types.CallbackQuery):
    text = (
        "Send your post text and choose platform:\n\n"
        "Example: /optimize telegram Here is my text\n\n"
        "Platforms: telegram, instagram, tiktok, vk, youtube"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Back", callback_data="btn_back")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data == "btn_analyze")
async def callback_analyze(callback: types.CallbackQuery):
    text = (
        "Send post content or description:\n\n"
        "/analyze [post text or description]\n\n"
        "I'll analyze tone, audience, strengths and generate similar ideas."
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Back", callback_data="btn_back")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data == "btn_stats")
async def callback_stats(callback: types.CallbackQuery):
    text = (
        "Your Statistics:\n\n"
        "Free plan: 10 requests/day\n"
        "Requests today: 0/10\n\n"
        "Upgrade to Premium for unlimited requests!\n"
        "Price: 300 RUB/month"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Back", callback_data="btn_back")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data == "btn_back")
async def callback_back(callback: types.CallbackQuery):
    text = (
        f"I'm SocialPilotBot - your AI assistant for social media content.\n\n"
        f"What I can do:\n"
        f"✓ Generate post ideas\n"
        f"✓ Optimize text for any platform\n"
        f"✓ Analyze competitor posts"
    )
    
    await callback.message.edit_text(text, reply_markup=get_main_keyboard())
    await callback.answer()
