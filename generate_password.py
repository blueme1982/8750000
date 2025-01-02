import streamlit_authenticator as stauth

hashed_passwords = stauth.Hasher(['admin123', 'admin123']).generate()
print(f"Admin password hash: {hashed_passwords[0]}")
print(f"User1 password hash: {hashed_passwords[1]}") 