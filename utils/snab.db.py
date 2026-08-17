from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QPushButton, QVBoxLayout, QWidget, QComboBox, QHBoxLayout, QMenu, QUndoStack, QMessageBox, QFileDialog, QShortcut, QPlainTextEdit, QStyledItemDelegate
from PyQt5.QtGui import QDesktopServices, QKeySequence
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from datetime import datetime


class Database(QMainWindow):
    '''Главное окно + создание колонок таблицы'''

    def __init__(self):
        super().__init__()

        self.table = QTableWidget()  # Создание таблицы
        self.load_data() # Загрузка последних изменений в бд при открытии
        self.table.setColumnCount(10)  # Кол-во колонок
        self.table.setHorizontalHeaderLabels(['Дата', 'Срочность', 'Товар', 'Участок', 'Ответственный', 'Статус', 'Срок поставки', 'Документы', 'Комментарии', 'путь к файлу'])  # Названия колонок

        self.filter_layout = QHBoxLayout()  # Поля ввода для фильтрации
        self.filtering()  # Фильтры по колонкам
        self.contro_button()  # Добавление кнопок
        self.decoration()  # Оформление интерфейса

        # Контекстное меню (правая кнопка мыши)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        self.table.cellChanged.connect(self.on_cell_changed) # Обновления в ответ на изменения

        self.back = QUndoStack()  # Функция отмены действия
        undo_shortcut = QShortcut(QKeySequence("Ctrl+Z"), self)  # Коннект с кнопками
        undo_shortcut.activated.connect(self.cancellation) # Привязка действий к Ctrl+Z

        # 'Enter' для переноса строк
        delegate = NewParagraph()
        for col in [0, 2, 6, 8]:  # все текстовые колонки
            self.table.setItemDelegateForColumn(col, delegate)

    def data(self):
        '''Создание новой строки + дата и время подгружаются автоматически'''
        self.save_state()  # Сохранение состояния таблицы

        self.new_row = 0  # Позиция новой строки
        self.table.insertRow(self.new_row)  # Новая строка

        self.today = QTableWidgetItem(str(datetime.now().strftime('%d.%m.%y %H:%M')))  # Формат даты
        self.table.setItem(self.new_row, 0, self.today)  # Подгрузка даты в первую колонку

        self.variants_urgency()  # Всплывающие варианты для колонки 'Срочность'
        self.variants_stage()  # Всплывающие варианты для колонки 'Статус'
        self.variants_region() # Всплывающие варианты для колонки 'Участок'
        self.variants_responsible() # Всплывающие варианты для колонки 'Ответственный'

        self.colour()  # Цвет кнопок для колонки 'Статус'
        self.uploading_doc()  # Подгрузить PDF в колонку 'Документы'

        self.update_filters()  # Обновление уникальных значений для фильтрации

    def variants_urgency(self):
        '''Всплывающие варианты для колонки "Срочность"'''
        self.box_urgency = QComboBox()  # Выпадающий список
        self.box_urgency.addItems(['Текущая', 'Срочно'])  # Варианты для выпадающего списка
        self.table.setCellWidget(self.new_row, 1, self.box_urgency)  # Подгрузка списка в колонку 'Срочность'

    def variants_region(self):
        '''Всплывающие варианты для колонки "Участок"'''
        self.box_region = QComboBox()  # Выпадающий список
        self.box_region.addItems(['IT', 'Бобинорезка', 'Воздух', 'Гофра', 'Грузовые', 'Кадры', 'Качество В1', 'Качество Д3', 'Литьё В1', 'Литьё Д3', 'Маркетинг', 'Офис', 'Охрана труда', 'Ремонт В1', 'Ремонт Д3', 'Салон', 'Склад В1', 'Склад Д3', 'Упаковка В1', 'Упаковка Д3'])  # Варианты для выпадающего списка
        self.table.setCellWidget(self.new_row, 3, self.box_region)  # Подгрузка списка в колонку 'Участок'

        def update_region():
            '''Отслеживает изменение значения в колонке "Участок"'''
            self.update_filters()

        self.box_region.currentIndexChanged.connect(update_region)

    def variants_responsible(self):
        '''Всплывающие варианты для колонки "Ответственный"'''
        self.box_responsible = QComboBox()  # Выпадающий список
        self.box_responsible.addItems(['Андреев А', 'Астанин А', 'Будылёва Т', 'Боярогло Е', 'Васильев С', 'Ершова В', 'Заречнев С', 'Зеленская А', 'Иванова А', 'Козьяков М', 'Кудуков А', 'Максимов А', 'Мохов С.В', 'Муштатова Э', 'Петухов А', 'Сим К', 'Туровцев И', 'Фомин А.В', 'Чернобривченко Т'])  # Варианты для выпадающего списка
        self.table.setCellWidget(self.new_row, 4, self.box_responsible)  # Подгрузка списка в колонку 'Участок'

        def update_responsible():
            '''Отслеживает изменение значения в колонке "Ответственный"'''
            self.update_filters()

        self.box_responsible.currentIndexChanged.connect(update_responsible)

    def variants_stage(self):
        '''Всплывающие варианты для колонки "Статус"'''
        self.box_stage = QComboBox()  # Выпадающий список
        self.box_stage.addItems(
            ['Не просмотрено', 'В работе', 'Заказано', 'Доставлено', 'Отклонено'])  # Варианты для выпадающего списка
        self.table.setCellWidget(self.new_row, 5, self.box_stage)  # Подгрузка списка в колонку 'Статус'

        self.default_item = QTableWidgetItem('Не просмотрено')  # Создание значения 'Не просмотрено'
        self.table.setItem(self.new_row, 5, self.default_item)  # 'Не просмотрено' указано по умолчанию

        def update_item():
            '''Отслеживает изменение значения в колонке "Статус"'''
            self.default_item.setText(self.box_stage.currentText())  # Обновляет ячейку
            self.colour()  # Устанавливает цвет значения в колонке
            self.update_filters() # Обновление фильтров

        self.box_stage.currentIndexChanged.connect(update_item)  # Изменение значения в ячейке = обновление ячейки и выбор цвета

    def remove_data(self):
        '''Удаление выбранной строки'''
        self.save_state()  # Сохранение состояния таблицы
        self.current_row = self.table.currentRow()  # Выделенная строка
        if self.current_row >= 0:
            self.table.removeRow(self.current_row)  # Удаление

    def contro_button(self):
        '''Кнопки "добавить" и "удалить"'''
        self.button_add = QPushButton('Добавить')  # Кнопка добавления новой строки
        self.button_remove = QPushButton('Удалить')  # Кнопка удаления выбранной строки

        self.button_add.clicked.connect(self.data)  # Реагирование на клик 'Добавить'
        self.button_remove.clicked.connect(self.remove_data)  # Реагирование на клик 'Удалить'

    def decoration(self):
        '''Оформление интерфейса'''
        self.layout = QVBoxLayout()  # Формат макета (Вертикальный. Друг под другом)
        self.widget = QWidget()  # Контейнер макета
        self.widget.setLayout(self.layout)  # Установка макета
        self.setCentralWidget(self.widget)  # Контейнер = центральный виджет

        self.layout.addWidget(self.button_add)  # Кнопка 'Добавить'
        self.layout.addWidget(self.button_remove)  # Кнопка 'Удалить'

        self.layout.addLayout(self.filter_layout)  # Панель фильтров

        self.layout.addWidget(self.table)  # Основная таблица

    def filtering(self):
        '''Фильтрация по колонкам + Всплывающие варианты уникальных значений в фильтрах'''
        self.filter_fields = {} # Для хранения фильтров

        unique_data = {0: set(), 2: set(), 4: set(), 5: set()}  # Фильтрующиеся колонки
        row_count = self.table.rowCount()
        for row in range(row_count):  # Сбор уникальных значений
            for col in [0, 2, 4, 5]:
                item = self.table.item(row, col)
                if item and item.text():
                    unique_data[col].add(item.text())

        for col, name in {0: 'Дата', 2: 'Товар', 4: 'Ответственный', 5: 'Статус'}.items():
            field = QComboBox()  # Поле ввода для фильтров
            field.addItem('Все')  # Строка для сброса фильтров
            field.addItems(sorted(unique_data[col]))  # Уникальные значения из столбцов
            field.setToolTip(f"Фильтр по колонке '{name}'")  # Подсказка-название колонки
            self.filter_fields[col] = field  # Сохранение строки-фильтра
            self.filter_layout.addWidget(field)  # Добавление строки-фильтра в панель
            field.currentTextChanged.connect(self.apply_filter)  # Фильтрация по запросу

    def apply_filter(self):
        '''Скрывает неподходящие по фильтрации строки'''
        for row in range(self.table.rowCount()): # Проходимся по всей таблице
            hide = False # По умолчанию все строки видно
            for col, field in self.filter_fields.items(): # Проходимся по всем фильтрам
                text = field.currentText().lower() # Регистр не имеет значения
                if text:
                    if col == 5:  # Колонка "Статус"
                        widget = self.table.cellWidget(row, col) # Фильтрация для виджета с выпадающим списком
                        if isinstance(widget, QComboBox):
                            cell_text = widget.currentText().lower()
                            if text not in cell_text:
                                hide = True # Скрываем неподходящее
                                break
                    else:
                        item = self.table.item(row, col) # Фильтрация для обычных ячеек
                        if not item or text not in item.text().lower():
                            hide = True
                            break
            self.table.setRowHidden(row, hide)  # Функция скрытия/показа строки

    def update_filters(self):
        '''Обновление данных в фильтрах по актуальным значениям в столбцах'''
        unique_data = {0: set(), 2: set(), 4: set(), 5: set()} # Колонки: 'Дата', 'Товар', 'Ответственный', 'Статус'
        for row in range(self.table.rowCount()): # Проходимся по таблице
            for col in [0, 2, 4, 5]:
                if col in [4, 5]:  # Колонки 'ответственный' и 'статус' с QComboBox
                    widget = self.table.cellWidget(row, col)
                    if isinstance(widget, QComboBox):
                        value = widget.currentText() # Показывает актуальное значение
                        if value:
                            unique_data[col].add(value) # Собираем только уникальные значения
                else: # Проверка, если ячейка не является виджетом, как выше
                    item = self.table.item(row, col) # Содержимое ячейки
                    if item and item.text():
                        unique_data[col].add(item.text()) # Собираем только уникальные значения

        for col, field in self.filter_fields.items(): # Проходимся по собранным данным
            field.clear() # Чистим списки
            field.addItem("") # Кнопка сброса фильтра
            if unique_data[col]:
                field.addItems(sorted(unique_data[col])) # Если данные собраны, то они показываются в фильтре

        self.apply_filter() # Применение новой фильтрации

    def on_cell_changed(self, row, column):
        '''Автоматически обновляет фильтры при изменении в колонках, на которые они установлены'''
        if column in [0, 2, 4, 5]:
            self.update_filters()

    def colour(self):
        '''Установка цвета для значений в колонке "Статус"'''
        for row in range(self.table.rowCount()):
            widget = self.table.cellWidget(row, 5)
            if isinstance(widget, QComboBox):
                text = widget.currentText()  # Значение в колонке
                if text == 'Не просмотрено':
                    widget.setStyleSheet("background-color: red;")  # Красный
                elif text == 'Доставлено':
                    widget.setStyleSheet("background-color: green;")  # Зелёный
                else:
                    widget.setStyleSheet("")  # Прозрачный

    def uploading_doc(self):
        '''Кнопка "Загрузить документ"'''
        add_doc = QPushButton('Загрузить документ')  # Создание кнопки
        add_doc.clicked.connect(lambda: self.upload_or_open(self.new_row, add_doc))  # Привязка кнопки к клику (загрузка файла)
        self.table.setCellWidget(self.new_row, 7, add_doc)  # Вставить кнопку в ячейку

    def upload_or_open(self, row, btn):
        '''Управление PDF. Загрузка файла / открытие файла'''
        if btn.text() == 'Загрузить документ':
            # Режим загрузки
            file_path, _ = QFileDialog.getOpenFileName(self, 'Выберите PDF', '', 'PDF Files (*.pdf)')  # Выбор файла для загрузки
            if file_path:
                btn.setText(file_path.split('/')[-1])  # Сменить 'Загрузить документ' на имя документа
                self.table.setItem(row, 9,QTableWidgetItem(file_path))  # Сохранение пути файла в СКРЫТУЮ колонку
        else:
            # Режим открытия
            item = self.table.item(row, 9)  # Получить путь
            if item and item.text():
                QDesktopServices.openUrl(QUrl.fromLocalFile(item.text()))  # Открыть файл

        self.table.setColumnHidden(9, True)  # Скрыть колонку с путём (колонка исчезает при подгрузке первого документа)

    def show_context_menu(self, position):
        '''Удаление подгруженного файла правой кнопкой мыши'''
        index = self.table.indexAt(position)  # Выбранная ячейка
        if index.column() == 7:  # Колонка с документами
            menu = QMenu()  # Контекстное меню
            delete_action = menu.addAction("Удалить документ")  # Пункт 'удаление' в меню
            if menu.exec_(self.table.mapToGlobal(position)):  # Выбрасывание меню
                row = index.row()
                self.clear_document(row)  # Удалить

    def clear_document(self, row):
        '''Доступ к подгрузке нового документа после удаления старого'''
        self.table.setItem(row, 8, QTableWidgetItem(""))  # Очищаем старый путь к файлу
        btn = self.table.cellWidget(row, 7)  # Возвращаем кнопку добавления файла
        if btn:
            btn.setText("Загрузить документ")  # Возвращаем текст в кнопку

    def save_state(self):
        '''Сохраняет состояние бд, чтобы отменить изменения через Ctrl+Z'''
        self.backup = [] # Для хранения состояния каждой строки
        for row in range(self.table.rowCount()):
            row_data = {} # Для каждой строки {'Номер колонки': (Тип данных, Значение)}
            for col in range(self.table.columnCount()):
                if col == 1:  # Срочность
                    widget = self.table.cellWidget(row, col) # Пройтись по виджету
                    if isinstance(widget, QComboBox):
                        row_data[col] = ('combo_urgency', widget.currentText()) # Сохранить последнее значение виджета
                elif col == 3:  # Участок
                    widget = self.table.cellWidget(row, col)
                    if isinstance(widget, QComboBox):
                        row_data[col] = ('combo_region', widget.currentText())
                elif col == 4:  # Ответственный
                    widget = self.table.cellWidget(row, col)
                    if isinstance(widget, QComboBox):
                        row_data[col] = ('combo_responsible', widget.currentText())
                elif col == 5:  # Статус
                    widget = self.table.cellWidget(row, col)
                    if isinstance(widget, QComboBox):
                        row_data[col] = ('combo_stage', widget.currentText())
                elif col == 7:  # Документы
                    btn = self.table.cellWidget(row, col)
                    if btn:
                        row_data[col] = ('button', btn.text())
                else:
                    item = self.table.item(row, col)
                    row_data[col] = ('text', item.text() if item else "") # Сохранить значение в ячейке
            self.backup.append(row_data) # Сохранить состояние

    def cancellation(self):
        '''Отмена последнего изменения через Ctrl+Z'''
        if hasattr(self, 'backup') and self.backup:
            self.table.setRowCount(0) # Полностью очистить таблицу, чтобы заполнить её заново резервной копией
            for row_data in self.backup: # Взять 1 строку из резерва
                row = self.table.rowCount() # Кол-во строк
                self.table.insertRow(row) # Вставить новую пустую строку в конец таблицы
                for col, data in row_data.items(): # Пройтись по всем её колонкам
                    typ, value = data # Заполнить
                    if typ == 'text':
                        self.table.setItem(row, col, QTableWidgetItem(value)) # Вставить текст, если в ячейке предпологается текст...
                    #...если виджет - вставить виджет
                    elif typ == 'combo_urgency':
                        combo = QComboBox()
                        combo.addItems(['Текущая', 'Срочно'])
                        combo.setCurrentText(value)
                        self.table.setCellWidget(row, col, combo)
                    elif typ == 'combo_region':
                        combo = QComboBox()
                        combo.addItems(['IT', 'Бобинорезка', 'Воздух', 'Гофра', 'Грузовые', 'Кадры', 'Качество В1', 'Качество Д3', 'Литьё В1', 'Литьё Д3', 'Маркетинг', 'Офис', 'Охрана труда', 'Ремонт В1', 'Ремонт Д3', 'Салон', 'Склад В1', 'Склад Д3', 'Упаковка В1', 'Упаковка Д3'])
                        combo.setCurrentText(value)
                        self.table.setCellWidget(row, col, combo)
                    elif typ == 'combo_responsible':
                        combo = QComboBox()
                        combo.addItems(['Андреев А', 'Астанин А', 'Будылёва Т', 'Боярогло Е', 'Васильев С', 'Ершова В', 'Заречнев С', 'Зеленская А', 'Иванова А', 'Козьяков М', 'Кудуков А', 'Максимов А', 'Мохов С.В', 'Муштатова Э', 'Петухов А', 'Сим К', 'Туровцев И', 'Фомин А.В', 'Чернобривченко Т'])
                        combo.setCurrentText(value)
                        self.table.setCellWidget(row, col, combo)
                    elif typ == 'combo_stage':
                        combo = QComboBox()
                        combo.addItems(['Не просмотрено', 'В работе', 'Заказано', 'Доставлено', 'Отклонено'])
                        combo.setCurrentText(value)
                        combo.currentIndexChanged.connect(lambda: self.colour())
                        self.table.setCellWidget(row, col, combo)
                    elif typ == 'button': # Если кнопка - вернуть кнопку/файл
                        btn = QPushButton(value)
                        btn.clicked.connect(lambda: self.upload_or_open(row, btn))
                        self.table.setCellWidget(row, col, btn)
            self.backup = [] # Очистка резервных данных
            self.colour() # Обновить цвет в колонке "Статус"
            self.update_filters() # Обновить фильтры

    def closeEvent(self, event): # НЕЛЬЗЯ ПЕРЕИМЕНОВЫВАТЬ
        '''Окно с вопросом "сохранить изменения?" при выходе из программы'''
        if QMessageBox.question(self, "Сохранение", "Сохранить изменения?", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.save_changes()  # Функция сохранения
            event.accept() # Разрешение закрыть окно
        else:
            event.accept()

    def save_changes(self):
        '''Подключение к SQL'''
        '''Сохранение изменений при выходе из программы'''
        db = QSqlDatabase.addDatabase("QPSQL") # Создание объекта для подключения к PostgreSQL
        db.setHostName("-")  # ЗАМЕНИТЬ НА НАШ ХОСТ
        db.setDatabaseName("-")  # ЗАМЕНИТЬ НА ИМЯ НАШЕЙ БД
        db.setUserName("-")  # ЗАМЕНИТЬ НА ЛОГИН (ПОЛЬЗОВАТЕЛЯ)
        db.setPassword("-")  # ЗАМЕНИТЬ НА ПАРОЛЬ
        db.setPort(5432) # стандартный порт PostgreSQL

        if not db.open(): # Проверка на успешность подключения
            print("Ошибка подключения:", db.lastError().text())
            return

        db.transaction() # Режим транзакции (защита от повреждений при сохранении)
        try:
            clear = QSqlQuery() # Для отправки SQL-запросов
            clear.exec_("DELETE FROM tasks;") # Удаление старых данных из таблицы

            query = QSqlQuery()
            query.prepare("""
                INSERT INTO tasks (
                    date, urgency, product, region, responsible,
                    stage, delivery, document, comment, file_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """) # Защита от текстов-команд

            for row in range(self.table.rowCount()): # Пройтись по всей таблице
                date = self._get_text(row, 0) # Собрать данные по всем строкам...
                urgency = self._get_combo_text(row, 1)
                product = self._get_text(row, 2)
                region = self._get_combo_text(row, 3)
                responsible = self._get_combo_text(row, 4)
                stage = self._get_combo_text(row, 5)
                delivery = self._get_text(row, 6)
                document = self._get_button_text(row, 7)
                comment = self._get_text(row, 8)
                file_path = self._get_text(row, 9)

                query.bindValue(0, date) #...передать собранные данные в базу
                query.bindValue(1, urgency)
                query.bindValue(2, product)
                query.bindValue(3, region)
                query.bindValue(4, responsible)
                query.bindValue(5, stage)
                query.bindValue(6, delivery)
                query.bindValue(7, document)
                query.bindValue(8, comment)
                query.bindValue(9, file_path)

                if not query.exec_():
                    raise Exception(query.lastError().text()) # Перехват ошибок

            db.commit() # Фиксация сохранения
            print("Данные сохранены.")
        except Exception as e:
            db.rollback() # Отмена изменений
            print("Ошибка сохранения:", e) # Перехват ошибок
        finally:
            db.close() # Закрытие соединения с бд
            QSqlDatabase.removeDatabase("QPSQL") # Удаления объекта подключения

    def load_data(self):
        '''Загрузка сохранённых данных из бд при открытии программы'''
        db = QSqlDatabase.addDatabase("QPSQL")
        db.setHostName("-") # ЗАМЕНИТЬ НА НАШ ХОСТ
        db.setDatabaseName("-") # ЗАМЕНИТЬ НА ИМЯ НАШЕЙ БД
        db.setUserName("-") # ЗАМЕНИТЬ НА ЛОГИН (ПОЛЬЗОВАТЕЛЯ)
        db.setPassword("-") # ЗАМЕНИТЬ НА ПАРОЛЬ
        db.setPort(5432) # Порт стандартный

        if not db.open(): # Перехват ошибок
            print("Ошибка подключения при загрузке:", db.lastError().text())
            return

        query = QSqlQuery("SELECT * FROM tasks ORDER BY id") # Запрос на загрузку данных из БД в таблицу при её открытии

        while query.next(): # Пройтись по всем записям, которые вернул SQL
            row = self.table.rowCount() # Кол-во строк
            self.table.insertRow(row) #Вставить новую строку

            # Заполнить новую строку текстом
            self.table.setItem(row, 0, QTableWidgetItem(query.value(1)))  # дата
            self.table.setItem(row, 2, QTableWidgetItem(query.value(3)))  # товар
            self.table.setItem(row, 6, QTableWidgetItem(query.value(7)))  # срок поставки
            self.table.setItem(row, 8, QTableWidgetItem(query.value(9)))  # комментарии
            self.table.setItem(row, 9, QTableWidgetItem(query.value(10)))  # путь к файлу

            # Заполнить новую строку виджетами
            # Срочность
            self._restore_combo(row, 1, ['Текущая', 'Срочно'], query.value(2))
            # Участок
            self._restore_combo(row, 3, ['IT', 'Бобинорезка', 'Воздух', 'Гофра', 'Грузовые', 'Кадры',
                                         'Качество В1', 'Качество Д3', 'Литьё В1', 'Литьё Д3',
                                         'Маркетинг', 'Офис', 'Охрана труда', 'Ремонт В1', 'Ремонт Д3',
                                         'Салон', 'Склад В1', 'Склад Д3', 'Упаковка В1', 'Упаковка Д3'], query.value(4))
            # Ответственный
            self._restore_combo(row, 4, ['Андреев А', 'Астанин А', 'Будылёва Т', 'Боярогло Е',
                                         'Васильев С', 'Ершова В', 'Заречнев С', 'Зеленская А',
                                         'Иванова А', 'Козьяков М', 'Кудуков А', 'Максимов А',
                                         'Мохов С.В', 'Муштатова Э', 'Петухов А', 'Сим К',
                                         'Туровцев И', 'Фомин А.В', 'Чернобривченко Т'], query.value(5))
            # Статус
            self._restore_combo(row, 5, ['Не просмотрено', 'В работе', 'Заказано', 'Доставлено', 'Отклонено'],
                                query.value(6))

            # Кнопка документа
            doc_text = query.value(8) or "Загрузить документ" # Название документа либо название кнопки
            btn = QPushButton(doc_text) # Сама новая кнопка
            btn.clicked.connect(lambda _, r=row: self.upload_or_open(r, btn)) # Привязка действий к нажатию кнопки
            self.table.setCellWidget(row, 7, btn) # Поместить кнопку в ячейку

        db.close() # Закрыть соединение с БД
        self.colour() # Применить цвет к колонке "Статус"
        self.update_filters() # Обновить фильтры
        print(f"Загружено {self.table.rowCount()} строк.")

#-----------------ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ------------------
    def _get_text(self, row, col):
        '''Достаёт текст из любой ячейки'''
        item = self.table.item(row, col) # Получить содержимое ячейки
        return item.text() if item else ""

    def _get_combo_text(self, row, col):
        '''Достаёт текст из любой ячейки с выпадающим списком'''
        widget = self.table.cellWidget(row, col) # Получить содержимое ячейки
        if isinstance(widget, QComboBox):
            return widget.currentText()
        return ""

    def _get_button_text(self, row, col):
        '''Достаёт текст ячейки с кнопкой'''
        widget = self.table.cellWidget(row, col) # Получить содержимое ячейки
        if isinstance(widget, QPushButton):
            return widget.text()
        return ""

    def _restore_combo(self, row, col, items, current_text):
        combo = QComboBox() # Выпадающий список
        combo.addItems(items) # Заполнить список
        combo.setCurrentText(current_text) # Установить последнее значение в момент сохранения
        self.table.setCellWidget(row, col, combo) # Разместить виджет
        if col == 5:
            combo.currentIndexChanged.connect(self.colour) # Обновление цвета для колонки "Статус"
        combo.currentIndexChanged.connect(self.update_filters) # Обновление фильтров (Кроме "Статус")

class NewParagraph(QStyledItemDelegate): # НАЗВАНИЯ МЕНЯТЬ НЕЛЬЗЯ!
    '''Привязка кнопки "Enter" к переносу текста на следующий абзац'''
    def createEditor(self, parent, option, index):
        editor = QPlainTextEdit(parent)
        editor.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        editor.setFixedHeight(60)
        return editor

    def setEditorData(self, editor, index):
        value = index.data(Qt.DisplayRole) or ""
        editor.setPlainText(value)

    def setModelData(self, editor, model, index):
        value = editor.toPlainText()
        model.setData(index, value)






if __name__ == "__main__":
    app = QApplication([])
    window = Database()
    window.show()
    app.exec()