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

    def build_and_send_gmail(self, to: list, subject: str, contents: dict = None, attach_images: bool = False):
        message = email.mime.multipart.MIMEMultipart('related')
        message['From'] = self.username
        message['To'] = ', '.join(to)
        message['Subject'] = subject

        body = self.__build_html_body(contents)
        message.attach(email.mime.text.MIMEText(body, 'html'))

        if attach_images:
            self.__add_image_to_email(message)

        self.send_gmail(to, message.as_string())

        if not bool(contents):
            init.email_content.clear()

    def send_gmail(self, to: list, body: str):
        with smtplib.SMTP(self.hostname) as server:
            server.starttls()
            server.login(self.username, self.password)
            server.sendmail(self.username, to, body)

    @staticmethod
    def add_email_content(report_name: str, report_content: str):
        init.email_content.append({'name': report_name, 'contents': report_content})

    @staticmethod
    def __build_html_body(contents: dict) -> str:
        report_sections = ''

        if bool(contents):
            report_sections += GMail.__build_body_section(contents)
        else:
            for report in init.email_content:
                report_sections += GMail.__build_body_section(report)

        template_path = util.configure_file_path('email_template.html')
        file = open(template_path, 'r')
        email_template = file.read()
        file.close()

        template = email_template.replace('{{{body_content}}}', report_sections)
        return template

    @staticmethod
    def __build_body_section(report: dict) -> str:
        section = '<div><div class="data-cell"> <div style="border-collapse: collapse; display: table; width: 100%; background-color: #ffffff;"> <div style="text-align: left; color: #697d71; font-size: 14px; line-height: 21px;"> <div style="margin-left: 20px; margin-right: 20px; margin-top: 12px;"><div style="line-height: 20px; font-size: 1px;">&nbsp;</div></div><div style="margin-left: 20px; margin-right: 20px;"> <div style="vertical-align: middle;"> <h1 style="margin-top: 0; margin-bottom: 0; font-style: normal; font-weight: normal; color: #555555; font-size: 22px; line-height: 31px; font-family: Open Sans, sans-serif; text-align: center;"> <strong>{{{report_title}}}&nbsp;</strong> </h1> <p class="size-16" style="margin-top: 20px; margin-bottom: 20px; font-size: 14px; line-height: 26px; text-align: center;">{{{report_body}}}</p></div></div><div style="margin-left: 20px; margin-right: 20px; margin-bottom: 12px;"><div style="line-height: 5px; font-size: 1px;">&nbsp;</div></div></div></div></div><div style="line-height: 20px; font-size: 20px;">&nbsp;</div></div>'
        title_section = section.replace('{{{report_title}}}', report['name'])
        body_section = title_section.replace('{{{report_body}}}', report['contents'])
        return body_section

    @staticmethod
    def __add_image_to_email(message):
        chart_directory = chart_builder.ChartBuilder.CONST_CHART_FILE_DIRECTORY
        charts = os.listdir(chart_directory)
        for chart in charts:
            file = open(chart_directory + chart, 'rb')
            chart_image = email.mime.image.MIMEImage(file.read())
            file.close()

            chart_image.add_header('Content-ID', '<' + chart.split('.')[0] + '>')
            message.attach(chart_image)
