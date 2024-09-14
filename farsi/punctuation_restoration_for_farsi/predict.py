from transformers import pipeline
import argparse

def predict_punctuation(model: str, sentence: str, task: str) -> str:
    # Load the NER model from Hugging Face Transformers
    pipe = pipeline("ner", model=model, grouped_entities=False, device=0)

    # Predict punctuation
    result = pipe(sentence)
    
    # Define mappings for task 1 and task 2
    #label_2_id = {"0": 0, ".": 1, "؟": 2, "،": 3}
    label_2_id = {"0":0, ".":1, "؛":2, "؟":3, "،":4, ":":5}
    id_2_label = list(label_2_id.keys())

    def map_label_task_2(label):
        label_id = int(label[-1])
        return id_2_label[label_id]

    def map_label_task_1(label):
        label_id = int(label[-1])
        if label_id != 1:
            label_id = 0
        return label_id

    def map_labels(result, task):
        text_index = 0
        tagged_words = []
        for entity in result:
            if entity["start"] >= text_index:
                if task == "1":
                    label = map_label_task_1(entity["entity"])
                elif task == "2":
                    label = map_label_task_2(entity["entity"])
                else:
                    raise ValueError("Invalid task. Choose '1' or '2'.")
                
                if label == 0:
                    tagged_words.append(entity["word"])  # No punctuation
                else:
                    tagged_words.append(f"{entity['word']} {id_2_label[label]}")
                text_index = entity["end"]
        return " ".join(tagged_words)

    # Map predictions based on the task
    formatted_output = map_labels(pipe(sentence), task)
    return formatted_output

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Predict punctuation for a given sentence using a transformer model')
    parser.add_argument("sentence", help="The input sentence to predict punctuation for")
    parser.add_argument("model", help="Path to the transformer model")
    parser.add_argument("task", help="Task number: '1' or '2'")
    args = parser.parse_args()
    
    # Predict punctuation
    output = predict_punctuation(args.model, args.sentence, args.task)
    print(output)

