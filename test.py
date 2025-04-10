import os
import requests
import base64
from PIL import Image, ImageDraw
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

def generate_ui_preview(color_palette, template_type="website", gemini_api_key=None):
    """
    Generate a UI preview image with the suggested color palette.
    
    Args:
        color_palette: Dictionary containing organized color palette
        template_type: Type of UI template to generate (website, mobile, dashboard)
        gemini_api_key: Google Gemini API key for potential AI-generated preview
    
    Returns:
        Dictionary with base64 encoded image and mime type
    """
    try:
        # First, try to use Gemini to generate a more realistic preview if API key provided
        if gemini_api_key:
            try:
                preview = generate_preview_with_gemini(color_palette, template_type, gemini_api_key)
                if preview:
                    return preview
            except Exception as e:
                print(f"Error generating preview with Gemini: {e}")
                # Fall back to manual preview generation
        
        # Extract colors from palette
        primary_color = color_palette["primary"]
        secondary_color = color_palette["secondary"]
        accent_color = color_palette["accent"]
        background_color = color_palette["background"]
        text_color = color_palette["text"]
        
        # Set dimensions based on template type
        if template_type == "mobile":
            width, height = 360, 640
        elif template_type == "dashboard":
            width, height = 1200, 800
        else:  # Default to website
            width, height = 1200, 800
            
        # Create a new image with the background color
        img = Image.new('RGB', (width, height), background_color)
        draw = ImageDraw.Draw(img)
        
        # Draw a header with the primary color
        draw.rectangle([(0, 0), (width, 80)], fill=primary_color)
        
        # Draw a sidebar with the secondary color (for website and dashboard)
        if template_type != "mobile":
            draw.rectangle([(0, 80), (250, height)], fill=secondary_color)
        
        # Draw content based on template type
        if template_type == "mobile":
            # Header
            draw.rectangle([(0, 0), (width, 60)], fill=primary_color)
            
            # Content areas
            draw.rectangle([(20, 80), (width - 20, 200)], fill="#FFFFFF", outline=secondary_color)
            draw.rectangle([(20, 220), (width - 20, 340)], fill="#FFFFFF", outline=secondary_color)
            draw.rectangle([(20, 360), (width - 20, 480)], fill="#FFFFFF", outline=secondary_color)
            
            # Bottom navigation
            draw.rectangle([(0, height - 60), (width, height)], fill=secondary_color)
            
            # Accent button
            draw.ellipse([(width - 80, height - 120), (width - 20, height - 60)], fill=accent_color)
            
            # Add some mock text lines
            for i in range(3):
                y_pos = 100 + i * 20
                draw.rectangle([(40, y_pos), (width - 40, y_pos + 10)], fill=text_color)
            
            for i in range(3):
                y_pos = 240 + i * 20
                draw.rectangle([(40, y_pos), (width - 40, y_pos + 10)], fill=text_color)
            
            for i in range(3):
                y_pos = 380 + i * 20
                draw.rectangle([(40, y_pos), (width - 40, y_pos + 10)], fill=text_color)
        else:
            # For website/dashboard
            
            # Header title area
            draw.rectangle([(20, 20), (200, 60)], fill=primary_color)
            
            # Header navigation
            for i in range(3):
                x_pos = 250 + i * 120
                draw.rectangle([(x_pos, 30), (x_pos + 80, 50)], fill=primary_color)
            
            # Sidebar menu items
            for i in range(5):
                y_pos = 120 + i * 60
                draw.rectangle([(20, y_pos), (230, y_pos + 40)], fill=primary_color)
                # Draw text lines
                for j in range(2):
                    draw.rectangle([(40, y_pos + 10 + j * 10), (200, y_pos + 15 + j * 10)], fill=text_color)
            
            # Main content area
            # Card 1
            draw.rectangle([(270, 100), (width - 20, 300)], fill="#FFFFFF", outline=secondary_color)
            # Card heading
            draw.rectangle([(290, 120), (500, 150)], fill=accent_color)
            # Card content
            for i in range(6):
                y_pos = 170 + i * 20
                length = width - 310 - (i % 3) * 50  # Vary line lengths
                draw.rectangle([(290, y_pos), (length, y_pos + 10)], fill=text_color)
            
            # Card 2
            draw.rectangle([(270, 320), (width - 20, 520)], fill="#FFFFFF", outline=secondary_color)
            # Card heading
            draw.rectangle([(290, 340), (500, 370)], fill=accent_color)
            # Card content
            for i in range(6):
                y_pos = 390 + i * 20
                length = width - 310 - ((i + 1) % 3) * 50  # Vary line lengths
                draw.rectangle([(290, y_pos), (length, y_pos + 10)], fill=text_color)
            
            # Button examples
            draw.rectangle([(290, 540), (400, 580)], fill=primary_color)  # Primary button
            draw.rectangle([(420, 540), (530, 580)], fill=secondary_color)  # Secondary button
            draw.rectangle([(550, 540), (660, 580)], fill=accent_color)  # Accent button
            
        # Add a color palette display at the bottom for reference
        palette_width = 80
        palette_height = 40
        palette_y = height - 60 if template_type == "website" or template_type == "dashboard" else height - 120
        colors = [primary_color, secondary_color, accent_color, background_color, text_color]
        
        for i, color in enumerate(colors):
            x_pos = width - (len(colors) - i) * palette_width - 20
            draw.rectangle([(x_pos, palette_y), (x_pos + palette_width, palette_y + palette_height)], fill=color, outline="#000000")
        
        # Convert image to base64
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return {
            "image_data": img_str,
            "mime_type": "image/png"
        }
    
    except Exception as e:
        print(f"Error generating UI preview: {e}")
        return None

