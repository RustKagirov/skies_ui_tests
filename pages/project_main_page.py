from pages.base import Base
from locators.project_page import ProjectPage
from data.assertions import Assertions
from playwright.sync_api import Page


class Project(Base):
    def __init__(self, page: Page):
        super().__init__(page)
        self.assertions = Assertions(page)

    def input_to_search_on_project_page(self):
        self.input(ProjectPage.SEARCH_FIELD, 'Привет')
        self.page.locator(ProjectPage.SEARCH_FIELD).press('Enter')

    def check_about_author(self):
        self.assertions.check_element_visible_and_active(
            ProjectPage.ABOUT_AUTHOR_BUTTON, 'Не отображается/не активен блок "Об авторе"')

    def check_blog(self):
        self.assertions.check_element_visible_and_active_by_index(
            ProjectPage.NAVIGATION_BUTTON, 1, 'Не отображается/не активен блок "Блог"')

    def check_author_community(self):
        self.assertions.check_element_visible_and_active_by_index(
            ProjectPage.NAVIGATION_BUTTON, 2, 'Не отображается/не активен блок "Сообщество автора проекта"')

    def check_support_button(self):
        self.assertions.check_element_visible_and_active(
            ProjectPage.SUPPORT_BUTTON, 'Не найдена кнопка Поддержать')

    async def click_blog_button(self):
        self.click_element_by_index(ProjectPage.NAVIGATION_BUTTON, 1)

    def leave_and_check_comment(self):
        random_comment = f'Комментарий номер {str(Base.generate_random_number())}'
        self.input(ProjectPage.COMMENT_FIELD, random_comment)
        self.click_first_element(ProjectPage.COMMENT_BUTTON)
        self.page.reload()
        last_comment = Base.get_element_by_index(
            self, '.comment-list__comments-list', 0, 'comment', -1)
        self.assertions.to_contain_text(
            last_comment, random_comment, 'Текст комментария не совпал')

    def click_and_check_support_button(self):
        self.click(ProjectPage.SUPPORT_BUTTON)
        self.assertions.check_URL(
            'user/42/support', 'Не совпал url страницы поддержки')

    def click_and_check_style_favorite_button(self):
        button_selector = '.poster__button-icon.ng-star-inserted'
        title_value = self.page.locator(button_selector).get_attribute("title")
        if title_value == 'Удалить из закладок':
            self.click(button_selector)
        element = self.page.query_selector(button_selector)
        if element is None:
            raise ValueError(
                f"Элемент с селектором '{button_selector}' не найден на странице.")
        initial_style = element.evaluate('el => el.getAttribute("style")')
        self.click(button_selector)
        new_style = element.evaluate('el => el.getAttribute("style")')
        assert initial_style != new_style, "Стиль кнопки не изменился после нажатия"

    def click_and_check_my_favorites_project(self):
        name_my_added_project = self.get_text(ProjectPage.NAME_PROJECT, 0)
        self.click_by_text_by_index(' Избранные проекты ', 0)
        last_added_project = Base.get_element_by_index(
            self, ProjectPage.ELEMENT_LIST_AD_PROJECT, 0, ProjectPage.NAME_ADDED_PROJECT, 0)
        self.assertions.to_contain_text(
            last_added_project, name_my_added_project, 'Название добавленного проекта не нашлось в списке проектов')
        self.click_element_by_index(
            ProjectPage.DELETE_PROJECT_FROM_LIST_BUTTON, 0)
