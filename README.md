# Daily Sales

## Description
Daily Sales is a Python project designed to manage and record daily sales transactions.

## Prerequisite
- Ensure you have Python installed on your system. You can download it from [here](https://www.python.org/downloads/).
- Docker: To install Docker, follow the instructions for your specific operating system:
  - [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
  - [Docker Desktop for Linux](https://docs.docker.com/desktop/install/linux-install/)

## Installation
1. Clone the repository using Git:
   ```
   git clone https://github.com/ramprasath25/daily-sales.git
   ```
2. Navigate to the project directory:
   ```
   cd daily-sales
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Start PostgreSQL database using Docker Compose:
   ```
   docker-compose up -d postgres
   ```
5. To populate sample data in the database, follow these steps:
   - Access the PostgreSQL container shell:
     ```
     docker exec -it postgres_db bash
     ```
   - Log in to the database:
     ```
     psql -U bruvvers_admin -d bruvvers
     ```
   - Insert sample products data:
     ```
     insert into products (name) values ('coffee'), ('tea');
     ```

## Usage
1. Run the Python script to start the application:
   ```
   python3 main.py
   ```
2. Visit the following URL in your web browser to access the application:
   ```
   http://127.0.0.1:5000/
   ```
