import email_handler
import init
import report.coingecko_trending
import report.dinosaur_footprints
import report.public_company_holdings
import report.dip_watcher
import report.moving_average
import report.stock_tracker
import sys
import money_alert_unit_tests.unit_test
import time
import traceback
import util

if '--dev' in sys.argv:
    init.logger.info('Development Mode')
    ####################################

    # Test your shit code here!!!

    ####################################

elif '--build' in sys.argv:
    init.logger.info('Building Report Data')
    moving_average_report = report.moving_average.MovingAverages()
    moving_average_report.build_report_data()

elif '--run-now' in sys.argv:
    init.logger.info('Running Reports Now!')
    gmail = email_handler.GMail()

    try:
        moving_average_report = report.moving_average.MovingAverages()
        trending_report = report.coingecko_trending.Trending()
        trending_report.email_trenders = True
        public_holdings = report.public_company_holdings.PublicCompanyHoldings()
        dinosaur_report = report.dinosaur_footprints.DinosaurFootprints()
        stock_tracker = report.stock_tracker.StockTracker()

        init.scheduler.enter(0, 1, moving_average_report.run)
        init.scheduler.enter(0, 1, trending_report.run)
        init.scheduler.enter(0, 1, dinosaur_report.run)
        init.scheduler.enter(0, 1, public_holdings.run)
        init.scheduler.enter(0, 1, stock_tracker.run)
        init.scheduler.run()

        gmail.build_and_send_gmail(init.config['emails'], '24 Hour Reports - Forced Run', None, True)
        stock_tracker.cleanup_charts()
        init.logger.info('Emails Sent')

    except Exception as e:
        crash_call_stack = str(e) + '<br/><br/>' + traceback.format_exc()
        gmail.add_email_content('Application Crash', crash_call_stack)
        gmail.build_and_send_gmail(init.config['emails'], 'Application Crash')
        init.logger.exception(f'Application Crash: {e}')
        quit()

elif '--daily' in sys.argv:
    gmail = email_handler.GMail()

    try:
        unit_test = money_alert_unit_tests.unit_test.UnitTest()
        unit_test.launch_unit_test()

        moving_average_report = report.moving_average.MovingAverages()
        trending_report = report.coingecko_trending.Trending()
        public_holdings = report.public_company_holdings.PublicCompanyHoldings()
        dinosaur_report = report.dinosaur_footprints.DinosaurFootprints()
        stock_tracker = report.stock_tracker.StockTracker()

        while True:
            run_time = util.get_report_run_time(init.config['report_settings']['run_time'])
            init.logger.info(f'Time Left: {run_time} seconds')

            init.scheduler.enter(run_time, 1, moving_average_report.run)
            init.scheduler.enter(run_time, 1, trending_report.run)
            init.scheduler.enter(run_time, 1, dinosaur_report.run)
            init.scheduler.enter(run_time, 1, public_holdings.run)
            init.scheduler.enter(run_time, 1, stock_tracker.run)
            init.scheduler.run()

            gmail.build_and_send_gmail(init.config['emails'], '24 Hour Reports', None, True)
            stock_tracker.cleanup_charts()
            init.logger.info('Emails Sent')

    except Exception as e:
        crash_call_stack = str(e) + '<br/><br/>' + traceback.format_exc()
        gmail.add_email_content('Application Crash', crash_call_stack)
        gmail.build_and_send_gmail(init.config['emails'], 'Application Crash')
        init.logger.exception(f'Application Crash: {e}')
        quit()

elif '--watchers' in sys.argv:
    gmail = email_handler.GMail()

    try:
        init.logger.info('Running supervisor reports')
        watcher = report.dip_watcher.DipWatcher()
        while True:
            watcher.run()
            time.sleep(60)

    except Exception as e:
        crash_call_stack = str(e) + '<br/><br/>' + traceback.format_exc()
        gmail.add_email_content('Application Crash', crash_call_stack)
        gmail.build_and_send_gmail(init.config['emails'], 'Application Crash')
        init.logger.exception(f'Application Crash: {e}')
        quit()

elif '--pull-named-wallets' in sys.argv:
    report.dinosaur_footprints.DinosaurFootprints().pull_named_wallets()
