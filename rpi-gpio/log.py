from time import sleep
from sensor import read
import config


delay = config.delay
DT_LOG_FORMAT = config.log_date_format

while True:
    sample = read()
    print(f"[{sample['timestamp']}] "
          f"{sample['temperature']} "
          f"{sample['humidity']} "
          f"{sample['pressure']}")
    
    with open("/data-log/hpt.log", "+a") as f:
        f.write(f"[{sample['timestamp']}] "
                f"{sample['temperature']} "
                f"{sample['humidity']} "
                f"{sample['pressure']}\n")

    sleep(delay)
