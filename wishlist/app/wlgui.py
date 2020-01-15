import sys
from typing import List

from PyQt5.QtCore import (QEvent, Qt)
from PyQt5.Qt import QDesktopWidget
from PyQt5.QtWidgets import (
    QPushButton, QTextEdit, QWidget, QGridLayout,
    QLabel, QMessageBox, QApplication
)

from controller import Controller


# TODO:
#  сделать сеттингсы нормальные;
#  добавить стили;
#  определять размер окна в зависимости от размера экрана;
#  порефакторить;
#  доделать контроллер;
#  добавить логгирование, аннотации и доки


class settings:
    line_count = 15  # you can change it
    first_wish_line_number = 2
    wish_view_count = line_count - 3
    last_wish_line_number = first_wish_line_number + wish_view_count
    navigation_buttons_line_number = line_count - 1
    window_width = int(1100 * line_count / 9)
    window_height = int(800 * line_count / 9)


class WLPushButton(QPushButton):
    def __init__(self, text, wish_id, parent=None):
        super(WLPushButton, self).__init__(parent)
        self.setText(text)
        self.wish_id = wish_id


class WLTextEdit(QTextEdit):
    def __init__(self, label, text="", wish_id=None, parent=None):
        super(WLTextEdit, self).__init__(parent)
        self.previous_value = text
        self.setText(text)
        self.label = label
        self.wish_id = wish_id
        self.is_changed_now = False

    @classmethod
    def is_wish_instance(cls, obj):
        return isinstance(obj, cls) and obj.wish_id is not None

    def setText(self, p_str):
        super().setText(p_str)
        self.set_alignment()

    def undo(self):
        super().undo()
        self.clearFocus()

    def set_alignment(self):
        self.setAlignment(Qt.AlignCenter)

    def clearFocus(self):
        self.setCursorWidth(0)
        super().clearFocus()


class WLWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.controller = Controller()
        self.labels = ("title", "price", "link", "note")
        self.context = {"wish_count": 0, "page": 0}
        self.initUI()

    def initUI(self):
        self._init_layout()
        self._init_labels()
        self._init_new_wish_textboxes()
        self._init_message_box()
        self._init_buttons()
        self.update_wishlist_view(True)

        self.setFixedSize(settings.window_width, settings.window_height)
        self.setWindowTitle("Wish List")
        self._move_window_to_center()
        self.show()

    def _init_layout(self):
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.setAlignment(Qt.AlignTop)
        self.setLayout(grid)

    def _init_labels(self) -> None:
        for i, label_value in enumerate(self.labels):
            label = QLabel(label_value)
            label.setAlignment(Qt.AlignCenter | Qt.AlignTop)
            label.setMaximumHeight(50)
            self.layout().addWidget(label, 0, i)

    def _init_new_wish_textboxes(self) -> None:
        layout: QGridLayout = self.layout()
        for i in range(4):
            textbox = WLTextEdit(self.labels[i])
            textbox.set_alignment()
            textbox.setMaximumHeight(90)
            layout.addWidget(textbox, 1, i)
        button = QPushButton("+")
        button.setMaximumSize(60, 90)
        button.clicked.connect(self.create_button_clicked)
        layout.addWidget(button, 1, 4)

    def _init_message_box(self):
        self.message_box = QMessageBox()
        self.message_box.resize(1000, 1000)

    def update_wishlist_view(self, is_init=False):
        count = settings.wish_view_count
        self.context["wish_count"] = 0
        wishes = self.controller.read(
            count,
            count * self.context["page"]
        )

        for wish in wishes:
            self._add_wish(wish)
        self._normalize_layout(is_init)
        need_show_next_button = self.controller.count() - self.context["page"] * \
                                settings.wish_view_count > self.context["wish_count"]
        if need_show_next_button:
            self.next_button.setVisible(True)
        elif self.next_button.isVisible():
            self.next_button.setVisible(False)

        if self.context["page"] > 0:
            self.previous_button.setVisible(True)
        elif self.previous_button.isVisible():
            self.previous_button.setVisible(False)

    def _normalize_layout(self, is_init):
        if self.context["wish_count"] == settings.wish_view_count:
            return

        range_to_fix = range(
            self.context["wish_count"] + settings.first_wish_line_number,
            settings.last_wish_line_number
        )

        for line in range_to_fix:
            self._replace_wish_line(line, [QLabel("") for _ in range(5)])

    def _move_window_to_center(self):
        qreact = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qreact.moveCenter(cp)
        self.move(qreact.topLeft())

    def _add_wish(self, src_wish: tuple) -> None:
        if self.context["wish_count"] > (settings.wish_view_count - 1):
            return

        line_number = settings.first_wish_line_number + self.context["wish_count"]
        wish_widgets = []
        for i in range(4):
            textbox = WLTextEdit(self.labels[i], f"{src_wish[i + 1]}", src_wish[0], self)
            textbox.set_alignment()
            textbox.setMaximumHeight(80)
            textbox.installEventFilter(self)
            wish_widgets.append(textbox)
        button = WLPushButton("x", src_wish[0])
        button.setMaximumSize(60, 80)
        button.clicked.connect(self.delete_button_clicked)
        wish_widgets.append(button)
        self._replace_wish_line(line_number, wish_widgets)
        self.context["wish_count"] += 1

    def _replace_wish_line(self, line, widgets):
        layout = self.layout()
        for i in range(5):
            item_widget = layout.itemAtPosition(line, i)
            if item_widget is not None:
                widget: QWidget = item_widget.widget()
                layout.removeWidget(widget)
                widget.deleteLater()
            layout.addWidget(widgets[i], line, i)

    def _init_buttons(self):
        layout: QGridLayout = self.layout()

        self.previous_button = QPushButton("<<")
        self.previous_button.setMaximumSize(60, 80)
        self.previous_button.clicked.connect(self._previous_button_clicked)
        self.previous_button.setVisible(False)

        self.next_button = QPushButton(">>")
        self.next_button.setMaximumSize(60, 80)
        self.next_button.clicked.connect(self._next_button_clicked)
        self.next_button.setVisible(False)

        layout.addWidget(self.previous_button, settings.navigation_buttons_line_number, 0)
        layout.addWidget(self.next_button, settings.navigation_buttons_line_number, 4)

    def show_message(self, text, title="Error", info=""):
        self.message_box.setText(text)
        self.message_box.setWindowTitle(title)
        self.message_box.setInformativeText(info)
        self.message_box.show()

    def _previous_button_clicked(self):
        print(f"clicked `{self.sender().text()}` button")
        self.context["page"] -= 1
        self.update_wishlist_view()

    def _next_button_clicked(self):
        print(f"clicked `{self.sender().text()}` button")
        self.context["page"] += 1
        self.update_wishlist_view()

    def create_button_clicked(self):
        sender: WLPushButton = self.sender()
        layout: QGridLayout = self.layout()
        index = layout.indexOf(sender)
        textboxes: List[WLTextEdit] = [layout.itemAt(i).widget() for i in range(index - 4, index)]
        new_wish = {}
        for textbox in textboxes:
            new_wish.update({textbox.label: textbox.toPlainText()})
            textbox.setText("")
        try:
            self.controller.create(**new_wish)
            self.update_wishlist_view()
        except Exception as e:
            print(e)

    def delete_button_clicked(self):
        sender: WLPushButton = self.sender()
        self.controller.delete(sender.wish_id)
        self.update_wishlist_view()

    def eventFilter(self, obj: WLTextEdit, event):
        if WLTextEdit.is_wish_instance(obj):
            self.wish_textbox_event_handler(obj, event)
        return super().eventFilter(obj, event)

    def wish_textbox_event_handler(self, wish_item, event):
        if event.type() == QEvent.FocusIn:
            print("in focus")
            self.on_focus_wish(wish_item)
        elif not wish_item.is_changed_now:
            if event.type() == QEvent.KeyPress:
                if event.key() == Qt.Key_Return:
                    print("changed value")
                    self.on_changed_wish(wish_item)
                elif event.key() == Qt.Key_Escape:
                    print("set previous value")
                    wish_item.undo()
                elif event.key() == Qt.Key_Tab:
                    self.on_tab(wish_item)
            elif event.type() == QEvent.FocusOut:
                print("changed value")
                wish_item.is_changed_now = True
                self.on_changed_wish(wish_item)

    def on_focus_wish(self, wish_item):
        wish_item.setCursorWidth(1)
        wish_item.setTextCursor(wish_item.textCursor())
        wish_item.is_changed_now = False
        wish_item.previous_value = wish_item.toPlainText()

    def on_changed_wish(self, wish_item: WLTextEdit):
        current_value = wish_item.toPlainText()
        if current_value.strip(" \n") != wish_item.previous_value.strip(" \n"):
            to_update = {"id": wish_item.wish_id, wish_item.label: current_value}
            self.controller.update(to_update)
        wish_item.clearFocus()

    @classmethod
    def run(cls):
        app = QApplication(sys.argv)
        window = cls()
        sys.exit(app.exec_())


if __name__ == "__main__":
    WLWidget.run()
