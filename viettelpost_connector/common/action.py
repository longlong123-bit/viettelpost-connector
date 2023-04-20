from typing import Dict, Any


class Action:

    @staticmethod
    def display_notification(title: str, message: str, notification_type: str = 'success') -> Dict[str, Any]:
        action = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': f'{title}',
                'type': f'{notification_type}',
                'message': f'{message}',
                'sticky': False,
                'next': {
                    'type': 'ir.actions.act_window_close'
                }
            }
        }
        return action
