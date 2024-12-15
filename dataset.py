from datasets import load_dataset



def get_dataset():

    dataset = load_dataset('json', data_files='crypto.jsonl')
    print(dataset)
    print(dataset['train'])

if __name__ == "__main__":
    get_dataset()
