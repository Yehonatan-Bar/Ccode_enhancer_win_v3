from datetime import datetime
import json
from typing import List, Dict
import logging
from logs.setup_logging import setup_logging

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)


    def process_network_logs(self, driver) -> List[Dict]:
        """Process browser network logs."""
        network_logs = []
        try:
            logs = driver.get_log('performance')
            for entry in logs:
                try:
                    log = json.loads(entry['message'])['message']
                    if 'Network.requestWillBeSent' in log['method']:
                        request = log['params']['request']
                        network_logs.append({
                            'url': request['url'],
                            'method': request['method'],
                            'timestamp': datetime.fromtimestamp(
                                log['params']['timestamp']
                            ).strftime('%Y-%m-%d %H:%M:%S.%f')
                        })
                except (KeyError, json.JSONDecodeError) as e:
                    self.logger.warning(f"Error processing log entry: {str(e)}")
            return network_logs
        except Exception as e:
            self.logger.error(f"Failed to process network logs: {str(e)}")
            return []
