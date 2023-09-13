from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot states
QUESTION, OPTIONS, POLL_FINISHED = range(3)

# Store poll data
poll_data = {}


def start(update: Update, context: CallbackContext) -> int:
    """Start the conversation and ask for a poll question."""
    update.message.reply_text(
        "Hi there! Let's create a poll.\n\n"
        "Please send me the poll question."
    )
    return QUESTION


def collect_question(update: Update, context: CallbackContext) -> int:
    """Collect the poll question and ask for poll options."""
    # Save the question
    poll_data['question'] = update.message.text

    update.message.reply_text(
        "Great! Now send me the options for the poll, one by one."
        "Send /done when you're finished."
    )
    return OPTIONS


def collect_options(update: Update, context: CallbackContext) -> int:
    """Collect the poll options."""
    # Store options
    options = poll_data.get('options', [])
    if update.message.text.strip() != '/done':
        options.append(update.message.text)
        poll_data['options'] = options
    else:
        if len(options) < 2:
            update.message.reply_text(
                "Please provide at least 2 options for the poll."
            )
            return OPTIONS

        update.message.reply_text(
            "Poll created successfully!"
            "\n\n"
            "Question: {}\n\n"
            "Options:\n{}".format(
                poll_data['question'],
                '\n'.join(options)
            )
        )
        return POLL_FINISHED


def cancel(update: Update, context: CallbackContext) -> int:
    """Cancel the poll creation and end the conversation."""
    update.message.reply_text("Poll creation cancelled.")
    return ConversationHandler.END


def main():
    updater = Updater("YOUR_BOT_TOKEN")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            QUESTION: [MessageHandler(Filters.text & ~Filters.command, collect_question)],
            OPTIONS: [MessageHandler(Filters.text & ~Filters.command, collect_options)],
            POLL_FINISHED: [CommandHandler('cancel', cancel)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()
    print("Bot started")
    updater.idle()


if __name__ == '__main__':
    main()
  
