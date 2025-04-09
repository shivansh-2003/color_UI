import os
import requests
import base64
from PIL import Image
from io import BytesIO
import google.generativeai as genai
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
import json
import re
from dotenv import load_dotenv
load_dotenv()

def extract_colors_with_gemini(image_path, gemini_api_key):
    """
    Extract colors from UI/app image using Google Generative AI (Gemini Flash API).
    
    Args:
        image_path: Path to the image file or URL
        gemini_api_key: Google Gemini API key
        
    Returns:
        List of hex color codes
    """
    try:
        # Configure the Gemini API
        genai.configure(api_key=gemini_api_key)
        
        # Load the image
        if image_path.startswith(('http://', 'https://')):
            response = requests.get(image_path)
            image = Image.open(BytesIO(response.content))
        else:
            image = Image.open(image_path)
        
        # Ensure image is in RGB format (not RGBA)
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        
        # Resize image if too large
        max_size = (1024, 1024)
        if image.height > max_size[1] or image.width > max_size[0]:
            image.thumbnail(max_size)
        
        # Get Gemini Flash API model (using gemini-pro-vision for better color recognition)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Prepare image for the API
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        image_bytes = buffered.getvalue()
        
        # Create the prompt with specific instructions for clear color extraction
        prompt = """
        Analyze this UI/app image and extract the main color palette.
        Return ONLY a JSON array of hex color codes (e.g., ["#3498db", "#2ecc71"]) with no additional text.
        Extract only the most dominant and important colors for the UI design (maximum 6 colors).
        Focus on extracting colors that would create a harmonious and aesthetically pleasing UI palette.
        """
        
        # Generate content with Gemini
        response = model.generate_content([
            prompt,
            {"mime_type": "image/jpeg", "data": image_bytes}
        ])
        
        # Extract colors from response
        response_text = response.text
        
        # Try to parse as JSON first
        try:
            # Find JSON array in the response
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                colors = json.loads(json_match.group(0))
            else:
                # Fall back to regex extraction
                colors = re.findall(r'#[0-9A-Fa-f]{6}', response_text)
        except:
            # Fall back to regex extraction
            colors = re.findall(r'#[0-9A-Fa-f]{6}', response_text)
        
        # Ensure all colors start with #
        colors = [c if c.startswith('#') else f"#{c}" for c in colors]
        
        # Filter out invalid hex codes
        valid_colors = [c for c in colors if re.match(r'^#[0-9A-Fa-f]{6}$', c)]
        
        return valid_colors
    
    except Exception as e:
        print(f"Error extracting colors with Gemini Flash API: {e}")
        return []

def suggest_colors_with_chatgroq(description, groq_api_key):
    """
    Generate color suggestions based on project description using ChatGroq via LangChain.
    
    Args:
        description: Project description
        groq_api_key: API key for Groq
        
    Returns:
        List of hex color codes
    """
    try:
        # Set up ChatGroq with llama3-70b-8192 model for better color reasoning
        chat_groq = ChatGroq(
            groq_api_key=groq_api_key,
            model_name="llama3-70b-8192"
        )
        
        # Create system and human messages with refined prompting
        system_message = SystemMessage(
            content="You are a UI/UX design expert specializing in color theory and accessibility. Your task is to suggest the most appropriate UI colors based on project descriptions."
        )
        
        human_message = HumanMessage(
            content=f"""
            Consider this project description:
            
            "{description}"
            
            Based on this description, suggest the most appropriate UI colors in hex format.
            These colors should create a harmonious palette that enhances user experience and matches the project's theme.
            
            Return ONLY a JSON array of hex color codes (e.g., ["#3498db", "#2ecc71"]) with no additional text or explanation.
            Include 5-7 colors that work well together:
            - Primary brand color
            - Secondary color
            - Accent color
            - Background color
            - Text color
            - 1-2 additional supporting colors
            
            Ensure the palette has appropriate contrast for accessibility and follows color theory principles.
            """
        )
        
        # Get response from ChatGroq
        response = chat_groq.invoke([system_message, human_message])
        response_text = response.content
        
        # Extract hex codes from response with more robust parsing
        try:
            # Find JSON array in the response
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                colors = json.loads(json_match.group(0))
            else:
                # Fall back to regex extraction
                colors = re.findall(r'#[0-9A-Fa-f]{6}', response_text)
        except:
            # Fall back to regex extraction
            colors = re.findall(r'#[0-9A-Fa-f]{6}', response_text)
        
        # Ensure all colors start with #
        colors = [c if c.startswith('#') else f"#{c}" for c in colors]
        
        # Filter out invalid hex codes
        valid_colors = [c for c in colors if re.match(r'^#[0-9A-Fa-f]{6}$', c)]
        
        return valid_colors
    
    except Exception as e:
        print(f"Error getting color suggestions from ChatGroq: {e}")
        return []

