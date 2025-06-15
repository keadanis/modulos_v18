# Odoo Server Management

Server administrator in Odoo

Run custom commands in the server
Install a ftp on the server with just one click. It also allows you to configure the users and the access folder
We have many servers sometimes it becomes chaos, this app allowed us to restart, upload files, know the resources, execute commands and install an ftp server with a single click.

By having this integrated with Odoo, we can use it in other apps and automate processes, copies, backups, among others.
You can install an ftp on the server with just one click. It also allows you to configure the users and the access folder
To configure the ssh key, you can choose username or password or upload the key file

Setup
=====

Go to TECHNICIAN, in INCOMING MAIL SERVERS, create and configure the following:

SERVER AND CONNECTION

    SERVER NAME: service host

    USER NAME: email or username

    PORT: Connection port

    PASSWORD: password

    SSL / TSL: Check if required

ADVANCED TAB

    It is recommended to leave the default values

    KEEP ORIGINAL: Select to keep the mail in the inbox (it is recommended not to mark it)

    After configuring save and click on the Test and confirm button

    ** Now is a good time to go to the scheduled task and modify the execution time if necessary, by default it is every 5 minutes **


Functioning
=====

The function is executed, reads the emails in the inbox and validates the information

When it finds an attached XML file, it validates the company's VAT number

    If the company's NIF matches, validate the supplier's NIF
        If the supplier's NIF exists
            Upload the information to a supplier invoice, leaving it in a draft state for later validation

        If the supplier's NIF does not exist
            Create the supplier with the XML information and upload the information in a supplier invoice, leaving it in a draft state for later validation

        All the messages referring to each supplier invoice are added in the messages section (Ex: The supplier does not exist, it has been created automatically - etc - etc)
        Attach the files (PDF, XML receipt and XML response)
        ** If you only find the response XML, attach this file to the corresponding invoice and delete the email from the inbox **
        Delete the email from the account if this option was selected in the incoming email settings (RECOMMENDED)

    If the company ID does not match
        Ignore mail and keep it in the inbox

    If it can't find valid files to process, ignore the email by leaving it in the inbox.
    When the supplier invoice is created with this process, the fields partner, supplier reference, voucher type, payment methods, currency, supplier xml and invoice date will be type fields (read only).
    If the numeric key already exists when validating the XML, the process is ignored and the email is removed from the inbox.
    When validating the XML invoice, if the numeric key already exists, the process is ignored and the mail is removed from the inbox.
    When validating the response XML if the "Has ACK" box is already checked, the process is ignored and the email is removed from the inbox.

Recommendations
===========
*** Important: Go to Technician - Pseudonyms and delete SUPPLIER INVOICES ***

You can create a single email to receive from several companies; each company validates the XML, takes the one that corresponds to it and executes the entire previous process.

Create an exclusive email for this service and schedule the resending from the email accounts that receive the FE
Mail must be maintained to eliminate junk mail


Bug Tracker
===========

Bugs are tracked on Issues section.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed
feedback.

Do not contact contributors directly about support or help with technical issues.


Contributors
============

* DMC
* KAV

You are welcome to contribute.
