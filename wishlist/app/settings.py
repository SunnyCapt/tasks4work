class GUISettings:
    line_count = 9
    first_wish_line_number = 2
    wish_view_count = line_count - 3
    last_wish_line_number = first_wish_line_number + wish_view_count
    navigation_buttons_line_number = line_count - 1
    zoom = line_count / 9


class DBSettings:
    host = "localhost"
    port = 3306
    user = "WishListUser"
    password = "53cr37"
    name = "wishlist"
    charset = "utf8"
