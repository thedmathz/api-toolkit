# API Toolkit

A modular collection of lightweight APIs designed to simplify and accelerate web application development.


### To Do
- SMS
- Payment Gateway Integration with Webhook
- Email Sending
- Identity Verification
- OCR


### How to Run in Windows 10/11?
- In project files, rename the file from **.env.example** to **.env**
- Open terminal then navigate to project path
    ```bash
    cd <project_path>
    ```
- Install virtual environment (if not yet installed)
    ```bash
    python -m venv .venv
    ```
- Activate virtual environment
    ```bash
    .venv\Scripts\activate
    ```
- Update pip version
    ```bash
    python -m pip install --upgrade pip
    ```
- Install dependencies
    ```bash
    pip install -r requirements.txt
    ```
- Run the app
    ```bash
    uvicorn application.main:app --reload --host 0.0.0.0
    ```
- You can look for the APIs in the browser with URL **<your_ip_address>:8000/docs**