import src.utils.database_util
import src.email.email_handler
import src.init
import json
import src.report.base_report
import traceback


class PublicCompanyHoldings(src.report.base_report.Report):
    def __init__(self):
        src.report.base_report.Report.__init__(self)
        self.notify_companies = dict()
        self.email = src.email.email_handler.GMail()

    def run(self):
        try:
            self.get_holdings_by_coin('bitcoin')
            self.get_holdings_by_coin('ethereum')
            self.send_notify_companies()

        except Exception as e:
            self.email.add_report_to_email('Public Company Holdings', str(e) + '<br/><br/>' + traceback.format_exc())
            return

    def get_holdings_by_coin(self, coin_id: str):
        response = json.loads(self.coingecko.get_public_company_holdings(coin_id))

        con = src.utils.database_util.DatabaseHelper().create_connection()
        select_statement = 'SELECT company_name, total_holdings FROM public_company_holdings WHERE coin = ? ORDER BY total_holdings DESC'
        rows = con.cursor().execute(select_statement, tuple([coin_id])).fetchall()

        coin_holdings = dict()
        for row in rows:
            coin_holdings[row[0] + coin_id] = {'total_holdings': row[1]}

        insert_list = []
        for company in response['companies']:
            company_name = company['name'] + coin_id
            if company_name in coin_holdings.keys():
                continue

            # Add company to holdings dict
            coin_holdings[company_name] = {'total_holdings': company['total_holdings']}

            insert_tuple = (company['name'], coin_id, company['total_holdings'])
            insert_list.append(insert_tuple)

        if len(insert_list) > 0:
            con.cursor().executemany('INSERT INTO public_company_holdings (company_name, coin, total_holdings) VALUES(?,?,?) ON CONFLICT DO NOTHING', insert_list)
            con.commit()

        for company in response['companies']:
            company_name = company['name'] + coin_id
            if coin_holdings[company_name]['total_holdings'] != company['total_holdings']:
                con.cursor().execute('UPDATE public_company_holdings SET total_holdings = ? WHERE company_name = ? AND coin = ?', tuple([company['total_holdings'], company['name'], coin_id]))

                balance_change = company['total_holdings'] - coin_holdings[company_name]['total_holdings']
                self.notify_companies[company['name']] = {'company': company['name'], 'coin': coin_id, 'change': balance_change, 'total_holdings': company['total_holdings']}

        con.commit()
        con.close()

    def send_notify_companies(self):
        src.init.logger.info(f'Public Company Holdings - Companies Holdings Changed: {len(self.notify_companies)}')
        if len(self.notify_companies) > 0:
            table = self.build_html_table(['Company', 'Coin', 'Change', 'Balance'], self.notify_companies, 'public_company_holdings')
            self.email.add_report_to_email('Public Company Holdings', table)
            return

        self.email.add_report_to_email('Public Company Holdings', self.build_no_data_result())
        src.init.logger.info(f'Public Company Holdings - Companies Changed: {len(self.notify_companies)}')