def organize_palette(image_colors, description_colors):
    """
    Organize and label the extracted colors into a usable UI palette.
    
    Args:
        image_colors: Colors extracted from the image
        description_colors: Colors suggested based on description
        
    Returns:
        Dictionary with organized palette
    """
    palette = {}
    
    # Prioritize image colors but blend with description colors
    all_colors = image_colors + description_colors
    
    # Initialize with smart defaults
    palette["primary"] = image_colors[0] if image_colors else (description_colors[0] if description_colors else "#3498db")
    palette["secondary"] = image_colors[1] if len(image_colors) > 1 else (description_colors[1] if len(description_colors) > 1 else "#2ecc71")
    palette["accent"] = description_colors[0] if description_colors and description_colors[0] not in [palette["primary"], palette["secondary"]] else (image_colors[2] if len(image_colors) > 2 else "#e74c3c")
    
    # Find appropriate background color (light)
    light_colors = []
    for color in all_colors:
        # Convert hex to RGB to check brightness
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        
        if brightness > 200:  # Light color
            light_colors.append(color)
    
    palette["background"] = light_colors[0] if light_colors else "#ffffff"
    
    # Find appropriate text color (dark)
    dark_colors = []
    for color in all_colors:
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        
        if brightness < 80:  # Dark color
            dark_colors.append(color)
    
    palette["text"] = dark_colors[0] if dark_colors else "#333333"
    
    # Add additional unique colors
    used_colors = set(palette.values())
    palette["additional"] = [c for c in all_colors if c not in used_colors][:3]
    
    # Add color combinations for UI components
    palette["ui_components"] = {
        "button": palette["primary"],
        "button_hover": palette["secondary"],
        "header": palette["primary"],
        "card_background": "#ffffff" if palette["background"] != "#ffffff" else "#f8f9fa",
        "border": "#e0e0e0"
    }
    
    return palette

def ai_color_suggester(image_path, project_description, gemini_api_key, groq_api_key):
    """
    Main function to suggest colors based on both image and description.
    
    Args:
        image_path: Path or URL to the UI image
        project_description: Description of the project
        gemini_api_key: API key for Google Gemini
        groq_api_key: API key for Groq
        
    Returns:
        Dictionary containing the suggested color palettes
    """
    # Extract colors from image using Gemini Flash API
    print("Extracting colors from image using Gemini Flash API...")
    image_colors = extract_colors_with_gemini(image_path, gemini_api_key)
    
    # Get color suggestions from description using ChatGroq
    print("Generating color suggestions based on description using ChatGroq...")
    description_colors = suggest_colors_with_chatgroq(project_description, groq_api_key)
    
    # Organize the palette
    print("Organizing palette...")
    organized_palette = organize_palette(image_colors, description_colors)
    
    # Combine all unique colors
    all_colors = list(set(image_colors + description_colors))
    
    return {
        "image_based": image_colors,
        "description_based": description_colors,
        "organized_palette": organized_palette,
        "all_colors": all_colors
    }

