from datetime import datetime, timezone
from firebase_admin import firestore
# from serializer_utils import serialize_parameter_data


def trigger_push_notification(notification_title, notification_text, user_refs, sender, notification_image_url=None, scheduled_time=None, notification_sound=None):
    try:
        if not notification_title or not notification_text:
            print("Notification title or text is empty.")
            return
        # Serialize parameter data if available
        # serialized_parameter_data = serialize_parameter_data(parameter_data)

        # Construct push notification data
        push_notification_data = {
            'notification_title': notification_title,
            'notification_text': notification_text,
            'user_refs': ",".join(user_refs),
            'initial_page_name': 'Tripspage',
            # 'parameter_data': serialized_parameter_data,
            'sender': sender,  # Replace with actual sender reference
            'timestamp': datetime.now(timezone.utc),
        }

        # Add optional fields if available
        if notification_image_url:
            push_notification_data['notification_image_url'] = notification_image_url
        if scheduled_time:
            push_notification_data['scheduled_time'] = scheduled_time
        if notification_sound:
            push_notification_data['notification_sound'] = notification_sound

        # Save push notification data to Firestore
        db = firestore.client()
        db.collection('ff_user_push_notifications').document().set(push_notification_data)

        print("Push notification sent successfully!")

    except Exception as e:
        print(f"Error sending push notification: {e}")


from firebase_admin import firestore

# Example function call with test data