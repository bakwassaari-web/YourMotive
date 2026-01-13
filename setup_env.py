import os

secrets_dir = ".streamlit"
secrets_file = os.path.join(secrets_dir, "secrets.toml")
placeholder_content = 'GOOGLE_API_KEY = "PASTE_YOUR_KEY_HERE"'

def setup_secrets():
    if not os.path.exists(secrets_dir):
        os.makedirs(secrets_dir)
        print(f"Created directory: {secrets_dir}")
    
    if not os.path.exists(secrets_file):
        with open(secrets_file, "w") as f:
            f.write(placeholder_content)
        print(f"Created secrets file: {secrets_file}")
    else:
        print(f"Secrets file already exists: {secrets_file}")

if __name__ == "__main__":
    setup_secrets()
