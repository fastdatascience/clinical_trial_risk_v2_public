from jinja2 import Environment, FileSystemLoader, select_autoescape

from app import schemas


class EmailGenerator:
    def __init__(self):
        pass

    def generate_sign_up(self, data: schemas.EmailGeneratorSignUpData) -> str:
        """
        Generate sign up email.

        :param data: The data.
        :returns: The HTML string.
        """

        return self.__render(data=data.model_dump(mode="json"), template="sign-up.html")

    def generate_reset_password(self, data: schemas.EmailGeneratorResetPasswordData) -> str:
        """
        Generate reset password email.

        :param data: The data.
        :returns: The HTML string.
        """

        return self.__render(data=data.model_dump(mode="json"), template="reset-password.html")

    def generate_general_message(self, data: schemas.EmailGeneratorGeneralMessageData) -> str:
        """
        Generate general message email.

        :param data: The data.
        :returns: The HTML string.
        """

        return self.__render(data=data.model_dump(mode="json"), template="general-message.html")

    @staticmethod
    def __render(data: dict, template: str) -> str:
        """
        Render data into template.

        :param data: The data.
        :param template: The template.
        :returns: The HTML string.
        """

        env = Environment(
            loader=FileSystemLoader(
                [
                    "app/services/email_generator/templates",
                ]
            ),
            autoescape=select_autoescape(['html', 'xml'])
        )

        # Template
        j2_template = env.get_template(template)

        # Render template
        render = j2_template.render(data)

        return render
