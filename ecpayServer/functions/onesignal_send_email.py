import onesignal
from onesignal.api import default_api
from onesignal.model.notification import Notification
import os

def send_notification(passengerCost, name, email, orderId, startTime, finishTime, driverName, startPlace, endPlace, numOfPassengers):
    configuration = onesignal.Configuration(
        app_key = os.environ.get('APP_KEY'),
        user_key = os.environ.get("USER_KEY")
    )

    payload = {
        "app_id": "f24dc978-8e85-4812-b040-60743e706da9",
        "include_email_tokens": [email],
        "target_channel": "email",
        # "contents": {
        #     "en": f"Hello, {first_name}! Your transaction of ${amount} has been successfully processed."
        # },
        "template_id": "3a7bb050-b37c-4aaf-9ca3-262790b96676",
        "custom_data": {
            "first_name": name,
            "total_price": passengerCost,
            "order_id": orderId,
            "start_time": startTime.strftime("%Y/%m/%d %H:%M"),
            "end_time": finishTime.strftime("%Y/%m/%d %H:%M"),
            "driver_name": driverName,
            "start_place": startPlace,
            "end_place": endPlace,
            "passengers_num": numOfPassengers

        }
    }

    with onesignal.ApiClient(configuration) as api_client:
        api_instance = default_api.DefaultApi(api_client)
        notification = Notification(payload)

        try: 
            api_response = api_instance.create_notification(notification)
            print("Email sent successfully!")
        except onesignal.ApiException as e:
            print('Exception when calling DefaultApi => create_notification: %s\n' % e)



def send_refund_notification(name, email, refund_price, orderId, startTime, finishTime, driverName, startPlace, endPlace, numOfPassengers):
    configuration = onesignal.Configuration(
        app_key = os.environ.get('APP_KEY'),
        user_key = os.environ.get("USER_KEY")
    )

    payload = {
        "app_id": "f24dc978-8e85-4812-b040-60743e706da9",
        "include_email_tokens": [email],
        "target_channel": "email",
        "template_id": "4ff2f4c2-523c-49dc-8faa-5461b5caa021",
        "custom_data": {
            "first_name": name,
            "refund_price": refund_price,
            "order_id": orderId,
            "start_time": startTime.strftime("%Y/%m/%d %H:%M"),
            "end_time": finishTime.strftime("%Y/%m/%d %H:%M"),
            "driver_name": driverName,
            "start_place": startPlace,
            "end_place": endPlace,
            "passengers_num": numOfPassengers
        }
    }

    with onesignal.ApiClient(configuration) as api_client:
        api_instance = default_api.DefaultApi(api_client)
        notification = Notification(payload)

        try: 
            api_response = api_instance.create_notification(notification)
            print("Refund email sent successfully!")
        except onesignal.ApiException as e:
            print('Exception when calling DefaultApi => create_notification: %s\n' % e)
