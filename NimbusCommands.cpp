#include <windows.h>
#include <algorithm>
#include <iostream>
#include <unordered_map>
#include <string>
#include <functional>
#include <iostream>
#include <string>
#include <NimbusCommands.hpp>


using namespace std;

volatile bool AutoOverride; //need to implement into smooth cursor 

POINT delta_finder(int xprime, int yprime) 
    {
    POINT start_point;
    GetCursorPos(&start_point);
    return {xprime - start_point.x, yprime - start_point.y};
    }
 
void cursor_jump(int dx, int dy) {
    //positive y is down
    //positive x is right
    POINT start_point;
    GetCursorPos(&start_point);
    SetCursorPos(start_point.x + dx, start_point.y + dy);
    }

void cursor_smooth(int dx, int dy, int movespeed) {
    
   
    POINT start_point;
    GetCursorPos(&start_point);
    
    int under = max(abs(dx), abs(dy));
    if (under == 0) under = 1;

    float y_step = (float)dy/under;
    float x_step = (float)dx/under;

    float move_x = start_point.x + x_step;
    float move_y = start_point.y + y_step;
    
    for (int i=0; i<=under; i++){

        SetCursorPos((int)move_x, (int)move_y);
        move_x += x_step;
        move_y += y_step;
        if (movespeed !=0 && i%movespeed == 0) Sleep(1);
        
        }
    Sleep(500);
    }
    
void flat_hold() {
    INPUT input = {};
    // ZeroMemory(&input, sizeof(INPUT));
    input.type = INPUT_MOUSE;
    input.mi.dwFlags = MOUSEEVENTF_LEFTDOWN;
    SendInput(1, &input, sizeof(INPUT));
    }

void flat_letgo(){
    INPUT input = {};
    input.type = INPUT_MOUSE;
    input.mi.dwFlags = MOUSEEVENTF_LEFTUP;
    SendInput(1, &input, sizeof(INPUT));
    }

void flat_select() {
    flat_hold();
    Sleep(5);
    flat_letgo();
    Sleep(5);
    }

void cursor_to_target(int targetx, int targety, int cursor_speed){
    POINT change = delta_finder(targetx, targety);
    cursor_smooth(change.x, change.y, cursor_speed);
}

void keyboard_string(string text, int typespeed){
    
    
    for (unsigned char current_char : text) 
        {
        Sleep(typespeed);
        INPUT input = {};
        input.type = INPUT_KEYBOARD;
        input.ki.wScan = current_char;
        input.ki.dwFlags = KEYEVENTF_UNICODE;
        SendInput(1, &input, sizeof(INPUT));


        input.ki.dwFlags = KEYEVENTF_KEYUP;
        SendInput(1, &input, sizeof(INPUT));
        }
}

void KeyCom(string Comm1, string Comm2in, string Comm3in, string Comm4in) 
    {
    unordered_map<string, unsigned short> keymap = 
            {
            {"ctrl", VK_CONTROL},
            {"shift", VK_SHIFT},
            {"alt", VK_MENU},
            {"tab", VK_TAB},
            {"enter", VK_RETURN},
            {"esc", VK_ESCAPE},
            {"space", VK_SPACE},
            {"up", VK_UP},
            {"down", VK_DOWN},
            {"left", VK_LEFT},
            {"right", VK_RIGHT},
            {"windows", VK_LWIN},
            {"backspace", VK_BACK},
            {"delete", VK_DELETE},
            {"play/pause", VK_MEDIA_PLAY_PAUSE},
            {"volume down", VK_VOLUME_DOWN},
            {"volume up", VK_VOLUME_UP},
            {"volume mute", VK_VOLUME_MUTE},
            {"caps", VK_CAPITAL},
            };

    unordered_map<string, function<void()>> comsend = 
            {
            {"copy", [](){KeyCom("ctrl", "C");}},
            {"paste",[](){KeyCom("ctrl", "V");}},
            {"cut",[](){KeyCom("ctrl", "X");}},
            {"select all",[](){KeyCom("ctrl", "A");}},
            {"undo",[](){KeyCom("ctrl", "Z");}},
            {"new tab",[](){KeyCom("ctrl", "T");}},
            {"close tab", [](){KeyCom("ctrl", "W");}},
            {"control enter", [](){KeyCom("ctrl", "enter");}},
            };
    
    if (comsend.count(Comm1)) {
        comsend[Comm1]();
        return; 
    }
    
    if (!keymap.count(Comm1)) return; 
    unsigned short Comm2;
    unsigned short Comm3;
    unsigned short Comm4;


    if (keymap.count(Comm2in))
        {Comm2 = keymap[Comm2in];} 
    else 
        {Comm2 = Comm2in[0];}
 
    if (keymap.count(Comm3in))
        {Comm3 = keymap[Comm3in];} 
    else 
        {Comm3 = Comm3in[0];}

    if (keymap.count(Comm4in))
        {Comm4 = keymap[Comm4in];} 
    else 
        {Comm4 = Comm4in[0];}

    //keys down
    INPUT inputs[8] = {};
    inputs[0].type = INPUT_KEYBOARD;
    inputs[0].ki.wVk = keymap[Comm1];

    inputs[1].type = INPUT_KEYBOARD;
    inputs[1].ki.wVk = Comm2;

    inputs[2].type = INPUT_KEYBOARD;
    inputs[2].ki.wVk = Comm3;

    inputs[3].type = INPUT_KEYBOARD;
    inputs[3].ki.wVk = Comm4;


    //keys up
    inputs[4].type = INPUT_KEYBOARD;
    inputs[4].ki.wVk = Comm4;
    inputs[4].ki.dwFlags = KEYEVENTF_KEYUP;

    inputs[5].type = INPUT_KEYBOARD;
    inputs[5].ki.wVk = Comm3;
    inputs[5].ki.dwFlags = KEYEVENTF_KEYUP;

    inputs[6].type = INPUT_KEYBOARD;
    inputs[6].ki.wVk = Comm2;
    inputs[6].ki.dwFlags = KEYEVENTF_KEYUP;

    inputs[7].type = INPUT_KEYBOARD;
    inputs[7].ki.wVk = keymap[Comm1];
    inputs[7].ki.dwFlags = KEYEVENTF_KEYUP;

    SendInput(8, inputs, sizeof(INPUT));
    }

void mouse_scroll(int scroll_amount) {
    INPUT input = {};
    input.type = INPUT_MOUSE;
    input.mi.dwFlags = MOUSEEVENTF_WHEEL;
    input.mi.mouseData = scroll_amount; //positive is up, negative is down
    SendInput(1, &input, sizeof(INPUT));
    }

void open_app(string app){
    KeyCom("windows");
    keyboard_string(app,2000);
    Sleep(750);
    KeyCom("enter");
    Sleep(1000);
}

void close_app(){
    KeyCom("alt", "F4");
}

int main()
{
    
    return 0;
}






































