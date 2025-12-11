# Bring in C++ std::string
from libcpp.string cimport string as cpp_string


# Tell Cython that these functions exist in NimbusCommands.hpp
cdef extern from "NimbusCommands.hpp" namespace "":
    void cursor_jump(int dx, int dy)
    void cursor_smooth(int dx, int dy, int movespeed)
    void flat_hold()
    void flat_letgo()
    void flat_select()
    void cursor_to_target(int targetx, int targety, int cursor_speed)
    void keyboard_string(cpp_string text, int typespeed)
    void KeyCom(cpp_string Comm1,
                cpp_string Comm2in,
                cpp_string Comm3in,
                cpp_string Comm4in)
    void mouse_scroll(int scroll_amount)
    void open_app(cpp_string app)
    void close_app()


# ----------------- PYTHON WRAPPER FUNCTIONS -----------------

def py_cursor_jump(dx, dy):
    cursor_jump(dx, dy)


def py_cursor_smooth(dx, dy, movespeed):
    cursor_smooth(dx, dy, movespeed)


def py_flat_hold():
    flat_hold()


def py_flat_letgo():
    flat_letgo()


def py_flat_select():
    flat_select()


def py_cursor_to_target(targetx, targety, cursor_speed):
    cursor_to_target(targetx, targety, cursor_speed)


def py_keyboard_string(text, typespeed):
    # Convert Python string -> C++ std::string
    cdef cpp_string s = text.encode("utf-8")
    keyboard_string(s, typespeed)


def py_KeyCom(Comm1, Comm2, Comm3, Comm4):
    # Convert Python strings -> C++ std::string
    cdef cpp_string c1 = Comm1.encode("utf-8")
    cdef cpp_string c2 = Comm2.encode("utf-8")
    cdef cpp_string c3 = Comm3.encode("utf-8")
    cdef cpp_string c4 = Comm4.encode("utf-8")
    KeyCom(c1, c2, c3, c4)


def py_mouse_scroll(scroll_amount):
    mouse_scroll(scroll_amount)


def py_open_app(app):
    cdef cpp_string s = app.encode("utf-8")
    open_app(s)


def py_close_app():
    close_app()
