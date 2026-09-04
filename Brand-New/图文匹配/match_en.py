'''
英文论文中进行图文配对，将图片与文字内容对应起来。
'''
import os  
import re  

def extract_text_from_markdown(markdown_filename):  
    """Extract text content from Markdown files associated with images."""  
    print(markdown_filename)  
    with open(markdown_filename, 'r', encoding='utf-8') as file:  
        content = file.read()  

    # Search for all image tags  
    img_pattern = r'!\[\]\((.*?)\)'  
    images = re.findall(img_pattern, content)  

    text_mapping = {}  

    # Split content by lines for easy indexing and retrieval  
    lines = content.splitlines()  

    # Iterate over each image to perform secondary search  
    for img in images:  
        img_name = os.path.basename(img)  # Get image name  

        # Get the position of the image  
        img_position = content.find(img)  
        
        # Find corresponding line number  
        line_index = content[:img_position].count('\n')  # Count how many lines are before the image  
        
        # Define the number of lines to search above and below  
        upper_index = max(0, line_index - 2)  # Two lines above  
        lower_index = min(len(lines) - 1, line_index + 2)  # Two lines below  
        
        # Get upper and lower contextual text  
        context_lines = lines[upper_index: lower_index + 1]  
        context_text = ' '.join(context_lines).strip()  # Merge context text  

        # Match the preceding "Figure" or "Table"  
        # number_pattern = r"(Fig.|Figure|Table)\s*(\d+)"  
        number_pattern = r"(Fig.|Figure)\s*(\d+)"  
        
        # Look for the most recent "Figure 1" or "Table 1"  
        numbers = re.findall(number_pattern, context_text)  
        if numbers:  
            last_section = numbers[-1]  
            section_name = f"{last_section[0]} {last_section[-1]}"  # Format as “Figure 1” or “Table 1”  
            # print(last_section[0], last_section[-1])  
            # Adjust the pattern to capture the full sentence after the Figure/Table reference  
            text_pattern = rf'(.*?{re.escape(last_section[0])}\s*{last_section[-1]}.*?[\.\?!])'  
            text_matches = re.findall(text_pattern, content)  # Find all matches 
            result_texts = []  

            if text_matches:  
                result_texts.extend(match.strip() for match in text_matches if match)
            # 
            if last_section[0] == 'Fig.':
                last_section = list(last_section)
                last_section[0] = 'Figure'
                last_section = tuple(last_section)
                fig_text_pattern = rf'(.*?{re.escape(last_section[0])}\s*{last_section[-1]}.*?[\.\?!])'  
                fig_matches = re.findall(fig_text_pattern, content)  
                if fig_matches:  
                    result_texts.extend(match.strip() for match in fig_matches if match)  
            if last_section[0] == 'FIG':
                last_section = list(last_section)
                last_section[0] = 'Figure'
                last_section = tuple(last_section)
                fig_text_pattern = rf'(.*?{re.escape(last_section[0])}\s*{last_section[-1]}.*?[\.\?!])'  
                fig_matches = re.findall(fig_text_pattern, content)  
                if fig_matches:  
                    result_texts.extend(match.strip() for match in fig_matches if match)  
            # if last_section[0] == 'TABLE':
            #     last_section = list(last_section)
            #     last_section[0] = 'Table'
            #     last_section = tuple(last_section)
            #     fig_text_pattern = rf'(.*?{re.escape(last_section[0])}\s*{last_section[-1]}.*?[\.\?!])'  
            #     fig_matches = re.findall(fig_text_pattern, content)  
            #     if fig_matches:  
            #         result_texts.extend(match.strip() for match in fig_matches if match)  
            if last_section[0] == 'FIGURE':
                last_section = list(last_section)
                last_section[0] = 'Figure'
                last_section = tuple(last_section)
                fig_text_pattern = rf'(.*?{re.escape(last_section[0])}\s*{last_section[-1]}.*?[\.\?!])'  
                fig_matches = re.findall(fig_text_pattern, content)  
                if fig_matches:  
                    result_texts.extend(match.strip() for match in fig_matches if match)  

            # Save all found text content  
            if text_matches:  
                text_mapping[img_name] = ' '.join(result_texts).strip()  

    return text_mapping  

def save_text_files(text_mapping, images_folder):  
    """Save text content as TXT files."""  
    for img_name, text in text_mapping.items():  
        if text:  
            # Use the base name of img_name as the TXT file name  
            base_name = os.path.splitext(img_name)[0]  # Remove the extension  
            txt_filename = os.path.join(images_folder, f"{base_name}.txt")  # Correct the extension  
            with open(txt_filename, 'w', encoding='utf-8') as txt_file:  
                txt_file.write(text)  

def process_folders(input_folder):  
    """Main processing function to traverse the input folder and process each subfolder."""  
    for root, dirs, files in os.walk(input_folder):  
        images_folder = os.path.join(root, 'images')  # Set the images folder path  
        
        # Only process paths containing 'images' folder  
        if 'images' in dirs:  
            # Find Markdown files  
            for file in files:  
                if file.endswith('.md'):  
                    markdown_file = os.path.join(root, file)  
                    text_mapping = extract_text_from_markdown(markdown_file)  
                    save_text_files(text_mapping, images_folder)  

if __name__ == "__main__":  
    input_folder = r"D:\多模态\人工智能\CNKI-progressed"  # Specify input folder  
    process_folders(input_folder)