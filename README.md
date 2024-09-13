
# Project Setup Guide
uvicorn main:app --host localhost --port 3000
Follow the steps below to set up and run this project on your macOS machine:

### Prerequisites

Make sure you have the following installed on your machine:
- **npm** (Node Package Manager)
- **Python 3**

#### Step 1: Install npm

If you don't have npm installed, follow these steps to install it:
1. Open the Terminal.
2. Install Homebrew (if you don’t have it already) by running:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
3. Once Homebrew is installed, use it to install npm:
   ```bash
   brew install npm
   ```

#### Step 2: Install Python

You also need Python 3. If you don’t have it installed, download and install Python from [here](https://www.python.org/downloads/).

### Project Setup

Once npm and Python are installed, follow these steps:

1. **Navigate to the project directory**  
   Open the Terminal and change into your working directory:
   ```bash
   cd /path/to/your/project
   ```

2. **Navigate to the `suno-api` directory**  
   ```bash
   cd suno-api
   ```

3. **Install npm dependencies**  
   Run the following command to install the necessary Node.js dependencies:
   ```bash
   npm install
   ```

4. **Run the development server**  
   After installing the dependencies, run the development server with:
   ```bash
   npm run dev
   ```

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

4. **Check if you are in the correct directory**  
   Ensure that you are in the project’s working directory before running the commands.
npm install concurrently --save-dev
