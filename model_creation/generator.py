from aitextgen.TokenDataset import TokenDataset
from aitextgen.tokenizers import train_tokenizer
from aitextgen.utils import GPT2ConfigCPU
from aitextgen import aitextgen


def main_func():
    file_name = "transcript.txt"
    train_tokenizer(file_name)
    tokenizer_file = "aitextgen.tokenizer.json"
    config = GPT2ConfigCPU(max_length=32)
    ai = aitextgen(tokenizer_file=tokenizer_file, config=config)
    data = TokenDataset(file_name, tokenizer_file=tokenizer_file, block_size=32)
    ai.train(
        data, batch_size=32, num_steps=100000, generate_every=5000, save_every=5000
    )


if __name__ == "__main__":
    main_func()
