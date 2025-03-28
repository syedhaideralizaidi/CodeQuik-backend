# Code Quick

Code Quick is a Django-based web application that provides an instant coding environment. It allows users to quickly create, edit, and execute code in a collaborative and efficient manner.

## Features

- **Instant Code Execution**: Run code snippets in multiple programming languages.
- **Collaboration**: Share and edit code with others in real-time.
- **User Authentication**: Secure user accounts with login and registration.
- **Database Support**: Store and retrieve code snippets for future use.
- **Syntax Highlighting**: Enhanced code readability with syntax highlighting.

## Installation

### Prerequisites

- Python 3.8+
- Django 4.0+
- Virtual environment (optional but recommended)

### Setup

```sh
# Clone the repository
git clone https://github.com/yourusername/code-quick.git
cd code-quick

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt

# Apply database migrations
python manage.py migrate

# Create a superuser (optional, for admin access)
python manage.py createsuperuser

# Run the development server
python manage.py runserver
```

Open the application in your browser:

[http://127.0.0.1:8000](http://127.0.0.1:8000)

## Usage

1. Sign up or log in to start creating and executing code snippets.
2. Share generated links to collaborate with others.
3. Save code snippets for later use.

## Configuration

- **Database**: Configure `DATABASES` in `settings.py`.
- **Allowed Hosts**: Update `ALLOWED_HOSTS` for production.
- **Static & Media Files**: Configure settings for serving static and media files.

## Deployment

To deploy Code Quick, follow these steps:

1. Set up a production database (PostgreSQL recommended).
2. Configure environment variables for `DEBUG=False`, `SECRET_KEY`, and `ALLOWED_HOSTS`.
3. Use Gunicorn and Nginx for production deployment.
4. Set up SSL using Let's Encrypt.

## Contributing

Pull requests are welcome! Please follow the contribution guidelines.

## License

MIT License

For questions and support, open an issue on GitHub.
