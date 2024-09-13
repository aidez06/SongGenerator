
# Project Setup Guide
Follow the steps below to set up and run this project on your macOS machine:

### Prerequisites

Make sure you have the following installed on your machine:
- **Python 3**

#### Step 2: Install Python

You also need Python 3. If you don’t have it installed, download and install Python from [here](https://www.python.org/downloads/).

### Python Setup

Now, let's set up Python for the project:

1. **Create a virtual environment**  
   In your project directory, create a virtual environment using Python 3:
   ```bash
   python3 -m venv venv
   ```

2. **Activate the virtual environment**  
   Activate the virtual environment with the following command:
   ```bash
   source venv/bin/activate
   ```

3. **Install Python dependencies**  
   Once the virtual environment is activated, install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

5. **Run The Flask Server**  
   ```bash
   uvicorn main:app --host localhost --port 3000
   ```
6. **Run the program**  
   ```bash
   app.py
   ```
