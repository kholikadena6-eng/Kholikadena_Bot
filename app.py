import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from duckduckgo_search import DDGS

BOT_TOKEN = os.getenv("BOT_TOKEN")

memory = {}
tasks = {}

def research(query):
    results_text = ""
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=3)
        for r in results:
            results_text += r["body"] + "\n"
    return results_text[:1000]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Your AI Assistant is now online!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    text = update.message.text.lower()

    if user_id not in memory:
        memory[user_id] = []

    # Research mode
    if text.startswith("research"):
        query = text.replace("research", "").strip()
        await update.message.reply_text("🔍 Researching...")
        result = research(query)
        await update.message.reply_text(result)

    # Add task
    elif text.startswith("add task"):
        task = text.replace("add task", "").strip()
        tasks.setdefault(user_id, []).append(task)
        await update.message.reply_text(f"✅ Task added: {task}")

    # List tasks
    elif text == "list tasks":
        user_tasks = tasks.get(user_id, [])
        if not user_tasks:
            await update.message.reply_text("📭 No tasks found.")
        else:
            task_list = "\n".join([f"{i+1}. {t}" for i, t in enumerate(user_tasks)])
            await update.message.reply_text(f"📝 Your Tasks:\n{task_list}")

    else:
        memory[user_id].append(text)
        await update.message.reply_text("🧠 I received your message. Use:\n- research <topic>\n- add task <task>\n- list tasks")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("AI Assistant is running...")
app.run_polling()
