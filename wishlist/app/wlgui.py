import sys
import json
import qdarkstyle

from typing import List
from PyQt5.QtCore import (QEvent, Qt)
from PyQt5.Qt import QDesktopWidget
from PyQt5.QtWidgets import (
    QPushButton, QTextEdit, QWidget, QGridLayout,
    QLabel, QMessageBox, QApplication
)

from controller import Controller
from settings import GUISettings

# TODO: added logging


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
        self.set_alignment()

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
    def __init__(self, settings=GUISettings, parent=None):
        super().__init__(parent=parent)
        self._controller = Controller()
        self._labels = ("title", "price", "link", "note")
        self._context = {"wish_count": 0, "page": 0}
        self._settings = settings
        self.initUI()

    def initUI(self):
        self.init_layout()
        self.init_labels()
        self.init_new_wish_textboxes()
        self.init_message_box()
        self.init_buttons()
        self.update_wishlist_view()

        self.setFixedSize(int(1100 * self._settings.zoom), int(800 * self._settings.zoom))
        self.setWindowTitle("Wish List")
        self.move_window_to_center()
        self.show()

    def init_layout(self):
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.setAlignment(Qt.AlignTop)
        self.setLayout(grid)

    def init_labels(self):
        for i, label_value in enumerate(self._labels):
            label = QLabel(
                f"<font color='red' size='5' face='SansSerif'>"
                f"{label_value.title()}"
                f"</font>"
            )
            label.setAlignment(Qt.AlignCenter | Qt.AlignTop)
            label.setMaximumHeight(50)
            self.layout().addWidget(label, 0, i)

    def init_new_wish_textboxes(self):
        layout = self.layout()
        for i in range(4):
            textbox = WLTextEdit(self._labels[i])
            textbox.setMaximumHeight(90)
            layout.addWidget(textbox, 1, i)
        button = QPushButton("+")
        button.setFixedSize(60, 80)
        button.clicked.connect(self.create_button_clicked)
        layout.addWidget(button, 1, 4)

    def init_message_box(self):
        self._message_box = QMessageBox()
        self._message_box.resize(1000, 1000)

    def update_wishlist_view(self):
        count = self._settings.wish_view_count
        self._context["wish_count"] = 0
        wishes = self._controller.read(
            count,
            count * self._context["page"]
        )

        for wish in wishes:
            self.add_wish(wish)
        self.normalize_layout()
        need_show_next_button = self._controller.count() - self._context["page"] * \
                                self._settings.wish_view_count > self._context["wish_count"]
        if need_show_next_button:
            self._next_button.setVisible(True)
        elif self._next_button.isVisible():
            self._next_button.setVisible(False)

        if self._context["page"] > 0:
            self._previous_button.setVisible(True)
        elif self._previous_button.isVisible():
            self._previous_button.setVisible(False)

    def normalize_layout(self):
        if self._context["wish_count"] == self._settings.wish_view_count:
            return

        range_to_fix = range(
            self._context["wish_count"] + self._settings.first_wish_line_number,
            self._settings.last_wish_line_number
        )

        for line in range_to_fix:
            self.replace_wish_line(line, [QLabel("") for _ in range(5)])

    def move_window_to_center(self):
        qreact = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qreact.moveCenter(cp)
        self.move(qreact.topLeft())

    def add_wish(self, src_wish: tuple):
        if self._context["wish_count"] > (self._settings.wish_view_count - 1):
            return

        line_number = self._settings.first_wish_line_number + self._context["wish_count"]
        wish_widgets = []
        for i in range(4):
            textbox = WLTextEdit(self._labels[i], f"{src_wish[i + 1]}", src_wish[0], self)
            textbox.setMaximumHeight(80)
            textbox.installEventFilter(self)
            wish_widgets.append(textbox)
        button = WLPushButton("x", src_wish[0])
        button.setFixedSize(60, 80)
        button.clicked.connect(self.delete_button_clicked)
        wish_widgets.append(button)
        self.replace_wish_line(line_number, wish_widgets)
        self._context["wish_count"] += 1

    def replace_wish_line(self, line, widgets):
        layout = self.layout()
        for i in range(5):
            item_widget = layout.itemAtPosition(line, i)
            if item_widget is not None:
                widget = item_widget.widget()
                layout.removeWidget(widget)
                widget.deleteLater()
            layout.addWidget(widgets[i], line, i)

    def init_buttons(self):
        layout = self.layout()

        self._previous_button = QPushButton("<<")
        self._previous_button.setFixedSize(60, 80)
        self._previous_button.clicked.connect(self.previous_button_clicked)
        self._previous_button.setVisible(False)

        self._next_button = QPushButton(">>")
        self._next_button.setFixedSize(60, 80)
        self._next_button.clicked.connect(self.next_button_clicked)
        self._next_button.setVisible(False)

        layout.addWidget(self._previous_button, self._settings.navigation_buttons_line_number, 0)
        layout.addWidget(self._next_button, self._settings.navigation_buttons_line_number, 4)

    def show_message(self, text, title="Error", info=""):
        self._message_box.setText(text)
        self._message_box.setWindowTitle(title)
        self._message_box.setInformativeText(info)
        self._message_box.show()

    def previous_button_clicked(self):
        self._context["page"] -= 1
        self.update_wishlist_view()

    def next_button_clicked(self):
        self._context["page"] += 1
        self.update_wishlist_view()

    def create_button_clicked(self):
        sender = self.sender()
        layout = self.layout()
        index = layout.indexOf(sender)
        textboxes = [layout.itemAt(i).widget() for i in range(index - 4, index)]
        new_wish = {}
        for textbox in textboxes:
            new_wish.update({textbox.label: textbox.toPlainText()})
            textbox.setText("")
        try:
            self._controller.create(**new_wish)
        except ValueError as e:
            self.show_message(str(e))
            return
        except Exception as e:
            # todo: logging error
            print(repr(e))
            self.show_message("Failed to update")
            return
        self.update_wishlist_view()

    def delete_button_clicked(self):
        sender = self.sender()
        self._controller.delete(sender.wish_id)
        self.update_wishlist_view()

    def eventFilter(self, obj, event):
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
            elif event.type() == QEvent.FocusOut:
                print("changed value")
                wish_item.is_changed_now = True
                self.on_changed_wish(wish_item)

    def on_focus_wish(self, wish_item):
        wish_item.setCursorWidth(1)
        wish_item.setTextCursor(wish_item.textCursor())
        wish_item.is_changed_now = False
        wish_item.previous_value = wish_item.toPlainText()

    def on_changed_wish(self, wish_item):
        current_value = wish_item.toPlainText()
        if current_value.strip(" \n") != wish_item.previous_value.strip(" \n"):
            to_update = {"id": wish_item.wish_id, wish_item.label: current_value}
            try:
                self._controller.update(to_update)
            except ValueError as e:
                self.show_message(str(e))
                wish_item.undo()
            except Exception as e:
                # todo: logging error
                print(e)
                self.show_message("Failed to update")
                wish_item.undo()
        wish_item.clearFocus()

    @classmethod
    def run(cls):
        app = QApplication(sys.argv)
        app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        window = cls()
        sys.exit(app.exec_())
