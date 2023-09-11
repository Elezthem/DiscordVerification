import discord
from discord.ext import commands
import random
import asyncio

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# Словарь для хранения капчей для каждого пользователя
captchas = {}
# Словарь для хранения таймеров ожидания верификации
verification_timers = {}

@client.event
async def on_ready():
  guilds = len(client.guilds)
  info = "!"
  print(f"{client.user.name} запущен(а))".format(info)) #в командную строку идёт инфа о запуске
  while True:
    await client.change_presence(status = discord.Status.dnd, activity = discord.Activity(name = f'verification', type = discord.ActivityType.playing)) #Идёт инфа о команде помощи (префикс изменить)
    await asyncio.sleep(15)
    await client.change_presence(status = discord.Status.dnd, activity = discord.Activity(name = f'behind {len(client.guilds)} servers', type = discord.ActivityType.watching)) #Инфа о количестве серверов, на котором находится бот.
    await asyncio.sleep(15)
    members = 0
    for guild in client.guilds:
      for member in guild.members:
        members += 1
    await client.change_presence(status = discord.Status.idle, activity = discord.Activity(name = f'behind {members} members', type = discord.ActivityType.watching)) #Общее количество участников, за которыми следит бот (Находятся на серверах)
    await asyncio.sleep(15)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!captcha'):
        user_id = message.author.id
        if user_id not in captchas:
            # Генерируем новую капчу для пользователя
            captcha_code = ''.join(random.sample('0123456789', 6))
            captchas[user_id] = {
                'code': captcha_code,
                'attempts': 0
            }
            await message.author.send(f'Captcha code: {captcha_code}')
            await message.author.send('Enter the captcha code.')

            # Запускаем таймер ожидания верификации в течение 5 минут
            verification_timers[user_id] = asyncio.create_task(wait_for_verification(user_id))
        else:
            captcha_data = captchas[user_id]
            if captcha_data['attempts'] < 5:
                # Если попытки не исчерпаны, генерируем новую капчу
                captcha_code = ''.join(random.sample('0123456789', 6))
                captcha_data['code'] = captcha_code
                captcha_data['attempts'] += 1
                await message.author.send(f'Incorrect code. Enter new captcha code: {captcha_code}')
            else:
                await message.author.kick(reason='`5` incorrect verification attempts')

    elif message.content.isdigit():
        user_id = message.author.id
        if user_id in captchas:
            captcha_data = captchas[user_id]
            if message.content == captcha_data['code']:
                # Правильный код капчи
                del captchas[user_id]
                await message.author.send('You have successfully passed verification ✅')
                # Добавьте код для присвоения роли, если необходимо

                # Отменяем таймер ожидания верификации
                if user_id in verification_timers:
                    verification_timers[user_id].cancel()
            else:
                await message.author.send('Incorrect code. Enter new captcha code.')
        else:
            await message.author.send('Enter the command `!captcha` before entering the captcha code.')

async def wait_for_verification(user_id):
    await asyncio.sleep(300)  # Ожидаем 5 минут (300 секунд)
    if user_id in captchas:
        del captchas[user_id]
        user = client.get_user(user_id)
        if user:
            await user.kick(reason='Failed to verify within 5 minutes')

# Токен вашего бота
client.run('токен')
