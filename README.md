# TechConf Registration Website

## Project Overview

The TechConf website allows attendees to register for an upcoming conference. Administrators can also view the list of attendees and notify all attendees via a personalized email message.

The application is currently working but the following pain points have triggered the need for migration to Azure:

- The web application is not scalable to handle user load at peak
- When the admin sends out notifications, it's currently taking a long time because it's looping through all attendees, resulting in some HTTP timeout exceptions
- The current architecture is not cost-effective

In this project, you are tasked to do the following:

- Migrate and deploy the pre-existing web app to an Azure App Service
- Migrate a PostgreSQL database backup to an Azure Postgres database instance
- Refactor the notification logic to an Azure Function via a service bus queue message

## Dependencies

You will need to install the following locally:

- [Postgres](https://www.postgresql.org/download/)
- [Visual Studio Code](https://code.visualstudio.com/download)
- [Azure Function tools V3](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local?tabs=windows%2Ccsharp%2Cbash#install-the-azure-functions-core-tools)
- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest)
- [Azure Tools for Visual Studio Code](https://marketplace.visualstudio.com/items?itemName=ms-vscode.vscode-node-azure-pack)

## Project Instructions

### Part 1: Create Azure Resources and Deploy Web App

1. Create a Resource group
2. Create an Azure Postgres Database single server
   - Add a new database `techconfdb`
   - Allow all IPs to connect to database server
   - Restore the database with the backup located in the data folder
3. Create a Service Bus resource with a `notificationqueue` that will be used to communicate between the web and the function
   - Open the web folder and update the following in the `config.py` file
     - `POSTGRES_URL`
     - `POSTGRES_USER`
     - `POSTGRES_PW`
     - `POSTGRES_DB`
     - `SERVICE_BUS_CONNECTION_STRING`
4. Create App Service plan
5. Create a storage account
6. Deploy the web app

### Part 2: Create and Publish Azure Function

1. Create an Azure Function in the `function` folder that is triggered by the service bus queue created in Part 1.

   **Note**: Skeleton code has been provided in the **README** file located in the `function` folder. You will need to copy/paste this code into the `__init.py__` file in the `function` folder.

   - The Azure Function should do the following:
     - Process the message which is the `notification_id`
     - Query the database using `psycopg2` library for the given notification to retrieve the subject and message
     - Query the database to retrieve a list of attendees (**email** and **first name**)
     - Loop through each attendee and send a personalized subject message
     - After the notification, update the notification status with the total number of attendees notified

2. Publish the Azure Function

### Part 3: Refactor `routes.py`

1. Refactor the post logic in `web/app/routes.py -> notification()` using servicebus `queue_client`:
   - The notification method on POST should save the notification object and queue the notification id for the function to pick it up
2. Re-deploy the web app to publish changes

## Monthly Cost Analysis

Complete a month cost
 analysis of each Azure resource to give an estimate total cost using the table below:

| Sr no | Name of Resources             | Pricing Tier            | Monthly Cost      | Why this resources is used?                                            |
| ----- | ----------------------------- | ----------------------- | ----------------- | ---------------------------------------------------------------------- |
| 1.    | Azure App Service (Web App)   | Free F1                 | Rs 0              | It hosts the website. Which handle the attendee registration.          |
| 2.    | App Service Plan              | Free F1                 | Rs 0              | It provides compute resources to web app to host website online.       |
| 3.    | Azure Function App            | Y1                      | Rs 0 - Rs 150     | It handles the notification task. To send notification asynchronously. |
| 4.    | Azure Database for PostgreSQL | Burstable (1-20 vCores) | Rs 2000 - Rs 2500 | Its attendee, conferences and notification data securely.              |
| 6.    | Azure Service Bus             | Basic tier              | Rs 0 - Rs 80      | It handles message queuing between the web app and azure function app  |
| 7.    | Azure Storage Account         | Standard                | Rs 80- Rs 120     | It requires for azure function to store logs etc.                      |

## Architecture Explanation

This is a placeholder section where you can provide an explanation and reasoning for your architecture selection for both the Azure Web App and Azure Function.

- Azure Web App

The main TechConf web application is hosted on Azure App Service. Azure Web App was chosen because it provides a fully managed platform for deploying web applications without managing infrastructure. It offers easy scalability, built-in monitoring, and high availability, making it suitable for handling varying user traffic during conference registrations and administrative operations.

- Azure Function

The notification processing logic was refactored into an Azure Function to improve performance and scalability. Previously, sending notifications synchronously caused long response times and HTTP timeouts. By using an Azure Function with a Service Bus trigger, notifications are processed asynchronously, allowing the web application to respond immediately while the background function handles email delivery efficiently.

- Azure Service Bus

Azure Service Bus acts as a messaging layer between the web application and the Azure Function. When an administrator submits a notification, the web app places a message containing the notification ID into a Service Bus queue. This decouples the web application from the notification processing logic, improves reliability, and ensures messages are processed even during peak load.

- Azure Database for PostgreSQL

Azure Database for PostgreSQL is used as the primary data store for the application. It stores attendee registrations, conference details, and notification data. Using a managed database service reduces operational overhead while providing scalability, backups, and security.

- Azure Storage Account

Azure Storage Account is used by the Azure Function App for runtime storage, logging, and state management. It is a required dependency for running Azure Functions reliably.
