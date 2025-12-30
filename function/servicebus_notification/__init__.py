import logging
import azure.functions as func
import psycopg2
import os
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def main(msg: func.ServiceBusMessage):

    # Read message from Service Bus
    notification_id = int(msg.get_body().decode('utf-8').strip())
    logging.info('Python ServiceBus queue trigger processed message: %s', notification_id)

    # Connect to PostgreSQL
    conn = psycopg2.connect(
        host=os.environ["DB_HOST"],
        database=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        port=os.environ.get("DB_PORT", 5432)
    )

    cursor = conn.cursor()

    try:
        # Get notification subject and message
        cursor.execute(
            "SELECT subject, message FROM notification WHERE id = %s",
            (notification_id,)
        )
        notification = cursor.fetchone()

        if not notification:
            logging.error(f"No notification found with ID {notification_id}")
            return

        subject, message = notification

        # Get all attendees
        cursor.execute(
            "SELECT email, first_name FROM attendee"
        )
        attendees = cursor.fetchall()

        # Send emails
        sendgrid_client = SendGridAPIClient(os.environ["SENDGRID_API_KEY"])
        from_email = os.environ["FROM_EMAIL"]

        notified_count = 0

        for email, first_name in attendees:
            personalized_subject = f"{first_name}, {subject}"

            mail = Mail(
                from_email=from_email,
                to_emails=email,
                subject=personalized_subject,
                plain_text_content=message
            )

            try:
                response = sendgrid_client.send(mail)
                if response.status_code in [200, 202]:
                    notified_count += 1
                else:
                    logging.error(f"Failed to send email to {email}: {response.status_code}")
            except Exception as e:
                logging.error(f"Error sending email to {email}: {e}")

        # Update notification status (matches DB structure)
        completed_date = datetime.utcnow()
        status_text = f"Notified {notified_count} attendees"

        cursor.execute(
            """
            UPDATE notification
            SET status = %s,
                completed_date = %s
            WHERE id = %s
            """,
            (status_text, completed_date, notification_id)
        )

        conn.commit()
        logging.info(f"Notification {notification_id} updated successfully")

    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)

    finally:
        cursor.close()
        conn.close()
