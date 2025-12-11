#include <string>
using namespace std;

void cursor_jump(int dx, int dy);

void cursor_smooth(int dx, int dy, int movespeed = 70);

void flat_hold();

void flat_letgo();

void flat_select();

void cursor_to_target(int targetx, int targety, int cursor_speed = 0);

void keyboard_string(string text, int typespeed = 0);

void KeyCom(string Comm1, string Comm2in = "", string Comm3in = "", string Comm4in = "");

void mouse_scroll(int scroll_amount);

void open_app(string app);

void close_app();





