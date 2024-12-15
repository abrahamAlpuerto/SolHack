import torch
from torch.utils.data import DataLoader
from torch.utils.data.distributed import DistributedSampler
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.distributed import init_process_group, destroy_process_group
from datasets import load_dataset
import os
import torch.multiprocessing as mp
import time

from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

HUGGINGFACE_TOKEN = ""
MODEL_NAME = "meta-llama/Llama-3.2-3B-Instruct-QLORA_INT4_EO8"

def ddp_setup(rank, world_size):
    os.environ["MASTER_ADDR"] = "localhost"
    os.environ["MASTER_PORT"] = "12355"
    init_process_group(backend="nccl", rank=rank, world_size=world_size)

class Trainer:
    def __init__(
            self,
            model: torch.nn.Module,
            train_data: DataLoader,
            optimizer: torch.optim.Optimizer,
            gpu_id: int,
            save_every: int,
            ) -> None:
        self.gpu_id = gpu_id
        self.model = model.to(gpu_id)
        self.train_data = train_data
        self.optimizer = optimizer
        self.save_every = save_every
        self.model = DDP(self.model, device_ids=[self.gpu_id], output_device=self.gpu_id)

    def _run_batch(self, input_ids, labels):
        self.optimizer.zero_grad()
        output = self.model(input_ids=input_ids, labels=labels)
        loss = output.loss
        loss.backward()
        self.optimizer.step()
        return loss.item()

    def _run_epoch(self, epoch):
        batch_example = next(iter(self.train_data))
        b_sz = len(batch_example["input_ids"])
        print(f"[GPU{self.gpu_id}] Epoch {epoch} | Batchsize: {b_sz} | Steps: {len(self.train_data)}")
        self.model.train()
        total_loss = 0
        for batch in self.train_data:
            input_ids = batch["input_ids"].to(self.gpu_id)
            labels = batch["labels"].to(self.gpu_id)
            loss = self._run_batch(input_ids, labels)
            total_loss += loss
        avg_loss = total_loss / len(self.train_data)
        print(f"[GPU{self.gpu_id}] Epoch {epoch} completed. Average loss: {avg_loss:.4f}")

    def _save_checkpoint(self, epoch):
        ckp = self.model.module.state_dict()
        torch.save(ckp, f"checkpoint_epoch_{epoch}.pt")
        print(f"Epoch {epoch} | Training checkpoint saved at checkpoint_epoch_{epoch}.pt")

    def train(self, max_epochs: int):
        for epoch in range(max_epochs):
            self._run_epoch(epoch)
            if self.gpu_id == 0 and epoch % self.save_every == 0:
                self._save_checkpoint(epoch)

def format_example(instruction, input_text, output_text):
    # A common instruction prompt format:
    if input_text.strip():
        prompt = f"Below is an instruction that describes a task. Write a response that appropriately completes the request.\n\nInstruction: {instruction}\nInput: {input_text}\nResponse:\n{output_text}"
    else:
        prompt = f"Below is an instruction that describes a task. Write a response that appropriately completes the request.\n\nInstruction: {instruction}\nResponse:\n{output_text}"
    return prompt

def load_train_objs():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_auth_token=HUGGINGFACE_TOKEN, trust_remote_code=True)
    # Load quantized model with trust_remote_code
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        device_map="auto",
        trust_remote_code=True,
        use_auth_token=HUGGINGFACE_TOKEN
    )

    # Apply LoRA with Peft
    lora_config = LoraConfig(
        r=8,
        lora_alpha=32,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"], # adjust as needed for Llama
        lora_dropout=0.1,
        bias="none",
        task_type="CAUSAL_LM"
    )

    # Prepare model for training with k-bit (QLoRA)
    model = prepare_model_for_kbit_training(model)
    model = get_peft_model(model, lora_config)

    dataset = load_dataset('json', data_files='crypto.jsonl')

    # Tokenize function
    def tokenize_function(examples):
        # We combine instruction, input, output into a single prompt
        # In instruction-tuning, we usually train the model to produce only 'output' after seeing 'instruction' and 'input'.
        # We'll put the 'output' as what the model should predict after the prompt.
        inputs = []
        labels = []
        for instruction, input_text, output_text in zip(examples["instruction"], examples["input"], examples["output"]):
            prompt = format_example(instruction, input_text, output_text)
            tokenized = tokenizer(prompt, truncation=True, padding='max_length', max_length=512)
            # In causal LM, we usually set labels = input_ids but we need to mask out the user prompt part if needed.
            # For simplicity, we label everything, model learns to reproduce full text including the output section.
            # If you only want model to predict output part, you'd need to find the boundary where output starts.
            # Let's assume we want to train full text (it can learn to follow instructions this way).
            tokenized["labels"] = tokenized["input_ids"].copy()
            inputs.append(tokenized["input_ids"])
            labels.append(tokenized["labels"])

        return {"input_ids": inputs, "labels": labels}

    # Map the dataset
    # dataset["train"] is your training split
    train_dataset = dataset["train"].map(tokenize_function, batched=True, remove_columns=dataset["train"].column_names)

    train_dataset.set_format(type="torch", columns=["input_ids", "labels"])

    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)

    return train_dataset, model, optimizer

def prepare_dataloader(dataset, batch_size: int):
    return DataLoader(
        dataset,
        batch_size=batch_size,
        pin_memory=True,
        shuffle=False,
        sampler=DistributedSampler(dataset)
    )

def main(rank: int, world_size: int, total_epochs: int, save_every: int):
    ddp_setup(rank, world_size)
    train_dataset, model, optimizer = load_train_objs()
    train_data = prepare_dataloader(train_dataset, batch_size=8) # adjust batch size as needed
    trainer = Trainer(model, train_data, optimizer, rank, save_every)
    trainer.train(total_epochs)
    destroy_process_group()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python script.py <total_epochs> <save_every>")
        sys.exit(1)
    total_epochs = int(sys.argv[1])
    save_every = int(sys.argv[2])
    world_size = torch.cuda.device_count()
    print(world_size)
    mp.spawn(main, args=(world_size, total_epochs, save_every), nprocs=world_size)
