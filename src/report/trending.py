import src.utils.database_util
import src.email.email_handler
import src.init
import json
import src.report.base_report
import time
import traceback


class Trending(src.report.base_report.Report):
    CONST_DAY_IN_SECONDS = 60 * 60 * 24
    CONST_FIVE_MINUTES_IN_SECONDS = 60 * 5
    CONST_DATA_INTEGRITY_THRESHOLD = 60 * 60 * 25

    def __init__(self):
        src.report.base_report.Report.__init__(self)
        self.formatted_response = None
        self.trenders = dict()
        self.email_trenders = False
        self.data_threshold = False

    def run(self):
        email = src.email.email_handler.GMail()

        try:
            self.__pull_trenders_and_update_trending_tracker()
            wallets = dict((k, v) for k, v in self.trenders.items() if v >= 5)

            if self.data_threshold:
                email.add_report_to_email('Trending Report - Data Integrity Reset', self.build_no_data_result())
                self.data_threshold = False
                return

            if self.email_trenders:
                self.formatted_response = [(key, value) for key, value in self.trenders.items()]
                self.formatted_response = {key: value for key, value in sorted(self.formatted_response, key=lambda x: x[1]) if value >= src.init.config['report_settings']['trending_report_appearance_threshold']}
                table = self.build_html_table(['Coin', 'Appearances'], self.formatted_response, 'trending')
                email.add_report_to_email('Trending Report', table)
                return

            email.add_report_to_email('Trending Report', self.build_no_data_result())
            src.init.logger.info(f'Trending Report - Wallets Found: {len(wallets.keys())}')

        except Exception as e:
            email.add_report_to_email('Trending Report', str(e) + '<br/><br/>' + traceback.format_exc())
            return

    def __pull_trenders_and_update_trending_tracker(self):
        last_modify_date = 0
        self.trenders = dict()
        con = src.utils.database_util.DatabaseHelper().create_connection()
        rows = con.cursor().execute('SELECT coingecko_id, appearances, modify_date FROM trending_report_data').fetchall()
        if len(rows) != 0:
            for row in rows:
                self.trenders[row[0]] = row[1]
                if last_modify_date < row[2]:
                    last_modify_date = row[2]

        if (time.time() - last_modify_date) > self.CONST_DATA_INTEGRITY_THRESHOLD:
            src.init.logger.warn(f'Unix timestamp {time.time()} minus the last modify date of {last_modify_date} is greater than the data integrity threshold of {self.CONST_DATA_INTEGRITY_THRESHOLD}. This happens almost imperceptibly as compounding time from delays in processing move the target window outside of acceptable bounds.')
            con.cursor().execute('DELETE FROM trending_report_data')
            con.commit()
            con.close()
            self.data_threshold = True
            return

        elif (time.time() - last_modify_date) < (self.CONST_DAY_IN_SECONDS - self.CONST_FIVE_MINUTES_IN_SECONDS):
            src.init.logger.info('Trending Report - Less than a day has passed since the last Trending report run')
            return

        for i in range(1, 6):
            if i != 1:
                time.sleep(60)
            trending_result = self.coingecko.get_trending()
            if trending_result is not None:
                search_trending = json.loads(bytes.decode(trending_result))
                break
            if i == 5:
                search_trending = {"coins": [{"item": {"id": "placeholderdata"}}]}

        trending_ids = list()
        for item in search_trending['coins']:
            for trender in item.values():
                trending_ids.append(trender['id'])
                if trender['id'] in self.trenders.keys():
                    self.trenders[trender['id']] += 1
                if trender['id'] not in self.trenders.keys():
                    self.trenders[trender['id']] = 1

        for previous_trender in self.trenders.keys():
            if previous_trender not in trending_ids:
                self.trenders[previous_trender] -= 1

        delete_list = []
        for key, value in self.trenders.items():
            if value < 1:
                delete_tuple = (key,)
                delete_list.append(delete_tuple)

        self.trenders = {key: value for key, value in self.trenders.items() if value > 0}
        self.__check_trenders_email_threshold()

        insert_list = []
        for key, value in self.trenders.items():
            insert_tuple = (key, value, time.time())
            insert_list.append(insert_tuple)

        con.cursor().executemany('INSERT INTO trending_report_data(coingecko_id, appearances, modify_date) VALUES(?,?,?) ON CONFLICT (coingecko_id) DO UPDATE SET (appearances, modify_date) = (excluded.appearances, excluded.modify_date)', insert_list)
        con.cursor().executemany('DELETE FROM trending_report_data WHERE coingecko_id=?', delete_list)
        con.commit()
        con.close()

    def __check_trenders_email_threshold(self):
        for appearance in self.trenders.values():
            if appearance >= src.init.config['report_settings']['trending_report_appearance_threshold']:
                self.email_trenders = True
                return
            else:
                self.email_trenders = False
        return
