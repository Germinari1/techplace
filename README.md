# TechPlace
TechPlace is an "auction-like" marketplace where programmers can sell software products and services from different categories (web development, AI, game development, etc). It is a project implemented as a Django web application.

## Quick Start and Requirements
You can follow these steps to start the application:
1. Clone the repository
  ```txt
  git clone https://github.com/Germinari1/techplace.git
  ```

2. If you want to (even though this is optional), you can set up a virtual environment:
```txt
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```
3. Install dependencies.
```txt
pip install -r requirements.txt
```
4. Set up the database:
```txt
python manage.py migrate
```
5. Create a superuser:
```txt
python manage.py createsuperuser
```
6. Run the development server:
```txt
python manage.py runserver
```
7. Access the application. Open your web browser and navigate to http://localhost:8000

## Features
Some features of TechPlace are:
- Create offerings with custom titles, descriptions, supporting links, and images/videos for demos.
- Bid on offerings posted by other users, and close your own when you feel happy with the offered price.
- Edit your user profile with descriptions and contact information, and view the profile page of other users.
- View your dashboard and keep track of offerings you posted, sold, won, and closed.
- Navigate through different categories of offerings.
