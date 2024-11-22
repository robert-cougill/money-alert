import src.email.email_handler
import src.init
import src.report.trending
import src.report.dinosaur_footprints
import src.report.public_company_holdings
import src.report.dip_watcher
import src.report.moving_average
import src.report.stock_tracker
import src.report.metal_tracker
import sys
import src.unit_tests.unit_test
import time
import traceback
import src.utils.util


if '--dev' in sys.argv:
    src.init.logger.info('Development Mode')
    ####################################

    # Test your shit code here!!!


    ####################################

elif '--build' in sys.argv:
    src.init.logger.info('Building Report Data')
    moving_average_report = src.report.moving_average.MovingAverages()
    moving_average_report.build_report_data()

elif '--run-now' in sys.argv:
    src.init.logger.info('Running Reports Now!')
    email = src.email.email_handler.GMail()

    try:
        moving_average_report = src.report.moving_average.MovingAverages()
        trending_report = src.report.trending.Trending()
        trending_report.email_trenders = True
        public_holdings = src.report.public_company_holdings.PublicCompanyHoldings()
        dinosaur_report = src.report.dinosaur_footprints.DinosaurFootprints()
        metal_tracker = src.report.metal_tracker.MetalTracker()
        stock_tracker = src.report.stock_tracker.StockTracker()

        src.init.scheduler.enter(0, 1, moving_average_report.run)
        src.init.scheduler.enter(1, 1, trending_report.run)
        src.init.scheduler.enter(2, 1, dinosaur_report.run)
        src.init.scheduler.enter(3, 1, public_holdings.run)
        src.init.scheduler.enter(4, 1, metal_tracker.run)
        src.init.scheduler.enter(5, 1, stock_tracker.run)
        src.init.scheduler.run()

        email.send_email('24 Hour Reports - Forced Run')
        stock_tracker.cleanup_charts()
        src.init.logger.info('Scheduler - Complete')

    except Exception as e:
        email.send_error_email("Application Crash", str(e) + '<br/><br/>' + traceback.format_exc())
        src.init.logger.exception(f'Application Crash: {e}')
        quit()

elif '--daily' in sys.argv:
    email = src.email.email_handler.GMail()

    try:
        unit_test = src.unit_tests.unit_test.UnitTest()
        unit_test.launch_unit_test()

        moving_average_report = src.report.moving_average.MovingAverages()
        trending_report = src.report.trending.Trending()
        public_holdings = src.report.public_company_holdings.PublicCompanyHoldings()
        dinosaur_report = src.report.dinosaur_footprints.DinosaurFootprints()
        metal_tracker = src.report.metal_tracker.MetalTracker()
        stock_tracker = src.report.stock_tracker.StockTracker()

        while True:
            run_time = src.utils.util.get_report_run_time(src.init.config['report_settings']['daily_report_run_time'])
            src.init.logger.info(f'Scheduler - Time Left: {run_time} seconds')

            src.init.scheduler.enter(run_time, 1, moving_average_report.run)
            src.init.scheduler.enter(run_time+1, 1, trending_report.run)
            src.init.scheduler.enter(run_time+2, 1, dinosaur_report.run)
            src.init.scheduler.enter(run_time+3, 1, public_holdings.run)
            src.init.scheduler.enter(run_time+4, 1, metal_tracker.run)
            src.init.scheduler.enter(run_time+5, 1, stock_tracker.run)
            src.init.scheduler.run()

            email.send_email('24 Hour Reports')
            stock_tracker.cleanup_charts()
            src.init.logger.info('Scheduler - Complete')

    except Exception as e:
        email.send_error_email("Application Crash", str(e) + '<br/><br/>' + traceback.format_exc())
        src.init.logger.exception(f'Application Crash: {e}')
        quit()

elif '--watchers' in sys.argv:
    email = src.email.email_handler.GMail()

    try:
        src.init.logger.info('Running supervisor reports')
        watcher = src.report.dip_watcher.DipWatcher()
        while True:
            watcher.run()
            time.sleep(60)

    except Exception as e:
        email.send_error_email("Application Crash", str(e) + '<br/><br/>' + traceback.format_exc())
        src.init.logger.exception(f'Application Crash: {e}')
        quit()

elif '--pull-named-wallets' in sys.argv:
    src.report.dinosaur_footprints.DinosaurFootprints().pull_named_wallets()
