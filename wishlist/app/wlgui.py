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


# TODO:
#  порефакторить;
#  доделать контроллер;
#  добавить логгирование, аннотации и доки


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
        self._init_layout()
        self._init_labels()
        self._init_new_wish_textboxes()
        self._init_message_box()
        self._init_buttons()
        self.update_wishlist_view(True)

        self.setFixedSize(int(1100 * self._settings.zoom), int(800 * self._settings.zoom))
        self.setWindowTitle("Wish List")
        self._move_window_to_center()
        self.show()

    def _init_layout(self):
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.setAlignment(Qt.AlignTop)
        self.setLayout(grid)

    def _init_labels(self) -> None:
        for i, label_value in enumerate(self._labels):
            label = QLabel(
                f"<font color='red' size='5' face='SansSerif'>"
                f"{label_value.title()}"
                f"</font>"
            )
            label.setAlignment(Qt.AlignCenter | Qt.AlignTop)
            label.setMaximumHeight(50)
            self.layout().addWidget(label, 0, i)

    def _init_new_wish_textboxes(self) -> None:
        layout: QGridLayout = self.layout()
        for i in range(4):
            textbox = WLTextEdit(self._labels[i])
            textbox.setMaximumHeight(90)
            layout.addWidget(textbox, 1, i)
        button = QPushButton("+")
        button.setFixedSize(60, 80)
        button.clicked.connect(self._create_button_clicked)
        layout.addWidget(button, 1, 4)

    def _init_message_box(self):
        self._message_box = QMessageBox()
        self._message_box.resize(1000, 1000)

    def update_wishlist_view(self, is_init=False):
        count = self._settings.wish_view_count
        self._context["wish_count"] = 0
        wishes = self._controller.read(
            count,
            count * self._context["page"]
        )

        for wish in wishes:
            self._add_wish(wish)
        self._normalize_layout(is_init)
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

    def _normalize_layout(self, is_init):
        if self._context["wish_count"] == self._settings.wish_view_count:
            return

        range_to_fix = range(
            self._context["wish_count"] + self._settings.first_wish_line_number,
            self._settings.last_wish_line_number
        )

        for line in range_to_fix:
            self._replace_wish_line(line, [QLabel("") for _ in range(5)])

    def _move_window_to_center(self):
        qreact = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qreact.moveCenter(cp)
        self.move(qreact.topLeft())

    def _add_wish(self, src_wish: tuple) -> None:
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
        button.clicked.connect(self._delete_button_clicked)
        wish_widgets.append(button)
        self._replace_wish_line(line_number, wish_widgets)
        self._context["wish_count"] += 1

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

        self._previous_button = QPushButton("<<")
        self._previous_button.setFixedSize(60, 80)
        self._previous_button.clicked.connect(self._previous_button_clicked)
        self._previous_button.setVisible(False)

        self._next_button = QPushButton(">>")
        self._next_button.setFixedSize(60, 80)
        self._next_button.clicked.connect(self._next_button_clicked)
        self._next_button.setVisible(False)

        layout.addWidget(self._previous_button, self._settings.navigation_buttons_line_number, 0)
        layout.addWidget(self._next_button, self._settings.navigation_buttons_line_number, 4)

    def show_message(self, text, title="Error", info=""):
        self._message_box.setText(text)
        self._message_box.setWindowTitle(title)
        self._message_box.setInformativeText(info)
        self._message_box.show()

    def _previous_button_clicked(self):
        print(f"clicked `{self.sender().text()}` button")
        self._context["page"] -= 1
        self.update_wishlist_view()

    def _next_button_clicked(self):
        print(f"clicked `{self.sender().text()}` button")
        self._context["page"] += 1
        self.update_wishlist_view()

    def _create_button_clicked(self):
        sender: WLPushButton = self.sender()
        layout: QGridLayout = self.layout()
        index = layout.indexOf(sender)
        textboxes: List[WLTextEdit] = [layout.itemAt(i).widget() for i in range(index - 4, index)]
        new_wish = {}
        for textbox in textboxes:
            new_wish.update({textbox.label: textbox.toPlainText()})
            textbox.setText("")
        try:
            self._controller.create(**new_wish)
            self.update_wishlist_view()
        except ValueError as e:
            self.show_message(str(e))
            wish_item.undo()
        except Exception as e:
            # todo: logging error
            print(repr(e))
            self.show_message("Failed to update")
            wish_item.undo()

    def _delete_button_clicked(self):
        sender: WLPushButton = self.sender()
        self._controller.delete(sender.wish_id)
        self.update_wishlist_view()

    def eventFilter(self, obj, event):
        if WLTextEdit.is_wish_instance(obj):
            self._wish_textbox_event_handler(obj, event)
        return super().eventFilter(obj, event)

    def _wish_textbox_event_handler(self, wish_item, event):
        if event.type() == QEvent.FocusIn:
            print("in focus")
            self._on_focus_wish(wish_item)
        elif not wish_item.is_changed_now:
            if event.type() == QEvent.KeyPress:
                if event.key() == Qt.Key_Return:
                    print("changed value")
                    self._on_changed_wish(wish_item)
                elif event.key() == Qt.Key_Escape:
                    print("set previous value")
                    wish_item.undo()
                elif event.key() == Qt.Key_Tab:
                    self.on_tab(wish_item)
            elif event.type() == QEvent.FocusOut:
                print("changed value")
                wish_item.is_changed_now = True
                self._on_changed_wish(wish_item)

    def _on_focus_wish(self, wish_item):
        wish_item.setCursorWidth(1)
        wish_item.setTextCursor(wish_item.textCursor())
        wish_item.is_changed_now = False
        wish_item.previous_value = wish_item.toPlainText()

    def _on_changed_wish(self, wish_item: WLTextEdit):
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
                print(repr(e))
                self.show_message("Failed to update")
                wish_item.undo()
        wish_item.clearFocus()

    @classmethod
    def run(cls):
        app = QApplication(sys.argv)
        app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        window = cls()
        sys.exit(app.exec_())
