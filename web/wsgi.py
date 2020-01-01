import sys
sys.path.insert(0, '/home/pi/weather-report/web')

from server import app as application

if __name__ == "__main__":
    application.run()
