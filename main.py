from schedule import every, repeat, run_pending
from aitextgen import aitextgen
from dggbot import DGGBot, Message
from time import sleep
from threading import Thread
from logging.handlers import RotatingFileHandler
import logging
import sys
import re
import os

sys.tracebacklimit = 3

log_format = "[%(asctime)s] %(name)s:%(levelname)s: %(message)s"
logging.basicConfig(
    level=logging.DEBUG,
    format=log_format,
    handlers=[RotatingFileHandler("logs.log", maxBytes=250000000, backupCount=1)],
)
logger = logging.getLogger("vaush_bot")
log_stream_handler = logging.StreamHandler(sys.stdout)
log_stream_handler.setLevel(logging.INFO)
log_formatter = logging.Formatter(log_format)
log_stream_handler.setFormatter(log_formatter)
logger.addHandler(log_stream_handler)
logger.info("Starting")

dgg_bot = DGGBot(auth_token=os.getenv("DGG_AUTH"), username="hac")
dgg_bot.last_mention = None
dgg_bot.enabled = False
ai = aitextgen(
    model_folder="trained_model",
    tokenizer_file="trained_model/aitextgen.tokenizer.json",
)


def is_admin(msg: Message):
    if msg.nick in ("Cake", "RightToBearArmsLOL", "Destiny", "tena"):
        return True
    else:
        logger.info(f'"{msg.nick}" failed admin check')
        return False


@repeat(every(5).minutes)
def generate_message():
    m_data = m_nick = ""
    if isinstance(dgg_bot.last_mention, Message):
        m_data = dgg_bot.last_mention.data
        m_nick = dgg_bot.last_mention.nick
    if len(m_data) > 60:
        m_data = m_data[:59]
    ai_msg = ai.generate_one(max_length=len(m_data) + 30, prompt=m_data)
    if m_nick:
        dgg_msg = f"{m_nick} {ai_msg[len(m_data):]}"
    else:
        dgg_msg = ai_msg[ai_msg.find(" ") :]
    logger.info(f'Message: "{dgg_msg}"')
    if dgg_bot.enabled:
        dgg_bot.send(dgg_msg)
        logger.info("Message sent")
    dgg_bot.last_mention = None


@dgg_bot.event("on_msg")
def update_mention(msg: Message):
    if re.search(r"\bhac\b", msg.data):
        dgg_bot.last_mention = msg


@dgg_bot.command(["venable"])
@dgg_bot.check(is_admin)
def enable_bot(msg: Message):
    dgg_bot.enabled = True
    logger.info(f"Bot enabled by {msg.nick}")


@dgg_bot.command(["vdisable"])
@dgg_bot.check(is_admin)
def disable_bot(msg: Message):
    dgg_bot.enabled = False
    logger.info(f"Bot disabled by {msg.nick}")


@dgg_bot.command(["vreset"])
@dgg_bot.check(is_admin)
def reset_bot(msg: Message):
    logger.info(f"Bot reset by {msg.nick}")
    sys.stdout.flush()
    os.execv(sys.argv[0], sys.argv)


def run_scheduled():
    while True:
        run_pending()
        sleep(5)


if __name__ == "__main__":
    sched_thread = Thread(target=run_scheduled)
    sched_thread.start()
    logger.info("Connecting to DGG")
    while True:
        dgg_bot.run()
        sleep(5)