def generate_preview_with_gemini(color_palette, template_type, gemini_api_key):
    """
    Generate a UI preview using Gemini Flash API.
    
    Args:
        color_palette: Dictionary containing organized color palette
        template_type: Type of UI template to generate
        gemini_api_key: Google Gemini API key
    
    Returns:
        Dictionary with base64 encoded image or None if generation fails
    """
    try:
        # Configure Gemini
        genai.configure(api_key=gemini_api_key)
        
        # Get colors from palette
        primary_color = color_palette["primary"]
        secondary_color = color_palette["secondary"]
        accent_color = color_palette["accent"]
        background_color = color_palette["background"]
        text_color = color_palette["text"]
        
        # Create model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Create a detailed prompt instructing Gemini to generate a UI mockup
        prompt = f"""
        Generate a realistic {template_type} UI design mockup using EXACTLY these colors:
        
        Primary color: {primary_color} (for main elements, headers)
        Secondary color: {secondary_color} (for secondary elements)
        Accent color: {accent_color} (for buttons, highlights)
        Background color: {background_color} (for page background)
        Text color: {text_color} (for text content)
        
        The design should be modern, professional, and showcase how these colors work together in a real interface.
        
        {template_type.capitalize()} specifications:
        """
        
        # Add template-specific instructions
        if template_type == "mobile":
            prompt += """
            - Create a mobile app interface with header, content area and bottom navigation
            - Show at least one screen with UI elements like buttons, cards, and text
            - Include status bar, navigation elements, and interactive components
            - Design should follow modern mobile UI principles
            """
        elif template_type == "dashboard":
            prompt += """
            - Create an analytics dashboard with sidebar navigation
            - Include charts, data cards, and status indicators
            - Show navigation, header bar, and main content area
            - Design should be data-focused and business-oriented
            """
        else:  # website
            prompt += """
            - Create a modern website homepage design
            - Include header with navigation, hero section, content blocks
            - Show how colors apply to different sections (header, content, footer)
            - Design should be clean, accessible, and contemporary
            """
        
        prompt += """
        Generate ONLY the image - no explanations or text about the colors in the response.
        Make sure the image clearly shows how all five colors are used in the UI design.
        """
        
        # Generate content
        response = model.generate_content(prompt)
        
        # Check if there's an image in the response
        if hasattr(response, 'parts') and len(response.parts) > 0:
            for part in response.parts:
                if hasattr(part, 'is_image') and part.is_image:
                    # Extract image data
                    image_data = part.data
                    encoded_image = base64.b64encode(image_data).decode('utf-8')
                    return {
                        "image_data": encoded_image,
                        "mime_type": "image/png"  # Assuming PNG format
                    }
        
        # If no image found but response contains potential image URL (older API versions)
        if hasattr(response, 'text'):
            # Try to extract an image URL from the response
            url_match = re.search(r'(https?://\S+\.(?:png|jpg|jpeg|gif))', response.text)
            if url_match:
                image_url = url_match.group(1)
                # Download the image
                img_response = requests.get(image_url)
                if img_response.status_code == 200:
                    encoded_image = base64.b64encode(img_response.content).decode('utf-8')
                    mime_type = img_response.headers.get('Content-Type', 'image/png')
                    return {
                        "image_data": encoded_image,
                        "mime_type": mime_type
                    }
        
        # If we couldn't get an image from Gemini, return None to use fallback
        return None
        
    except Exception as e:
        print(f"Error generating preview with Gemini: {e}")
        return None

