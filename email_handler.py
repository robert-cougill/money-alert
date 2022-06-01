import email.mime.multipart
import email.mime.text
import email.mime.image
import init
import os
import smtplib
import util
import chart_builder  # leave me at the bottom, order matters here


class GMail:
    def __init__(self):
        self.hostname = init.config['email']['hostname']
        self.username = init.config['email']['username']
        self.password = init.config['email']['secret']

    @staticmethod
    def add_report_to_email(report_name: str, report_content: str = None):
        init.email_content.append({'name': report_name, 'contents': report_content})

    def send_error_email(self, subject, stacktrace):
        self.add_report_to_email(subject, stacktrace)
        self.send_email(subject)
        init.email_content.clear()

    def send_email(self, subject: str):
        message = email.mime.multipart.MIMEMultipart('related')
        message['From'] = self.username
        message['To'] = ', '.join(init.config['emails'])
        message['Subject'] = subject

        content = self.__get_email_content()
        message.attach(email.mime.text.MIMEText(content, 'html'))

        self.__attach_images(message)

        with smtplib.SMTP(self.hostname) as server:
            server.starttls()
            server.login(self.username, self.password)
            server.sendmail(self.username, init.config['emails'], message.as_string())

        init.email_content.clear()

    @staticmethod
    def __get_email_content() -> str:
        report_sections = ''

        for report in init.email_content:
            report_sections += GMail.__get_report_body(report)

        template_path = util.configure_file_path('email_template.html')
        file = open(template_path, 'r')
        email_template = file.read()
        file.close()

        email_template = email_template.replace('MONEY_ALERT_LOGO', os.getenv('MONEY_ALERT_LOGO'))
        template = email_template.replace('{{{body_content}}}', report_sections)
        return template

    @staticmethod
    def __get_report_body(report: dict) -> str:
        section = '<div><div class="data-cell"> <div style="border-collapse: collapse; display: table; width: 100%; background-color: #ffffff;"> <div style="text-align: left; color: #697d71; font-size: 14px; line-height: 21px;"> <div style="margin-left: 20px; margin-right: 20px; margin-top: 12px;"><div style="line-height: 20px; font-size: 1px;">&nbsp;</div></div><div style="margin-left: 20px; margin-right: 20px;"> <div style="vertical-align: middle;"> <h1 style="margin-top: 0; margin-bottom: 0; font-style: normal; font-weight: normal; color: #555555; font-size: 22px; line-height: 31px; font-family: Open Sans, sans-serif; text-align: center;"> <strong>{{{report_title}}}&nbsp;</strong> </h1> <p class="size-16" style="margin-top: 20px; margin-bottom: 20px; font-size: 14px; line-height: 26px; text-align: center;">{{{report_body}}}</p></div></div><div style="margin-left: 20px; margin-right: 20px; margin-bottom: 12px;"><div style="line-height: 5px; font-size: 1px;">&nbsp;</div></div></div></div></div><div style="line-height: 20px; font-size: 20px;">&nbsp;</div></div>'
        title_section = section.replace('{{{report_title}}}', report['name'])
        body_section = title_section.replace('{{{report_body}}}', report['contents'])
        return body_section

    @staticmethod
    def __attach_images(message):
        chart_directory = chart_builder.ChartBuilder.CONST_CHART_FILE_DIRECTORY
        charts = os.listdir(chart_directory)
        for chart in charts:
            file = open(chart_directory + chart, 'rb')
            chart_image = email.mime.image.MIMEImage(file.read())
            file.close()

            chart_image.add_header('Content-ID', '<' + chart.split('.')[0] + '>')
            message.attach(chart_image)
