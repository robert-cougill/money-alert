import src.email.email_handler
import init
import report.trending
import report.dinosaur_footprints
import report.public_company_holdings
import report.dip_watcher
import report.moving_average
import report.stock_tracker
import report.metal_tracker
import sys
import src.unit_tests.unit_test
import time
import traceback
import src.utils.util


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
    email = src.email.email_handler.GMail()

    try:
        moving_average_report = report.moving_average.MovingAverages()
        trending_report = report.trending.Trending()
        trending_report.email_trenders = True
        public_holdings = report.public_company_holdings.PublicCompanyHoldings()
        dinosaur_report = report.dinosaur_footprints.DinosaurFootprints()
        metal_tracker = report.metal_tracker.MetalTracker()
        stock_tracker = report.stock_tracker.StockTracker()

        init.scheduler.enter(0, 1, moving_average_report.run)
        init.scheduler.enter(1, 1, trending_report.run)
        init.scheduler.enter(2, 1, dinosaur_report.run)
        init.scheduler.enter(3, 1, public_holdings.run)
        init.scheduler.enter(4, 1, metal_tracker.run)
        init.scheduler.enter(5, 1, stock_tracker.run)
        init.scheduler.run()

        email.send_email('24 Hour Reports - Forced Run')
        stock_tracker.cleanup_charts()
        init.logger.info('Scheduler - Complete')

    except Exception as e:
        email.send_error_email("Application Crash", str(e) + '<br/><br/>' + traceback.format_exc())
        init.logger.exception(f'Application Crash: {e}')
        quit()

elif '--daily' in sys.argv:
    email = src.email.email_handler.GMail()

    try:
        unit_test = src.unit_tests.unit_test.UnitTest()
        unit_test.launch_unit_test()

        moving_average_report = report.moving_average.MovingAverages()
        trending_report = report.trending.Trending()
        public_holdings = report.public_company_holdings.PublicCompanyHoldings()
        dinosaur_report = report.dinosaur_footprints.DinosaurFootprints()
        metal_tracker = report.metal_tracker.MetalTracker()
        stock_tracker = report.stock_tracker.StockTracker()

        while True:
            run_time = src.utils.util.get_report_run_time(init.config['report_settings']['daily_report_run_time'])
            init.logger.info(f'Scheduler - Time Left: {run_time} seconds')

            init.scheduler.enter(run_time, 1, moving_average_report.run)
            init.scheduler.enter(run_time+1, 1, trending_report.run)
            init.scheduler.enter(run_time+2, 1, dinosaur_report.run)
            init.scheduler.enter(run_time+3, 1, public_holdings.run)
            init.scheduler.enter(run_time+4, 1, metal_tracker.run)
            init.scheduler.enter(run_time+5, 1, stock_tracker.run)
            init.scheduler.run()

            email.send_email('24 Hour Reports')
            stock_tracker.cleanup_charts()
            init.logger.info('Scheduler - Complete')

    except Exception as e:
        email.send_error_email("Application Crash", str(e) + '<br/><br/>' + traceback.format_exc())
        init.logger.exception(f'Application Crash: {e}')
        quit()

elif '--watchers' in sys.argv:
    email = src.email.email_handler.GMail()

    try:
        init.logger.info('Running supervisor reports')
        watcher = report.dip_watcher.DipWatcher()
        while True:
            watcher.run()
            time.sleep(60)

    except Exception as e:
        email.send_error_email("Application Crash", str(e) + '<br/><br/>' + traceback.format_exc())
        init.logger.exception(f'Application Crash: {e}')
        quit()

elif '--pull-named-wallets' in sys.argv:
    report.dinosaur_footprints.DinosaurFootprints().pull_named_wallets()
