from schedule import every, repeat, run_pending
from aitextgen import aitextgen
from dggbot import DGGBot, Message
from os import getenv
from time import sleep
from threading import Thread
from logging.handlers import RotatingFileHandler
import logging
import sys
import re

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

dgg_bot = DGGBot(auth_token=getenv("DGG_AUTH"), username="hac")
dgg_bot.last_mention = ""
dgg_bot.enabled = True
ai = aitextgen(
    model_folder="trained_model",
    tokenizer_file="trained_model/aitextgen.tokenizer.json",
)


def is_admin(msg: Message):
    return msg.nick in ("Cake", "RightToBearArmsLOL", "Destiny", "tena")


@repeat(every(5).minutes)
def generate_message():
    ai_msg = ai.generate_one(max_length=30, prompt=dgg_bot.last_mention)
    dgg_msg = f'{dgg_bot.last_mention} {ai_msg[ai_msg.find(" "):]}'
    logger.info(f'Message: "{dgg_msg}"')
    if dgg_bot.enabled:
        dgg_bot.send(dgg_msg)
        logger.info("Message sent")
    dgg_bot.last_mention = ""


@dgg_bot.event("on_msg")
def update_mention(msg: Message):
    if re.search(r"hac\b", msg.data):
        dgg_bot.last_mention = f"{msg.nick} "


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
