import schedule
import time

from automation import auto_pay



# run once at start

auto_pay()



# every day

schedule.every().day.at("09:00").do(auto_pay)
schedule.every().day.at("17:00").do(auto_pay)



while True:

    schedule.run_pending()

    time.sleep(60)
