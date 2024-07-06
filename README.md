# Flask Backend App

This README will guide you through the setup and running of the project.

## Description

This is a simple backend application built with Flask, using a Machine Learning model to recommend movies based on the selected movie informations.

## Prerequisites

Ensure you have the following software installed on your machine:

- **Python 3.8+**: The programming language used for the project.
- **pip**: The Python package installer, usually comes with Python but you can install it manually if needed.
- **virtualenv** (recommended): A tool to create isolated Python environments.

(Note: Check the last section of this document for basic installation instructions)

## Installation

Follow these steps to get the project running on your local machine.

### 1. Clone the repository

```bash
git clone github.com/LuaGeo/ml_cine-creuse-backend
cd ml_cine-creuse-backend
```

### 2. Create and activate a virtual environment

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install the dependencies

The requirements.txt file lists all the Python packages that your project depends on.

```bash
pip install -r requirements.txt
```

### 4. Configure the Environment Variables

This project uses environment variables for configuration. You need to create a .env file in the root directory of your project. A sample .env.sample file is provided for reference. Copy the contents of .env.sample to your .env file and replace the placeholder values with your actual configuration values.

```
MONGO_URI=mongodb+srv://your-server
SECRET_KEY=your_secret_key
TMDB_API_KEY=your_tmdb_api_key
```

#### MongoDB and TMDB Configuration

To use all the features of this project, you need to create accounts and get the necessary keys:

MongoDB: Create an account at [MongoDB Atlas](https://www.mongodb.com/products/platform/atlas-database) and create a new cluster. Replace your-server with your actual MongoDB connection string.
TMDB: Create an account at [The Movie Database (TMDB)](https://developer.themoviedb.org/reference/intro/getting-started), go to your account settings to get your API key, and replace your_tmdb_api_key with your actual TMDB API key.

### 5. Run the application

There are two ways to run the application: for development and for production.

#### Development

Use the Flask development server:

```bash
flask run
```

#### Production

Use gunicorn to run the application. This is more suitable for production environments:

```bash
gunicorn app:app
```

### OBS: Front-End Integration

This backend is designed to be used with the [My Frontend App](https://github.com/LuaGeo/ml_cine-creuse-frontend) which provides the user interface for this project. You will find all informations you need in its README section there.

> ### Basic installation instructions:
>
> ### Windows:
>
> #### Install Python:
>
> - Download the latest version of Python from the [official Python website](https://www.python.org/downloads/).
> - Run the installer and make sure to check the box "Add Python to PATH".
>
> #### Verify Installation:
>
> ```bash
> python --version
> ```
>
> #### Install pip:
>
> - pip is included by default with Python 3.4+.
>
> #### Verify pip Installation:
>
> ```bash
> pip --version
> ```
>
> ### macOS:
>
> #### Install Homebrew (if not already installed):
>
> ```bash
> /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
> ```
>
> #### Install Python:
>
> ```bash
> brew install python
> ```
>
> #### Verify Installation:
>
> ```bash
> python3 --version
> ```
>
> #### Verify pip Installation:
>
> ```bash
> pip3 --version
> ```
