Advertising CRM
---------------

https://github.com/rzurawicki/advert-crm

## Purpose

This project is a custom CRM (Customer Relationship Manager) for the any publishing company.

This site allows advertisers to create accounts, update their contact information, and upload advertisement media. Business staff can also create accounts, assign advertisers to personnel, and manage contracts for each issue.


## What's included
    mysite - the Django web project. This manages the whole website including user authentication
    contracts - this custom Django webapp manages the Advertisers and contracts for the business

## Functionality
  * Advertisers can create their own accounts
  * Users are verified via confirmation email
  * Advertisers can order and upload advertisements
  * Staff must approve users that sign up
  * Staff can create ads and profile for current clients.
  * Emails are sent to clients when payment is received. the site will email to make sure that advertisement media has been uploaded
  * All sent emails are logged
  * All extra communications are logged and tied to an account.
  * Staff permissions allow staff members to modifiy only contracts they "own"

## How to Setup Backend
  1. Install python, pip, and the packages specified by requirements.txt. (Follow the direcitons below)
        
  2. Run server: `python manage.py runserver`
     This script setups up a Django web server. You must fist syncdb and collectstatic as specified below.


## Known Bugs
  * None :)

Getting Started:

1. Install the Python environment (uses python 2.7)
```
pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```
2. Setup the database and static files.
```
python manage.py syncdb
python manage.py collectstatic
```
3. Run Server
```
python manage.py runserver
```
