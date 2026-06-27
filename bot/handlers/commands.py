from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.services.ai_service import ai_service
from bot.database.db import (
    save_user, increment_request_count, get_user_requests_today,
    save_request
)
from config import FREE_REQUESTS_PER_DAY

router = Router()

async def check_limit(user_id: int) -> bool:
    requests_today = get_user_requests_today(user_id)
    return requests_today < FREE_REQUESTS_PER_DAY

async def get_limit_message(user_id: int) -> str:
    requests_today = get_user_requests_today(user_id)
    remaining = FREE_REQUESTS_PER_DAY - requests_today
    return f"Requests today: {requests_today}/{FREE_REQUESTS_PER_DAY}\nRemaining: {remaining}"

@router.message(Command("idea"))
async def cmd_idea(message: types.Message):
    save_user(message.from_user.id, message.from_user.username)
    
    if not await check_limit(message.from_user.id):
        await message.answer("You've reached daily limit. Upgrade to Premium for unlimited!")
        return
    
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Usage: /idea <topic>\nExample: /idea fitness for moms")
        return
    
    topic = args[1]
    status_msg = await message.answer("Generating ideas...")
    
    try:
        ideas = await ai_service.generate_ideas(topic)
        increment_request_count(message.from_user.id)
        save_request(message.from_user.id, "idea", topic, ideas)
        
        await status_msg.delete()
        
        text = f"Ideas for topic: '{topic}'\n\n{ideas}"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Generate more", callback_data="more_ideas")]
        ])
        
        await message.answer(text, reply_markup=keyboard)
        limit_text = await get_limit_message(message.from_user.id)
        await message.answer(limit_text)
        
    except Exception as e:
        await status_msg.edit_text(f"Error: {str(e)}")

@router.message(Command("optimize"))
async def cmd_optimize(message: types.Message):
    save_user(message.from_user.id, message.from_user.username)
    
    if not await check_limit(message.from_user.id):
        await message.answer("You've reached daily limit. Upgrade to Premium for unlimited!")
        return
    
    args = message.text.split(maxsplit=2)
    
    if len(args) < 3:
        text = (
            "Usage: /optimize <platform> <text>\n\n"
            "Platforms:\n"
            "• telegram - Long, informative\n"
            "• instagram - Engaging, with hashtags\n"
            "• tiktok - Short, catchy, trendy\n"
            "• vk - Personality-driven\n"
            "• youtube - Compelling descriptions\n\n"
            "Example: /optimize instagram Check out my new video!"
        )
        await message.answer(text)
        return
    
    platform = args[1].lower()
    text = args[2]
    
    if platform not in ["telegram", "instagram", "tiktok", "vk", "youtube"]:
        await message.answer("Unknown platform. Use: telegram, instagram, tiktok, vk, youtube")
        return
    
    status_msg = await message.answer("Optimizing text...")
    
    try:
        optimized = await ai_service.optimize_text(text, platform)
        increment_request_count(message.from_user.id)
        save_request(message.from_user.id, "optimize", f"{platform}: {text}", optimized)
        
        await status_msg.delete()
        
        result_text = f"Optimized for {platform.upper()}:\n\n{optimized}"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Optimize again", callback_data="optimize_again")]
        ])
        
        await message.answer(result_text, reply_markup=keyboard)
        limit_text = await get_limit_message(message.from_user.id)
        await message.answer(limit_text)
        
    except Exception as e:
        await status_msg.edit_text(f"Error: {str(e)}")

@router.message(Command("analyze"))
async def cmd_analyze(message: types.Message):
    save_user(message.from_user.id, message.from_user.username)
    
    if not await check_limit(message.from_user.id):
        await message.answer("You've reached daily limit. Upgrade to Premium for unlimited!")
        return
    
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Usage: /analyze <post content>\nExample: /analyze Check out my new workout routine!")
        return
    
    content = args[1]
    status_msg = await message.answer("Analyzing post...")
    
    try:
        analysis = await ai_service.analyze_post(content)
        increment_request_count(message.from_user.id)
        save_request(message.from_user.id, "analyze", content, analysis)
        
        await status_msg.delete()
        
        result_text = f"Post Analysis:\n\n{analysis}"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Analyze another", callback_data="analyze_again")]
        ])
        
        await message.answer(result_text, reply_markup=keyboard)
        limit_text = await get_limit_message(message.from_user.id)
        await message.answer(limit_text)
        
    except Exception as e:
        await status_msg.edit_text(f"Error: {str(e)}")

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    text = (
        "SocialPilotBot - Your SMM Assistant\n\n"
        "Commands:\n"
        "/start - Main menu\n"
        "/idea <topic> - Generate post ideas\n"
        "/optimize <platform> <text> - Optimize text\n"
        "/analyze <content> - Analyze competitor post\n"
        "/help - This message\n\n"
        "Free: 10 requests/day\n"
        "Premium: Unlimited requests"
    )
    
    await message.answer(text)
