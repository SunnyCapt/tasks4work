class GUISettings:
    line_count = 15  # you can change it
    first_wish_line_number = 2
    wish_view_count = line_count - 3
    last_wish_line_number = first_wish_line_number + wish_view_count
    navigation_buttons_line_number = line_count - 1
    zoom = line_count / 9


class ControllerSettings:
    db_name = "wishlist"
    db_user = "wishlist"
    db_password = "qwerty"
    db_port = 1488
