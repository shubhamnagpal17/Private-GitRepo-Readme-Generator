from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_readme_material(repo_name, repo_url, repo_description="", language="", topics="", stars=0, license_name="", files_list=""):
    
    '''
    Function to call gemini api to create readme file using metadata
    '''
    
    # Gemini Prompt
    prompt = f'''You are a professional software documentation assistant. 
    Generate a **well-structured, attractive README.md** for a GitHub repository.

    Guidelines:
    1. Use **emojis in headings only** instead of plain text (no ## plain headings). Example: 🤖 Project Title, 💡 Description, ✨ Features, 🛠️ Installation Guide, 💻 Tech Stack, 📂 Project Structure, ⚖️ License.
    2. Sprinkle **relevant emojis in the content** to make it visually appealing.
    3. Keep content **concise, professional, and developer-friendly**. Minimal text is preferred.
    4. Do **not include badges, shields, or unnecessary links** at the top.
    5. Use **code blocks** for installation, setup, or usage instructions.
    6. Output should be **ready to save as README.md**.

    Sections to include:
    - 🤖 Project Title
    - 💡 Description
    - ✨ Features
    - 🛠️ Installation Guide
    - 💻 Tech Stack
    - 📂 Project Structure
    - ⚖️ License

    Repository Details:
    - Repository Name: {repo_name}
    - Repository URL: {repo_url}
    - Repository Description: {repo_description}
    - Primary Language: {language}
    - Topics: {topics}
    - Stars: {stars}
    - License: {license_name}
    - Files: {files_list}

'''


    response = client.models.generate_content(
      model='gemini-2.5-flash',
        contents=prompt,
    )

    return response.text

