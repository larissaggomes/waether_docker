import os
import logging
import requests
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# Configuração de logs
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Variáveis de ambiente
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
OPENWEATHER_BASE_URL = os.getenv("OPENWEATHER_URL")

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'Olá! Eu sou o ClimaBot. Envie o nome de uma cidade para saber o clima atual.'
    )

# Comando /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'Para saber o clima de uma cidade, basta digitar o nome dela. Exemplo: "Manaus" ou "Sao Paulo".'
    )

# Função para buscar clima
async def get_weather(city: str) -> dict:
    params = {
        'q': city,
        'appid': OPENWEATHER_API_KEY,
        'units': 'metric',
        'lang': 'pt'
    }

    try:
        response = requests.get(OPENWEATHER_BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao consultar a API do OpenWeatherMap: {e}")
        return None

# Mensagem de texto do usuário
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    city = update.message.text.strip()
    logger.info(f"Solicitação para a cidade: {city}")

    weather_data = await get_weather(city)

    if weather_data:
        if weather_data.get('cod') == 200:
            main_data = weather_data['main']
            weather_desc = weather_data['weather'][0]['description']
            city_name = weather_data['name']
            country = weather_data['sys']['country']
            temp = main_data['temp']
            feels_like = main_data['feels_like']
            humidity = main_data['humidity']

            message = (
                f"Clima atual em {city_name}, {country}:\n"
                f"🌡️ Temperatura: {temp}°C (sensação de {feels_like}°C)\n"
                f"☁️ Condição: {weather_desc.capitalize()}\n"
                f"💧 Umidade: {humidity}%"
            )

            await update.message.reply_text(message)
        else:
            await update.message.reply_text(
                f"Não foi possível encontrar o clima para '{city}'. Verifique o nome."
            )
    else:
        await update.message.reply_text(
            "Ocorreu um erro ao buscar o clima. Tente novamente mais tarde."
        )

# Função principal
def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN não configurado no .env")
        return

    if not OPENWEATHER_API_KEY:
        logger.error("OPENWEATHER_API_KEY não configurado no .env")
        return

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot rodando...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
