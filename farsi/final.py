# Specify the file name
file_name = 'annotated_pos_sent.txt'

# Open the file and read its contents
with open(file_name, 'r', encoding='utf-8') as file:
    file_contents = file.read()

# Print the contents to verify
#print(file_contents)
def convert_dependency_tree(vrt_content):
    result = []
    for line in vrt_content.strip().split('\n'):
        parts = line.split()
        
        if len(parts) < 8:  # Skip lines that don't have enough parts
            continue
        token_index = int(parts[0])
        parent_index = int(parts[6])
        x = parent_index - token_index
        y = 0
        string=str((x,y))
        parts.append(string)
        result.append(parts)
    return result

result = convert_dependency_tree(file_contents)
with open('output.vrt', 'w', encoding='utf-8') as f:
# print(result)
    for item in result:
        item.pop(0)
        #print(f"{item[0]}\t{item[1]}\t{item[2]}\t{item[3]}\t{item[4]}\t{item[5]}\t{item[6]}\t{item[7]}\t{item[8]}\t{item[9]}\n")
        #print(item[0],item[1],item[2],item[3])
        #print(item)
        # Join the elements with a space
        if item[1]=="_":
            item[1]=item[0]
       
        start, end = item[7].split("__")
        start_secs, start_centisecs = start.split(":")
        end_secs, end_centisecs = end.split(":")
        start_time, end_time = item[8].split("__")
        f.write(f"{item[0]}\t{item[3]}\t{item[1]}\t{item[2]}\t{item[1]}_{item[2]}\t{item[0]}\t_\t_\t{item[4]}\t_\t_\t_\t{item[9]}\t{item[6]}\t{start_secs}\t{start_centisecs}\t{end_secs}\t{end_centisecs}\t{start_time}\t{end_time}\n")

# Print the result
        
        #print(output_line[0])
