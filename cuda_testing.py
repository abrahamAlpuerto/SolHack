# run.py
import torch

def main():
    # Check how many GPUs are available
    num_gpus = torch.cuda.device_count()
    print(f"Number of GPUs available: {num_gpus}")

    # List each GPU and its name
    for i in range(num_gpus):
        gpu_name = torch.cuda.get_device_name(i)
        print(f"GPU {i}: {gpu_name}")

    # Example: If you want to use them in a distributed manner,
    # you would typically spawn one process per GPU and assign rank = GPU index.
    # For instance:
    # world_size = num_gpus
    # print("You could run DistributedDataParallel with world_size =", world_size)
    # print("Each process would handle one GPU, for example rank 0 -> GPU 0, rank 1 -> GPU 1, etc.")

if __name__ == "__main__":
    main()
