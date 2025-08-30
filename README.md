# Django Digital Signature Application

This is a web application built with Django that allows users to upload, digitally sign, and verify documents using RSA cryptographic algorithm.<br> Live Site: https://soumik2024.pythonanywhere.com/

## Features
- Secure user registration and login
- Automatic RSA key-pair generation for new users
- File upload and management for authenticated users
- Digital signing of files using the user's encrypted private key
- Public-facing page for signature verification

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Soumik8114/digital_signature.git
    cd digital_signature
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    venv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Create a `.env` file** in the root directory and add your `SECRET_KEY`:
    ```
    SECRET_KEY='generate-a-new-secret-key-here'
    DEBUG=True
    ```
5.  **Run database migrations:**
    ```bash
    python manage.py migrate
    ```
6.  **Create a superuser:**
    ```bash
    python manage.py createsuperuser
    ```
    Provide admin passwords and username

7.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```
