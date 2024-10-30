from playwright.sync_api import Page, TimeoutError, Response, expect
from data.environment import host
import random


class Base:
    def __init__(self, page: Page):
        self.page = page

    def open(self, uri) -> Response | None:
        return self.page.goto(f"{host.get_base_url()}{uri}", wait_until='domcontentloaded')

    # клик, при необходимости сам делает скролл к нужному элементу
    def click(self, locator: str) -> None:
        self.page.locator(locator).first.click()

    def input(self, locator: str, data: str) -> None:  # ввод в поле
        self.page.locator(locator).first.fill(data)

    # достаем текст, если локатор один, то в аргумент прокидываем значение 0
    def get_text(self, locator: str, index: int) -> str:
        return self.page.locator(locator).nth(index).text_content()

    # находим элемент по индексу и кликаем
    def click_element_by_index(self, locator: str, index: int) -> None:
        self.page.locator(locator).nth(index).click()

    # вводим данные в нужные поля по индексу
    def input_value_by_index(self, locator: str, index: int, data: str) -> None:
        self.page.locator(locator).nth(index).fill(data)

    # ожидание какого то элемента если нужно
    def wait_for_element(self, locator, timeout=12000) -> None:
        self.page.wait_for_selector(locator, timeout=timeout)

    def current_url(self) -> str:  # возвращает урл
        return self.page.url

    # кликаем по первому элементу, если по индексу выдает out of range
    def click_first_element(self, locator: str):
        self.page.locator(locator).first.click()

    # находим элемент(кнопку)с нужным текстом внутри и кликаем
    def click_by_text_by_index(self, text: str, index: int):
        self.page.get_by_text(text).nth(index).click()

    def input_in_shadow_root(self, shadow_locator: str, shadow_input_locator: str, data: str):
        # ищем элемент в шадоуруте
        shadow_root = self.page.evaluate_handle(
            f'document.querySelector("{shadow_locator}").shadowRoot')
        input_element = shadow_root.evaluate_handle(
            f'document.querySelector("{shadow_input_locator}")')
        input_element.as_element().fill(data)

    # проверяем является ли элемент чек-боксом и проставляем чекбокс
    def checkbox(self, locator: str) -> None:
        self.page.locator(locator).check()

    def is_element_present(self, locator: str) -> bool:  # если элемент есть то все ок
        try:
            self.page.wait_for_selector(locator, timeout=10000)
        except TimeoutError as e:
            return False
        return True

    # выпадающи список, выбираем значение в валуе
    def selector(self, locator: str, value: str):
        self.page.select_option(locator, value)

    def drag_and_drop(self, source, target):  # перетаскивать из-куда то
        self.page.drag_and_drop(source, target)

    # сначала идет слушатель, который говорит, что нужно сделать с алертом
    def alert_accept(self, locator: str):
        # анонимная функция обрабатывающая событие
        self.page.on('dialog', lambda dialog: dialog.accept())
        self.click(locator)

    # ожидаем открытие нового таба и свитчаемся и делаем ассерт, что нужный элемент есть на странице
    def open_new_tab_and_check_presence(self, locclick, locpresence):
        with self.page.expect_popup() as page1_info:
            self.page.click(locclick)
        page1 = page1_info.value
        page1.bring_to_front()
        loc = page1.locator(locpresence)
        expect(loc).to_be_visible(visible=True, timeout=12000)

    # закрываем таб и возвращаемся на предыщущий, number-номер таба который хотим закрыть
    def close_tab(self, number):
        all_tabs = self.page.context.pages
        all_tabs[number].close()

    # number - номер вкладки на которую хотим свичнуться, сначала используем этот метод, потом закрываем вкладки
    def switch_to_previous_tab(self, number):
        # Получаем список всех вкладок в контексте браузера
        all_tabs = self.page.context.pages
        new_tab = all_tabs[number]  # Получаем вкладку по указанному индексу
        self.page.bring_to_front()  # Переключаемся на текущую вкладку (делаем ее активной)
        # Ожидаем завершения загрузки страницы в текущей вкладке
        self.page.wait_for_load_state()
        return new_tab

    # закрываем все табы, кроме первогоо
    def close_all_tabs_except_first(self):
        all_tabs = self.page.context.pages
        for p in range(1, len(all_tabs)):
            all_tabs[p].close()

    def refresh(self) -> Response | None:  # рефреш страницы
        return self.page.reload(wait_until='domcontentloaded')

    def alert_with_double_input(self, key1, value1, key2, value2):
        # ключ значения нужно вводить в ковычках,в ключ указывать название поля, а в значение что хотим ввести
        dialog = self.page.wait_for_event('dialog')
        inputs = {key1: value1, key2: value2}
        dialog.fill(inputs)
        dialog.accept()

    # переключаемся на iframe по локатору и кликаем
    def switch_to_iframe_and_click(self, iframe_locator, locator_for_click):
        frame = self.page.frame_locator(iframe_locator)
        if frame is not None:
            frame.locator(locator_for_click).click()
        else:
            print("Iframe not found with the specified locator:", iframe_locator)

    # переключаемся на iframe по локатору и вводим нужные данные
    def switch_to_iframe_and_input(self, iframe_locator, locator_for_input, data: str):
        frame = self.page.frame_locator(iframe_locator)
        if frame is not None:
            frame.locator(locator_for_input).fill(data)
        else:
            print("Iframe not found with the specified locator:", iframe_locator)

    def get_iframe_by_index(self, index):  # переходим на iframe по индексу
        return self.page.main_frame.child_frames[index]

    def switch_to_main_frame(self):  # возврат на основной фрейм
        return self.page.main_frame

    # находим элемент(кнопку) и возвращаем
    def search_element_by_text(self, text: str):
        return self.page.get_by_text(text)

    def generate_random_number(min_value=1, max_value=1000000):
        return random.randint(min_value, max_value)

    # def get_element_by_index(self, parent_locator, parent_index, child_locator, child_index):
    #     parent_loc = self.page.locator(parent_locator)
    #     if parent_index < 0:
    #         parent_index += parent_loc.count()
    #
    #     if parent_index < 0 or parent_index >= parent_loc.count():
    #         raise IndexError(f"Индекс родителя {parent_index} вне диапазона.")
    #
    #     parent_loc = parent_loc.nth(parent_index)
    #     child_loc = parent_loc.locator(child_locator)
    #     if child_index < 0:
    #         child_index += child_loc.count()
    #
    #     if child_index < 0 or child_index >= child_loc.count():
    #         raise IndexError(f"Индекс ребенка {child_index} вне диапазона.")
    #
    #     return child_loc.nth(child_index)
    def get_element_by_index(self, parent_locator, parent_index, child_locator, child_index):
        parent_loc = self.page.locator(parent_locator)

        # # Проверка наличия элементов
        # if parent_loc.count() == 0:
        #     raise IndexError(f"Нет элементов для локатора {parent_locator}.")
        #
        # if parent_index < 0:
        #     parent_index += parent_loc.count()
        #
        # if parent_index < 0 or parent_index >= parent_loc.count():
        #     raise IndexError(f"Индекс родителя {parent_index} вне диапазона.")

        parent_loc = parent_loc.nth(parent_index)
        child_loc = parent_loc.locator(child_locator)

        # # Проверка наличия дочерних элементов
        # if child_loc.count() == 0:
        #     raise IndexError(f"Нет дочерних элементов для локатора {child_locator}.")
        #
        # if child_index < 0:
        #     child_index += child_loc.count()
        #
        # if child_index < 0 or child_index >= child_loc.count():
        #     raise IndexError(f"Индекс ребенка {child_index} вне диапазона.")

        return child_loc.nth(child_index)