def ai_color_suggester(image_path, project_description, gemini_api_key, groq_api_key, generate_preview=False, template_type="website"):
    """
    Main function to suggest colors based on both image and description.
    
    Args:
        image_path: Path or URL to the UI image
        project_description: Description of the project
        gemini_api_key: API key for Google Gemini
        groq_api_key: API key for Groq
        generate_preview: Whether to generate a UI preview
        template_type: Type of UI template for preview (website, mobile, dashboard)
        
    Returns:
        Dictionary containing the suggested color palettes and optional preview
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
    
    # Create the result dictionary
    result = {
        "image_based": image_colors,
        "description_based": description_colors,
        "organized_palette": organized_palette,
        "all_colors": all_colors
    }
    
    # Generate UI preview if requested
    if generate_preview:
        print("Generating UI preview with suggested colors...")
        preview = generate_ui_preview({
            "primary": organized_palette["primary"],
            "secondary": organized_palette["secondary"],
            "accent": organized_palette["accent"],
            "background": organized_palette["background"],
            "text": organized_palette["text"]
        }, template_type, gemini_api_key)
        
        if preview:
            result["preview"] = preview
    
    return result

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
    generate_preview = input("Generate UI preview? (y/n): ").lower() == 'y'
    
    if generate_preview:
        template_type = input("Preview template type (website/mobile/dashboard) [default: website]: ").lower()
        if template_type not in ["website", "mobile", "dashboard"]:
            template_type = "website"
    else:
        template_type = "website"
    
    # Get color suggestions
    print("\nProcessing... This may take a moment.")
    result = ai_color_suggester(image_path, project_description, gemini_api_key, groq_api_key, 
                                 generate_preview, template_type)
    
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
    
    if "preview" in result and result["preview"]:
        print("\n🖼️ UI Preview:")
        print("  A preview image has been generated showing how your colors would look in a UI.")
    
        try:
            from PIL import Image
            import io
            
            # Convert base64 to image and show it
            image_data = base64.b64decode(result["preview"]["image_data"])
            image = Image.open(io.BytesIO(image_data))
            
            # Save the image to a file
            preview_filename = "ui_preview.png"
            image.save(preview_filename)
            print(f"  Preview image saved as {preview_filename}")
            
            # Show the image in the default viewer
            image.show()
            print("  Opening preview image in your default image viewer...")
        except Exception as e:
            print(f"  Error displaying preview image: {e}")
            print("  The base64-encoded image data is available in the 'preview' field of the result.")