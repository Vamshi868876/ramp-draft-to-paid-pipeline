import schedule
import time

from automation import auto_pay



# run once at start

auto_pay()



# every day

schedule.every(1).minutes.do(auto_pay)



while True:

    schedule.run_pending()

    time.sleep(60)