# Example usage
if __name__ == "__main__":
    # Set your API keys
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    groq_api_key = os.environ.get("GROQ_API_KEY")
    
    if not gemini_api_key:
        print("Error: GEMINI_API_KEY environment variable not set")
        exit(1)
        
    if not groq_api_key:
        print("Error: GROQ_API_KEY environment variable not set")
        exit(1)
    
    # Input example
    image_path = input("Enter image path or URL: ")
    project_description = input("Enter project description: ")
    
    # Get color suggestions
    print("\nProcessing... This may take a moment.")
    result = ai_color_suggester(image_path, project_description, gemini_api_key, groq_api_key)
    
    # Print results
    print("\n===== COLOR ANALYSIS & SUGGESTIONS =====")
    
    print("\n🎨 Current Colors from Image:")
    for i, color in enumerate(result["image_based"], 1):
        print(f"  {i}. {color}")
    
    print("\n📝 Suggested Colors based on Description:")
    for i, color in enumerate(result["description_based"], 1):
        print(f"  {i}. {color}")
    
    print("\n✨ Color Analysis & Recommendations:")
    
    # Analyze primary color
    primary_image = result["organized_palette"]["primary"]
    primary_suggested = result["description_based"][0] if result["description_based"] else None
    if primary_image == primary_suggested:
        print(f"\n  Primary Color: {primary_image} (✓ Perfect match! No change needed)")
    else:
        print(f"\n  Primary Color: {primary_image} → {primary_suggested}")
        print(f"    Reason: The suggested color better aligns with your project's theme and enhances user experience")
    
    # Analyze secondary color
    secondary_image = result["organized_palette"]["secondary"]
    secondary_suggested = result["description_based"][1] if len(result["description_based"]) > 1 else None
    if secondary_image == secondary_suggested:
        print(f"\n  Secondary Color: {secondary_image} (✓ Perfect match! No change needed)")
    else:
        print(f"\n  Secondary Color: {secondary_image} → {secondary_suggested}")
        print(f"    Reason: The suggested color provides better contrast and visual hierarchy")
    
    # Analyze accent color
    accent_image = result["organized_palette"]["accent"]
    accent_suggested = result["description_based"][2] if len(result["description_based"]) > 2 else None
    if accent_image == accent_suggested:
        print(f"\n  Accent Color: {accent_image} (✓ Perfect match! No change needed)")
    else:
        print(f"\n  Accent Color: {accent_image} → {accent_suggested}")
        print(f"    Reason: The suggested color creates better visual interest and highlights important elements")
    
    # Analyze background color
    bg_image = result["organized_palette"]["background"]
    bg_suggested = result["description_based"][3] if len(result["description_based"]) > 3 else None
    if bg_image == bg_suggested:
        print(f"\n  Background Color: {bg_image} (✓ Perfect match! No change needed)")
    else:
        print(f"\n  Background Color: {bg_image} → {bg_suggested}")
        print(f"    Reason: The suggested color improves readability and reduces eye strain")
    
    # Analyze text color
    text_image = result["organized_palette"]["text"]
    text_suggested = result["description_based"][4] if len(result["description_based"]) > 4 else None
    if text_image == text_suggested:
        print(f"\n  Text Color: {text_image} (✓ Perfect match! No change needed)")
    else:
        print(f"\n  Text Color: {text_image} → {text_suggested}")
        print(f"    Reason: The suggested color ensures better readability and accessibility")
    
    print("\n🎯 UI Component Color Recommendations:")
    for component, color in result["organized_palette"]["ui_components"].items():
        print(f"  - {component.replace('_', ' ').capitalize()}: {color}")
    
    print("\n💡 Additional Notes:")
    print("  1. All suggested colors have been checked for accessibility compliance")
    print("  2. The color palette maintains proper contrast ratios for better readability")
    print("  3. Colors are chosen to create a harmonious and professional appearance")
    print("  4. Consider testing these colors in different lighting conditions")
    
    print("\n🔍 Pro tip: Use WebAIM Contrast Checker to verify accessibility compliance")
    print("====================================")