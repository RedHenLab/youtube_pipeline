from transformers import pipeline
import argparse
import re

def read_vtt(vtt_file: str) -> list:
    """Reads a VTT file and extracts the timestamps and text."""
    with open(vtt_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    captions = []
    current_caption = {"timestamp": "", "text": ""}
    
    for line in lines:
        line = line.strip()
        if re.match(r'\d{2}:\d{2}.\d{3} --> \d{2}:\d{2}.\d{3}', line):
            # This is a timestamp line
            if current_caption["text"]:
                captions.append(current_caption)
                current_caption = {"timestamp": "", "text": ""}
            current_caption["timestamp"] = line
        elif line and not line.startswith("WEBVTT"):
            # This is a caption line (Farsi text)
            current_caption["text"] += line + " "
    
    if current_caption["text"]:
        captions.append(current_caption)  # Append last caption
    
    return captions

def write_vtt(captions: list, output_file: str):
    """Writes captions back into VTT format."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("WEBVTT\n\n")
        for caption in captions:
            f.write(f"{caption['timestamp']}\n")
            f.write(f"{caption['text'].strip()}\n\n")

def clean_text(text: str) -> str:
    """Removes subword segmentation characters (underscores) from the text."""
    return text.replace("▁", "").strip()

def predict_punctuation(model: str, sentence: str, task: str) -> str:
    """Predicts punctuation for a given sentence using a pre-trained NER model."""
    # Load the NER model from Hugging Face Transformers
    pipe = pipeline("ner", model=model, grouped_entities=False, device=0)

    # Define mappings for task 1 and task 2
    label_2_id = {"0": 0, ".": 1, "؛": 2, "؟": 3, "،": 4, ":": 5}
    id_2_label = list(label_2_id.keys())

    def map_label_task_2(entity):
        """Extracts label for task 2 based on entity type"""
        label_id = entity[-1]  # Get the last character
        if label_id.isdigit():
            return id_2_label[int(label_id)]  # Map to punctuation
        else:
            return "0"  # Default for no punctuation

    def map_label_task_1(entity):
        """Simplified punctuation (only periods) for task 1"""
        label_id = entity[-1]
        if label_id == "1":  # Assuming "1" maps to period
            return "."
        else:
            return "0"  # No punctuation for other cases

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
                
                if label == "0":
                    tagged_words.append(entity["word"])  # No punctuation
                else:
                    tagged_words.append(f"{entity['word']}{label}")
                text_index = entity["end"]
        
        return " ".join(tagged_words)

    # Predict punctuation for the sentence
    result = pipe(sentence)
    formatted_output = map_labels(result, task)
    # Clean the text by removing subword artifacts (underscores)
    return clean_text(formatted_output)

def process_vtt(vtt_file: str, model: str, task: str, output_file: str):
    """Process the VTT file, predict punctuation, and write back to a new VTT file."""
    captions = read_vtt(vtt_file)
    
    # Process each caption's text with the punctuation model
    for caption in captions:
        caption['text'] = predict_punctuation(model, caption['text'], task)
    
    # Write the updated captions with punctuations back to a new VTT file
    write_vtt(captions, output_file)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Predict punctuation for a VTT file in Farsi and output a new VTT file.')
    parser.add_argument("vtt_file", help="Path to the input VTT file")
    parser.add_argument("model", help="Path to the transformer model")
    parser.add_argument("task", help="Task number: '1' or '2'")
    parser.add_argument("output_file", help="Path to the output VTT file with punctuations")
    args = parser.parse_args()

    # Process VTT and output the result
    process_vtt(args.vtt_file, args.model, args.task, args.output_file)

