# VacationTracker Web Application

## Introduction

This is a Web application for managing the vacation dates of employees as a 
self-service. The backend uses the Flask micro framework for Python based on 
Werkzeug and Jinja 2. The frontend uses the Bootstrap 4 CSS and JavaScript
framework and is based on the SB Admin Bootstrap admin template. For the 
database SQLite3 is used.

  * Flask: http://flask.pocoo.org/
  * Bootstrap: https://getbootstrap.com/
  * SB Admin: https://startbootstrap.com/template-overviews/sb-admin

## Requirements

This Web application requires the following software:

  * python3: Python interpreter version 3
  * python3-pip: Python module installer PIP
  * python3-venv: Python virtual environment
  * sqlite3: SQLite version 3 for the database export

Install this software as usual. Here is an example of installing it on Ubuntu.

  sudo apt-get install python3 python3-pip python3-venv sqlite3

## Setup

Setup the project by executing bin/setup from the project directory.

  cd VacationTracker
  bin/setup

This will be required only once to create the virtual environment, install
Flask and its dependencies into the virtual environment, and to initialize the
database. 

ATTENTION: If the database already exists, it will be deleted!

## Project Structure

The project follows and extends the folder structure as expected by Flask.

  VacationTracker
  |-- VacationTracker.py     # Main application file.
  |-- VacationTracker.wsgi   # WSGI wrapper for Apache.
  |-- example.host.conf      # Example Apache virtual host configuration.
  |-- database.db            # Application database.
  |-- bin/                   # Custom binaries.
      |-- cleanup              # Cleanup the project.
      |-- debug_env            # Change to debugging environment.
      |-- prod_env             # Change to production environment.
      |-- setup                # Setup the project.
      |-- vacations            # Export vacation dates from the database.
  |-- templates/             # HTML page templates supporting Jinja2.
      |-- login.html           # Login page.
      |-- base.html            # Base template for all pages except login.html.
      |-- vacation.html        # Vacation page extending base.html.
  |-- static/                # Static page content.
      |-- css/                 # Custom CSS files.
      |-- js/                  # Custom JavaScript files.
      |-- images/              # Images and icons.
      |-- vendor/              # CSS and JavaScript frameworks.
  |-- venv/                  # Virtual Python environment.
  |-- .idea/                 # PyCharm IDE project files.

## Development and Debugging

The application can be developed using just a text editor, or using the PyCharm
IDE or any other Python IDE supporting Flask. 

Flask comes with a built-in Web server that can be run in production (default) 
or development mode supporting application debugging. The application can be
run from the command line in debugging mode as follows.

  cd VacationTracker
  . bin/debug_env
  run

If to run in production mode, execute following commands instead.

  cd VacationTracker
  . bin/prod_env
  run

## Apache Deployment

Flask is not a native Web language. To get the Python code running on Apache,
Apache needs to use a WSGI (Web Server Gateway Interface) file to access the 
Flask application.

Install and enable the Apache server module mod_wsgi:

  sudo apt-get install libapache2-mod-wsgi-py3
  sudo a2enmod wsgi

Copy the application into the www folder:

  sudo cp -r VacationTracker /var/www/
  sudo chown -R www-data:www-data /var/www/VacationTracker

Setup the virtual host. File example.host.conf demonstates how to setup an
Apache virtual host to work with the application. The virtual host configuration
for host example.host would be installed as follows:

  cd VacationTracker
  sudo cp example.host.conf /etc/apache2/sites-available/
  sudo mkdir -p /var/www/example.host/logs
  sudo chown -R www-data:www-data /var/www/example.host
  sudo a2ensite example.host.conf

Restart Apache to apply all changes:

  sudo systemctl restart apache2

## Vacations Export

The current, or next if there is no current, vacation date of each employees
in the database can be dumped to stdout in format email;enddate;startdate as
follows.

  cd VacationTracker
  bin/vacations  
